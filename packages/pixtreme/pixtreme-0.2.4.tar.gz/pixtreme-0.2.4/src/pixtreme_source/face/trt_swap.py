from typing import Optional

import cupy as cp
import cupyx.scipy.ndimage as ndi
import tensorrt as trt

from ..color.bgr import bgr_to_rgb, rgb_to_bgr
from ..transform.resize import INTER_AUTO, resize
from ..utils.dimention import batch_to_images, images_to_batch, images_to_batch_pixelshift, pixelshift_fuse
from ..utils.dtypes import to_float32
from .emap import load_emap
from .schema import PxFace


class TrtFaceSwap:
    def __init__(self, *, model_path: Optional[str] = None, model_bytes: Optional[bytes] = None, device_id: int = 0) -> None:
        self.device_id = device_id
        with cp.cuda.Device(self.device_id):
            logger = trt.Logger(trt.Logger.WARNING)
            runtime = trt.Runtime(logger)

            if model_path:
                with open(model_path, "rb") as f:
                    model_bytes = f.read()
            if model_bytes is None:
                raise ValueError("model_path / model_bytes の指定が必要です")

            self.engine = runtime.deserialize_cuda_engine(model_bytes)
            self.ctx = self.engine.create_execution_context()
            self.stream = cp.cuda.Stream()
            print("TensorRT engine ✓")

            # ---- バインディングを次元数で判定 -----------------------------
            self.target_name, self.source_name = None, None
            self.d_inputs: dict[str, Optional[cp.ndarray]] = {}
            self.d_outputs: dict[str, cp.ndarray] = {}

            for name in self.engine:
                if self.engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT:
                    if len(self.engine.get_tensor_shape(name)) == 4:
                        self.target_name = name
                    else:  # len == 2
                        self.source_name = name
                    self.d_inputs[name] = None  # 遅延確保
                else:
                    dtype = trt.nptype(self.engine.get_tensor_dtype(name))
                    shape = tuple(max(int(s), 1) for s in self.engine.get_tensor_shape(name))
                    buf = cp.empty(shape, dtype=dtype)
                    self.d_outputs[name] = buf
                    self.ctx.set_tensor_address(name, buf.data.ptr)

            if not self.target_name or not self.source_name:
                raise RuntimeError("target/source バインディング検出失敗")

            self.patch = 128
            self.input_mean, self.input_std = 0.0, 1.0
            self.emap = cp.asarray(load_emap(), dtype=cp.float32)

            self.output_names = [name for name in self.engine if self.engine.get_tensor_mode(name) == trt.TensorIOMode.OUTPUT]

    # --------------------------------------------------------------------- #
    def forward(self, batch: cp.ndarray, latent: cp.ndarray) -> cp.ndarray:
        # 1. shape を純 Python int 化
        img_shape = tuple(int(x) for x in batch.shape)  # (N,3,128,128)
        lat_shape = (int(latent.shape[0]), 512)  # (N,512)

        print("img_shape :", batch.shape, "->", img_shape, batch.dtype)
        print("lat_shape :", latent.shape, "->", lat_shape, latent.dtype)
        print("target dims engine:", self.engine.get_tensor_shape(self.target_name))
        print("source dims engine:", self.engine.get_tensor_shape(self.source_name))
        print("Outputs :", self.output_names)

        # 2. TensorRT に登録
        self.ctx.set_input_shape(self.target_name, img_shape)
        self.ctx.set_input_shape(self.source_name, lat_shape)

        # 3. 入力バッファを必要に応じて確保
        for name, need_shape, src in [(self.target_name, img_shape, batch), (self.source_name, lat_shape, latent)]:
            if self.d_inputs[name] is None or self.d_inputs[name].shape != need_shape:
                buf = cp.empty(need_shape, dtype=src.dtype)
                self.d_inputs[name] = buf
                self.ctx.set_tensor_address(name, buf.data.ptr)
                print(f"{name} src shape    :", src.shape)

                print(f"{name}input buffer shape :", buf.shape)
            self.d_inputs[name][:] = src if name == self.source_name else (src - self.input_mean) / self.input_std

        # 4. 出力バッファもバッチごとに確保し直す
        out_shape = (img_shape[0], 3, 128, 128)  # (N,3,128,128)
        out_name = self.output_names[0]
        if self.d_outputs[out_name].shape != out_shape:
            buf = cp.empty(out_shape, dtype=self.d_outputs[out_name].dtype)
            self.d_outputs[out_name] = buf
            self.ctx.set_tensor_address(out_name, buf.data.ptr)

        # 5. 推論
        self.ctx.execute_async_v3(self.stream.ptr)
        self.stream.synchronize()

        return cp.copy(self.d_outputs[out_name])

    def get(
        self, target_image: cp.ndarray | list[cp.ndarray], latent: cp.ndarray, max_batch: int = 16
    ) -> cp.ndarray | list[cp.ndarray]:
        """
        Inference with TensorRT face swap model.

        Args:
            target_image (cp.ndarray | list[cp.ndarray]): Input image(s) of shape (H, W, C) or list of such images.
            latent (cp.ndarray): Latent vector of shape (1, 512).
            max_batch (int): Maximum batch size for inference. Default is 16.

        """

        batch = images_to_batch(
            target_image,
            scalefactor=1 / self.input_std,
            size=(self.patch, self.patch),
            mean=self.input_mean,
            swap_rb=True,
            layout="HWC",
        )
        latent_row = cp.asarray(latent, cp.float32).reshape(-1, 512)

        batch_size = batch.shape[0]
        if batch_size > max_batch:
            # If batch size exceeds max_batch, split into smaller batches
            preds = []
            for start in range(0, batch_size, max_batch):
                end = min(start + max_batch, batch_size)
                batch_part = batch[start:end]
                latent_part = cp.repeat(latent_row, batch_part.shape[0], axis=0)
                preds_part = self.forward(batch_part, latent_part)
                preds.append(preds_part)
            preds = cp.concatenate(preds, axis=0)
        else:
            # If batch size is within max_batch, process the entire batch
            latent_row = cp.repeat(latent_row, batch_size, axis=0)
            preds = self.forward(batch, latent_row)  # バッチを TensorRT に登録

        output_images = batch_to_images(preds, swap_rb=True, layout="NCHW")

        if len(output_images) == 1:
            return output_images[0]
        else:
            return output_images

    # --------------------------------------------------------------------- #
    def get_subpixel(self, target_image: cp.ndarray, latent: cp.ndarray, max_batch: int = 16):
        """
        Inference with subpixel pixelshift.

        Args:
            target_image (cp.ndarray): Input image of shape (H, W, C).
            latent (cp.ndarray): Latent vector of shape (1, 512).

        Returns:
            cp.ndarray: Output image of shape (H, W, C).

        Description:
            The input image is in BGR format.
            Input image is divided into dim² tiles of size (dim, dim).
            Auto-calculate dim from target_image height. # dim = H // 128.
            Forward the tiles in batches of max_batch.
            Combine the results using pixelshift_fuse.
            The output image is in BGR format.
        """
        h, w, _ = target_image.shape
        dim = h // self.patch

        batch = images_to_batch_pixelshift(
            target_image, dim=dim, scalefactor=1 / self.input_std, mean=self.input_mean, swap_rb=True
        )
        N, C, Hs, Ws = batch.shape  # N = dim²
        H_out, W_out = Hs * dim, Ws * dim  # output size (H, W)

        # Buffer for pixelshift_fuse
        acc = cp.zeros((C, H_out, W_out), dtype=cp.float32)
        hits = cp.zeros((1, H_out, W_out), dtype=cp.int32)

        # 512-d latent vector
        latent_row = cp.asarray(latent, cp.float32).reshape(-1, 512)

        for start in range(0, N, max_batch):
            end = min(start + max_batch, N)
            _batch = batch[start:end]  # ≤16 max_batch
            latent_b = cp.repeat(latent_row, _batch.shape[0], axis=0)

            preds = self.forward(_batch, latent_b)  # (N, C, Hs, Ws)
            pixelshift_fuse(preds, acc, hits, start_idx=start, dim=dim)

        fused = acc / hits  # mean
        output_image = fused.transpose(1, 2, 0)  # (C, H, W) -> (H, W, C)
        output_image = rgb_to_bgr(output_image)
        output_image = to_float32(output_image)
        return output_image

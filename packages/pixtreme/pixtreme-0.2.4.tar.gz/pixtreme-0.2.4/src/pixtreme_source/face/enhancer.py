import cupy as cp
import onnxruntime

from ..color.bgr import rgb_to_bgr
from ..transform.resize import INTER_AUTO, resize
from ..utils.dimention import batch_to_images, images_to_batch, images_to_batch_pixelshift, pixelshift_fuse
from ..utils.dlpack import to_cupy, to_numpy
from ..utils.dtypes import to_float32


class GFPGAN:
    def __init__(self, model_file, *args, **kwargs):
        self.session = onnxruntime.InferenceSession(model_file, **kwargs)
        self.input_size = 512
        self.input_name = self.session.get_inputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape
        print(f"GFPGAN model loaded: {model_file}")
        print(f"Input name: {self.input_name}, Input shape: {self.input_shape}")

    def get(self, image: cp.ndarray | list[cp.ndarray]) -> cp.ndarray | list[cp.ndarray]:
        image = to_float32(image)

        print(f"GFPGAN: Processing image(s) with shape: {image.shape}")

        batch = images_to_batch(
            image,
            scalefactor=2.0,
            size=self.input_size,
            mean=0.5,
            swap_rb=True,
            layout="HWC",
        )

        batch = to_numpy(batch)
        preds = self.session.run(None, {self.input_name: batch})
        preds = to_cupy(preds[0])

        images = batch_to_images(preds, scalefactor=2.0, mean=0.5, swap_rb=True, layout="NCHW")

        if len(images) == 1:
            return images[0]
        else:
            return images

    def get_subpixel(self, image: cp.ndarray) -> cp.ndarray:
        """
        Apply GFPGAN to enhance the input image(s) with subpixel pixelshift.

        Args:
            image (cp.ndarray | list[cp.ndarray]): Input image(s) of shape (H, W, C) or list of such images.

        Returns:
            cp.ndarray | list[cp.ndarray]: Enhanced image(s).
        """
        print("GFPGAN.get_subpixel: Running FaceEnhancer with subpixel pixelshift...")
        print(f"GFPGAN.get_subpixel: Processing image with shape: {image.shape}")
        max_batch: int = 1

        h, w, _ = image.shape
        dim = h // self.input_size

        print(f"GFPGAN.get_subpixel: Image dimensions (H, W): ({h}, {w}), dim: {dim}")

        if dim == 1:
            dim = 2
            print("GFPGAN.get_subpixel: Image is smaller than input size, resizing...")
            image = resize(image, (self.input_size * dim, self.input_size * dim), interpolation=INTER_AUTO)

        batch = images_to_batch_pixelshift(
            image,
            dim=dim,
            scalefactor=2.0,
            mean=0.5,
            swap_rb=True,
        )
        N, C, Hs, Ws = batch.shape  # N = dim²
        H_out, W_out = Hs * dim, Ws * dim  # output size (H, W)
        print(f"GFPGAN.get_subpixel: Batch shape: {batch.shape}, Output size: ({H_out}, {W_out})")

        acc = cp.zeros((C, H_out, W_out), dtype=cp.float32)
        hits = cp.zeros((1, H_out, W_out), dtype=cp.int32)

        batch = to_numpy(batch)

        for start in range(0, N, max_batch):
            end = min(start + max_batch, N)
            _batch = batch[start:end]
            preds = self.session.run(None, {self.input_name: _batch})
            pixelshift_fuse(to_cupy(preds[0]), acc, hits, start_idx=start, dim=dim)

        fused = acc / hits  # mean
        output_image = fused.transpose(1, 2, 0)  # (C, H, W) -> (H, W, C)

        output_image /= 2.0  # Rescale to [0, 1] range
        output_image += cp.array((0.5, 0.5, 0.5), dtype=output_image.dtype)

        output_image = rgb_to_bgr(output_image)
        output_image = to_float32(output_image)

        return output_image

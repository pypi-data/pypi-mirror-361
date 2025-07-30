from typing import Optional

import cupy as cp
import numpy as np
import tensorrt as trt

from ..utils.dimention import images_to_batch
from .emap import load_emap
from .schema import PxFace


class TrtFaceEmbedding:
    def __init__(self, model_path: Optional[str] = None, model_bytes: Optional[bytes] = None, device_id: int = 0) -> None:
        """
        Initialize the TrtFaceEmbedding.

        Args:
            model_path (str): Path to the TensorRT engine file.
            model_bytes (bytes): TensorRT engine bytes.
            device_id (int): CUDA device ID.
        Raises:
            FileNotFoundError: If the specified path does not exist.
        """

        self.device_id = device_id
        self.emap = cp.asarray(load_emap())

        with cp.cuda.Device(self.device_id):
            # Load the TensorRT engine
            self.logger = trt.Logger(trt.Logger.WARNING)
            self.runtime = trt.Runtime(self.logger)

            if model_path is not None:
                with open(model_path, "rb") as f:
                    model_bytes = f.read()

            if model_bytes is None:
                raise ValueError("model_bytes must be provided if model_path is not specified")

            self.engine = self.runtime.deserialize_cuda_engine(model_bytes)
            self.ctx = self.engine.create_execution_context()

            print("face embedding engine loaded ✔  tensors:", self.engine)

            self.initialize()

    def initialize(self):
        """Initialize processing"""
        # Prepare CuPy stream and device buffers
        self.stream = cp.cuda.Stream()
        self.d_inputs = {}
        self.d_outputs = {}

        # Automatically get tensor names
        input_names = []
        output_names = []

        for name in self.engine:
            shape = self.ctx.get_tensor_shape(name)
            dtype = trt.nptype(self.engine.get_tensor_dtype(name))

            # Convert TensorRT shape to list for CuPy compatibility
            shape_list = [int(dim) for dim in shape]

            # Create a CuPy array for the tensor
            d_arr = cp.empty(shape_list, dtype=dtype)

            if self.engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT:
                self.d_inputs[name] = d_arr
                input_names.append(name)
            else:
                self.d_outputs[name] = d_arr
                output_names.append(name)

        # Use the first input/output tensor names
        self.input_tensor = input_names[0] if input_names else "input"
        self.output_tensor = output_names[0] if output_names else "output"
        self.output_names = output_names

        # Set tensor addresses only once during initialization
        for name in self.engine:
            if self.engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT:
                self.ctx.set_tensor_address(name, self.d_inputs[name].data.ptr)
            else:
                self.ctx.set_tensor_address(name, self.d_outputs[name].data.ptr)

        # Get input/output shapes
        input_shape = list(self.d_inputs[self.input_tensor].shape)
        output_shape = list(self.d_outputs[self.output_tensor].shape)

        self.input_shape = input_shape
        self.output_shape = output_shape
        self.input_size = tuple(input_shape[2:4][::-1]) if len(input_shape) >= 4 else (112, 112)

        # Set normalization parameters
        # For face embedding models, typically use these values
        # TODO: Could be auto-detected from ONNX graph analysis like in original FaceEmbedding
        self.input_mean = 127.5 / 255.0
        self.input_std = 127.5 / 255.0

        print(f"Input shape: {self.input_shape}")
        print(f"Output shape: {self.output_shape}")
        print(f"Input size: {self.input_size}")
        print(f"Normalization - mean: {self.input_mean}, std: {self.input_std}")

        # Buffer pool
        self.input_buffer = None
        self.output_buffer = None

    def forward(self, images: list[cp.ndarray] | cp.ndarray) -> cp.ndarray:
        """Forward pass using TensorRT"""
        print("TrtFaceEmbedding: Forward pass started")

        if not isinstance(images, list):
            images = [images]

        # Convert images to blob format
        # blob = to_blobs(imgs, 1.0 / self.input_std, input_size, (self.input_mean, self.input_mean, self.input_mean))
        batch = images_to_batch(images=[images], scalefactor=1.0 / self.input_std, size=self.input_size, mean=self.input_mean)

        # Copy input data to GPU buffer
        in_gpu = self.d_inputs[self.input_tensor]
        if in_gpu.shape != batch.shape:
            # Explicitly delete old buffer
            del self.d_inputs[self.input_tensor]
            # Allocate new buffer
            in_gpu = cp.empty(batch.shape, dtype=batch.dtype)
            self.d_inputs[self.input_tensor] = in_gpu
            # Reset tensor address
            self.ctx.set_tensor_address(self.input_tensor, in_gpu.data.ptr)

        # Copy data
        in_gpu[:] = batch

        # Execute the TensorRT engine asynchronously
        self.ctx.execute_async_v3(self.stream.ptr)

        # Wait for inference completion
        self.stream.synchronize()

        # Get output data
        out_gpu = self.d_outputs[self.output_tensor]

        # Return a copy to avoid memory issues
        return cp.copy(out_gpu).flatten()

    def get(self, face: PxFace) -> cp.ndarray:
        """Extract embedding for a single face"""

        # Use CuPy for GPU processing in TensorRT version
        # image = bgr_to_rgb(face.image)
        # image = to_float32(image)

        embedding = self.forward(face.image)

        # Calculate normalized embedding
        normed_embedding = embedding / cp.linalg.norm(embedding)
        latent = normed_embedding.reshape((1, -1))
        latent = cp.dot(latent, self.emap)
        latent = latent / cp.linalg.norm(latent)

        return latent

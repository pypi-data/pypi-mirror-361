import argparse
import os
import timeit

import cupy as cp
import pytest

import pixtreme_source as px


@pytest.fixture
def source_image_path():
    return "examples/example2.png"


@pytest.fixture
def target_image_path():
    return "examples/target"


@pytest.fixture
def output_image_path():
    return "examples/output.png"


def test_trt_face(source_image_dir: str, target_dir: str, output_dir: str):
    detector = px.TrtFaceDetection(model_path="models/face/detection.trt")
    print("Face detection model loaded successfully.")

    embedding = px.TrtFaceEmbedding(model_path="models/face/embedding.trt")
    print("Face embedding model loaded successfully.")

    swapper = px.TrtFaceSwap(model_path="models/face/swap.trt")
    print("Face swap model loaded successfully.")

    enhancer = px.GFPGAN(model_file="models/face/GFPGANv1.4.onnx")
    print("GFPGAN model loaded successfully.")

    # enhancer2 = px.TorchUpscaler(model_path="models/1x_Loupe_Portrait_DeJpeg_v2_net_g_318000.pth")

    # upscaler = px.TorchUpscaler(model_path="models/4xFaceUpDAT.pth")
    upscaler = px.TorchUpscaler(model_path="models/2x_Loupe_Portrait_DeJpeg_v3_net_g_214000.pth")
    print("Upscaler model loaded successfully.")

    mask = px.create_rounded_mask(dsize=(512, 512), mask_offsets=(0.2, 0.2, 0.2, 0.2), density=1, blur_size=51, sigma=16.0)
    print("Mask created successfully.")

    source_image_pathes = []
    for root, dirs, files in os.walk(source_image_dir):
        for file in files:
            if file.endswith((".png", ".jpg", ".jpeg")):
                source_image_pathes.append(os.path.join(root, file))

    for source_image_path in source_image_pathes:
        if not os.path.exists(source_image_path):
            raise FileNotFoundError(f"Source image not found: {source_image_path}")

        source_image = px.imread(source_image_path)
        source_image = px.to_float32(source_image)
        print("Source image loaded successfully.")

        source_faces = detector.get(source_image)
        source_face = source_faces[0] if source_faces else None
        assert source_face is not None, "No face detected in source image."
        source_face = embedding.get(source_face)
        print("Source face detected and embedded successfully.")

        square_black_image = cp.zeros_like(source_face.image)

        target_pathes = []
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                # if "_shape" in file:
                #    continue
                if file.endswith((".png", ".jpg", ".jpeg")):
                    target_pathes.append(os.path.join(root, file))

        for target_image_path in target_pathes:
            if not os.path.exists(target_image_path):
                raise FileNotFoundError(f"Target image not found: {target_image_path}")

            target_relative_dir = os.path.dirname(os.path.relpath(target_image_path, start=target_dir))
            output_image_dir = os.path.join(output_dir, target_relative_dir)
            os.makedirs(output_image_dir, exist_ok=True)

            source_file_name = os.path.basename(source_image_path).split(".")[0]
            target_file_name = os.path.basename(target_image_path).split(".")[0]
            output_image_path = os.path.abspath(
                os.path.join(output_image_dir, f"{source_file_name}_vs_{target_file_name}.png")
            )

            if os.path.exists(output_image_path):
                print(f"Output image already exists: {output_image_path}. Skipping...")
                continue

            target_image: cp.ndarray = px.imread(target_image_path)
            target_image = px.to_float32(target_image)

            if target_image.shape[0] < 768 or target_image.shape[1] < 768:
                if target_image.shape[0] < target_image.shape[1]:
                    new_height = 768
                    new_width = int(target_image.shape[1] * (768 / target_image.shape[0]))
                    target_image = px.resize(target_image, dsize=(new_width, new_height), interpolation=px.INTER_AUTO)
                else:
                    new_width = 768
                    new_height = int(target_image.shape[0] * (768 / target_image.shape[1]))
                    target_image = px.resize(target_image, dsize=(new_width, new_height), interpolation=px.INTER_AUTO)

            print(f"Target image size: {target_image.shape[0]}x{target_image.shape[1]}")
            print("Target image loaded successfully.")

            start = timeit.default_timer()
            pasted_image = None

            target_faces = detector.get(target_image)
            target_face = target_faces[0] if target_faces else None

            if len(target_faces) == 0 or target_face is None:
                print("No face detected in target image. Skipping...")

                _sample_images = px.stack_images(
                    [source_face.image, square_black_image, square_black_image, square_black_image],
                    axis=0,
                )

                black_target_image = cp.zeros_like(target_image)

                _result = px.stack_images([target_image, _sample_images, black_target_image], axis=1)

                px.imwrite(output_image_path, _result)
                continue

            target_face = embedding.get(target_face)
            print("Target face detected and embedded successfully.")

            original_target_face_image = target_face.image
            target_face.image = enhancer.get(target_face.image)

            swapped_face_image: cp.ndarray = swapper.get(target_face, source_face)
            e_swapped_face_image = enhancer.get(swapped_face_image)
            # e_swapped_face_image = enhancer2.get(e_swapped_face_image)
            u_swapped_face_image = upscaler.get(e_swapped_face_image)
            assert target_face.matrix is not None, "Target face matrix is None."
            M = target_face.matrix * 2
            pasted_image = px.paste_back(target_image=target_image, paste_image=u_swapped_face_image, M=M, mask=mask)
            print("Face swap completed successfully.")

            end = timeit.default_timer()
            print(f"Processed in {end - start:.2f} seconds.")

            assert pasted_image is not None, "Face swap failed."

            sample_images = px.stack_images(
                [source_face.image, original_target_face_image, swapped_face_image, u_swapped_face_image],
                axis=0,
            )

            result = px.stack_images([target_image, sample_images, pasted_image], axis=1)
            result = px.to_uint8(result)

            px.imwrite(output_image_path, result)
            print(f"Output image saved to {output_image_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test TRT Face Swap")
    parser.add_argument("--source_dir", type=str, default="examples/hige/source", help="Path to the source image directory")
    parser.add_argument("--target_dir", type=str, default="examples/hige/target", help="Path to the target image directory")
    parser.add_argument(
        "--output_dir", type=str, default="examples/hige/output", help="Path to save the output image directory"
    )
    args = parser.parse_args()

    members = [
        "1_Vo",
        "2_Gt",
        "3_Sax",
        "4_Drs",
    ]

    for member in members:
        source_dir = os.path.join(args.source_dir, member)
        target_dir = os.path.join(args.target_dir, member)
        output_dir = os.path.join(args.output_dir, member)
        os.makedirs(output_dir, exist_ok=True)
        print(f"Testing for member: {member}")
        test_trt_face(source_dir, target_dir, output_dir)

    print("Test completed successfully.")

from pathlib import Path
import json
import shutil

from PIL import Image


# ============================================================
# IMAGE PIPELINE
# ============================================================

def validate_image(image_path):
    """
    Validate that the image exists and can be opened.
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image file not found: {image_path}"
        )

    if not image_path.is_file():
        raise ValueError(
            f"Image path is not a file: {image_path}"
        )

    try:
        with Image.open(image_path) as image:
            image.verify()

    except Exception as error:
        raise ValueError(
            f"Invalid or unreadable image: {error}"
        )

    return True


# ============================================================
# IMAGE METADATA
# ============================================================

def get_image_metadata(image_path):
    """
    Read basic metadata from an image.
    """

    image_path = Path(image_path)

    validate_image(image_path)

    with Image.open(image_path) as image:

        metadata = {
            "file_name": image_path.name,
            "file_format": image.format,
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
        }

    return metadata


# ============================================================
# REQUEST-SPECIFIC FOLDER
# ============================================================

def create_request_folder(
    request_id,
    output_root="outputs/requests",
):
    """
    Create a folder for a specific sofa request.
    """

    output_root = Path(output_root)

    request_folder = (
        output_root / str(request_id)
    )

    request_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    return request_folder


# ============================================================
# STORE ORIGINAL IMAGE
# ============================================================

def store_original_image(
    image_path,
    request_folder,
):
    """
    Copy the original image into the request folder.
    """

    image_path = Path(image_path)
    request_folder = Path(request_folder)

    validate_image(image_path)

    destination = (
        request_folder / "original_image"
    ).with_suffix(
        image_path.suffix.lower()
    )

    shutil.copy2(
        image_path,
        destination,
    )

    return destination


# ============================================================
# SAVE IMAGE METADATA
# ============================================================

def save_image_metadata(
    metadata,
    request_folder,
):
    """
    Save image metadata as JSON.
    """

    request_folder = Path(request_folder)

    metadata_path = (
        request_folder /
        "image_metadata.json"
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
        )

    return metadata_path


# ============================================================
# OPTIONAL RESIZED IMAGE
# ============================================================

def create_resized_image(
    image_path,
    request_folder,
    max_size=1280,
):
    """
    Create an optional resized copy for future
    image processing.

    The original image remains unchanged.
    """

    image_path = Path(image_path)
    request_folder = Path(request_folder)

    validate_image(image_path)

    resized_path = (
        request_folder /
        "processing_image.jpg"
    )

    with Image.open(image_path) as image:

        image = image.convert("RGB")

        image.thumbnail(
            (max_size, max_size)
        )

        image.save(
            resized_path,
            format="JPEG",
            quality=90,
        )

    return resized_path


# ============================================================
# COMPLETE IMAGE PIPELINE
# ============================================================

def process_image(
    image_path,
    request_id,
    output_root="outputs/requests",
    create_resized=True,
):
    """
    Complete Phase 2 image pipeline.

    Steps:
        1. Validate image
        2. Read metadata
        3. Create request folder
        4. Copy original image
        5. Save metadata
        6. Optionally create processing image
    """

    image_path = Path(image_path)

    # --------------------------------------------------------
    # 1. Validate image
    # --------------------------------------------------------

    validate_image(image_path)


    # --------------------------------------------------------
    # 2. Read metadata
    # --------------------------------------------------------

    metadata = get_image_metadata(
        image_path
    )


    # --------------------------------------------------------
    # 3. Create request folder
    # --------------------------------------------------------

    request_folder = create_request_folder(
        request_id=request_id,
        output_root=output_root,
    )


    # --------------------------------------------------------
    # 4. Copy original image
    # --------------------------------------------------------

    original_image_path = (
        store_original_image(
            image_path=image_path,
            request_folder=request_folder,
        )
    )


    # --------------------------------------------------------
    # 5. Save metadata
    # --------------------------------------------------------

    metadata["request_id"] = str(
        request_id
    )

    metadata_path = save_image_metadata(
        metadata=metadata,
        request_folder=request_folder,
    )


    # --------------------------------------------------------
    # 6. Optional processing image
    # --------------------------------------------------------

    processing_image_path = None

    if create_resized:

        processing_image_path = (
            create_resized_image(
                image_path=image_path,
                request_folder=request_folder,
            )
        )


    # --------------------------------------------------------
    # Return pipeline result
    # --------------------------------------------------------

    return {
        "request_id": str(request_id),

        "request_folder": str(
            request_folder
        ),

        "original_image": str(
            original_image_path
        ),

        "metadata_file": str(
            metadata_path
        ),

        "processing_image": (
            str(processing_image_path)
            if processing_image_path
            else None
        ),

        "metadata": metadata,
    }
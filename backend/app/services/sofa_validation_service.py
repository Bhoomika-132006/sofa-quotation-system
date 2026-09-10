from pathlib import Path

from PIL import Image


def validate_sofa_image(image_path):
    """
    Basic Phase 3 image validation.

    Checks:
    1. Image exists
    2. Image can be opened
    3. Image has valid dimensions
    4. Basic visual properties are collected

    This is a basic validation layer.
    Advanced YOLO-based sofa/component detection
    will be added separately.
    """

    image_path = Path(image_path)

    # --------------------------------------------------------
    # Check file exists
    # --------------------------------------------------------

    if not image_path.exists():
        return {
            "valid": False,
            "detected_object": None,
            "predicted_type": None,
            "reason": "Image file does not exist.",
        }

    if not image_path.is_file():
        return {
            "valid": False,
            "detected_object": None,
            "predicted_type": None,
            "reason": "Image path is not a file.",
        }

    # --------------------------------------------------------
    # Open image
    # --------------------------------------------------------

    try:

        with Image.open(image_path) as image:

            image_width = image.width
            image_height = image.height
            image_format = image.format
            image_mode = image.mode

    except Exception as error:

        return {
            "valid": False,
            "detected_object": None,
            "predicted_type": None,
            "reason": f"Unable to open image: {error}",
        }

    # --------------------------------------------------------
    # Validate dimensions
    # --------------------------------------------------------

    if image_width <= 0 or image_height <= 0:

        return {
            "valid": False,
            "detected_object": None,
            "predicted_type": None,
            "reason": "Invalid image dimensions.",
        }

    # --------------------------------------------------------
    # Basic aspect ratio
    # --------------------------------------------------------

    aspect_ratio = (
        float(image_width) / float(image_height)
    )

    # --------------------------------------------------------
    # Phase 3 basic prediction
    # --------------------------------------------------------
    #
    # At this stage we do NOT claim true AI detection.
    # We only classify the uploaded reference image
    # as a valid image and mark the sofa type as
    # pending visual/YOLO validation.
    # --------------------------------------------------------

    result = {
        "valid": True,
        "detected_object": "unknown",
        "predicted_type": "pending_visual_validation",

        "image_width": image_width,
        "image_height": image_height,
        "aspect_ratio": round(aspect_ratio, 4),
        "image_format": image_format,
        "image_mode": image_mode,

        "bbox": None,
        "mask_path": None,

        "validation_status": "IMAGE_VALID",
        "reason": (
            "Image is valid and can be processed. "
            "Sofa classification requires the Phase 3 "
            "visual detection model."
        ),
    }

    return result
from pathlib import Path

from backend.app.services.sofa_validation_service import (
    validate_sofa_image,
)


# ============================================================
# Find the latest Phase 2 request automatically
# ============================================================

OUTPUT_ROOT = Path("outputs/requests")

request_folders = [
    folder
    for folder in OUTPUT_ROOT.iterdir()
    if folder.is_dir()
    and folder.name != "phase2_test_001"
]


if not request_folders:
    print("No Phase 2 request folders found.")
    print("Please generate a quotation with an uploaded image first.")
    raise SystemExit(1)


# Latest request folder
latest_request_folder = max(
    request_folders,
    key=lambda folder: folder.stat().st_mtime,
)


# ============================================================
# Find the original image automatically
# ============================================================

original_images = list(
    latest_request_folder.glob("original_image.*")
)


if not original_images:
    print("No original image found in:")
    print(latest_request_folder)
    raise SystemExit(1)


IMAGE_PATH = original_images[0]


# ============================================================
# Run Phase 3 validation
# ============================================================

try:

    result = validate_sofa_image(IMAGE_PATH)

    print()
    print("=" * 60)
    print("PHASE 3 SOFA IMAGE VALIDATION TEST")
    print("=" * 60)

    print("Request Folder:")
    print(latest_request_folder)

    print()
    print("Image:")
    print(IMAGE_PATH)

    print()
    print("Validation Result:")

    for key, value in result.items():
        print(f"{key}: {value}")

    print("=" * 60)

except Exception as error:

    print()
    print("=" * 60)
    print("PHASE 3 VALIDATION TEST FAILED")
    print("=" * 60)
    print("Error:", error)
    print("=" * 60)
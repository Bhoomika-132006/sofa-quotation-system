import sys
from pathlib import Path

from app.services.image_pipeline import process_image


if len(sys.argv) < 2:
    print("Please provide an image path.")
    print('Example: python backend\\test_image_pipeline.py ".\\uploads\\image.jpg"')
    sys.exit(1)


IMAGE_PATH = Path(sys.argv[1])
REQUEST_ID = "phase2_test_001"


try:
    result = process_image(
        image_path=IMAGE_PATH,
        request_id=REQUEST_ID,
        output_root="outputs/requests",
        create_resized=True,
    )

    print()
    print("=" * 60)
    print("IMAGE PIPELINE TEST SUCCESSFUL")
    print("=" * 60)
    print("Request ID:", result["request_id"])
    print("Request Folder:", result["request_folder"])
    print("Original Image:", result["original_image"])
    print("Metadata File:", result["metadata_file"])
    print("Processing Image:", result["processing_image"])

    print()
    print("Image Metadata:")

    for key, value in result["metadata"].items():
        print(f"  {key}: {value}")

    print("=" * 60)

except Exception as error:

    print()
    print("=" * 60)
    print("IMAGE PIPELINE TEST FAILED")
    print("=" * 60)
    print("Error:", error)
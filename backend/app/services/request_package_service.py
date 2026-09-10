from pathlib import Path
import json
import csv


def create_request_package(
    request_folder,
    request_data,
    quotation,
):
    """
    Create Phase 2 request package files.

    Files created:
        request_summary.json
        quote_summary.json
        bom.csv
        cost.csv
    """

    request_folder = Path(request_folder)
    request_folder.mkdir(parents=True, exist_ok=True)

    # ========================================================
    # REQUEST SUMMARY
    # ========================================================

    request_summary = {
        "request_id": request_data.get("request_id"),
        "sofa_type": request_data.get("sofa_type"),
        "seating_capacity": request_data.get("seating_capacity"),
        "dimensions_mm": request_data.get("dimensions_mm"),
        "master_template": request_data.get("master_template"),
        "customer": {
            "name": request_data.get("customer_name"),
            "phone": request_data.get("customer_phone"),
        },
        "image": {
            "original_path": request_data.get("image_path"),
            "processing_path": request_data.get("processing_image"),
            "metadata_path": request_data.get("metadata_file"),
        },
        "scale_factors": request_data.get("scale_factors"),
    }

    request_summary_path = (
        request_folder / "request_summary.json"
    )

    with open(
        request_summary_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            request_summary,
            file,
            indent=4,
            default=str,
        )

    # ========================================================
    # QUOTE SUMMARY
    # ========================================================

    quote_summary = {
        "quotation_id": quotation.get("quotation_id"),
        "quotation_number": quotation.get("quotation_number"),
        "request_id": request_data.get("request_id"),
        "material_cost": quotation.get("material_cost"),
        "labour_cost": quotation.get("labour_cost"),
        "stitching_cost": quotation.get("stitching_cost"),
        "overhead": quotation.get("overhead"),
        "production_cost": quotation.get("production_cost"),
        "profit": quotation.get("profit"),
        "final_price": quotation.get("final_price"),
    }

    quote_summary_path = (
        request_folder / "quote_summary.json"
    )

    with open(
        quote_summary_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            quote_summary,
            file,
            indent=4,
            default=str,
        )

    # ========================================================
    # BOM CSV
    # ========================================================

    bom_path = request_folder / "bom.csv"

    with open(
        bom_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "Component",
                "Material",
                "Base Quantity",
                "Scaled Quantity",
                "Unit",
                "Unit Price INR",
                "Total Price INR",
            ]
        )

        for item in quotation.get("items", []):

            writer.writerow(
                [
                    item.get("component_name", ""),
                    item.get("material_name", ""),
                    item.get("base_quantity", 0),
                    item.get("scaled_quantity", 0),
                    item.get("unit", ""),
                    item.get("unit_price_inr", 0),
                    item.get("total_price_inr", 0),
                ]
            )

    # ========================================================
    # COST CSV
    # ========================================================

    cost_path = request_folder / "cost.csv"

    with open(
        cost_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "Cost Component",
                "Amount INR",
            ]
        )

        writer.writerow(
            ["Material Cost", quotation.get("material_cost", 0)]
        )

        writer.writerow(
            ["Labour Cost", quotation.get("labour_cost", 0)]
        )

        writer.writerow(
            ["Stitching Cost", quotation.get("stitching_cost", 0)]
        )

        writer.writerow(
            ["Overhead", quotation.get("overhead", 0)]
        )

        writer.writerow(
            ["Production Cost", quotation.get("production_cost", 0)]
        )

        writer.writerow(
            ["Profit", quotation.get("profit", 0)]
        )

        writer.writerow(
            ["Final Price", quotation.get("final_price", 0)]
        )

    return {
        "request_summary": str(request_summary_path),
        "quote_summary": str(quote_summary_path),
        "bom_csv": str(bom_path),
        "cost_csv": str(cost_path),
    }
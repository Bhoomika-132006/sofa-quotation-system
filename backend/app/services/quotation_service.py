from datetime import datetime
import secrets

from backend.app.database import get_connection
from backend.app.services.pricing_service import (
    get_current_material_prices,
)

def get_costing_parameters():
    """
    Get active costing parameters from PostgreSQL.
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    parameter_name,
                    parameter_value
                FROM public.costing_parameters
                WHERE is_active = TRUE
                ORDER BY parameter_name;
            """)

            rows = cur.fetchall()

            parameters = {
                row[0]: float(row[1])
                for row in rows
            }

            return parameters

    finally:
        conn.close()

def calculate_material_cost(scaled_items, current_prices):
    """
    Calculate material cost:

        scaled quantity × material unit cost
    """

    prices_by_material = {
        price["material_id"]: price
        for price in current_prices
    }

    total_material_cost = 0.0
    quotation_items = []

    for item in scaled_items:

        material_id = item["material_id"]

        price = prices_by_material.get(material_id)

        if price is None:
            raise ValueError(
                f"No material price found for material ID {material_id}."
            )

        scaled_quantity = float(
            item["scaled_quantity"]
        )

        unit_price = float(
            price["unit_price_inr"]
        )

        line_total = scaled_quantity * unit_price

        quotation_items.append({
            "bom_item_id": item.get("bom_item_id"),
            "component_name": item.get("component_name"),
            "material_id": material_id,
            "material_name": item.get(
                "material_name",
                price["material_name"]
            ),
            "base_quantity": float(
                item.get("base_quantity", item.get("quantity", 0))
            ),
            "scaled_quantity": scaled_quantity,
            "unit": item["unit"],
            "material_unit": price["material_unit"],
            "unit_price_inr": unit_price,
            "total_price_inr": line_total,
        })

        total_material_cost += line_total

    return total_material_cost, quotation_items


def calculate_costs(material_cost, costing_parameters):

    labour = float(
        costing_parameters.get("LABOUR_COST", 0)
    )

    stitching = float(
        costing_parameters.get("STITCHING_COST", 0)
    )

    overhead = float(
        costing_parameters.get("OVERHEAD_COST", 0)
    )

    transportation = 0.0

    profit = float(
        costing_parameters.get("PROFIT_MARGIN", 0)
    )

    production_cost = (
        material_cost
        + labour
        + stitching
        + overhead
    )

    final_price = production_cost + profit

    return {
        "material_cost": material_cost,
        "labour_cost": labour,
        "stitching_cost": stitching,
        "overhead": overhead,
        "production_cost": production_cost,
        "profit": profit,
        "final_price": final_price,
    }


def build_quotation(
    request_id,
    scaled_items,
    current_prices=None,
):

    if current_prices is None:
        current_prices = get_current_material_prices()

    costing_parameters = get_costing_parameters()

    material_cost, material_bill = calculate_material_cost(
        scaled_items,
        current_prices,
    )

    costs = calculate_costs(
        material_cost,
        costing_parameters,
    )

    return {
        "quotation_number": generate_quotation_number(),
        "request_id": request_id,
        **costs,
        "items": material_bill,
    }


def generate_quotation_number():

    timestamp = datetime.now().strftime("%Y%m%d")

    random_part = secrets.token_hex(4).upper()

    return f"QT-{timestamp}-{random_part}"


def save_quotation(quotation):

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            # Save quotation summary
            cur.execute("""
                INSERT INTO public.quotations
                (
                    request_id,
                    material_cost,
                    labour_cost,
                    stitching_cost,
                    overhead,
                    production_cost,
                    profit,
                    final_price
                )
                VALUES
                (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                RETURNING id;
            """, (
                quotation["request_id"],
                quotation["material_cost"],
                quotation["labour_cost"],
                quotation["stitching_cost"],
                quotation["overhead"],
                quotation["production_cost"],
                quotation["profit"],
                quotation["final_price"],
            ))

            quotation_id = cur.fetchone()[0]

            # Save individual BOM/material items
            for item in quotation["items"]:

                cur.execute("""
                    INSERT INTO public.quotation_items
                    (
                        quotation_id,
                        bom_item_id,
                        component_name,
                        material_id,
                        quantity,
                        unit,
                        unit_price_inr,
                        total_price_inr
                    )
                    VALUES
                    (
                        %s, %s, %s, %s,
                        %s, %s, %s, %s
                    );
                """, (
                    quotation_id,
                    item.get("bom_item_id"),
                    item.get("component_name"),
                    item["material_id"],
                    item["scaled_quantity"],
                    item["unit"],
                    item["unit_price_inr"],
                    item["total_price_inr"],
                ))

            conn.commit()

            return quotation_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
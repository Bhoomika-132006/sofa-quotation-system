from datetime import datetime
import secrets

from backend.app.database import get_connection
from backend.app.services.pricing_service import (
    get_current_material_prices,
)


def get_costing_parameters():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    parameter_name,
                    parameter_type,
                    parameter_value,
                    unit
                FROM costing_parameters
                WHERE is_active = TRUE
                  AND effective_from <= CURRENT_DATE
                  AND (
                      effective_to IS NULL
                      OR effective_to >= CURRENT_DATE
                  )
                ORDER BY parameter_name
            """)

            rows = cur.fetchall()

            return {
                row[0]: {
                    "parameter_type": row[1],
                    "parameter_value": float(row[2]),
                    "unit": row[3],
                }
                for row in rows
            }

    finally:
        conn.close()


def calculate_material_cost(
    scaled_items,
    current_prices,
):
    """
    Calculate the material bill from:

        scaled quantity × current database price

    Material prices are never hardcoded.
    """

    prices_by_material = {
        price["material_id"]: price
        for price in current_prices
    }

    total_material_cost = 0.0
    quotation_items = []

    for item in scaled_items:

        material_id = item["material_id"]

        price = prices_by_material.get(
            material_id
        )

        if price is None:
            raise ValueError(
                "No active material price found "
                f"for material ID {material_id}."
            )

        scaled_quantity = float(
            item["scaled_quantity"]
        )

        unit_price = float(
            price["unit_price_inr"]
        )

        line_total = (
            scaled_quantity * unit_price
        )

        quotation_items.append({
            "bom_item_id": item.get(
                "bom_item_id"
            ),

            "component_id": item[
                "component_id"
            ],

            "component_name": item.get(
                "component_name"
            ),

            "material_id": material_id,

            "material_name": item.get(
                "material_name",
                price["material_name"]
            ),

            "base_quantity": float(
                item.get("quantity", 0)
            ),

            "scaled_quantity": scaled_quantity,

            "unit": item["unit"],

            "material_unit": price[
                "material_unit"
            ],

            "unit_price_inr": unit_price,

            "total_price_inr": line_total,

            "price_effective_from": price[
                "effective_from"
            ],

            "price_effective_to": price[
                "effective_to"
            ],

            "price_source": price[
                "source"
            ],
        })

        total_material_cost += line_total

    return (
        total_material_cost,
        quotation_items,
    )


def calculate_costs(
    material_cost,
    costing_parameters,
):

    def get_value(name):

        parameter = (
            costing_parameters.get(name)
        )

        if parameter is None:
            return 0.0

        return float(
            parameter["parameter_value"]
        )

    labour = get_value(
        "LABOUR_COST"
    )

    stitching = get_value(
        "STITCHING_COST"
    )

    overhead = get_value(
        "OVERHEAD_COST"
    )

    transportation = get_value(
        "TRANSPORTATION_COST"
    )

    profit_parameter = (
        costing_parameters.get(
            "PROFIT_MARGIN"
        )
    )

    if profit_parameter is None:

        profit = 0.0

    elif (
        profit_parameter["parameter_type"]
        == "PERCENTAGE"
    ):

        profit_base = (
            material_cost
            + labour
            + stitching
            + overhead
            + transportation
        )

        profit = (
            profit_base
            * get_value("PROFIT_MARGIN")
            / 100
        )

    else:

        profit = get_value(
            "PROFIT_MARGIN"
        )

    subtotal = (
        material_cost
        + labour
        + stitching
        + overhead
        + transportation
    )

    total = (
        subtotal + profit
    )

    return {
        "material_cost_inr": material_cost,
        "labour_cost_inr": labour,
        "stitching_cost_inr": stitching,
        "overhead_inr": overhead,
        "transportation_cost_inr": transportation,
        "profit_inr": profit,
        "subtotal_inr": subtotal,
        "total_inr": total,
    }


def build_quotation(
    quotation_number,
    sofa_model_id,
    scaled_items,
    current_prices=None,
):
    """
    Build the quotation using database-driven
    material prices and costing parameters.
    """

    if current_prices is None:
        current_prices = (
            get_current_material_prices()
        )

    costing_parameters = (
        get_costing_parameters()
    )

    material_cost, material_bill = (
        calculate_material_cost(
            scaled_items,
            current_prices,
        )
    )

    costs = calculate_costs(
        material_cost,
        costing_parameters,
    )

    return {
        "quotation_number":
            quotation_number,

        "sofa_model_id":
            sofa_model_id,

        **costs,

        "items":
            material_bill,
    }


def generate_quotation_number():

    timestamp = (
        datetime.now()
        .strftime("%Y%m%d")
    )

    random_part = (
        secrets.token_hex(4)
        .upper()
    )

    return (
        f"QT-{timestamp}-{random_part}"
    )


def save_quotation(
    quotation,
    customer_name=None,
    customer_phone=None,
):

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO quotations
                (
                    quotation_number,
                    sofa_model_id,
                    customer_name,
                    customer_phone,
                    subtotal_inr,
                    labour_cost_inr,
                    stitching_cost_inr,
                    overhead_inr,
                    profit_inr,
                    transportation_cost_inr,
                    total_amount_inr,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING quotation_id
            """, (
                quotation[
                    "quotation_number"
                ],

                quotation[
                    "sofa_model_id"
                ],

                customer_name,

                customer_phone,

                quotation[
                    "subtotal_inr"
                ],

                quotation[
                    "labour_cost_inr"
                ],

                quotation[
                    "stitching_cost_inr"
                ],

                quotation[
                    "overhead_inr"
                ],

                quotation[
                    "profit_inr"
                ],

                quotation[
                    "transportation_cost_inr"
                ],

                quotation[
                    "total_inr"
                ],

                "DRAFT",
            ))

            quotation_id = (
                cur.fetchone()[0]
            )

            for item in quotation["items"]:

                cur.execute("""
                    INSERT INTO quotation_items
                    (
                        quotation_id,
                        component_id,
                        material_id,
                        quantity,
                        unit,
                        unit_price_inr,
                        total_price_inr
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                """, (
                    quotation_id,

                    item[
                        "component_id"
                    ],

                    item[
                        "material_id"
                    ],

                    item[
                        "scaled_quantity"
                    ],

                    item[
                        "unit"
                    ],

                    item[
                        "unit_price_inr"
                    ],

                    item[
                        "total_price_inr"
                    ],
                ))

            conn.commit()

            return quotation_id

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()
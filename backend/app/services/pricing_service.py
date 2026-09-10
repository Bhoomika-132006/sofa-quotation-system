from datetime import date

from backend.app.database import get_connection


def get_current_material_prices(price_date=None):
    """
    Get the current material prices from the materials table.
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    id,
                    material_name,
                    unit,
                    unit_cost,
                    supplier
                FROM public.materials
                ORDER BY material_name
            """)

            rows = cur.fetchall()

            return [
                {
                    "material_id": row[0],
                    "material_name": row[1],
                    "material_unit": row[2],
                    "unit_price_inr": float(row[3]),
                    "supplier": row[4],
                }
                for row in rows
            ]

    finally:
        conn.close()


def get_material_price(material_id, price_date=None):
    """
    Get the price of one material.
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    id,
                    material_name,
                    unit,
                    unit_cost,
                    supplier
                FROM public.materials
                WHERE id = %s
                LIMIT 1
            """, (material_id,))

            row = cur.fetchone()

            if row is None:
                return None

            return {
                "material_id": row[0],
                "material_name": row[1],
                "material_unit": row[2],
                "unit_price_inr": float(row[3]),
                "supplier": row[4],
            }

    finally:
        conn.close()
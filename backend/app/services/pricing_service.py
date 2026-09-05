from datetime import date

from backend.app.database import get_connection


def get_current_material_prices(price_date=None):

    if price_date is None:
        price_date = date.today()

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    mp.material_id,
                    m.material_name,
                    m.unit,
                    mp.unit_price_inr,
                    mp.effective_from,
                    mp.effective_to,
                    mp.source
                FROM material_prices mp
                INNER JOIN materials m
                    ON m.material_id = mp.material_id
                WHERE mp.is_active = TRUE
                  AND mp.effective_from <= %s
                  AND (
                      mp.effective_to IS NULL
                      OR mp.effective_to >= %s
                  )
                ORDER BY m.material_name
            """, (
                price_date,
                price_date,
            ))

            rows = cur.fetchall()

            return [
                {
                    "material_id": row[0],
                    "material_name": row[1],
                    "material_unit": row[2],
                    "unit_price_inr": float(row[3]),
                    "effective_from": row[4],
                    "effective_to": row[5],
                    "source": row[6],
                }
                for row in rows
            ]

    finally:
        conn.close()


def get_material_price(
    material_id,
    price_date=None,
):

    if price_date is None:
        price_date = date.today()

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    mp.material_id,
                    m.material_name,
                    m.unit,
                    mp.unit_price_inr,
                    mp.effective_from,
                    mp.effective_to,
                    mp.source
                FROM material_prices mp
                INNER JOIN materials m
                    ON m.material_id = mp.material_id
                WHERE mp.material_id = %s
                  AND mp.is_active = TRUE
                  AND mp.effective_from <= %s
                  AND (
                      mp.effective_to IS NULL
                      OR mp.effective_to >= %s
                  )
                ORDER BY mp.effective_from DESC
                LIMIT 1
            """, (
                material_id,
                price_date,
                price_date,
            ))

            row = cur.fetchone()

            if row is None:
                return None

            return {
                "material_id": row[0],
                "material_name": row[1],
                "material_unit": row[2],
                "unit_price_inr": float(row[3]),
                "effective_from": row[4],
                "effective_to": row[5],
                "source": row[6],
            }

    finally:
        conn.close()
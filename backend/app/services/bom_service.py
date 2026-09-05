from backend.app.database import get_connection


def get_bom(model_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    bh.bom_id,
                    bh.bom_version,
                    bh.status,
                    bi.bom_item_id,
                    bi.component_id,
                    c.component_name,
                    c.category,
                    bi.material_id,
                    m.material_name,
                    bi.unit,
                    bi.quantity,
                    bi.unit_cost_inr,
                    bi.total_cost_inr
                FROM sofa_models sm
                JOIN bom_headers bh
                    ON bh.sofa_model_id = sm.sofa_model_id
                JOIN bom_items bi
                    ON bi.bom_id = bh.bom_id
                JOIN components c
                    ON c.component_id = bi.component_id
                JOIN materials m
                    ON m.material_id = bi.material_id
                WHERE sm.sofa_model_id = %s
                  AND bh.status = 'ACTIVE'
                ORDER BY bi.bom_item_id
            """, (model_id,))

            rows = cur.fetchall()

            return [
                {
                    "bom_id": row[0],
                    "bom_version": row[1],
                    "status": row[2],
                    "bom_item_id": row[3],
                    "component_id": row[4],
                    "component_name": row[5],
                    "category": row[6],
                    "material_id": row[7],
                    "material_name": row[8],
                    "unit": row[9],
                    "quantity": float(row[10]),
                    "unit_cost_inr": float(row[11]),
                    "total_cost_inr": float(row[12])
                }
                for row in rows
            ]

    finally:
        conn.close()
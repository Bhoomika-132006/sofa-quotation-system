from backend.app.database import get_connection


def get_bom(model_id):
    """
    Return BOM items for a sofa template.

    Parameters
    ----------
    model_id : int
        ID of the sofa template from public.sofa_templates.

    Returns
    -------
    list
        List of BOM components with material and costing information.
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    bi.id,
                    bi.template_id,
                    bi.material_id,
                    bi.component_name,

                    m.material_name,
                    m.material_category,
                    m.material_type,

                    bi.unit,
                    bi.quantity,
                    bi.unit_cost,
                    bi.total_cost

                FROM public.bom_items bi

                LEFT JOIN public.materials m
                    ON m.id = bi.material_id

                WHERE bi.template_id = %s

                ORDER BY bi.id;
                """,
                (model_id,),
            )

            rows = cur.fetchall()

            return [
                {
                    "bom_item_id": row[0],
                    "template_id": row[1],
                    "material_id": row[2],
                    "component_name": row[3],

                    "material_name": row[4],
                    "material_category": row[5],
                    "material_type": row[6],

                    "unit": row[7],
                    "quantity": float(row[8]),
                    "unit_cost_inr": float(row[9]),
                    "total_cost_inr": float(row[10]),
                }
                for row in rows
            ]

    finally:
        conn.close()
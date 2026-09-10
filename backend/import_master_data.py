from decimal import Decimal

from app.database import get_connection


def main():
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            # =====================================================
            # 1. GET ONE 3-SEATER RECORD
            # =====================================================

            cur.execute("""
                SELECT
                    sofa_id,
                    sofa_type,
                    seating_capacity,
                    length_cm,
                    depth_cm,
                    height_cm,

                    wood_type,
                    wood_quantity_kg,
                    wood_cost_inr,

                    plywood_grade,
                    plywood_quantity_sqft,
                    plywood_cost_inr,

                    seat_foam_type,
                    seat_foam_quantity_kg,
                    seat_foam_cost_inr,

                    back_foam_type,
                    back_foam_quantity_kg,
                    back_foam_cost_inr,

                    handle_foam_type,
                    handle_foam_quantity_kg,
                    handle_foam_cost_inr,

                    fabric_type,
                    fabric_quantity_m,
                    fabric_cost_inr,

                    spring_type,
                    spring_quantity,
                    spring_cost_inr,

                    clip_type,
                    clip_quantity,
                    clip_cost_inr,

                    seat_belt_type,
                    seat_belt_quantity_m,
                    seat_belt_cost_inr,

                    back_rest_belt_type,
                    back_rest_belt_quantity_m,
                    back_rest_belt_cost_inr,

                    handle_frame_type,
                    handle_frame_quantity_kg,
                    handle_frame_cost_inr

                FROM public.sofa_dataset

                WHERE sofa_type = '3-Seater'

                ORDER BY sofa_id

                LIMIT 1;
            """)

            row = cur.fetchone()

            if row is None:
                raise RuntimeError(
                    "No 3-Seater record found in sofa_dataset."
                )

            print("Using dataset record:", row[0])

            # =====================================================
            # 2. CREATE 3-SEATER MASTER TEMPLATE
            # =====================================================

            cur.execute("""
                INSERT INTO public.sofa_templates (
                    template_code,
                    name,
                    sofa_type,
                    seating_capacity,
                    length_cm,
                    depth_cm,
                    height_cm,
                    description
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (template_code)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    sofa_type = EXCLUDED.sofa_type,
                    seating_capacity = EXCLUDED.seating_capacity,
                    length_cm = EXCLUDED.length_cm,
                    depth_cm = EXCLUDED.depth_cm,
                    height_cm = EXCLUDED.height_cm,
                    description = EXCLUDED.description,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id;
            """, (
                "MASTER-3S-001",
                "Master 3-Seater Sofa",
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                "Initial 3-seater master template created from manufacturing dataset."
            ))

            template_id = cur.fetchone()[0]

            print("Master template ID:", template_id)

            # =====================================================
            # 3. MATERIAL DATA
            # =====================================================

            materials = [
                (
                    "Wood",
                    "Frame",
                    row[6],
                    "kg",
                    row[8] / row[7] if row[7] else 0,
                    None
                ),

                (
                    "Plywood",
                    "Board",
                    row[9],
                    "sqft",
                    row[11] / row[10] if row[10] else 0,
                    None
                ),

                (
                    "Seat Foam",
                    "Foam",
                    row[12],
                    "kg",
                    row[14] / row[13] if row[13] else 0,
                    None
                ),

                (
                    "Back Foam",
                    "Foam",
                    row[15],
                    "kg",
                    row[17] / row[16] if row[16] else 0,
                    None
                ),

                (
                    "Handle Foam",
                    "Foam",
                    row[18],
                    "kg",
                    row[20] / row[19] if row[19] else 0,
                    None
                ),

                (
                    "Fabric",
                    "Upholstery",
                    row[21],
                    "m",
                    row[23] / row[22] if row[22] else 0,
                    None
                ),

                (
                    "Springs",
                    "Spring",
                    row[24],
                    "piece",
                    row[26] / row[25] if row[25] else 0,
                    None
                ),

                (
                    "Clips",
                    "Hardware",
                    row[27],
                    "piece",
                    row[29] / row[28] if row[28] else 0,
                    None
                ),

                (
                    "Seat Belts",
                    "Webbing",
                    row[30],
                    "m",
                    row[32] / row[31] if row[31] else 0,
                    None
                ),

                (
                    "Back Rest Belts",
                    "Webbing",
                    row[33],
                    "m",
                    row[35] / row[34] if row[34] else 0,
                    None
                ),

                (
                    "Handle Frame",
                    "Frame",
                    row[36],
                    "kg",
                    row[38] / row[37] if row[37] else 0,
                    None
                ),
            ]

            # =====================================================
            # 4. INSERT MATERIALS + BOM
            # =====================================================

            bom_data = [
                # component, material_name, quantity, unit, total cost
                (
                    "Wood Frame",
                    materials[0][0],
                    row[7],
                    "kg",
                    row[8]
                ),
                (
                    "Plywood",
                    materials[1][0],
                    row[10],
                    "sqft",
                    row[11]
                ),
                (
                    "Seat Foam",
                    materials[2][0],
                    row[13],
                    "kg",
                    row[14]
                ),
                (
                    "Back Foam",
                    materials[3][0],
                    row[16],
                    "kg",
                    row[17]
                ),
                (
                    "Handle Foam",
                    materials[4][0],
                    row[19],
                    "kg",
                    row[20]
                ),
                (
                    "Fabric",
                    materials[5][0],
                    row[22],
                    "m",
                    row[23]
                ),
                (
                    "Springs",
                    materials[6][0],
                    row[25],
                    "piece",
                    row[26]
                ),
                (
                    "Clips",
                    materials[7][0],
                    row[28],
                    "piece",
                    row[29]
                ),
                (
                    "Seat Belts",
                    materials[8][0],
                    row[31],
                    "m",
                    row[32]
                ),
                (
                    "Back Rest Belts",
                    materials[9][0],
                    row[34],
                    "m",
                    row[35]
                ),
                (
                    "Handle Frame",
                    materials[10][0],
                    row[37],
                    "kg",
                    row[38]
                ),
            ]

            for material, bom in zip(materials, bom_data):

                material_name = material[0]
                category = material[1]
                material_type = material[2]
                unit = material[3]
                unit_cost = material[4]

                # ---------------------------------------------
                # Insert material
                # ---------------------------------------------

                cur.execute("""
                    SELECT id
                    FROM public.materials
                    WHERE material_name = %s
                      AND material_type = %s
                    LIMIT 1;
                """, (
                    material_name,
                    material_type
                ))

                existing = cur.fetchone()

                if existing:
                    material_id = existing[0]

                else:
                    cur.execute("""
                        INSERT INTO public.materials (
                            material_name,
                            material_category,
                            material_type,
                            unit,
                            unit_cost,
                            supplier
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id;
                    """, (
                        material_name,
                        category,
                        material_type,
                        unit,
                        unit_cost,
                        None
                    ))

                    material_id = cur.fetchone()[0]

                # ---------------------------------------------
                # Insert BOM item
                # ---------------------------------------------

                component_name = bom[0]
                quantity = bom[2]
                bom_unit = bom[3]
                total_cost = bom[4]

                cur.execute("""
                    SELECT id
                    FROM public.bom_items
                    WHERE template_id = %s
                      AND component_name = %s
                    LIMIT 1;
                """, (
                    template_id,
                    component_name
                ))

                existing_bom = cur.fetchone()

                if existing_bom:

                    cur.execute("""
                        UPDATE public.bom_items
                        SET
                            material_id = %s,
                            quantity = %s,
                            unit = %s,
                            unit_cost = %s,
                            total_cost = %s
                        WHERE id = %s;
                    """, (
                        material_id,
                        quantity,
                        bom_unit,
                        unit_cost,
                        total_cost,
                        existing_bom[0]
                    ))

                else:

                    cur.execute("""
                        INSERT INTO public.bom_items (
                            template_id,
                            material_id,
                            component_name,
                            quantity,
                            unit,
                            unit_cost,
                            total_cost
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s
                        );
                    """, (
                        template_id,
                        material_id,
                        component_name,
                        quantity,
                        bom_unit,
                        unit_cost,
                        total_cost
                    ))

            # =====================================================
            # COMMIT
            # =====================================================

            conn.commit()

            print()
            print("======================================")
            print("MASTER DATA IMPORT SUCCESSFUL")
            print("======================================")
            print("Template ID:", template_id)
            print("Template Code: MASTER-3S-001")
            print("BOM Components:", len(bom_data))

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()
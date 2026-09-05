from backend.app.database import get_connection


def get_sofa_types():
    """Return all sofa types available in the database."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    sofa_type_id,
                    sofa_type,
                    seating_capacity
                FROM sofa_types
                ORDER BY sofa_type_id
                """
            )

            rows = cur.fetchall()

            return [
                {
                    "sofa_type_id": row[0],
                    "sofa_type": row[1],
                    "seating_capacity": row[2],
                }
                for row in rows
            ]

    finally:
        conn.close()


def get_sofa_models(sofa_type_id=None):
    """Return sofa models, optionally filtered by sofa type."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            query = """
                SELECT
                    sm.sofa_model_id,
                    sm.sofa_id,
                    sm.sofa_type_id,
                    st.sofa_type,
                    st.seating_capacity,
                    sm.length_cm,
                    sm.depth_cm,
                    sm.height_cm
                FROM sofa_models sm
                JOIN sofa_types st
                    ON st.sofa_type_id = sm.sofa_type_id
            """

            params = ()

            if sofa_type_id is not None:
                query += """
                    WHERE sm.sofa_type_id = %s
                """
                params = (sofa_type_id,)

            query += """
                ORDER BY sm.sofa_model_id
            """

            cur.execute(query, params)

            rows = cur.fetchall()

            return [
                {
                    "sofa_model_id": row[0],
                    "sofa_id": row[1],
                    "sofa_type_id": row[2],
                    "sofa_type": row[3],
                    "seating_capacity": row[4],

                    # Database: cm
                    # Application: mm
                    "length_mm": float(row[5]) * 10,
                    "depth_mm": float(row[6]) * 10,
                    "height_mm": float(row[7]) * 10,
                }
                for row in rows
            ]

    finally:
        conn.close()


def get_sofa_model(sofa_id):
    """Return one sofa model using its sofa code."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    sm.sofa_model_id,
                    sm.sofa_id,
                    sm.sofa_type_id,
                    st.sofa_type,
                    st.seating_capacity,
                    sm.length_cm,
                    sm.depth_cm,
                    sm.height_cm
                FROM sofa_models sm
                JOIN sofa_types st
                    ON st.sofa_type_id = sm.sofa_type_id
                WHERE sm.sofa_id = %s
                """,
                (sofa_id,),
            )

            row = cur.fetchone()

            if row is None:
                return None

            return {
                "sofa_model_id": row[0],
                "sofa_id": row[1],
                "sofa_type_id": row[2],
                "sofa_type": row[3],
                "seating_capacity": row[4],

                # Database: cm
                # Application: mm
                "length_mm": float(row[5]) * 10,
                "depth_mm": float(row[6]) * 10,
                "height_mm": float(row[7]) * 10,
            }

    finally:
        conn.close()


def get_sofa_model_by_id(sofa_model_id):
    """Return one sofa model using its database primary key."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    sm.sofa_model_id,
                    sm.sofa_id,
                    sm.sofa_type_id,
                    st.sofa_type,
                    st.seating_capacity,
                    sm.length_cm,
                    sm.depth_cm,
                    sm.height_cm
                FROM sofa_models sm
                JOIN sofa_types st
                    ON st.sofa_type_id = sm.sofa_type_id
                WHERE sm.sofa_model_id = %s
                """,
                (sofa_model_id,),
            )

            row = cur.fetchone()

            if row is None:
                return None

            return {
                "sofa_model_id": row[0],
                "sofa_id": row[1],
                "sofa_type_id": row[2],
                "sofa_type": row[3],
                "seating_capacity": row[4],

                # Database: cm
                # Application: mm
                "length_mm": float(row[5]) * 10,
                "depth_mm": float(row[6]) * 10,
                "height_mm": float(row[7]) * 10,
            }

    finally:
        conn.close()


def get_all_sofa_models():
    """Return all sofa models from the database."""

    return get_sofa_models()
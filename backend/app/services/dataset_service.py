from app.database import get_connection


# =========================================================
# SOFA TYPES
# =========================================================

def get_sofa_types():
    """
    Return all sofa types available in the PostgreSQL database.

    Data source:
        public.sofa_dataset

    The current database does not have a separate sofa_types
    table, so sofa types are generated from the dataset.
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    ROW_NUMBER() OVER (ORDER BY sofa_type) AS sofa_type_id,
                    sofa_type,
                    seating_capacity
                FROM (
                    SELECT DISTINCT
                        sofa_type,
                        seating_capacity
                    FROM public.sofa_dataset
                ) AS types
                ORDER BY sofa_type;
                """
            )

            rows = cur.fetchall()

            return [
                {
                    "sofa_type_id": int(row[0]),
                    "sofa_type": row[1],
                    "seating_capacity": int(row[2]),
                }
                for row in rows
            ]

    finally:
        conn.close()


# =========================================================
# SOFA MODELS
# =========================================================

def get_sofa_models(sofa_type_id=None):
    """
    Return sofa models from public.sofa_dataset.

    Optionally filter by sofa type ID.

    The current database uses sofa_id as the actual
    manufacturing dataset identifier. A generated
    sofa_model_id is provided for compatibility with
    the existing Phase-1 application.
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            query = """
                WITH sofa_type_map AS (
                    SELECT
                        sofa_type,
                        seating_capacity,
                        ROW_NUMBER() OVER (
                            ORDER BY sofa_type
                        ) AS sofa_type_id
                    FROM (
                        SELECT DISTINCT
                            sofa_type,
                            seating_capacity
                        FROM public.sofa_dataset
                    ) AS types
                ),

                sofa_models AS (
                    SELECT
                        ROW_NUMBER() OVER (
                            ORDER BY d.sofa_id
                        ) AS sofa_model_id,

                        d.sofa_id,
                        m.sofa_type_id,
                        d.sofa_type,
                        d.seating_capacity,
                        d.length_cm,
                        d.depth_cm,
                        d.height_cm

                    FROM public.sofa_dataset d

                    JOIN sofa_type_map m
                        ON m.sofa_type = d.sofa_type
                        AND m.seating_capacity = d.seating_capacity
                )

                SELECT
                    sofa_model_id,
                    sofa_id,
                    sofa_type_id,
                    sofa_type,
                    seating_capacity,
                    length_cm,
                    depth_cm,
                    height_cm

                FROM sofa_models
            """

            params = ()

            if sofa_type_id is not None:

                query += """
                    WHERE sofa_type_id = %s
                """

                params = (sofa_type_id,)

            query += """
                ORDER BY sofa_model_id;
            """

            cur.execute(query, params)

            rows = cur.fetchall()

            return [
                {
                    "sofa_model_id": int(row[0]),
                    "sofa_id": row[1],
                    "sofa_type_id": int(row[2]),
                    "sofa_type": row[3],
                    "seating_capacity": int(row[4]),

                    # PostgreSQL database: cm
                    # Existing application: mm

                    "length_mm": float(row[5]) * 10,
                    "depth_mm": float(row[6]) * 10,
                    "height_mm": float(row[7]) * 10,
                }
                for row in rows
            ]

    finally:
        conn.close()


# =========================================================
# GET ONE SOFA USING SOFA ID
# =========================================================

def get_sofa_model(sofa_id):
    """
    Return one sofa model using its sofa_id.

    Example:
        get_sofa_model("S001")
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                WITH sofa_type_map AS (
                    SELECT
                        sofa_type,
                        seating_capacity,
                        ROW_NUMBER() OVER (
                            ORDER BY sofa_type
                        ) AS sofa_type_id
                    FROM (
                        SELECT DISTINCT
                            sofa_type,
                            seating_capacity
                        FROM public.sofa_dataset
                    ) AS types
                ),

                sofa_models AS (
                    SELECT
                        ROW_NUMBER() OVER (
                            ORDER BY d.sofa_id
                        ) AS sofa_model_id,

                        d.sofa_id,
                        m.sofa_type_id,
                        d.sofa_type,
                        d.seating_capacity,
                        d.length_cm,
                        d.depth_cm,
                        d.height_cm

                    FROM public.sofa_dataset d

                    JOIN sofa_type_map m
                        ON m.sofa_type = d.sofa_type
                        AND m.seating_capacity = d.seating_capacity
                )

                SELECT
                    sofa_model_id,
                    sofa_id,
                    sofa_type_id,
                    sofa_type,
                    seating_capacity,
                    length_cm,
                    depth_cm,
                    height_cm

                FROM sofa_models

                WHERE sofa_id = %s

                LIMIT 1;
                """,
                (sofa_id,),
            )

            row = cur.fetchone()

            if row is None:
                return None

            return {
                "sofa_model_id": int(row[0]),
                "sofa_id": row[1],
                "sofa_type_id": int(row[2]),
                "sofa_type": row[3],
                "seating_capacity": int(row[4]),

                # Database: cm
                # Application: mm

                "length_mm": float(row[5]) * 10,
                "depth_mm": float(row[6]) * 10,
                "height_mm": float(row[7]) * 10,
            }

    finally:
        conn.close()


# =========================================================
# GET ONE SOFA USING GENERATED MODEL ID
# =========================================================

def get_sofa_model_by_id(sofa_model_id):
    """
    Return one sofa model using the generated
    sofa_model_id.
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                WITH sofa_type_map AS (
                    SELECT
                        sofa_type,
                        seating_capacity,
                        ROW_NUMBER() OVER (
                            ORDER BY sofa_type
                        ) AS sofa_type_id
                    FROM (
                        SELECT DISTINCT
                            sofa_type,
                            seating_capacity
                        FROM public.sofa_dataset
                    ) AS types
                ),

                sofa_models AS (
                    SELECT
                        ROW_NUMBER() OVER (
                            ORDER BY d.sofa_id
                        ) AS sofa_model_id,

                        d.sofa_id,
                        m.sofa_type_id,
                        d.sofa_type,
                        d.seating_capacity,
                        d.length_cm,
                        d.depth_cm,
                        d.height_cm

                    FROM public.sofa_dataset d

                    JOIN sofa_type_map m
                        ON m.sofa_type = d.sofa_type
                        AND m.seating_capacity = d.seating_capacity
                )

                SELECT
                    sofa_model_id,
                    sofa_id,
                    sofa_type_id,
                    sofa_type,
                    seating_capacity,
                    length_cm,
                    depth_cm,
                    height_cm

                FROM sofa_models

                WHERE sofa_model_id = %s

                LIMIT 1;
                """,
                (sofa_model_id,),
            )

            row = cur.fetchone()

            if row is None:
                return None

            return {
                "sofa_model_id": int(row[0]),
                "sofa_id": row[1],
                "sofa_type_id": int(row[2]),
                "sofa_type": row[3],
                "seating_capacity": int(row[4]),

                # Database: cm
                # Application: mm

                "length_mm": float(row[5]) * 10,
                "depth_mm": float(row[6]) * 10,
                "height_mm": float(row[7]) * 10,
            }

    finally:
        conn.close()


# =========================================================
# GET ALL SOFA MODELS
# =========================================================

def get_all_sofa_models():
    """
    Return all sofa models from PostgreSQL.
    """

    return get_sofa_models()
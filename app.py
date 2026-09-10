import json
import uuid
from pathlib import Path
from datetime import datetime

import streamlit as st

from backend.app.database import get_connection

from backend.app.services.bom_service import get_bom

from backend.app.services.scaling_service import (
    calculate_scale_factors,
    get_engineering_rules,
    scale_bom,
)

from backend.app.services.image_pipeline import process_image
from backend.app.services.request_package_service import create_request_package

from backend.app.services.quotation_service import (
    build_quotation,
    save_quotation,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Sofa Cost Estimation System",
    page_icon="🛋️",
    layout="wide",
)


# ============================================================
# WHITE + SKY BLUE THEME
# ============================================================
st.markdown(
    """
    <style>
        /* Main page */
        .stApp {
            background-color: #ffffff;
            color: #1f2937;
        }

        /* Main content */
        .main .block-container {
            background-color: #ffffff;
            padding-top: 2rem;
        }

        /* Headings */
        h1, h2, h3, h4 {
            color: #0284c7 !important;
        }

        /* Header title */
        h1 {
            border-bottom: 3px solid #38bdf8;
            padding-bottom: 10px;
        }

        /* Buttons */
        .stButton > button {
            background-color: #0ea5e9;
            color: #ffffff;
            border: 1px solid #0284c7;
            border-radius: 8px;
            font-weight: 600;
        }

        .stButton > button:hover {
            background-color: #0284c7;
            color: #ffffff;
            border-color: #0369a1;
        }

        /* Primary button */
        .stButton > button[kind="primary"] {
            background-color: #0284c7;
            color: #ffffff;
        }

        .stButton > button[kind="primary"]:hover {
            background-color: #0369a1;
        }

        /* Input fields */
        .stTextInput input,
        .stNumberInput input,
        .stSelectbox div[data-baseweb="select"] > div,
        .stTextArea textarea {
            background-color: #ffffff;
            border: 1px solid #7dd3fc;
            border-radius: 6px;
            color: #1f2937;
        }

        /* File uploader */
        [data-testid="stFileUploader"] {
            background-color: #f0f9ff;
            border: 2px dashed #38bdf8;
            border-radius: 10px;
            padding: 10px;
        }

        /* Info boxes */
        [data-testid="stAlert"] {
            border-radius: 8px;
        }

        /* Metric cards */
        [data-testid="stMetric"] {
            background-color: #f0f9ff;
            border: 1px solid #bae6fd;
            border-radius: 10px;
            padding: 12px;
        }

        /* Dataframes */
        [data-testid="stDataFrame"] {
            border: 1px solid #bae6fd;
            border-radius: 8px;
        }

        /* Horizontal lines */
        hr {
            border-color: #bae6fd !important;
        }

        /* Captions */
        .stCaption {
            color: #64748b !important;
        }

        /* Sidebar, if used */
        section[data-testid="stSidebar"] {
            background-color: #f0f9ff;
        }
    </style>
    """,
    unsafe_allow_html=True,
)



# ============================================================
# ============================================================
# WHITE + SKY BLUE THEME
# ============================================================

st.markdown(
    """
    <style>
    /* Main Streamlit containers */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {
        background-color: #ffffff !important;
    }

    .main,
    .main .block-container {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #0284c7 !important;
        font-weight: 700 !important;
    }

    h1 {
        border-bottom: 3px solid #38bdf8;
        padding-bottom: 10px;
    }

    /* Normal text */
    p, label, .stMarkdown, [data-testid="stCaptionContainer"] {
        color: #334155 !important;
    }

    /* Text and number inputs */
    input, textarea {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #7dd3fc !important;
    }

    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1px solid #7dd3fc !important;
    }

    /* Select boxes */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #7dd3fc !important;
    }

    div[data-baseweb="select"] span {
        color: #1e293b !important;
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {
        background-color: #0ea5e9 !important;
        color: #ffffff !important;
        border: 1px solid #0284c7 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background-color: #0284c7 !important;
        color: #ffffff !important;
    }

    /* File uploader */
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #f0f9ff !important;
        border: 2px dashed #38bdf8 !important;
        border-radius: 10px !important;
    }

    section[data-testid="stFileUploaderDropzone"] * {
        color: #334155 !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background-color: #f0f9ff !important;
        border: 1px solid #bae6fd !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"] {
        color: #0284c7 !important;
    }

    /* Alerts */
    div[data-testid="stAlert"] {
        background-color: #f0f9ff !important;
        border: 1px solid #7dd3fc !important;
        color: #1e293b !important;
    }

    /* Tables / dataframes */
    [data-testid="stDataFrame"] {
        border: 1px solid #bae6fd !important;
        border-radius: 8px !important;
        background-color: #ffffff !important;
    }

    /* Horizontal separators */
    hr {
        border-color: #bae6fd !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f0f9ff !important;
    }

    /* Dropdown menu */
    ul[role="listbox"],
    li[role="option"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }

    /* Links */
    a {
        color: #0284c7 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# CONSTANTS
# ============================================================

MASTER_TEMPLATES = {
    "1-Seater": {"id": 2, "code": "MASTER-1S-001", "length_mm": 846.8, "depth_mm": 825.3, "height_mm": 823.1, "capacity": 1},
    "2-Seater": {"id": 3, "code": "MASTER-2S-001", "length_mm": 1503.1, "depth_mm": 851.0, "height_mm": 845.3, "capacity": 2},
    "3-Seater": {"id": 1, "code": "MASTER-3S-001", "length_mm": 2060.0, "depth_mm": 900.0, "height_mm": 820.0, "capacity": 3},
}

PROJECT_ROOT = Path(__file__).resolve().parent

UPLOAD_DIR = PROJECT_ROOT / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🛋️ Sofa Cost Estimation System")

st.subheader(
    "PHASE 1 — 1/2/3-Seater Costing Engine"
)


# ============================================================
# DATABASE REQUEST CREATION
# ============================================================

def create_request(
    request_code,
    sofa_type,
    seating_capacity,
    length_mm,
    depth_mm,
    height_mm,
):
    """
    Create a costing request in PostgreSQL.

    UI dimensions are entered in millimetres.
    Database dimensions are stored in centimetres.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            length_cm = float(length_mm) / 10.0
            depth_cm = float(depth_mm) / 10.0
            height_cm = float(height_mm) / 10.0

            cur.execute(
                """
                INSERT INTO public.requests
                (
                    request_id,
                    sofa_type,
                    seating_capacity,
                    length_cm,
                    depth_cm,
                    height_cm,
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
                    %s
                )
                RETURNING id;
                """,
                (
                    request_code,
                    sofa_type,
                    seating_capacity,
                    length_cm,
                    depth_cm,
                    height_cm,
                    "PENDING",
                ),
            )

            request_db_id = cur.fetchone()[0]

            conn.commit()

            return request_db_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ============================================================
# UPDATE REQUEST STATUS
# ============================================================

def update_request_status(
    request_db_id,
    status,
):
    """
    Update request status in PostgreSQL.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                UPDATE public.requests
                SET
                    status = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s;
                """,
                (
                    status,
                    request_db_id,
                ),
            )

            conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ============================================================
# GET COSTING PARAMETERS
# ============================================================

def get_costing_parameters_from_db():
    """
    Read active costing parameters from PostgreSQL.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    parameter_name,
                    parameter_value
                FROM public.costing_parameters
                WHERE is_active = TRUE
                ORDER BY parameter_id;
                """
            )

            rows = cur.fetchall()

            return {
                row[0]: float(row[1])
                for row in rows
            }

    finally:
        conn.close()


# ============================================================
# UPDATE COSTING PARAMETER
# ============================================================

def update_costing_parameter(
    parameter_name,
    parameter_value,
):
    """
    Update one costing parameter in PostgreSQL.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                UPDATE public.costing_parameters
                SET
                    parameter_value = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE parameter_name = %s;
                """,
                (
                    parameter_value,
                    parameter_name,
                ),
            )

            conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ============================================================
# GET QUOTATION HISTORY
# ============================================================

def get_quotation_history():
    """
    Retrieve previously generated quotations
    from PostgreSQL.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    q.id,
                    r.request_id,
                    r.sofa_type,
                    r.length_cm,
                    r.depth_cm,
                    r.height_cm,
                    q.material_cost,
                    q.production_cost,
                    q.profit,
                    q.final_price,
                    q.created_at
                FROM public.quotations q
                LEFT JOIN public.requests r
                    ON q.request_id = r.id
                ORDER BY q.created_at DESC;
                """
            )

            rows = cur.fetchall()

            history = []

            for row in rows:

                history.append(
                    {
                        "quotation_id": row[0],
                        "request_id": row[1],
                        "sofa_type": row[2],
                        "length_cm": float(row[3]),
                        "depth_cm": float(row[4]),
                        "height_cm": float(row[5]),
                        "material_cost": float(row[6]),
                        "production_cost": float(row[7]),
                        "profit": float(row[8]),
                        "final_price": float(row[9]),
                        "created_at": row[10],
                    }
                )

            return history

    finally:
        conn.close()


# ============================================================
# GET QUOTATION ITEMS
# ============================================================

def get_quotation_items(
    quotation_id,
):
    """
    Retrieve detailed BOM/material items
    for a quotation.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    qi.component_name,
                    m.material_name,
                    qi.quantity,
                    qi.unit,
                    qi.unit_price_inr,
                    qi.total_price_inr
                FROM public.quotation_items qi
                LEFT JOIN public.materials m
                    ON qi.material_id = m.id
                WHERE qi.quotation_id = %s
                ORDER BY qi.id;
                """,
                (
                    quotation_id,
                ),
            )

            rows = cur.fetchall()

            items = []

            for row in rows:

                items.append(
                    {
                        "component_name": row[0],
                        "material_name": row[1],
                        "quantity": float(row[2]),
                        "unit": row[3],
                        "unit_price_inr": float(row[4]),
                        "total_price_inr": float(row[5]),
                    }
                )

            return items

    finally:
        conn.close()


# ============================================================
# SESSION STATE
# ============================================================

if "quotation" not in st.session_state:
    st.session_state.quotation = None

if "request_db_id" not in st.session_state:
    st.session_state.request_db_id = None

if "request_code" not in st.session_state:
    st.session_state.request_code = None

if "uploaded_image_path" not in st.session_state:
    st.session_state.uploaded_image_path = None


# ============================================================
# INPUT SECTION
# ============================================================

st.header("1. Sofa Dimensions")

col1, col2, col3 = st.columns(3)

with col1:

    length_mm = st.number_input(
        "Length (mm)",
        min_value=1.0,
        value=2060.0,
        step=10.0,
    )

with col2:

    depth_mm = st.number_input(
        "Depth (mm)",
        min_value=1.0,
        value=900.0,
        step=10.0,
    )

with col3:

    height_mm = st.number_input(
        "Height (mm)",
        min_value=1.0,
        value=820.0,
        step=10.0,
    )


# ============================================================
# MASTER TEMPLATE / SOFA TYPE
# ============================================================

st.header("2. Master Sofa Template")

sofa_type = st.selectbox(
    "Sofa Type",
    options=["1-Seater", "2-Seater", "3-Seater"],
    index=2,
)

selected_master = MASTER_TEMPLATES[sofa_type]
seating_capacity = selected_master["capacity"]

template_col1, template_col2 = st.columns(2)

with template_col1:
    st.text_input(
        "Template Code",
        value=selected_master["code"],
        disabled=True,
    )

with template_col2:
    st.text_input(
        "Sofa Type",
        value=sofa_type,
        disabled=True,
    )

st.info(
    f"Reference Dimensions: **{selected_master['length_mm']:.1f} × "
    f"{selected_master['depth_mm']:.1f} × "
    f"{selected_master['height_mm']:.1f} mm**"
)

st.caption(
    "The selected master template is used as the engineering baseline."
)


# ============================================================
# COSTING PARAMETERS
# ============================================================

st.header("⚙️ Costing Parameters")

try:

    costing_parameters = (
        get_costing_parameters_from_db()
    )

    labour_cost = st.number_input(
        "Labour Cost (INR)",
        min_value=0.0,
        value=float(
            costing_parameters.get(
                "LABOUR_COST",
                0.0,
            )
        ),
        step=100.0,
    )

    stitching_cost = st.number_input(
        "Stitching Cost (INR)",
        min_value=0.0,
        value=float(
            costing_parameters.get(
                "STITCHING_COST",
                0.0,
            )
        ),
        step=100.0,
    )

    overhead_cost = st.number_input(
        "Overhead Cost (INR)",
        min_value=0.0,
        value=float(
            costing_parameters.get(
                "OVERHEAD_COST",
                0.0,
            )
        ),
        step=100.0,
    )

    profit_margin = st.number_input(
        "Profit Margin (INR)",
        min_value=0.0,
        value=float(
            costing_parameters.get(
                "PROFIT_MARGIN",
                0.0,
            )
        ),
        step=100.0,
    )

    if st.button(
        "💾 Update Costing Parameters",
        use_container_width=True,
    ):

        try:

            update_costing_parameter(
                "LABOUR_COST",
                labour_cost,
            )

            update_costing_parameter(
                "STITCHING_COST",
                stitching_cost,
            )

            update_costing_parameter(
                "OVERHEAD_COST",
                overhead_cost,
            )

            update_costing_parameter(
                "PROFIT_MARGIN",
                profit_margin,
            )

            st.success(
                "Costing parameters updated successfully "
                "in PostgreSQL."
            )

        except Exception as error:

            st.error(
                f"Failed to update costing parameters: {error}"
            )

except Exception as error:

    st.error(
        f"Failed to load costing parameters: {error}"
    )


st.divider()


# ============================================================
# CUSTOMER INFORMATION
# ============================================================

st.header("3. Customer Information")

customer_col1, customer_col2 = st.columns(2)

with customer_col1:

    customer_name = st.text_input(
        "Customer Name",
        placeholder="Enter customer name",
    )

with customer_col2:

    customer_phone = st.text_input(
        "Customer Phone",
        placeholder="Enter phone number",
    )


# ============================================================
# REFERENCE IMAGE
# ============================================================

st.header("4. Reference Image")

uploaded_file = st.file_uploader(
    "Upload sofa reference image",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp",
    ],
)

if uploaded_file is not None:

    st.image(
        uploaded_file,
        caption="Reference Sofa Image",
        width=500,
    )
    


# ============================================================
# GENERATE QUOTATION
# ============================================================

st.header("5. Generate Quotation")

generate_button = st.button(
    "🚀 Generate Quotation",
    type="primary",
    use_container_width=True,
)


# ============================================================
# QUOTATION GENERATION
# ============================================================

if generate_button:

    # --------------------------------------------------------
    # Validate image upload
    # --------------------------------------------------------

    if uploaded_file is None:
        st.error(
            "Please upload a sofa reference image before generating the quotation."
        )
        st.stop()

    # --------------------------------------------------------
    # Validate dimensions
    # --------------------------------------------------------

    if (
        length_mm <= 0
        or depth_mm <= 0
        or height_mm <= 0
    ):

        st.error(
            "Length, depth and height must all "
            "be greater than zero."
        )

        st.stop()


    # --------------------------------------------------------
    # Generate unique request code
    # --------------------------------------------------------

    timestamp = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )

    random_part = uuid.uuid4().hex[:6].upper()

    request_code = (
        f"REQ-{timestamp}-{random_part}"
    )


    # --------------------------------------------------------
    # Save uploaded image + Phase 2 processing
    # --------------------------------------------------------

    image_path = None
    image_pipeline_result = None

    file_extension = Path(uploaded_file.name).suffix.lower()
    safe_filename = f"{request_code}{file_extension}"
    image_path = UPLOAD_DIR / safe_filename

    with open(image_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    st.session_state.uploaded_image_path = str(image_path)

    try:
        image_pipeline_result = process_image(
            image_path=image_path,
            request_id=request_code,
            output_root=PROJECT_ROOT / "outputs" / "requests",
            create_resized=True,
        )
    except Exception as error:
        st.error(f"Failed to process uploaded image: {error}")
        st.stop()


# --------------------------------------------------------
    # Save current costing parameters
    # --------------------------------------------------------

    try:

        update_costing_parameter(
            "LABOUR_COST",
            labour_cost,
        )

        update_costing_parameter(
            "STITCHING_COST",
            stitching_cost,
        )

        update_costing_parameter(
            "OVERHEAD_COST",
            overhead_cost,
        )

        update_costing_parameter(
            "PROFIT_MARGIN",
            profit_margin,
        )

    except Exception as error:

        st.error(
            f"Failed to save costing parameters: {error}"
        )

        st.stop()


    # --------------------------------------------------------
    # Create request in PostgreSQL
    # --------------------------------------------------------

    try:

        request_db_id = create_request(
            request_code=request_code,
            sofa_type=sofa_type,
            seating_capacity=seating_capacity,
            length_mm=length_mm,
            depth_mm=depth_mm,
            height_mm=height_mm,
        )

    except Exception as error:

        st.error(
            f"Failed to create request: {error}"
        )

        st.stop()


    # --------------------------------------------------------
    # Load master BOM
    # --------------------------------------------------------

    try:

        bom_items = get_bom(
            selected_master["id"]
        )

    except Exception as error:

        st.error(
            f"Failed to load master BOM: {error}"
        )

        st.stop()


    if not bom_items:

        st.error(
            "No BOM items were found "
            "for the master template."
        )

        st.stop()


    # --------------------------------------------------------
    # Load engineering rules
    # --------------------------------------------------------

    try:

        engineering_rules = (
            get_engineering_rules()
        )

    except Exception as error:

        st.error(
            f"Failed to load engineering rules: {error}"
        )

        st.stop()


    if not engineering_rules:

        st.error(
            "No active engineering rules were found."
        )

        st.stop()


    # --------------------------------------------------------
    # Calculate scaling factors
    # --------------------------------------------------------

    try:

        scale_factors = calculate_scale_factors(

            reference_dimensions={
                "length_mm": selected_master["length_mm"],
                "depth_mm": selected_master["depth_mm"],
                "height_mm": selected_master["height_mm"],
            },

            target_dimensions={
                "length_mm": length_mm,
                "depth_mm": depth_mm,
                "height_mm": height_mm,
            },
        )

    except Exception as error:

        st.error(
            f"Failed to calculate scaling factors: {error}"
        )

        st.stop()


    # --------------------------------------------------------
    # Scale BOM
    # --------------------------------------------------------

    try:

        scaled_items = scale_bom(

            bom_items=bom_items,

            rules=engineering_rules,

            scale_factors=scale_factors,
        )

    except Exception as error:

        st.error(
            f"Failed to scale BOM: {error}"
        )

        st.stop()


    if not scaled_items:

        st.error(
            "Scaled BOM is empty."
        )

        st.stop()


    # --------------------------------------------------------
    # Build quotation
    # --------------------------------------------------------

    try:

        quotation = build_quotation(

            request_id=request_db_id,

            scaled_items=scaled_items,
        )

    except Exception as error:

        st.error(
            f"Failed to calculate quotation: {error}"
        )

        st.stop()


    # --------------------------------------------------------
    # Save quotation
    # --------------------------------------------------------

    try:

        quotation_id = save_quotation(
            quotation
        )

    except Exception as error:

        st.error(
            f"Failed to save quotation: {error}"
        )

        st.stop()


    # --------------------------------------------------------
    # Update request status
    # --------------------------------------------------------

    try:

        update_request_status(
            request_db_id,
            "QUOTED",
        )

    except Exception:

        # Quotation has already been saved.
        # Do not hide the quotation if only
        # the status update fails.

        pass


    # --------------------------------------------------------
    # Add application-level information
    # --------------------------------------------------------

    quotation["quotation_id"] = (
        quotation_id
    )

    quotation["request_code"] = (
        request_code
    )

    quotation["customer_name"] = (
        customer_name
    )

    quotation["customer_phone"] = (
        customer_phone
    )

    quotation["sofa_type"] = sofa_type

    quotation["seating_capacity"] = seating_capacity

    quotation["dimensions_mm"] = {

        "length": length_mm,

        "depth": depth_mm,

        "height": height_mm,
    }

    quotation["master_template"] = {
        "template_id": selected_master["id"],
        "template_code": selected_master["code"],
        "length_mm": selected_master["length_mm"],
        "depth_mm": selected_master["depth_mm"],
        "height_mm": selected_master["height_mm"],
    }

    quotation["scale_factors"] = (
        scale_factors
    )

    quotation["image_path"] = (

        str(image_path)

        if image_path is not None

        else None
    )


    # --------------------------------------------------------
    # PHASE 2 — Create request package
    # --------------------------------------------------------

    try:
        request_data = {
            "request_id": request_code,
            "sofa_type": sofa_type,
            "seating_capacity": seating_capacity,
            "dimensions_mm": {
                "length": length_mm,
                "depth": depth_mm,
                "height": height_mm,
            },
            "master_template": quotation["master_template"],
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "image_path": image_pipeline_result["original_image"],
            "processing_image": image_pipeline_result["processing_image"],
            "metadata_file": image_pipeline_result["metadata_file"],
            "scale_factors": scale_factors,
        }

        package_result = create_request_package(
            request_folder=image_pipeline_result["request_folder"],
            request_data=request_data,
            quotation=quotation,
        )

        quotation["request_package"] = package_result

    except Exception as error:
        st.error(f"Failed to create Phase 2 request package: {error}")
        st.stop()


    # --------------------------------------------------------
    # Save to session state
    # --------------------------------------------------------

    st.session_state.quotation = (
        quotation
    )

    st.session_state.request_db_id = (
        request_db_id
    )

    st.session_state.request_code = (
        request_code
    )


    # --------------------------------------------------------
    # Success message
    # --------------------------------------------------------

    st.success(
        "Quotation generated and saved successfully!"
    )


# ============================================================
# DISPLAY CURRENT QUOTATION
# ============================================================

quotation = (
    st.session_state.quotation
)


if quotation is not None:

    st.divider()

    st.header(
        "6. Quotation Result"
    )


    # ========================================================
    # REQUEST INFORMATION
    # ========================================================

    st.subheader(
        "Request Information"
    )

    request_col1, request_col2, request_col3 = (
        st.columns(3)
    )

    with request_col1:

        st.metric(
            "Request ID",
            quotation["request_code"],
        )

    with request_col2:

        st.metric(
            "Sofa Type",
            quotation["sofa_type"],
        )

    with request_col3:

        st.metric(
            "Seating Capacity",
            quotation["seating_capacity"],
        )


    # ========================================================
    # DIMENSIONS
    # ========================================================

    st.subheader(
        "Target Dimensions"
    )

    dimensions = (
        quotation["dimensions_mm"]
    )

    dimension_col1, dimension_col2, dimension_col3 = (
        st.columns(3)
    )

    with dimension_col1:

        st.metric(
            "Length",
            f'{dimensions["length"]:.0f} mm',
        )

    with dimension_col2:

        st.metric(
            "Depth",
            f'{dimensions["depth"]:.0f} mm',
        )

    with dimension_col3:

        st.metric(
            "Height",
            f'{dimensions["height"]:.0f} mm',
        )


    # ========================================================
    # SCALING FACTORS
    # ========================================================

    st.subheader(
        "Engineering Scaling Factors"
    )

    factors = (
        quotation["scale_factors"]
    )

    factor_col1, factor_col2, factor_col3 = (
        st.columns(3)
    )

    with factor_col1:

        st.metric(
            "SL",
            f'{factors["SL"]:.4f}',
        )

    with factor_col2:

        st.metric(
            "SW",
            f'{factors["SW"]:.4f}',
        )

    with factor_col3:

        st.metric(
            "SH",
            f'{factors["SH"]:.4f}',
        )


    factor_col4, factor_col5, factor_col6 = (
        st.columns(3)
    )

    with factor_col4:

        st.metric(
            "Area Ratio",
            f'{factors["AREA_RATIO"]:.4f}',
        )

    with factor_col5:

        st.metric(
            "Surface Area Ratio",
            f'{factors["SURFACE_AREA_RATIO"]:.4f}',
        )

    with factor_col6:

        st.metric(
            "Volume Ratio",
            f'{factors["VOLUME_RATIO"]:.4f}',
        )


    # ========================================================
    # COST SUMMARY
    # ========================================================

    st.subheader(
        "Cost Summary"
    )

    cost_col1, cost_col2, cost_col3, cost_col4 = (
        st.columns(4)
    )

    with cost_col1:

        st.metric(
            "Material Cost",
            f'₹{quotation["material_cost"]:,.2f}',
        )

    with cost_col2:

        st.metric(
            "Production Cost",
            f'₹{quotation["production_cost"]:,.2f}',
        )

    with cost_col3:

        st.metric(
            "Profit",
            f'₹{quotation["profit"]:,.2f}',
        )

    with cost_col4:

        st.metric(
            "Final Price",
            f'₹{quotation["final_price"]:,.2f}',
        )


    # ========================================================
    # DETAILED COST BREAKDOWN
    # ========================================================

    st.subheader(
        "Detailed Cost Breakdown"
    )

    cost_breakdown = {

        "Material Cost": (
            quotation["material_cost"]
        ),

        "Labour Cost": (
            quotation["labour_cost"]
        ),

        "Stitching Cost": (
            quotation["stitching_cost"]
        ),

        "Overhead": (
            quotation["overhead"]
        ),

        "Production Cost": (
            quotation["production_cost"]
        ),

        "Profit": (
            quotation["profit"]
        ),

        "Final Price": (
            quotation["final_price"]
        ),
    }

    breakdown_rows = []

    for name, value in (
        cost_breakdown.items()
    ):

        breakdown_rows.append(
            {
                "Cost Component": name,
                "Amount (INR)": round(
                    float(value),
                    2,
                ),
            }
        )

    st.dataframe(
        breakdown_rows,
        use_container_width=True,
        hide_index=True,
    )


    # ========================================================
    # MATERIAL BILL / SCALED BOM
    # ========================================================

    st.subheader(
        "Scaled Material Bill"
    )

    material_rows = []

    for item in quotation["items"]:

        material_rows.append(
            {
                "Component": item.get(
                    "component_name",
                    "",
                ),

                "Material": item.get(
                    "material_name",
                    "",
                ),

                "Base Qty": round(
                    float(
                        item.get(
                            "base_quantity",
                            0,
                        )
                    ),
                    3,
                ),

                "Scaled Qty": round(
                    float(
                        item.get(
                            "scaled_quantity",
                            0,
                        )
                    ),
                    3,
                ),

                "Unit": item.get(
                    "unit",
                    "",
                ),

                "Unit Price (INR)": round(
                    float(
                        item.get(
                            "unit_price_inr",
                            0,
                        )
                    ),
                    2,
                ),

                "Total (INR)": round(
                    float(
                        item.get(
                            "total_price_inr",
                            0,
                        )
                    ),
                    2,
                ),
            }
        )

    st.dataframe(
        material_rows,
        use_container_width=True,
        hide_index=True,
    )


    # ========================================================
    # CUSTOMER INFORMATION
    # ========================================================

    if (
        quotation.get("customer_name")
        or quotation.get("customer_phone")
    ):

        st.subheader(
            "Customer Information"
        )

        customer_data = []

        if quotation.get(
            "customer_name"
        ):

            customer_data.append(
                {
                    "Field": "Customer Name",
                    "Value": quotation[
                        "customer_name"
                    ],
                }
            )

        if quotation.get(
            "customer_phone"
        ):

            customer_data.append(
                {
                    "Field": "Customer Phone",
                    "Value": quotation[
                        "customer_phone"
                    ],
                }
            )

        st.dataframe(
            customer_data,
            use_container_width=True,
            hide_index=True,
        )


    # ========================================================
    # REFERENCE IMAGE
    # ========================================================

    if quotation.get(
        "image_path"
    ):

        image_file = Path(
            quotation["image_path"]
        )

        if image_file.exists():

            st.subheader(
                "Reference Image"
            )

            st.image(
                str(image_file),
                width=500,
            )


    # ========================================================
    # EXPORT SECTION
    # ========================================================

    st.subheader(
        "Export"
    )

    export_col1, export_col2, export_col3 = (
        st.columns(3)
    )


    # ========================================================
    # JSON EXPORT
    # ========================================================

    with export_col1:

        json_data = json.dumps(
            quotation,
            indent=4,
            default=str,
        )

        st.download_button(
            label="📄 Download JSON",
            data=json_data,
            file_name=(
                f'{quotation["request_code"]}'
                f"_quotation.json"
            ),
            mime="application/json",
            use_container_width=True,
        )


    # ========================================================
    # BOM CSV EXPORT
    # ========================================================

    with export_col2:

        csv_header = (
            "Component,"
            "Material,"
            "Base Quantity,"
            "Scaled Quantity,"
            "Unit,"
            "Unit Price INR,"
            "Total Price INR\n"
        )

        csv_rows = ""

        for item in quotation["items"]:

            component = str(
                item.get(
                    "component_name",
                    "",
                )
            ).replace(",", " ")

            material = str(
                item.get(
                    "material_name",
                    "",
                )
            ).replace(",", " ")

            base_quantity = float(
                item.get(
                    "base_quantity",
                    0,
                )
            )

            scaled_quantity = float(
                item.get(
                    "scaled_quantity",
                    0,
                )
            )

            unit = str(
                item.get(
                    "unit",
                    "",
                )
            ).replace(",", " ")

            unit_price = float(
                item.get(
                    "unit_price_inr",
                    0,
                )
            )

            total_price = float(
                item.get(
                    "total_price_inr",
                    0,
                )
            )

            csv_rows += (
                f"{component},"
                f"{material},"
                f"{base_quantity:.3f},"
                f"{scaled_quantity:.3f},"
                f"{unit},"
                f"{unit_price:.2f},"
                f"{total_price:.2f}\n"
            )

        bom_csv = (
            csv_header
            + csv_rows
        )

        st.download_button(
            label="📦 Download BOM CSV",
            data=bom_csv,
            file_name=(
                f'{quotation["request_code"]}'
                f"_bom.csv"
            ),
            mime="text/csv",
            use_container_width=True,
        )


    # ========================================================
    # COST CSV EXPORT
    # ========================================================

    with export_col3:

        cost_csv = (
            "Cost Component,Amount INR\n"

            f'Material Cost,'
            f'{quotation["material_cost"]:.2f}\n'

            f'Labour Cost,'
            f'{quotation["labour_cost"]:.2f}\n'

            f'Stitching Cost,'
            f'{quotation["stitching_cost"]:.2f}\n'

            f'Overhead,'
            f'{quotation["overhead"]:.2f}\n'

            f'Production Cost,'
            f'{quotation["production_cost"]:.2f}\n'

            f'Profit,'
            f'{quotation["profit"]:.2f}\n'

            f'Final Price,'
            f'{quotation["final_price"]:.2f}\n'
        )

        st.download_button(
            label="💰 Download Cost CSV",
            data=cost_csv,
            file_name=(
                f'{quotation["request_code"]}'
                f"_cost.csv"
            ),
            mime="text/csv",
            use_container_width=True,
        )


    # ========================================================
    # QUOTATION NUMBER
    # ========================================================

    st.divider()

    st.success(
        f'Quotation Number: '
        f'**{quotation["quotation_number"]}**'
    )

    st.info(
        f'Quotation ID in PostgreSQL: '
        f'**{quotation["quotation_id"]}**'
    )


# ============================================================
# QUOTATION HISTORY
# ============================================================

st.divider()

st.header(
    "7. Quotation History"
)

history = get_quotation_history()


if not history:

    st.info(
        "No quotations have been generated yet."
    )

else:

    # ========================================================
    # HISTORY TABLE
    # ========================================================

    history_table = []

    for q in history:

        history_table.append(
            {
                "Quotation ID": q[
                    "quotation_id"
                ],

                "Request ID": q[
                    "request_id"
                ],

                "Sofa Type": q[
                    "sofa_type"
                ],

                "Dimensions (mm)": (
                    f'{q["length_cm"] * 10:.0f} × '
                    f'{q["depth_cm"] * 10:.0f} × '
                    f'{q["height_cm"] * 10:.0f}'
                ),

                "Material Cost (₹)": round(
                    q["material_cost"],
                    2,
                ),

                "Production Cost (₹)": round(
                    q["production_cost"],
                    2,
                ),

                "Profit (₹)": round(
                    q["profit"],
                    2,
                ),

                "Final Price (₹)": round(
                    q["final_price"],
                    2,
                ),

                "Created": q[
                    "created_at"
                ].strftime(
                    "%Y-%m-%d %H:%M"
                ),
            }
        )

    st.dataframe(
        history_table,
        use_container_width=True,
        hide_index=True,
    )


    # ========================================================
    # SELECT QUOTATION
    # ========================================================

    st.subheader(
        "View Previous Quotation"
    )

    quotation_options = {}

    for q in history:

        label = (
            f'Quotation ID {q["quotation_id"]} | '
            f'{q["request_id"]} | '
            f'₹{q["final_price"]:,.2f}'
        )

        quotation_options[label] = (
            q["quotation_id"]
        )


    selected_label = st.selectbox(
        "Select a quotation to view details",
        options=list(
            quotation_options.keys()
        ),
    )

    selected_quotation_id = (
        quotation_options[
            selected_label
        ]
    )


    # ========================================================
    # FIND SELECTED QUOTATION
    # ========================================================

    selected_quotation = next(
        q
        for q in history
        if q["quotation_id"]
        == selected_quotation_id
    )


    # ========================================================
    # SELECTED QUOTATION SUMMARY
    # ========================================================

    st.markdown(
        "### Selected Quotation"
    )

    selected_col1, selected_col2, selected_col3 = (
        st.columns(3)
    )

    with selected_col1:

        st.metric(
            "Final Price",
            f'₹'
            f'{selected_quotation["final_price"]:,.2f}',
        )

    with selected_col2:

        st.metric(
            "Material Cost",
            f'₹'
            f'{selected_quotation["material_cost"]:,.2f}',
        )

    with selected_col3:

        st.metric(
            "Profit",
            f'₹'
            f'{selected_quotation["profit"]:,.2f}',
        )


    # ========================================================
    # SELECTED QUOTATION INFORMATION
    # ========================================================

    st.write(
        f'**Request ID:** '
        f'{selected_quotation["request_id"]}'
    )

    st.write(
        f'**Sofa Type:** '
        f'{selected_quotation["sofa_type"]}'
    )

    st.write(
        f'**Dimensions:** '
        f'{selected_quotation["length_cm"] * 10:.0f} × '
        f'{selected_quotation["depth_cm"] * 10:.0f} × '
        f'{selected_quotation["height_cm"] * 10:.0f} mm'
    )

    st.write(
        f'**Created:** '
        f'{selected_quotation["created_at"].strftime("%Y-%m-%d %H:%M:%S")}'
    )


    # ========================================================
    # DETAILED QUOTATION ITEMS
    # ========================================================

    st.markdown(
        "### Material / BOM Breakdown"
    )

    quotation_items = get_quotation_items(
        selected_quotation_id
    )


    if quotation_items:

        items_table = []

        for item in quotation_items:

            items_table.append(
                {
                    "Component": item[
                        "component_name"
                    ],

                    "Material": item[
                        "material_name"
                    ],

                    "Quantity": round(
                        item["quantity"],
                        3,
                    ),

                    "Unit": item[
                        "unit"
                    ],

                    "Unit Price (₹)": round(
                        item["unit_price_inr"],
                        2,
                    ),

                    "Total (₹)": round(
                        item["total_price_inr"],
                        2,
                    ),
                }
            )

        st.dataframe(
            items_table,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No detailed material items found "
            "for this quotation."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()


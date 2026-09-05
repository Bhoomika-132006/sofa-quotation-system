import json
import csv
import io
from pathlib import Path

import streamlit as st

from backend.app.services.dataset_service import (
    get_sofa_types,
    get_sofa_models,
)
from backend.app.services.bom_service import get_bom
from backend.app.services.scaling_service import (
    get_engineering_rules,
    scale_sofa_bom,
)
from backend.app.services.quotation_service import (
    build_quotation,
    generate_quotation_number,
    save_quotation,
)


# =========================================================
# APPLICATION CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "backend" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


st.set_page_config(
    page_title="Sofa Cost Estimation",
    page_icon="🛋️",
    layout="wide",
)


# =========================================================
# HEADER
# =========================================================

st.title("Sofa Cost Estimation System")
st.caption(
    "Phase 1 — Engineering Scaling, Material Billing and Quotation"
)


# =========================================================
# DATABASE DATA
# =========================================================

@st.cache_data(ttl=300)
def load_sofa_types():
    return get_sofa_types()


@st.cache_data(ttl=300)
def load_sofa_models(sofa_type_id):
    return get_sofa_models(sofa_type_id)


# =========================================================
# LOAD SOFA TYPES
# =========================================================

try:
    sofa_types = load_sofa_types()

except Exception as error:
    st.error(
        f"Database connection failed: {error}"
    )
    st.stop()


if not sofa_types:
    st.warning(
        "No sofa types are available in the database."
    )
    st.stop()


# =========================================================
# SOFA TYPE
# =========================================================

st.header("1. Sofa Selection")

sofa_type_names = [
    item["sofa_type"]
    for item in sofa_types
]

selected_type_name = st.selectbox(
    "Sofa Type",
    sofa_type_names,
)

selected_type = next(
    item
    for item in sofa_types
    if item["sofa_type"] == selected_type_name
)


# =========================================================
# SOFA MODEL
# =========================================================

models = load_sofa_models(
    selected_type["sofa_type_id"]
)

if not models:
    st.warning(
        "No sofa models are available for this sofa type."
    )
    st.stop()


model_labels = [
    (
        f'{model["sofa_id"]} — '
        f'{model["length_mm"]:.0f} × '
        f'{model["depth_mm"]:.0f} × '
        f'{model["height_mm"]:.0f} mm'
    )
    for model in models
]

selected_model_label = st.selectbox(
    "Master Sofa Model",
    model_labels,
)

selected_model = models[
    model_labels.index(selected_model_label)
]


# =========================================================
# MASTER DIMENSIONS
# =========================================================

st.header("2. Master Dimensions")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Master Length",
    f'{selected_model["length_mm"]:.0f} mm',
)

c2.metric(
    "Master Depth",
    f'{selected_model["depth_mm"]:.0f} mm',
)

c3.metric(
    "Master Height",
    f'{selected_model["height_mm"]:.0f} mm',
)


# =========================================================
# REQUIRED DIMENSIONS
# =========================================================

st.header("3. Required Dimensions")

d1, d2, d3 = st.columns(3)

with d1:
    required_length = st.number_input(
        "Required Length (mm)",
        min_value=1.0,
        value=float(selected_model["length_mm"]),
        step=1.0,
    )

with d2:
    required_depth = st.number_input(
        "Required Depth (mm)",
        min_value=1.0,
        value=float(selected_model["depth_mm"]),
        step=1.0,
    )

with d3:
    required_height = st.number_input(
        "Required Height (mm)",
        min_value=1.0,
        value=float(selected_model["height_mm"]),
        step=1.0,
    )


# =========================================================
# CUSTOMER DETAILS
# =========================================================

st.header("4. Customer Details")

customer_col1, customer_col2 = st.columns(2)

with customer_col1:
    customer_name = st.text_input(
        "Customer Name"
    )

with customer_col2:
    customer_phone = st.text_input(
        "Customer Contact"
    )


# =========================================================
# REFERENCE IMAGE
# =========================================================

uploaded_image = st.file_uploader(
    "Reference Sofa Image (Optional)",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp",
    ],
)

if uploaded_image is not None:

    st.image(
        uploaded_image,
        caption="Reference Image",
        width=360,
    )


# =========================================================
# GENERATE QUOTATION
# =========================================================

if st.button(
    "Generate Quotation",
    type="primary",
    use_container_width=True,
):

    try:

        # -------------------------------------------------
        # SAVE REFERENCE IMAGE
        # -------------------------------------------------

        if uploaded_image is not None:

            safe_filename = Path(
                uploaded_image.name
            ).name

            image_path = (
                UPLOAD_DIR / safe_filename
            )

            image_path.write_bytes(
                uploaded_image.getbuffer()
            )


        # -------------------------------------------------
        # MASTER DIMENSIONS
        # -------------------------------------------------

        reference_dimensions = {
            "length_mm": selected_model["length_mm"],
            "depth_mm": selected_model["depth_mm"],
            "height_mm": selected_model["height_mm"],
        }


        # -------------------------------------------------
        # CUSTOMER TARGET DIMENSIONS
        # -------------------------------------------------

        target_dimensions = {
            "length_mm": required_length,
            "depth_mm": required_depth,
            "height_mm": required_height,
        }


        # -------------------------------------------------
        # GET MASTER BOM
        # -------------------------------------------------

        bom = get_bom(
            selected_model["sofa_model_id"]
        )

        if not bom:

            st.error(
                "No active BOM exists for the selected sofa model."
            )

            st.stop()


        # -------------------------------------------------
        # GET ENGINEERING RULES
        # -------------------------------------------------

        engineering_rules = (
            get_engineering_rules()
        )


        # -------------------------------------------------
        # SCALE BOM
        # -------------------------------------------------

        scaling_result = scale_sofa_bom(
            reference_dimensions,
            target_dimensions,
            bom,
            engineering_rules,
        )


        scaled_bom = scaling_result[
            "scaled_bom"
        ]


        # -------------------------------------------------
        # VALIDATE SCALING
        # -------------------------------------------------

        if not scaled_bom["complete"]:

            st.error(
                "Scaling cannot be completed."
            )

            st.json(
                scaled_bom["missing_rules"]
            )

            st.stop()


        # -------------------------------------------------
        # BUILD QUOTATION
        # -------------------------------------------------

        quotation = build_quotation(
            quotation_number=(
                generate_quotation_number()
            ),

            sofa_model_id=(
                selected_model[
                    "sofa_model_id"
                ]
            ),

            scaled_items=(
                scaled_bom["items"]
            ),
        )


        # -------------------------------------------------
        # SAVE QUOTATION
        # -------------------------------------------------

        quotation_id = save_quotation(
            quotation=quotation,
            customer_name=(
                customer_name
                or None
            ),
            customer_phone=(
                customer_phone
                or None
            ),
        )


        # -------------------------------------------------
        # STORE RESULT
        # -------------------------------------------------

        st.session_state[
            "quotation"
        ] = quotation

        st.session_state[
            "quotation_id"
        ] = quotation_id

        st.session_state[
            "scale_factors"
        ] = scaling_result[
            "scale_factors"
        ]

        st.session_state[
            "selected_model"
        ] = selected_model


        st.success(
            "Quotation generated and saved successfully."
        )


    except Exception as error:

        st.error(
            f"Quotation generation failed: {error}"
        )


# =========================================================
# QUOTATION RESULT
# =========================================================

if "quotation" in st.session_state:

    quotation = st.session_state[
        "quotation"
    ]

    scale_factors = st.session_state[
        "scale_factors"
    ]

    selected_model = st.session_state[
        "selected_model"
    ]


    # =====================================================
    # SCALING RESULT
    # =====================================================

    st.divider()

    st.header("5. Engineering Scaling")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "SL",
        f'{scale_factors["SL"]:.4f}',
    )

    c2.metric(
        "SW",
        f'{scale_factors["SW"]:.4f}',
    )

    c3.metric(
        "SH",
        f'{scale_factors["SH"]:.4f}',
    )


    # =====================================================
    # QUOTATION INFORMATION
    # =====================================================

    st.header("6. Quotation")

    st.write(
        f'**Quotation Number:** '
        f'{quotation["quotation_number"]}'
    )

    st.write(
        f'**Quotation ID:** '
        f'{st.session_state["quotation_id"]}'
    )

    st.write(
        f'**Sofa Model:** '
        f'{selected_model["sofa_id"]}'
    )

    st.write(
        f'**Sofa Type:** '
        f'{selected_model["sofa_type"]}'
    )

    st.write(
        f'**Required Dimensions:** '
        f'{required_length:.0f} × '
        f'{required_depth:.0f} × '
        f'{required_height:.0f} mm'
    )


    # =====================================================
    # COST BREAKDOWN
    # =====================================================

    st.subheader("Cost Breakdown")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Material Cost",
        f'₹{quotation["material_cost_inr"]:,.2f}',
    )

    c2.metric(
        "Labour",
        f'₹{quotation["labour_cost_inr"]:,.2f}',
    )

    c3.metric(
        "Stitching",
        f'₹{quotation["stitching_cost_inr"]:,.2f}',
    )


    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Overhead",
        f'₹{quotation["overhead_inr"]:,.2f}',
    )

    c2.metric(
        "Transportation",
        f'₹{quotation["transportation_cost_inr"]:,.2f}',
    )

    c3.metric(
        "Profit",
        f'₹{quotation["profit_inr"]:,.2f}',
    )


    # =====================================================
    # FINAL QUOTATION
    # =====================================================

    st.subheader(
        "Final Quotation Amount"
    )

    st.success(
        f'₹{quotation["total_inr"]:,.2f}'
    )


    # =====================================================
    # MATERIAL BILL
    # =====================================================

    st.header(
        "7. Material Bill"
    )

    material_rows = []

    for item in quotation["items"]:

        material_rows.append(
            {
                "Component": item[
                    "component_name"
                ],

                "Material": item[
                    "material_name"
                ],

                "Base Quantity": item[
                    "base_quantity"
                ],

                "Scaled Quantity": item[
                    "scaled_quantity"
                ],

                "Unit": item[
                    "unit"
                ],

                "Unit Price (₹)": item[
                    "unit_price_inr"
                ],

                "Line Total (₹)": item[
                    "total_price_inr"
                ],

                "Price Effective From": item[
                    "price_effective_from"
                ],

                "Price Source":
    item.get(
        "price_source"
    ),

                "Price Source": item[
                    "price_source"
                ],
            }
        )


    st.dataframe(
        material_rows,
        use_container_width=True,
        hide_index=True,
    )


    # =====================================================
    # BILL TOTAL
    # =====================================================

    st.subheader(
        "Total Material Cost"
    )

    st.success(
        f'₹{quotation["material_cost_inr"]:,.2f}'
    )
    # =========================================================
# QUOTATION FILE EXPORT
# =========================================================

if "quotation" in st.session_state:

    quotation = st.session_state["quotation"]
    quotation_id = st.session_state["quotation_id"]
    model = st.session_state["selected_model"]
    scale = st.session_state["scale_factors"]

    st.divider()

    st.header("8. Quotation Documents")

    # -----------------------------------------------------
    # QUOTATION SUMMARY
    # -----------------------------------------------------

    quotation_summary = {
        "quotation_number": quotation[
            "quotation_number"
        ],

        "quotation_id": quotation_id,

        "sofa_model": model[
            "sofa_id"
        ],

        "sofa_type": model[
            "sofa_type"
        ],

        "master_dimensions_mm": {
            "length": model[
                "length_mm"
            ],
            "depth": model[
                "depth_mm"
            ],
            "height": model[
                "height_mm"
            ],
        },

        "required_dimensions_mm": {
            "length": required_length,
            "depth": required_depth,
            "height": required_height,
        },

        "scale_factors": {
            "SL": scale["SL"],
            "SW": scale["SW"],
            "SH": scale["SH"],
        },

        "cost_breakdown": {
            "material_cost_inr":
                quotation[
                    "material_cost_inr"
                ],

            "labour_cost_inr":
                quotation[
                    "labour_cost_inr"
                ],

            "stitching_cost_inr":
                quotation[
                    "stitching_cost_inr"
                ],

            "overhead_inr":
                quotation[
                    "overhead_inr"
                ],

            "transportation_cost_inr":
                quotation[
                    "transportation_cost_inr"
                ],

            "profit_inr":
                quotation[
                    "profit_inr"
                ],

            "subtotal_inr":
                quotation[
                    "subtotal_inr"
                ],

            "total_inr":
                quotation[
                    "total_inr"
                ],
        },

        "material_bill":
            quotation["items"],
    }


    # -----------------------------------------------------
    # JSON FILE
    # -----------------------------------------------------

    json_data = json.dumps(
        quotation_summary,
        indent=4,
        default=str,
    )


    # -----------------------------------------------------
    # BOM CSV
    # -----------------------------------------------------

    bom_buffer = io.StringIO()

    bom_writer = csv.writer(
        bom_buffer
    )

    bom_writer.writerow([
        "Component",
        "Material",
        "Base Quantity",
        "Scaled Quantity",
        "Unit",
        "Unit Price INR",
        "Line Total INR",
        "Price Effective From",
        "Price Effective To",
        "Price Source",
    ])


    for item in quotation["items"]:

        bom_writer.writerow([

            item.get(
                "component_name",
                item[
                    "component_id"
                ],
            ),

            item.get(
                "material_name",
                item[
                    "material_id"
                ],
            ),

            item[
                "base_quantity"
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

            item[
                "price_effective_from"
            ],

            item[
                "price_effective_to"
            ],

            item[
                "price_source"
            ],
        ])


    bom_csv = (
        bom_buffer.getvalue()
    )


    # -----------------------------------------------------
    # COST CSV
    # -----------------------------------------------------

    cost_buffer = io.StringIO()

    cost_writer = csv.writer(
        cost_buffer
    )

    cost_writer.writerow([
        "Cost Head",
        "Amount INR",
    ])

    cost_writer.writerow([
        "Material Cost",
        quotation[
            "material_cost_inr"
        ],
    ])

    cost_writer.writerow([
        "Labour Cost",
        quotation[
            "labour_cost_inr"
        ],
    ])

    cost_writer.writerow([
        "Stitching Cost",
        quotation[
            "stitching_cost_inr"
        ],
    ])

    cost_writer.writerow([
        "Overhead",
        quotation[
            "overhead_inr"
        ],
    ])

    cost_writer.writerow([
        "Transportation",
        quotation[
            "transportation_cost_inr"
        ],
    ])

    cost_writer.writerow([
        "Profit",
        quotation[
            "profit_inr"
        ],
    ])

    cost_writer.writerow([
        "Subtotal",
        quotation[
            "subtotal_inr"
        ],
    ])

    cost_writer.writerow([
        "Final Quotation",
        quotation[
            "total_inr"
        ],
    ])


    cost_csv = (
        cost_buffer.getvalue()
    )


    # -----------------------------------------------------
    # DOWNLOAD BUTTONS
    # -----------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        st.download_button(
            label="Download Quotation JSON",
            data=json_data,
            file_name=(
                f'{quotation["quotation_number"]}.json'
            ),
            mime="application/json",
            use_container_width=True,
        )


    with col2:

        st.download_button(
            label="Download BOM CSV",
            data=bom_csv,
            file_name=(
                f'{quotation["quotation_number"]}_BOM.csv'
            ),
            mime="text/csv",
            use_container_width=True,
        )


    with col3:

        st.download_button(
            label="Download Cost CSV",
            data=cost_csv,
            file_name=(
                f'{quotation["quotation_number"]}_COST.csv'
            ),
            mime="text/csv",
            use_container_width=True,
        )
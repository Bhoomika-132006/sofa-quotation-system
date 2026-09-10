# 🛋️ Sofa Cost Estimation System

A Python and PostgreSQL-based application for estimating sofa manufacturing costs.

## Main Features

- Supports **1-Seater, 2-Seater and 3-Seater** sofas.
- Uses master sofa templates and BOM data.
- Accepts customer dimensions in mm.
- Calculates engineering scaling factors.
- Calculates material, labour, stitching and overhead costs.
- Generates the final sofa quotation.
- Stores quotations in PostgreSQL.
- Maintains quotation history.
- Allows reference sofa image upload.
- Validates and stores uploaded images.
- Creates request-specific image and quotation files.

## Technologies

- Python
- Streamlit
- PostgreSQL
- Pandas
- Pillow

## Current Status

- **Phase 1 — Costing Engine:** ✅ Complete
- **Phase 2 — Image Intake & Request Packaging:** ✅ Complete
- **Phase 3 — Image Understanding:** ⏸️ Not implemented

## Run

```bash
python -m streamlit run app.py
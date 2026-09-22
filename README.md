# 🛋️ Sofa Quotation System

A Python, Streamlit, and PostgreSQL-based application for estimating sofa manufacturing costs, generating quotations, managing BOM data, and handling reference sofa images.

---

## 📌 Project Overview

The Sofa Quotation System is designed to support sofa manufacturing cost estimation using predefined master sofa templates, customer-provided dimensions, BOM data, material prices, engineering scaling rules, and quotation parameters.

The current implementation focuses on:

- **Phase 1 — Costing Engine**
- **Phase 2 — Image Intake & Request Packaging**

The system currently supports **1-Seater, 2-Seater, and 3-Seater** sofa configurations.

> **Note:** Image understanding, object detection, CAD automation, and automatic sofa identification are future phases and are not implemented in the current version.

---

# 🎯 Project Objectives

The current system aims to:

1. Maintain master sofa templates.
2. Store sofa BOM and material information.
3. Accept customer sofa dimensions.
4. Calculate engineering scaling factors.
5. Generate a scaled BOM.
6. Calculate material costs.
7. Calculate labour, stitching, and overhead costs.
8. Calculate profit and final quotation price.
9. Store quotation information in PostgreSQL.
10. Accept and validate reference sofa images.
11. Create request-specific image and quotation files.
12. Provide a Streamlit-based user interface.

---

# 🚀 Current Features

## Phase 1 — Costing Engine

The costing engine supports:

- 1-Seater sofas
- 2-Seater sofas
- 3-Seater sofas
- Master sofa templates
- Customer dimensions in millimetres
- Engineering scaling factors
- Scaled BOM generation
- Material pricing
- Labour cost
- Stitching cost
- Overhead cost
- Production cost
- Profit
- Final quotation
- Quotation history
- PostgreSQL database storage

---

## Phase 2 — Image Intake & Request Packaging

The image pipeline supports:

- JPG images
- JPEG images
- PNG images
- WEBP images
- Image validation
- Image metadata extraction
- Original image storage
- Processing image generation
- Request-specific folders
- Request metadata
- Request summary
- Quote summary
- BOM output
- Cost output

### Important

Phase 2 currently handles **image intake and packaging**.

It does **not** perform:

- Sofa detection
- Component detection
- Image segmentation
- Automatic sofa identification
- CAD generation
- 3D model generation

Those belong to future phases.

---

# 🏗️ Current Architecture

```text
                    CUSTOMER
                       │
             ┌─────────┴─────────┐
             │                   │
       Sofa Type          Reference Image
             │                   │
       Dimensions              Image
             │                   │
             └─────────┬─────────┘
                       │
                       ▼
                STREAMLIT APP
                       │
                       ▼
                PYTHON SERVICES
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   BOM Service   Scaling Service  Pricing Service
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
               Quotation Service
                       │
                       ▼
                Image Pipeline
                       │
                       ▼
              PostgreSQL Database
```

---

# 📁 Project Structure

```text
sofa-quotation-system/
│
├── backend/
│   │
│   ├── app/
│   │   ├── models/
│   │   │
│   │   ├── services/
│   │   │   ├── bom_service.py
│   │   │   ├── scaling_service.py
│   │   │   ├── pricing_service.py
│   │   │   ├── quotation_service.py
│   │   │   ├── dataset_service.py
│   │   │   └── image_pipeline.py
│   │   │
│   │   └── database.py
│   │
│   ├── .env.example
│   ├── requirements.txt
│   ├── import_master_data.py
│   ├── test_connection.py
│   ├── test_image_pipeline.py
│   └── test_sofa_validation.py
│
├── app.py
├── .gitignore
└── README.md
```

---

# 🛋️ Supported Sofa Types

The current system supports three sofa types.

| Sofa Type | Master Template | Seating Capacity |
|---|---|---:|
| 1-Seater | MASTER-1S-001 | 1 |
| 2-Seater | MASTER-2S-001 | 2 |
| 3-Seater | MASTER-3S-001 | 3 |

---

# 📐 Master Sofa Templates

The current master templates are used as the reference for engineering scaling.

| Sofa Type | Master Code | Length | Depth | Height |
|---|---|---:|---:|---:|
| 1-Seater | MASTER-1S-001 | 846.8 mm | 825.3 mm | 823.1 mm |
| 2-Seater | MASTER-2S-001 | 1503.1 mm | 851.0 mm | 845.3 mm |
| 3-Seater | MASTER-3S-001 | 2060.0 mm | 900.0 mm | 820.0 mm |

---

# 🧱 BOM Components

The current BOM contains 11 major components:

1. Wood Frame
2. Plywood
3. Seat Foam
4. Back Foam
5. Handle Foam
6. Fabric
7. Springs
8. Clips
9. Seat Belts
10. Back Rest Belts
11. Handle Frame

The BOM quantities are maintained separately for the supported master sofa templates.

---

# 📊 Engineering Scaling

Customer dimensions are compared with the selected master template.

The system calculates scaling factors:

```text
SL = Customer Length / Master Length

SW = Customer Width / Master Width

SH = Customer Height / Master Height
```

Depending on the BOM component, the system applies an appropriate scaling relationship.

The current engineering rules use:

- `SL`
- `SW`
- `SH`
- `AREA_RATIO`
- `SURFACE_AREA_RATIO`
- `VOLUME_RATIO`

These rules are stored in the PostgreSQL database.

---

# 📦 Scaled BOM

After calculating the engineering scaling factors, the system generates a scaled BOM.

Conceptually:

```text
Master BOM
     │
     ▼
Engineering Rules
     │
     ▼
Scaling Factors
     │
     ▼
Scaled BOM
     │
     ▼
Material Pricing
```

The scaled BOM is then used for quotation calculation.

---

# 💰 Cost Calculation

The quotation calculation is divided into several components.

## Material Cost

Material cost is calculated using the scaled BOM quantity and current material price.

```text
Material Cost
=
Σ(Scaled Quantity × Material Unit Price)
```

---

## Production Cost

The current production cost is calculated from:

```text
Production Cost
=
Material Cost
+ Labour Cost
+ Stitching Cost
+ Overhead
```

---

## Final Quotation

The final quotation is calculated using:

```text
Final Price
=
Production Cost
+ Profit
```

The costing parameters are maintained in PostgreSQL.

---

# 🗄️ PostgreSQL Database

The application uses PostgreSQL as its primary database.

Default local configuration:

```text
Host: localhost
Port: 5432
Database: sofa_costing_db
User: postgres
```

The database contains the data required for:

- Sofa templates
- Materials
- BOM
- Requests
- Request images
- Image analysis
- Quotations
- Quotation items
- Engineering rules
- Costing parameters
- Sofa dataset

---

# 🧩 Main Database Tables

The current database includes the following tables:

```text
sofa_dataset
sofa_templates
materials
bom_items
requests
request_images
image_analysis
quotations
quotation_items
engineering_rules
costing_parameters
```

---

# 🖼️ Image Intake Pipeline

The current Phase 2 image pipeline follows:

```text
Reference Image
      │
      ▼
Image Validation
      │
      ▼
Metadata Extraction
      │
      ▼
Request Folder Creation
      │
      ├── Original Image
      │
      ├── Metadata
      │
      └── Processing Image
```

A request-specific directory is created for processing and storing generated files.

---

# 📂 Request Outputs

A processed request can contain files such as:

```text
request_folder/
│
├── original_image
├── image_metadata.json
├── processing_image.jpg
├── request_summary.json
├── quote_summary.json
├── bom.csv
└── cost.csv
```

These generated files are local runtime outputs and are excluded from Git.

---

# 🔐 Environment Configuration

Database credentials are stored in a local `.env` file.

The repository provides:

```text
backend/.env.example
```

Create:

```text
backend/.env
```

using the following structure:

```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=sofa_costing_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your_postgres_password
```

Replace:

```text
your_postgres_password
```

with the PostgreSQL password configured on your machine.

### ⚠️ Security

Never commit the real `.env` file to GitHub.

The repository `.gitignore` excludes environment files and secrets.

---

# 💻 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Bhoomika-132006/sofa-quotation-system.git
```

Move into the project:

```bash
cd sofa-quotation-system
```

---

# 🐍 Python Environment

## 2. Create Virtual Environment

On Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

After activation, the terminal should show:

```text
(.venv)
```

---

# 📦 Install Dependencies

## 3. Install Required Python Packages

Run:

```powershell
python -m pip install -r backend/requirements.txt
```

Current dependencies include:

- Streamlit
- Psycopg
- python-dotenv
- Pandas
- Pillow

---

# 🐘 PostgreSQL Setup

## 4. Install PostgreSQL

Install PostgreSQL locally.

The application expects PostgreSQL to be available on:

```text
localhost:5432
```

---

## 5. Create Database

Create a PostgreSQL database named:

```text
sofa_costing_db
```

This can be done using pgAdmin or PostgreSQL tools.

---

# 💾 Database Restore

## 6. Restore the Complete Database Backup

The application requires the complete PostgreSQL database backup.

Use:

```text
sofa_costing_db_complete.backup
```

Restore this backup into:

```text
sofa_costing_db
```

The backup should be shared separately with authorized team members because it is not stored inside the GitHub repository.

After restoring, verify that the required tables are available.

---

# 🔑 Configure `.env`

## 7. Create the Local Environment File

Inside:

```text
backend/
```

create:

```text
.env
```

Example:

```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=sofa_costing_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your_postgres_password
```

Use your own PostgreSQL password.

---

# 🧪 Database Connection Test

## 8. Test PostgreSQL Connection

Run from the project root:

```powershell
python backend/test_connection.py
```

A successful test should confirm:

```text
PostgreSQL connection successful
```

and the database name should be:

```text
sofa_costing_db
```

---

# 🧪 Image Pipeline Test

## 9. Test Phase 2 Image Processing

Run:

```powershell
python backend/test_image_pipeline.py
```

This verifies:

- Image validation
- Image metadata extraction
- Request folder creation
- Original image handling
- Processing image generation

---

# ▶️ Run the Application

## 10. Start Streamlit

From the project root:

```powershell
python -m streamlit run app.py
```

The application will start locally.

Open the Streamlit URL shown in the terminal, normally:

```text
http://localhost:8501
```

---

# 🔄 Application Workflow

The current application workflow is:

```text
1. Select Sofa Type
        │
        ▼
2. Select 1-Seater / 2-Seater / 3-Seater
        │
        ▼
3. Enter Customer Dimensions
        │
        ▼
4. Upload Reference Sofa Image
        │
        ▼
5. Validate Image
        │
        ▼
6. Calculate Scaling Factors
        │
        ▼
7. Generate Scaled BOM
        │
        ▼
8. Calculate Material Cost
        │
        ▼
9. Calculate Labour / Stitching / Overhead
        │
        ▼
10. Calculate Profit
        │
        ▼
11. Generate Final Quotation
        │
        ▼
12. Store Quotation in PostgreSQL
```

---

# 🧪 Testing Checklist

Before considering a local installation successful, verify:

### Database

- [ ] PostgreSQL is running
- [ ] `sofa_costing_db` exists
- [ ] Database backup has been restored
- [ ] `.env` is configured
- [ ] Database connection test passes

### Python

- [ ] Python environment is activated
- [ ] Dependencies are installed
- [ ] No import errors occur

### Phase 1

- [ ] 1-Seater works
- [ ] 2-Seater works
- [ ] 3-Seater works
- [ ] Customer dimensions are accepted
- [ ] Scaling factors are calculated
- [ ] BOM is generated
- [ ] Material cost is calculated
- [ ] Final quotation is generated
- [ ] Quotation is stored in PostgreSQL

### Phase 2

- [ ] Reference image can be uploaded
- [ ] Image validation works
- [ ] Image metadata is generated
- [ ] Request folder is created
- [ ] Processing image is generated

---

# 🛡️ Git and Security

The following files/directories should not be committed:

```text
.venv/
.env
uploads/
outputs/
__pycache__/
*.log
```

The project `.gitignore` is configured to exclude these runtime and secret files.

The following file can be committed:

```text
backend/.env.example
```

because it contains placeholder credentials only.

---

# 🔒 Data Separation

The project contains two conceptually separate data areas.

## Manufacturing / Costing Data

Used for:

- Sofa templates
- BOM
- Materials
- Engineering rules
- Cost calculation
- Quotations

## Future Computer Vision Data

Used for future:

- Sofa image datasets
- Object detection
- YOLO training
- Component detection

These datasets are maintained as **independent project components**.

The current Phase 1 manufacturing/costing database is not dependent on the future computer-vision training dataset.

---

# 🚧 Current Limitations

The current version does not implement:

- Automatic sofa recognition from an image
- YOLO detection
- Component detection
- Image segmentation
- Automatic dimension extraction from images
- CAD model generation
- Automatic Fusion 360 integration
- Automatic SolidWorks integration
- Automated 3D model generation

These are outside the current Phase 1 and Phase 2 implementation.

---

# 🔮 Future Development

Future phases may include the following pipeline:

```text
Customer Image
      │
      ▼
Image Processing
      │
      ▼
Sofa Identification
      │
      ▼
Master CAD Template
      │
      ▼
Engineering Scaling
      │
      ▼
Scaled 3D Model
      │
      ▼
BOM Generation
      │
      ▼
Cost Calculation
      │
      ▼
Output Reports
      │
      ▼
Customer Quotation
```

Possible future technologies include:

- YOLO
- OpenCV
- Computer Vision
- CAD automation
- Fusion 360
- SolidWorks APIs
- Parametric modelling

These technologies are planned for future development and are not part of the current implementation.

---

# 📈 Project Status

| Component | Status |
|---|---|
| PostgreSQL Database | ✅ Complete |
| Master Sofa Templates | ✅ Complete |
| BOM Management | ✅ Complete |
| Engineering Scaling | ✅ Complete |
| Material Pricing | ✅ Complete |
| Cost Calculation | ✅ Complete |
| Quotation Generation | ✅ Complete |
| Quotation Storage | ✅ Complete |
| Reference Image Upload | ✅ Complete |
| Image Validation | ✅ Complete |
| Image Metadata | ✅ Complete |
| Request Packaging | ✅ Complete |
| Image Understanding | ⏸️ Future |
| Sofa Detection | ⏸️ Future |
| CAD Automation | ⏸️ Future |
| 3D Model Generation | ⏸️ Future |

---

# 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | User interface |
| PostgreSQL | Database |
| Psycopg | PostgreSQL connectivity |
| Pandas | Data processing |
| Pillow | Image processing |
| python-dotenv | Environment configuration |
| Git | Version control |
| GitHub | Source-code repository |

---

# 👥 Team Setup

Every team member should have:

1. Git
2. Python
3. PostgreSQL
4. pgAdmin
5. The project GitHub repository
6. The complete PostgreSQL backup
7. Their own PostgreSQL password
8. Their own `backend/.env`

Each team member should restore the database locally and use their own local database credentials.

---

# 📌 Important Project Rule

Do not commit:

```text
.env
```

Do not commit:

```text
uploads/
outputs/
```

Do not commit PostgreSQL passwords or other credentials.

Use:

```text
backend/.env.example
```

as the configuration template.

---

# 📜 Current Version

Current development scope:

```text
Phase 1 — Costing Engine
Phase 2 — Image Intake & Request Packaging
```

Status:

```text
Phase 1: COMPLETE
Phase 2: COMPLETE
Phase 3: NOT IMPLEMENTED
```

---

# 👩‍💻 Repository

GitHub repository:

https://github.com/Bhoomika-132006/sofa-quotation-system
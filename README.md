# Sofa Cost Estimation & Quotation System – Phase 1

## Project Overview

The Sofa Cost Estimation & Quotation System is a database-driven application developed to automate sofa material costing and quotation generation.

Phase 1 focuses on building the foundation of the costing engine by using sofa master data, Bill of Materials (BOM), engineering scaling rules, and material prices stored in a PostgreSQL database.

The application allows users to select a sofa model, enter the required dimensions, calculate the scaled material requirements, generate a material bill, and create a quotation.

---

## Phase 1 Objective

The main objective of Phase 1 is to develop a reliable and database-driven sofa costing engine that can:

- Store sofa master models and dimensions
- Maintain component and material master data
- Maintain the Bill of Materials (BOM)
- Apply engineering-based scaling rules
- Calculate scaled component quantities
- Retrieve current material prices from the database
- Calculate material cost
- Generate customer quotations
- Store quotation details and quotation items in the database
- Provide a user-friendly application interface

---

## Sofa Components

The costing system currently covers the following sofa components:

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

---

## System Architecture

```text
User
  ↓
Streamlit Application
  ↓
Python Services
  ↓
Supabase PostgreSQL Database
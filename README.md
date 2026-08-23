# VeritasIQ

## AI-Powered Product Intelligence for Industrial Commerce

VeritasIQ transforms limited and fragmented industrial product information into **structured, validated, evidence-backed product intelligence** ready for commerce and catalog workflows.

> **AI proposes. Validation decides.**

---

## Problem

Industrial product information is distributed across manufacturer websites, catalogs, technical documents, spreadsheets, supplier listings, and other digital sources.

This creates recurring challenges:

- Incomplete product information
- Inconsistent specifications and units
- Difficult cross-source verification
- Manual catalog enrichment
- Poor visibility into data confidence
- Time-consuming preparation of commerce-ready product data

A conventional AI extraction system can produce a clean-looking answer while still containing incorrect or unsupported product information.

VeritasIQ addresses this by combining **AI-powered enrichment, structured product representation, evidence, cross-source validation, explainability, and product health scoring**.

---

## Solution

VeritasIQ takes sparse product information and transforms it through an end-to-end intelligence pipeline:

```text
Input
  ↓
Product Extraction & Normalization
  ↓
AI-Powered Enrichment
  ↓
Evidence Collection
  ↓
Field-Level Validation
  ↓
Product Health Score
  ↓
Structured Commerce Delivery
```

The system is designed to make product intelligence not only richer, but also **traceable and assessable**.

---

## Key Features

### Multi-Format Ingestion

The processing layer includes parsers for:

- Individual product input
- CSV catalogs
- XLSX catalogs
- PDF documents

The current demonstrated Streamlit workflow focuses on individual product and CSV/XLSX catalog ingestion.

### AI-Powered Product Enrichment

Uses the **Google Gemini API** to generate structured product intelligence from limited product information.

For the UniHack workflow, **Google Search grounding** is used to support web-grounded enrichment.

The enrichment workflow can identify and structure information such as:

- Product identity
- Brand
- Manufacturer
- Manufacturer part number
- Product type
- Category
- Subcategory
- Dimensions
- Weight
- Material
- Color
- Size
- Price
- Warranty
- Certifications
- Included items
- Category-specific attributes
- Product content
- Evidence
- Product images
- Specification sheets

### Structured Product Representation

Extracted information is converted into a common `Product` representation so that different input formats and product sources can be processed consistently.

### Evidence & Explainability

Generated product information is accompanied by available supporting evidence.

Users can understand:

- Which sources support a value
- Whether available sources agree
- Where conflicts exist
- Why a validation result was produced

### Field-Level Validation

Product attributes are evaluated individually for consistency and support.

Validation can identify:

- Agreement
- Partial support
- Conflict
- Missing information

The system does not simply overwrite conflicting information; conflicts can be preserved and explained.

### Product Health Score

Validation results are summarized into a product-level health score to provide a quick view of product information quality.

### Commerce-Ready Delivery

For the UniHack challenge, enriched product intelligence is mapped into the required **252-column delivery format** and can be exported as CSV.

The expected output headers are preserved.

### Catalog-Scale Workflow

The same processing architecture supports both individual product enrichment and catalog-oriented CSV/XLSX workflows.

---

## Why VeritasIQ Is Different

Many AI enrichment workflows focus primarily on generating product descriptions or filling missing fields.

VeritasIQ focuses on the additional question:

> **How trustworthy is the generated product information?**

The system therefore separates **generation** from **validation**.

```text
AI
 ↓
Proposes product intelligence
 ↓
Evidence + validation
 ↓
Measures consistency
 ↓
Health score
 ↓
Commerce-ready output
```

This makes uncertainty and data quality visible instead of treating every AI-generated value as equally reliable.

The core idea is:

> **AI proposes product intelligence. VeritasIQ validates it against available evidence instead of blindly trusting the model.**

---

## Architecture

The solution follows an end-to-end pipeline:

**Product Input → Parsing & Mapping → AI Enrichment → Evidence & Sources → Field-Level Validation → Product Health Score → 252-Column Mapper → Commerce-Ready CSV**

Detailed architecture and editable PlantUML diagrams are available in `docs/diagrams/`.

### Architecture Diagram

![VeritasIQ Architecture](docs/diagrams/architecture.png)

---

## How VeritasIQ Works

The processing workflow follows a deliberate sequence:

| Stage | Purpose |
|---|---|
| **01 — Ingest** | Accept product information from multiple source formats |
| **02 — Extract** | Use AI to identify candidate product information |
| **03 — Discover / Enrich** | Identify relevant external product information |
| **04 — Normalize** | Convert comparable values into consistent representations |
| **05 — Validate** | Compare information and evaluate field-level consistency |
| **06 — Evidence** | Preserve available supporting source information |
| **07 — Explain** | Surface agreements, conflicts, and validation outcomes |
| **08 — Score** | Calculate product data health |
| **09 — Deliver** | Produce structured, commerce-ready output |

### Process Flow

![VeritasIQ Process Flow](docs/diagrams/process_flow.png)

---

## Trust Layer

The most important architectural distinction in VeritasIQ is the separation between **AI extraction** and **cross-source validation**.

```text
                         PRODUCT INPUT
                              │
                              ▼
                   ┌─────────────────────┐
                   │  Gemini Enrichment  │
                   │                     │
                   │ Candidate product   │
                   │ intelligence        │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ Canonical Product   │
                   │      Schema         │
                   └──────────┬──────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
       ┌─────────────────┐       ┌─────────────────┐
       │ Evidence /      │       │ Normalization   │
       │ Source Context  │       │                 │
       └────────┬────────┘       └────────┬────────┘
                │                         │
                └────────────┬────────────┘
                             ▼
                  ┌─────────────────────┐
                  │ Field-Level         │
                  │ Validation          │
                  └──────────┬──────────┘
                             │
               ┌─────────────┼─────────────┐
               ▼             ▼             ▼
          Evidence     Explainability    Health
          & Provenance                 Score
               │             │             │
               └─────────────┼─────────────┘
                             ▼
                  ┌─────────────────────┐
                  │ Trusted Structured  │
                  │ Product Data        │
                  └─────────────────────┘
```

The validation layer evaluates whether information is:

- Supported by available sources
- Consistent across available evidence
- Conflicting
- Incomplete
- Backed by evidence

This is the core trust mechanism of the platform.

---

## Canonical Product Model

Extracted information is converted into a common `Product` representation.

The canonical model supports:

- Product identity
- Brand
- Manufacturer
- Model / product numbers
- Product type
- Category
- Subcategory
- Dimensions
- Weight
- Material
- Color
- Size
- Price
- Warranty
- Certifications
- Included items
- Category-specific attributes
- Product content
- Evidence
- Product images
- Specification sheets

This provides a consistent representation before downstream processing.

---

## Normalization & Validation

### Normalization

Product values can be normalized before comparison so that equivalent representations can be evaluated consistently.

Weight normalization is currently supported as part of the validation pipeline.

### Cross-Source Validation

VeritasIQ evaluates product information using available evidence and can identify:

- Agreement
- Conflicting values
- Missing values
- Source-level evidence

The system does **not** simply overwrite conflicting information.

Conflicts can be preserved and explained.

---

## Evidence & Explainability

Validation results retain source information so that product claims can be traced back to available supporting evidence.

Users can understand:

- Which sources support a value
- Whether sources agree
- Where conflicts exist
- Why a validation result was produced

This turns a product value from:

> "AI says this is correct."

into:

> **"This value is supported by available evidence, these sources agree or conflict, and this is why VeritasIQ assigns its validation outcome."**

---

## Product Health Score

The validation results are summarized into a product-level health score.

The score provides a compact view of the quality and consistency of the available product intelligence.

Conceptually:

```text
Product Attributes
       ↓
Field-Level Validation
       ↓
Evidence / Consistency
       ↓
Health Contributions
       ↓
Overall Product Health Score
```

The health score is therefore a summary of validation outcomes rather than a replacement for field-level evidence.

---

## UniHack Challenge Workflow

For the UniHack product intelligence challenge, VeritasIQ transforms limited product information into the expected structured output.

The delivery pipeline:

```text
Limited Product Input
        ↓
AI Enrichment
        ↓
Structured Product Representation
        ↓
Validation & Evidence
        ↓
Product Health Assessment
        ↓
252-Column Delivery Mapping
        ↓
Commerce-Ready CSV
```

The delivery mapper populates the required **252-column schema** without modifying the expected output headers.

Supporting challenge resources and sample data are maintained under `tests/`.

---

## Use Cases

VeritasIQ is designed around the workflow of a product or catalog manager:

- Upload product information
- Extract product information
- Normalize attributes
- Enrich missing information
- Evaluate available evidence
- Compare information
- Detect conflicts
- Review validation outcomes
- Review product health
- Export structured product data

### Use-Case Diagram

![VeritasIQ Use Cases](docs/diagrams/use_case.png)

---

## Technology Stack

### AI & Enrichment

- **Google Gemini API** — product intelligence generation
- **Google Search Grounding** — web-grounded enrichment

### Application

- **Python** — application and processing logic
- **Streamlit** — interactive web interface

### Data Processing

- **Pandas** — catalog processing
- **Pydantic** — structured product models and validation
- **Structured JSON** — standardized AI output
- **pdfplumber** — PDF processing
- **OpenPyXL** — Excel processing

### Validation & Storage

- **Python validation layer** — field-level consistency checks
- **SQLite** — product/catalog persistence

### Delivery

- **CSV** — commerce-ready catalog delivery
- **252-column delivery mapper** — maps enriched intelligence to the required UniHack schema

### Development & Deployment

- **Streamlit Community Cloud** — deployed MVP
- **Git & GitHub** — version control
- **Pytest** — automated testing
- **PlantUML** — architecture, process-flow and use-case diagrams

---

## Project Structure

```text
veritas-iq/
|
+-- src/
|   +-- ai/              # AI extraction and enrichment
|   +-- models/          # Product data models
|   +-- parser/          # CSV, Excel and PDF parsing
|   +-- processing/      # Validation, mapping, scoring and matching
|   +-- storage/         # SQLite persistence
|   +-- app.py           # Streamlit application
|
+-- scripts/             # Evaluation and UniHack utilities
|
+-- tests/               # Automated test suite and fixtures
|
+-- docs/
|   +-- PRD.md
|   +-- schema_design.md
|   +-- diagrams/        # Architecture and process diagrams
|
+-- requirements.txt
+-- requirements-dev.txt
+-- README.md
```

---

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/krutika-codesdev/veritas-iq.git
cd veritas-iq
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

For development and testing:

```bash
pip install -r requirements-dev.txt
```

### 4. Configure environment variables

Create a local `.env` file:

```text
GEMINI_API_KEY=your_api_key
```

**Never commit `.env` or API keys to GitHub.**

### 5. Run the application

```bash
python -m streamlit run src/app.py
```

The application will be available at the local Streamlit URL shown in the terminal.

---

## Testing

The repository includes automated tests covering parsing, mapping, matching, validation, health scoring, and the UniHack workflow.

Run:

```bash
pytest -q
```

Current local validation:

**11 tests passed**

---

## Known Limitation

The current MVP uses web-grounded AI enrichment to identify supporting product information and sources.

The returned URLs are **not independently verified by a separate crawler in the current implementation**.

Therefore, the current validation layer should be understood as evidence-based and consistency-oriented rather than as an independent guarantee that every source URL is valid.

Independent source verification is planned as a future enhancement.

---

## Project Status

### Implemented

- Multi-format product layer
- CSV catalog processing
- XLSX catalog processing
- PDF parsing
- AI-powered product extraction
- Gemini-based product enrichment
- Google Search grounded enrichment
- Structured product representation
- Product normalization
- Field-level validation
- Cross-source consistency checks
- Evidence/provenance handling
- Product Health Score
- 252-column UniHack delivery mapping
- CSV delivery generation
- SQLite persistence
- Automated test coverage
- Architecture documentation
- Streamlit MVP deployment

### Demonstrated

The enrichment workflow has been tested across different industrial product categories, including:

- Freud
- KitchenAid
- DEWALT

The same enrichment workflow was used without category-specific code changes.

### Remaining Submission Work

- Final MVP screenshots
- Demo video
- Final presentation
- Final repository review

---

## Future Development

Potential extensions include:

1. **Independent Source Verification**

   Independently validate discovered URLs and supporting evidence.

2. **Large-Scale Catalog Processing**

   Add optimized batching, parallel processing and stronger retry handling for enterprise-scale catalogs.

3. **Document Intelligence**

   Expand product intelligence extraction across manufacturer catalogs and technical datasheets.

4. **Human-in-the-Loop Review**

   Allow experts to review and approve low-confidence or conflicting attributes.

5. **Continuous Product Updates**

   Re-enrich products when source information changes.

6. **Enterprise Integration**

   Integrate product intelligence with PIM, ERP and e-commerce catalog systems.

---

## Repository Documentation

### Architecture

[View Architecture Diagram](docs/diagrams/architecture.png)

### Process Flow

[View Process Flow Diagram](docs/diagrams/process_flow.png)

### Use Cases

[View Use-Case Diagram](docs/diagrams/use_case.png)

Editable PlantUML source files are also included in `docs/diagrams/`.

---

## Links

**GitHub Repository**

https://github.com/krutika-codesdev/veritas-iq

**Live Prototype**

https://ztu5wqfhzvnm4xs4r5ha69.streamlit.app/

**Demo Video**

https://drive.google.com/file/d/1q0WrarUEIZYhmAzQrP9BtJVh3uap2jqo/view?usp=sharing

---

## Demo Video

[Watch the VeritasIQ Demo](https://drive.google.com/file/d/1q0WrarUEIZYhmAzQrP9BtJVh3uap2jqo/view?usp=sharing)

---

## Team

**Team:** VeritasIQ

**Member:** Krutika P Mohanty

---

## Core Idea

> **VeritasIQ turns limited industrial product information into structured, validated and evidence-backed product intelligence.**
>
> **AI proposes. Validation decides.**
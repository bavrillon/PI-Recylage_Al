# PI-Recylage_Al


## Project: Optimization of Aluminum Alloy Recycling

To meet its low-carbon objectives, a firm must produce its aluminum alloys by recycling metallic scrap at scale. This decision-support tool uses constrained optimization (PuLP) on scrap and raw-material compositions to recommend the best mix.

---

### Detailed Description

Aluminum alloys are defined by their mass-percentage composition of elements, with the remainder being aluminum.  
For example:

| Element | Si   | Fe   | Cu   | Mn   | Mg   | Cr   | Zn   | Ti   |
|---------|------|------|------|------|------|------|------|------|
| % mass  | 0.50 | 0.50 | 4.30 | 0.60 | 1.50 | 0.10 | 0.25 | 0.15 |

The aluminum fraction is 100 – sum(other elements). To manufacture an alloy you can:
1. Mix pure aluminum + alloying elements.  
2. Mix scrap (pre-alloyed) + pure elements.

---

### Project Objective

Compare two strategies at a plant for each alloy:
- **With scrap:** minimize cost, CO₂ and maximize scrap use.  
- **Without scrap:** minimize cost and CO₂ using only pure materials.

The tool runs both optimizations per alloy and presents a side-by-side comparison.

---

### Input Data

Place CSV files (or an Excel workbook with same sheet names) in  
`data/db_building/tables_csv/`:

- **site.csv**  
- **alloy.csv**  
- **composition.csv**  
- **raw_material.csv**  
- **scrap.csv**  
- **recycling_cost.csv**  
- **currency.csv**

---
### Data Model Conventions

In our SQLite schema, all primary-key values follow a clear naming convention:

- **site** (`site_code`): 3‐letter codes : 
  `PAR`, `GEN`, `NYC`  
- **alloy** (`alloy_id`): starts with `A` + integer :
  `A1`, `A2`, `A3`, …  
- **composition** (`composition_id`): starts with `C` + integer : 
  `C1`, `C2`, `C3`, …  
- **raw_material** (`raw_material_id`): starts with `R` + integer :
  `R1`, `R2`, `R3`, …  
- **scrap** (`scrap_id`): starts with `S` + integer, e.g.  
  `S0`, `S1`, `S2`, …

This makes it easy to trace each record back to its source table and to avoid ID collisions when joining tables.

---
### Output Data

Once the optimization runs, you’ll get:

1.  **Streamlit UI** : interactive tables showing the optimal mix.
2.  **Excel Report** (`.xlsx`) : 
---

## Technical Choices

- **Python 3.13.5**  
- **Streamlit** for an interactive web UI  
- **SQLite** as a file-based database  
- **PuLP** for linear programming  
- **OpenPyXL** for Excel report generation  

Recommended environment:
python==3.13.5
streamlit==1.46.1
pulp==3.2.1
openpyxl==3.1.5

---

### Usage

1. Launch the Streamlit interface.
2. Select or import scrap data (manual entry or Excel file).
3. In the web UI:  
   - Import or verify your CSV/Excel data  
   - Select a plant (`site_code`) and an alloy (`alloy_id`)  
   - Launch optimizations (cost, CO₂ emissions, scrap utilization)  
4. View results on-screen or export a detailed Excel report via the “Export” button.  

---

## Stable version
Tagged at commit : c2fe4036e34cd340991b3f9eba9399edc4cba4f7

---

## Authors

**Bastien Avrillon, Elyes Beloucif, Aude Vendeuvre, Grégoire Béraud et Honoré Boïarsky**

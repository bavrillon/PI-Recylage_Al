# PI-Recylage_Al

## Project: Optimization of Aluminum Alloy Recycling

To meet its low-carbon objectives, a firm must produce its aluminum alloys by massively recycling metallic scrap. Intelligent decision-making is needed for scrap purchasing; this is why we aim to develop a decision-support application. The tool is based on constrained optimization using the chemical compositions of available scraps and the alloys to be produced.

---

### Detailed Description

Aluminum alloys are defined by their chemical composition expressed as a mass percentage for each element, with the remainder being aluminum. For example:

| Element | Si   | Fe   | Cu   | Mn   | Mg   | Cr   | Zn   | Ti   |
|---------|------|------|------|------|------|------|------|------|
| % mass  | 0.50 | 0.50 | 4.30 | 0.60 | 1.50 | 0.10 | 0.25 | 0.15 |

This means the alloy contains 4.3% copper by mass, and the aluminum content is 92.1% (100 – sum of other elements).

To manufacture these alloys, raw materials must be mixed to achieve the correct chemical composition. There are two options:
1. Mix pure aluminum and alloying elements.
2. Mix metallic scraps (already alloyed) and complete with pure elements.

---

### Project Objective

The goal is to provide a tool to compare two strategies for producing each alloy at a plant:

- **With scrap:** For each available scrap, the tool computes the optimal mix of raw materials and scrap to minimize three objectives: **cost**, **CO2 emissions**, and **scrap usage** (maximize the use of scrap).
- **Without scrap:** The tool computes the optimal mix of pure raw materials only, minimizing **cost** and **CO2 emissions**.

For each alloy, the application performs all relevant optimizations and allows the user to compare the results for both strategies.

---

### Input Data


---

### Output Data


---

## Technical choices

- **Python** for its mature ecosystem of scientific computing and optimization libraries, enabling rapid development and maintainable code.  
- **Streamlit** for an interactive web interface that runs locally. 
- **SQLite** as a file-based database to store persistent information about plants, raw materials, scrap batches, and alloy specifications.
- **PuLP** to model and solve constrained linear optimization problems for multiple objectives (cost, CO₂, primary metal use).
- **OpenPyXL** to generate detailed, structured Excel reports tailored to industrial needs and compatible with existing workflows.  

The following environment is recommended to run the project:
- Python==3.13.5
- streamlit==1.46.1
- sqlite3 
- pulp==3.2.1
- openpyxl==3.1.5

---

### Usage

1. Launch the Streamlit interface.
2. Select or import scrap data (manual entry or Excel file).
3. Choose the plant and alloy to optimize.
4. Run the optimization for cost, CO2, or alloy, with or without scrap.
5. View and export the results.

---

## Stable version
The stable release is tagged at commit hash:  

---

## Authors

Bastien Avrillon, Elyes Beloucif, Aude Vendeuvre, Grégoire Béraud et Honoré Boïarsky
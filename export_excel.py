import os
import openpyxl


def export_to_excel(data, filename, folder="exports"):
    """
    Exporte une liste de listes dans un fichier Excel.

    Args:
        data (list): Liste de listes (chaque sous-liste = une ligne, la première ligne = en-têtes).
        filename (str): Nom du fichier Excel de sortie.
        folder (str): Dossier où enregistrer le fichier.
    """
    if not data:
        print("Aucune donnée à exporter.")
        return

    # Crée le dossier s'il n'existe pas
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    workbook = openpyxl.Workbook()
    sheet = workbook.active

    for row in data:
        sheet.append(row)

    workbook.save(filepath)
    print(f"Données exportées avec succès dans {filepath}.")


if __name__ == "__main__":
    output_data = [
        [
            "Alloy",
            "Objective",
            "Raw Material Mix",
            "Total Cost (€)",
            "Total CO2 (kg)",
            "Virgin Metal (%)",
        ],
        [
            "Alloy A",
            "Minimize Cost",
            "Al: 92.1%, Cu: 4.3%, Si: 0.5%, Fe: 0.5%",
            1200,
            350,
            80,
        ],
        [
            "Alloy A",
            "Minimize CO2",
            "Al: 90.0%, Cu: 5.0%, Si: 0.6%, Fe: 0.4%",
            1300,
            300,
            75,
        ],
        [
            "Alloy A",
            "Minimize Virgin Metal",
            "Al: 88.0%, Cu: 6.0%, Si: 0.7%, Fe: 0.3%",
            1400,
            370,
            60,
        ],
        [
            "Alloy B",
            "Minimize Cost",
            "Al: 91.0%, Cu: 5.0%, Si: 1.0%, Fe: 0.5%",
            1100,
            340,
            78,
        ],
    ]
    export_to_excel(output_data, "alloy_optimization_results.xlsx")
 




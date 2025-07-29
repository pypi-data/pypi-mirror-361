import pandas as pd
import sys
import csv

def hello_world():
    print('Hello world fron xls_to_csv')
    
def parse_csv(csv_file):
    # Ouvrir le fichier CSV en mode lecture
    with open(csv_file, newline='') as csvfile:
        # Créer un lecteur CSV
        lecteur_csv = csv.reader(csvfile, delimiter=';')
        donnees = list(lecteur_csv)
        # Parcourir chaque ligne du fichier CSV
        for lindex, ligne in enumerate(donnees):
            # Parcourir chaque cellule de la ligne
            for cindex, cellule in enumerate(ligne):
                if len(cellule) > 0:
                    donnees[lindex][cindex] = cellule.replace('\n','|')

    with open(csv_file, 'w', newline='') as fichier_sortie:
        writer_csv = csv.writer(fichier_sortie, delimiter=';')
        # Écrire les données modifiées dans le nouveau fichier CSV
        writer_csv.writerows(donnees)


def convert_to_csv(xls_file,csv_file):
    df = pd.read_excel(xls_file)
    df.to_csv(csv_file, index=False, sep=';')
    parse_csv(csv_file)
    return

if __name__ == '__main__':
    arguments = sys.argv

    if len(arguments) == 3:
        xl_filename = arguments[1].replace('\\','/')  # Premier argument
        csv_filename = arguments[2].replace('\\','/')  # Deuxième argument
        convert_to_csv(xl_filename, csv_filename)    
    else:
        xl_filename = "Q:/is/chantier/1000/1000_DETAIL.xlsx"  # Premier argument
        csv_filename = "Q:/is/chantier/1000/1000_DETAIL.csv"  # Deuxième argument
        convert_to_csv(xl_filename, csv_filename)    
        print("Veuillez spécifier des arguments.")


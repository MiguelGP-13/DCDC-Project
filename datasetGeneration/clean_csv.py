import pandas as pd
import csv

def clean_csv(input_file, output_file):
    # Lista para almacenar las filas limpias
    clean_rows = []
    
    # Leer el archivo original manteniendo las comillas
    with open(input_file, 'r', encoding='utf-8') as file:
        # Usar el csv.reader con un delimitador de punto y coma
        csv_reader = csv.reader(file, delimiter=';', quotechar='"')
        header = next(csv_reader)  # Guardar la cabecera
        clean_rows.append(header)
        
        for row in csv_reader:
            # Limpiar cada campo de la fila
            cleaned_row = [field.replace('\n', ' ').replace('\r', ' ').strip() for field in row]
            clean_rows.append(cleaned_row)
    
    # Escribir el archivo limpio
    with open(output_file, 'w', encoding='utf-8', newline='') as file:
        csv_writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerows(clean_rows)

if __name__ == "__main__":
    clean_csv('eures-utf8.csv', 'eures_clean_new.csv')
import csv

eures_path = 'eures_clean.csv'
input_path = 'ofertasAnonimizado_clean.csv'
output_path = 'ofertasAnonimizado_unique.csv'

# Leer ids de eures_clean.csv
ids = set()
with open(eures_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ids.add(row.get('id',''))

# Filtrar el archivo de ofertas
with open(input_path, 'r', encoding='utf-8') as fin, open(output_path, 'w', encoding='utf-8', newline='') as fout:
    reader = csv.DictReader(fin, delimiter=';')
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter=';')
    writer.writeheader()
    kept = 0
    removed = 0
    for row in reader:
        if row.get('id','') in ids:
            removed += 1
            continue
        writer.writerow(row)
        kept += 1

print(f'Kept: {kept}, Removed: {removed}')

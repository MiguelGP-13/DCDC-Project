import csv
from googletrans import Translator

input_file = 'ofertasAnonimizado_unique_ts.csv'
output_file = 'ofertasAnonimizado_unique_ts_traducido.csv'
provincias_catalanas = {'Barcelona', 'Girona', 'Tarragona', 'Lleida'}

translator = Translator()

with open(input_file, 'r', encoding='utf-8') as fin, open(output_file, 'w', encoding='utf-8', newline='') as fout:
    reader = csv.DictReader(fin, delimiter=';')
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter=';')
    writer.writeheader()
    for row in reader:
        region = row.get('region', '')
        if region in provincias_catalanas:
            desc = row.get('descripcion', '')
            # Detectar si hay catalán (heurística simple: palabras típicas)
            if any(pal in desc.lower() for pal in ['amb', 'per', 'dilluns', 'divendres', 'dimecres', 'dijous', 'dissabte', 'diumenge', 'treballar', 'ofereix', 'incorporació', 'contracte', 'empresa', 'persones', 'serveis', 'activitat', 'atenció', 'domiciliària', 'grans', 'català', 'castellà', 'client', 'oferta', 'inscripció', 'referència', 'convocatòria', 'col·lectiu', 'conveni', 'salarial', 'torn', 'matí', 'tarda', 'horari', 'dilluns', 'divendres', 'dimecres', 'dijous', 'dissabte', 'diumenge']):
                try:
                    translated = translator.translate(desc, src='ca', dest='es').text
                    row['descripcion'] = translated
                except Exception:
                    pass  # Si falla la traducción, deja el texto original
        writer.writerow(row)
print('Traducción completada')

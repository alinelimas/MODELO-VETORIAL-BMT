import os
import re
import csv
import logging
import xml.etree.ElementTree as ET
from nltk.stem import PorterStemmer

os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename='logs/processador.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def processador():
    logging.info(f'Executando {__file__}')
    conf_file = "PC.CFG"

    leia = 'C:/Users/aloli/Desktop/Python/Nova pasta/CysticFibrosis2-20230406/data/cfquery.xml'
    consultas = 'consultas.csv'
    esperados = 'esperados.csv'

    stem = False
    ps = PorterStemmer()

    with open("C:/Users/aloli/Desktop/Python/Nova pasta/CONFIG/PC.CFG.xml") as config_file:
        logging.info(f'Abrindo {conf_file}')

        for line in config_file:
            line = line.rstrip()
            print(line)

            if line == "STEMMER":
                logging.info("Escolhida a configuração de fazer stemming das consultas")
                stem = True
                continue
            elif line == "NOSTEMMER":
                logging.info("Escolhida a configuração de não fazer stemming das consultas")
                stem = False
                continue

            try:
                instruct, filename = line.split('=')
            except ValueError:
                logging.error(f'Erro ao ler a linha: {line}. A linha será ignorada.')
                continue

            if instruct == "LEIA":
                leia = filename
            elif instruct == "CONSULTAS":
                consultas = filename
            elif instruct == "ESPERADOS":
                esperados = filename
            else:
                logging.error(f'Erro ao ler {conf_file}')

    with open(leia) as xml_file, open(consultas, "w", newline='') as consulta_f, open(esperados, "w", newline='') as esperado_f:
        logging.info(f"Abrindo {leia}, {consultas} e {esperados}")
        tree = ET.parse(xml_file)
        root = tree.getroot()

        consulta_w = csv.writer(consulta_f, delimiter=";")
        consulta_w.writerow(["QueryNumber", "QueryText"])

        esperado_w = csv.writer(esperado_f, delimiter=";")
        esperado_w.writerow(["QueryNumber", "DocNumber", "DocVotes"])

        lines_read = 0
        lines_written_consulta = 0
        lines_written_esperado = 0

        for query in root:
            lines_read += 1
            lines_written_consulta += 1

            query_number = query.find("QueryNumber")
            query_text = query.find("QueryText")
            processed_text = re.sub('[^a-zA-Z]', ' ', query_text.text)

            if stem:
                processed_text = ' '.join(ps.stem(word) for word in processed_text.split())

            consulta_w.writerow([query_number.text, processed_text.upper()])

            records = query.find("Records")
            for item in records:
                lines_written_esperado += 1
                score = item.attrib['score']
                s = sum([1 for x in score if x != "0"])
                esperado_w.writerow([query_number.text, item.text, s])

        logging.info(f"{lines_read} consultas processadas de {leia}")
        logging.info(f"{lines_written_consulta} linhas escritas em {consultas}") 
        logging.info(f"{lines_written_esperado} linhas escritas em {esperados}") 
        logging.info(f"Fechando {leia}, {consultas} e {esperados}")

def main():
    processador()

if __name__ == "__main__":
    main()

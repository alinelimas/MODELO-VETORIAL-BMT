import os
import re
import csv
import logging
import xml.etree.ElementTree as ET
from collections import defaultdict
import sys
from nltk.stem import PorterStemmer

os.makedirs('logs', exist_ok=True)
os.makedirs('results', exist_ok=True)  # Criar diretório 'results' se não existir

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('logs/gerador.log', encoding='utf-8')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def read():
    logger.info(f'Executando {__file__}')
    min_length = 2
    conf_file = 'GLI.CFG.xml'
    stem = False

    with open('C:/Users/aloli/Desktop/Python/Nova pasta/CONFIG/GLI.CFG.xml') as config_file:
        logger.info('Abrindo C:/Users/aloli/Desktop/Python/Nova pasta/CONFIG/GLI.CFG.xml')
        gli_dict = defaultdict(list)

        for line in config_file:
            line = line.rstrip()

            if line == "STEMMER":
                logger.info("Escolhida a opção de fazer stemming das palavras")
                from nltk.stem import PorterStemmer
                ps = PorterStemmer()
                stem = True
                continue
            elif line == "NOSTEMMER":
                stem = False
                continue

            try:
                instruct, filename = line.split('=')
            except ValueError:
                logging.error(f'Erro ao ler a linha: {line}. A linha será ignorada.')
                continue

            if instruct == "LEIA":
                with open(f"C:/Users/aloli/Desktop/Python/Nova pasta/{filename}") as xml_file:
                    logger.info(f'Processando {filename}')
                    tree = ET.parse(xml_file)
                    root = tree.getroot()

                    for record in root:
                        record_num = int(record.find("RECORDNUM").text)

                        text_elem = record.find("ABSTRACT")
                        if text_elem is None:
                            text_elem = record.find("EXTRACT")

                        if text_elem is not None:
                            words = text_elem.text
                            words = re.sub('[^a-zA-Z]', ' ', words)
                            words = words.split()
                            if stem:
                                words = [ps.stem(word).upper() for word in words if len(word) >= min_length]
                            else:
                                words = [word.upper() for word in words if len(word) >= min_length]
                            for word in words:
                                gli_dict[word].append(record_num)
            elif instruct == "ESCREVA":
                return filename, gli_dict
            else:
                logger.error(f"Erro ao ler {conf_file}")
                sys.exit(1)  # Encerra a execução do programa com um código de erro

def write(filename, gli_dict):
    with open(f"results/{filename}", 'w', newline='') as csv_file:
        logger.info(f'Abrindo {filename}')

        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(["Word", "Documents"])

        lines_written = 0
        for key, value in sorted(gli_dict.items()):
            writer.writerow([key, value])
            lines_written += 1

        logger.info(f'{lines_written} linhas escritas em {filename}')
        logger.info(f'Fechando {filename}')

def main():
    filename, gli_dict = read()
    write(filename, gli_dict)

if __name__ == "__main__":
    main()


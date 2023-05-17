import os
import csv
import logging
from collections import Counter
import numpy as np

os.makedirs('logs', exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('logs/buscador.log', encoding='utf-8')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def buscador():
    logger.info(f'Executando {__file__}')
    min_length = 2
    conf_file = 'BUSCA.CFG.xml'
    result_lines = 0

    with open("C:/Users/aloli/Desktop/Python/Nova pasta/CONFIG/BUSCA.CFG.xml") as config_file:
        logger.info(f'Abrindo {conf_file}')
        for line in config_file:
            line = line.rstrip()

            if line == "STEMMER":
                stem = True
                continue
            elif line == "NOSTEMMER":
                stem = False
                continue

            instruct, filename = line.split('=')

            if instruct == "MODELO":
                modelo = filename
            elif instruct == "CONSULTAS":
                consultas = filename
            elif instruct == "RESULTADOS":
                oldname, extension = filename.split('.')

                if stem:
                    resultados = oldname + "-stemmer." + extension
                else:
                    resultados = oldname + "-nostemmer." + extension
            elif instruct == "SIMILARIDADE":
                logger.info(f"Utilizando similaridade por {filename}")
                sim = filename

    matrix_dict = {}

    with open('C:/Users/aloli/Desktop/Python/Nova pasta/PROGRAMAS/modelo.csv') as model_file:
        model_reader = csv.reader(model_file, delimiter=";")
        next(model_reader)

        for line in model_reader:
            if len(line) >= 3:
                matrix_dict[line[0]] = {int(line[1]): float(line[2])}

    with open(resultados, "w", newline='') as result_file:
        writer = csv.writer(result_file, delimiter=";")
        writer.writerow(["QueryNumber", "[DocRanking, DocNumber, Similarity]"])

    with open(consultas) as query_file:
        logger.info(f'Abrindo {consultas}')
        query_reader = csv.reader(query_file, delimiter=";")
        next(query_reader)

        query_num = 0
        for query in query_reader:
            query_dict = {}

            words = query[1].split()
            words = [word for word in words if len(word) >= min_length]
            query_vec = Counter(words)

            for word in query_vec:
                if word in matrix_dict.keys():
                    current_dict = matrix_dict[word]
                    weight_list = []
                    for key in current_dict:
                        weight_list.append(current_dict[key])
                        if key not in query_dict:
                            query_dict[key] = current_dict[key] * query_vec[word]
                        else:
                            query_dict[key] += current_dict[key] * query_vec[word]

                    # similaridade por cosseno
                    if sim == "cosseno":
                        for key in current_dict:
                            query_dict[key] /= np.linalg.norm(list(query_vec.values())) * np.linalg.norm(weight_list)

            query_num += 1
            sorted_values = sorted(query_dict.items(), key=lambda item: item[1], reverse=True)

            with open(resultados, "a", newline='') as result_file:
                result_writer = csv.writer(result_file, delimiter=";")

                for i, elem in enumerate(sorted_values):
                    li = [i, elem[0], elem[1]]
                    result_writer.writerow([query[0], li])
                    result_lines += 1
                    logger.info(f'{query_num} consultas processadas de {consultas}')

    logger.info(f'{result_lines} linhas escritas em {resultados}')
    logger.info(f'Fechando {consultas}')


def main():
    buscador()


if __name__ == '__main__':
    main()

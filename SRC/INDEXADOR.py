import re
import math
import xml.etree.ElementTree as ET

def read_config_file(config_file):
    tree = ET.parse(config_file)
    root = tree.getroot()
    read_filename = root.findtext('LEIA')
    write_filename = root.findtext('ESCREVA')
    frequency = root.findtext('FREQUÊNCIA')
    return read_filename, write_filename, frequency

def read_text_file(filename):
    with open(filename, 'r') as file:
        return file.read()

def write_text_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)

def tokenize_text(text):
    return re.findall(r'\b\w+\b', text)

def calculate_tf(word, document):
    word_count = document.count(word)
    return word_count / len(document)

def calculate_idf(word, documents):
    document_count = sum(1 for doc in documents if word in doc)
    return math.log(len(documents) / (1 + document_count))

def index_documents(documents):
    index = {}
    for i, document in enumerate(documents):
        words = [word.upper() for word in tokenize_text(document) if len(word) >= 2 and word.isalpha()]
        for word in words:
            if word not in index:
                index[word] = {}
            tf = calculate_tf(word, document)
            idf = calculate_idf(word, documents)
            index[word][i] = tf * idf
    return index

def save_index(index, filename):
    index_data = '\n'.join(f'{word}: {document}' for word, document in index.items())
    write_text_file(filename, index_data)

def load_index(filename):
    index_data = read_text_file(filename)
    index = {}
    for line in index_data.split('\n'):
        if line:
            word, document = line.split(':')
            index[word.strip()] = eval(document.strip())
    return index

def index_files(config_file):
    read_filename, write_filename, frequency = read_config_file(config_file)
    documents = read_text_file(read_filename).splitlines()
    index = index_documents(documents)
    save_index(index, write_filename)

index_files('C:/Users/aloli/Desktop/Python/Nova pasta/CONFIG/INDEX.CFG.xml')




import hashlib
from tkinter import filedialog
from xmlschema import XMLSchema
from lxml import etree
import os
import re
from mtranslate import translate
from tkinter import Tk
from tkinter.filedialog import askopenfilename




# Abrir o arquivo XML
janela = Tk()
janela.withdraw()
janela.attributes("-topmost", True) #manter no topo

# Exiba a caixa de diálogo para selecionar o arquivo

#xml_file_path = askopenfilename()
files = filedialog.askopenfilenames(title="Selecionar Arquivos", filetypes=(("Todos os arquivos", "*.*"),))

janela.destroy()
for xml_file_path in files:
    nome_do_arquivo = os.path.basename(xml_file_path)
   
    schemas = r'\SCHEMAS'

    correcoes = []  # Lista para armazenar as correções a serem aplicadas

    # Carrega o arquivo XML
    with open(xml_file_path, 'rb') as xml_file:
        xml_content = xml_file.read()

        # Converte o conteúdo XML em um objeto ElementTree
        schema_location = re.search(r'xsi:schemaLocation="([^"]+)"', str(xml_content)).group(1)
        # Extrai o nome do arquivo XSD
        filename = re.search(r'/([^/]+\.xsd)$', schema_location).group(1)
        filename = filename.split('/')[-1]
        filename = filename.rsplit(" ", 1)[-1]

        if 'tiss' in filename:
            prefixo = 'ans'
        elif 'ptu' in schema_location:
            prefixo = 'ptu'

        root = etree.fromstring(xml_content)
        #print(root)
        # Obtém o namespace do arquivo XML
        namespace = root.tag.split('}')[0][1:]
        if namespace == None:
            namespace = re.search(r'xmlns:ans="(.*?)"', xml_content).group(1)
            print(namespace)


        # Carrega o arquivo XSD
        xsd_arquivo = os.path.join(schemas, filename)
        print("xsd_arquivo: ", filename)
        schema = XMLSchema(xsd_arquivo)

        # Valida o XML em relação ao XSD e obtém todos os erros
        errors = schema.iter_errors(root)
        hash_element = root.find('{'+namespace+'}'+'hash')
        #hash_value = hash_element.text
        #print(hash_value)
        # Verifica se ocorreram erros e adiciona as correções à lista
        if errors:
            print(f'validação: {nome_do_arquivo}')
            for error in errors:
                xpath = error.path
                erro_reason = translate(error.reason, "pt")
                print(f"- Linha: {error.sourceline}, Coluna: {xpath}\n{erro_reason}")
                print()
def extract_text(elem):
    text = ''
    hash_value = None
    for e in elem.iter():
        
        hash_nomespace = elem.tag.split("}")[0][1:]
        if e.text and e.text != '\n' and e.tag != '{'+hash_nomespace+'}'+'hash':
            text += e.text
        elif e.tag == '{'+hash_nomespace+'}'+'hash':
            hash_value = e.text
    return text, hash_value
if xml_file_path:
    root = etree.parse(xml_file_path).getroot()
    
    text, hash_value = extract_text(root)
    hash_md5 = hashlib.md5(text.encode('ISO-8859-1')).hexdigest()
    if prefixo == 'ans':
            if hash_value == hash_md5.upper():
                print('Hash Válido!')
            else:
                print('Hash Atualizado: ', hash_md5.upper(), 'Hash Arquivo: ',hash_value)
    elif prefixo == 'ptu':
            if hash_value == hash_md5:
                print('Hash Válido!',)
            else:
                print('Hash Arquivo: ',hash_value, 'Hash Calculado: ',hash_md5)

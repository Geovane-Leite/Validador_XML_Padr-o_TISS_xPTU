import hashlib
from tkinter import filedialog
from xmlschema import XMLSchema
from lxml import etree
import os
import re
from mtranslate import translate
from tkinter import Tk

script_path = os.path.abspath(__file__)
directory = os.path.dirname(script_path)
dir_schemas = os.path.join(directory,'SCHEMAS')


janela = Tk()
janela.withdraw()
janela.attributes("-topmost", True)

files = filedialog.askopenfilenames(title="Selecionar Arquivos", filetypes=(("Todos os arquivos", "*.*"),))
janela.destroy()

for xml_file_path in files:
    nome_do_arquivo = os.path.basename(xml_file_path)
   
    schemas = dir_schemas 
    
    with open(xml_file_path, 'rb') as xml_file:
        xml_content = xml_file.read()

        filename = None
       
        try:
            schema_location = re.search(r'xsi:schemaLocation="([^"]+)"', str(xml_content)).group(1)
        
            # Extrai o nome do arquivo XSD
        
            filename = re.search(r'/([^/]+\.xsd)$', schema_location).group(1)
            filename = filename.split('/')[-1]
            filename = filename.rsplit(" ", 1)[-1]
            
        #Excessão quando não tem arquivo xsd informado no arquivo
        except:
            if 'ptuA500' in str(xml_content):
                filename = 'ptu_A500.xsd'
            elif 'ptuA550' in str(xml_content):
                filename = 'ptu_A550.xsd'
            elif 'ptuA560' in str(xml_content):
                filename = 'ptu_A560.xsd'
        

        if 'tiss' in filename:
            prefixo = 'ans'
        elif 'ptu' in filename:
            prefixo = 'ptu'
        elif 'ptu' in tp_arquivo2:
            prefixo = 'ptu'
        root = etree.fromstring(xml_content)

        namespace = root.tag.split('}')[0][1:]
        if namespace == None:
            namespace = re.search(r'xmlns:ans="(.*?)"', xml_content).group(1)
            print(namespace)

     
        dir_schemas = os.path.join(schemas, filename)

        xsd_arquivo = None 
        # Verifique se cada arquivo existe e pare quando encontrar o primeiro válido
        if os.path.isfile(dir_schemas):
            xsd_arquivo = dir_schemas
    
        elif xsd_arquivo == None:
            tp_arquivo_input = input('Não encontramos o schema, Qual Nome do arquivo XSD? ex: NNNNNN.xsd ')
            dir_schemas_2 = os.path.join(schemas, tp_arquivo_input)
            xsd_arquivo = dir_schemas_2
            
    
        print('xsd: ',xsd_arquivo)
        schema = XMLSchema(xsd_arquivo)

        # Valida o XML em relação ao XSD e obtém todos os erros
        errors = schema.iter_errors(root)

        if errors:
            print(f'validação: {nome_do_arquivo}')
            for error in errors:
                xpath = error.path
                erro_reason = translate(error.reason, "pt")
                print(f"- Linha: {error.sourceline}, Coluna: {xpath}\n{erro_reason}")
                print()
#Hash + Calculo Hash                
def extract_text(elem):
    text = ''
    hash_value = None
    hash_nomespace = elem.tag.split("}")[0][1:]
    
    for e in elem.iter():
        if e.text and not e.text.isspace() \
            and e.tag not in [
                '{'+hash_nomespace+'}'+'hash',
                '{'+hash_nomespace+'}'+'dt_postagem',
                '{'+hash_nomespace+'}'+'nr_protocolo'
            ]:
            text += e.text
        elif e.tag == '{'+hash_nomespace+'}'+'hash':
            hash_value = e.text
    
    return text, hash_value
    
if xml_file_path:
    root = etree.parse(xml_file_path).getroot()
    
    text, hash_value = extract_text(root)
    text = text.encode('iso-8859-1').decode('utf-8')
    hash_md5 = hashlib.md5(text.encode('ISO-8859-1')).hexdigest()
    if 'tissM' in filename:
            if hash_value == hash_md5.upper():
                print('Hash Válido!')
            else:
                print('Hash Calculado: ', hash_md5.upper(), 'Hash Arquivo: ',hash_value)
    elif prefixo == 'ptu':
            if hash_value == hash_md5:
                print('Hash Válido!',)
            else:
                print('Hash Arquivo: ',hash_value, 'Hash Calculado: ',hash_md5)

    elif 'tissV' in filename:
            if hash_value == hash_md5:
                print('Hash Válido!')
            else:
                print('Hash Atualizado: ', hash_md5, 'Hash Arquivo: ',hash_value)

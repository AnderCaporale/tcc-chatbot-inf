import glob
import os
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()  # Carregando QDRANT_API_KEY e QDRANT_URL

#embeddings_model = OllamaEmbeddings(model="deepseek-r1:8b")
embeddings_model = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

banco_directory = "banco_embbedings"

def load_docs():
    arquivos = glob.glob(r"documentos/*/*.txt")

    docs = []
    for arq in arquivos:
        loader = TextLoader(arq, encoding="utf-8")
        docs.extend(loader.load())

    return docs

def load_doc(path):
    arquivos = glob.glob(rf"{path}")

    docs = []
    for arq in arquivos:
        loader = TextLoader(arq, encoding="utf-8")
        docs.extend(loader.load())

    return docs

def create_chunks(docs):
    chunks = []

    for doc in docs:
        texto_original = Document(page_content=doc.page_content)
        docs_list = [texto_original]

        text_splitter = CharacterTextSplitter(
            separator="\n",  # dividir por paragrafos
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False,
        )
        texts = text_splitter.split_documents(docs_list)
        chunks.extend(texts)
            
    return chunks

# Cria o banco de dados vetorial, gerando os embeddings dos documentos
def cria_banco_vetorial_e_indexa_documentos(documentos):
    print(f">>> REALIZANDO INDEXAÇÃO DOS CHUNKS NO BANCO VETORIAL")
    # Cria o banco de dados vetorial, gerando os embeddings dos documentos
    # Adicionar os chunks no banco em lote
    Chroma.from_documents(documentos, collection_name="documents", embedding=embeddings_model, persist_directory=f"./{banco_directory}")


def ler_txt_e_retorna_texto_em_document():
    print(f">>> REALIZANDO A LEITURA DO TXT EXEMPLO")
    # lendo o txt com o texto exemplo e criando o Document:
    lista_documentos = TextLoader(r'arq_py_aula_15/exemplo_texto.txt', encoding='utf-8').load()

    print("Texto lido e convertido em Document")
    print(lista_documentos)
    print("-----------------------------------")
    return lista_documentos

def conecta_banco_vetorial_pre_criado():
    vector_store_from_client = Chroma(
        persist_directory=f"./{banco_directory}",
        collection_name="documents",
        embedding_function=embeddings_model,
    )
    return vector_store_from_client

def check_banco():
    # Verifica se o diretório "./banco_embbedings" não existe
    if not os.path.exists(f"./{banco_directory}"):
        print(f"O diretório './{banco_directory}' não existe... realizando a indexação")
        texto_completo_lido = load_docs()
        divide_texto = create_chunks(texto_completo_lido)
        cria_banco_vetorial_e_indexa_documentos(divide_texto)
    else:
        print(f"O diretório './{banco_directory}' já existe. Pulando a criação do banco vetorial.")

def add_documento(document_path):
    print("Path Fornecido: " + document_path)
    novos_documentos = load_doc(document_path)
    print("Novos Documentos: " )
    print(novos_documentos)
    novos_chunks = create_chunks(novos_documentos)
    print("Novos Chunks: ")
    print(novos_chunks)
    db = conecta_banco_vetorial_pre_criado()
    print(">> Adicionando novos embeddings ao banco existente...")
    db.add_documents(novos_chunks)
    print(">> Embeddings adicionados com sucesso!")



#add_documento(r"documentos/PosGraduacao/*.txt")

check_banco()
# Conectando ao banco vetorial pre criado com os dados indexados:
db = conecta_banco_vetorial_pre_criado()

# Agora podemos trabalhar com o banco uma vez que ele está com os dados já indexados.

# query = "Na expansão da inteligência artificial quais questões importantes são levantadas?"
query = "Como fazer intercambio?"
pedacoes_retornados = db.similarity_search(query, k=10)

# Total de docs retornados
print("Total de pedaços. Deve ter o valor de 'K':")
print(len(pedacoes_retornados))
# Exibir o conteúdo do primeiro documento retornado
# Imprimindo os pedaços retornados do banco:
i=0
for elm in pedacoes_retornados:
    print(f"------ chunk {i} -------")
    print(pedacoes_retornados[i].page_content)
    print("--------------------")
    i+=1
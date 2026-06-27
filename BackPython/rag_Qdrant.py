import glob
import os
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import time
from langchain_ollama import OllamaEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()  # Carregando QDRANT_API_KEY e QDRANT_URL

embeddings_model = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
banco_directory = "banco_embbedings" #Criado com modelo gemini-embedding-001

def load_docs():
    arquivos = glob.glob("documentos/**/*.*", recursive=True)
    docs = []

    for arq in arquivos:
        try:
            if arq.lower().endswith(".txt"):
                loader = TextLoader(arq, encoding="utf-8")
            elif arq.lower().endswith(".pdf"):
                loader = PyPDFLoader(arq)
            else:
                continue

            docs.extend(loader.load())
            print(f">>> CARREGADO: {arq}")

        except Exception as e:
            print(f">>> ERRO AO CARREGAR {arq}: {e}")

    return docs

def load_doc_txt(path):
    arquivos = glob.glob(rf"{path}")

    docs = []
    for arq in arquivos:
        loader = TextLoader(arq, encoding="utf-8")
        docs.extend(loader.load())

    return docs

def load_doc_pdf(path):
    arquivos = glob.glob(rf"{path}")

    docs = []
    for arq in arquivos:
        loader = PyPDFLoader(arq)
        docs.extend(loader.load())

    return docs

def create_chunks(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n"]
    )

    chunks = text_splitter.split_documents(docs)

    print(f">>> TOTAL DE CHUNKS: {len(chunks)}")

    return chunks


def cria_banco_vetorial_e_indexa_documentos(documentos):
    print(">>> REALIZANDO INDEXAÇÃO DOS CHUNKS NO BANCO VETORIAL")

    # cria banco vazio inicialmente
    db = QdrantVectorStore.from_documents(
        documents=[],
        embedding=embeddings_model,
        api_key=os.environ.get("QDRANT_API_KEY"),
        url=os.environ.get("QDRANT_URL"),
        prefer_grpc=True,
        collection_name=banco_directory
    )

    batch_size = 10
    for i in range(0, len(documentos), batch_size):
        lote = documentos[i:i + batch_size]
        print(f">>> INDEXANDO LOTE {i} até {i + len(lote)}")

        try:
            db.add_documents(lote)
            time.sleep(2)    # pequena pausa para evitar rate limit

        except:
            print(">>> LIMITE DA API ATINGIDO")
            print(">>> AGUARDANDO 60 SEGUNDOS...")
            time.sleep(60)
            db.add_documents(lote)

def conecta_banco_vetorial_pre_criado():
    server = QdrantVectorStore.from_existing_collection(
        collection_name=f"{banco_directory}",
        url=os.environ.get("QDRANT_URL"),
        embedding=embeddings_model,
        api_key=os.environ.get("QDRANT_API_KEY")
    )
    return server

def criar_banco():
    texto_completo_lido = load_docs()
    divide_texto = create_chunks(texto_completo_lido)
    cria_banco_vetorial_e_indexa_documentos(divide_texto)


def add_documento_txt(document_path):
    novos_documentos = load_doc_txt(document_path)
    novos_chunks = create_chunks(novos_documentos)
    db = conecta_banco_vetorial_pre_criado()
    db.add_documents(novos_chunks)


# add_documento_pdf("documentos/PlanosEnsino/INF01202.pdf")
def add_documento_pdf(document_path):
    novos_documentos = load_doc_pdf(document_path)
    print(f">>> PDF carregado: {len(novos_documentos)} páginas")
    novos_chunks = create_chunks(novos_documentos)
    db = conecta_banco_vetorial_pre_criado()
    db.add_documents(novos_chunks)


#Função para testar uma chamada ao banco vetorial
def chamar_banco():
    # Conectando ao banco vetorial pre criado com os dados indexados:
    db = conecta_banco_vetorial_pre_criado()

    query = "Qual o objetivo da disciplina ALGORÍTMOS E PROGRAMAÇÃO?"
    pedacoes_retornados = db.similarity_search(query, k=3)

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

#criar_banco()
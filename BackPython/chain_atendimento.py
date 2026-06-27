from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel
from operator import itemgetter
from models import choose_llm_model_ollama
from rag_Qdrant import *
import re

# Carregar as chaves APIs presentes no arquivo .env
load_dotenv()
# --------------------------------------------------------------------------------

# Conecta Banco Vetorial
db_vetorial = conecta_banco_vetorial_pre_criado()

db_retriever = db_vetorial.as_retriever(search_kwargs={'k': 5})

"""Função para pegar o conteúdo de cada chunk e criar um unico texto/string"""
def cria_texto_dos_documentos_retornados(documentos):
    return "\n\n".join(doc.page_content for doc in documentos)

# Criando o ChatPromptTemplate que irá responder a pergunta do usuário se estiver no escopo
sys_atendimento_geral_prompt = """ Você é um assistente de uma universidade e tem como objetivo responder às perguntas dos
alunos. Os assuntos serão sobre dúvidas em relação à faculdade UFRGS e ao Instituto de Informática, também chamado de INF.

## Regras:
1 - Nunca invente informação. Responda que desconhece o assunto caso você não souber responder e diga para consultar o site
oficial da faculdade.
2 - Sempre se baseie no contexto que é entregue entre as tags <contexto></contexto>. As informações presentes nestas tags
foram obtidas de uma base de conhecimento.
3 - Evite falar 'no contexto...' ou 'conforme o contexto...' porque o usuário desconheçe sobre a presença desse contexto.

## Contexto Recuperado:
<contexto>
{contexto_obtido}
</contexto>
"""

# Criando o ChatPromptTemplate que irá responder a alternativa correta da pergunta
sys_atendimento_geral_prompt_perguntas = """
Você é um assistente da universidade UFRGS e do Instituto de Informática (INF). Seu objetivo é responder questões objetivas de múltipla escolha.

Cada questão possui cinco alternativas: A, B, C, D e E.
Apenas UMA alternativa está correta.

## Regras:
1 - Utilize somente as informações presentes no contexto entre as tags <contexto></contexto>.
2 - Nunca mencione o contexto ou a existência do contexto.
3 - Sua resposta deve conter EXATAMENTE uma única letra:
A
B
C
D
E

4 - Não escreva palavras, frases, explicações ou justificativas.
5 - Não escreva pontuação.
6 - Não escreva espaços ou quebras de linha extras.

## Exemplos de resposta válida:
A
C
E

## Exemplos de resposta inválida:
Alternativa A
A)
A.
Resposta: B
A resposta correta é C

## Contexto Recuperado:
<contexto>
{contexto_obtido}
</contexto>

Sua resposta final deve conter somente uma letra entre A, B, C, D ou E.
"""


def criar_prompt(x):
    print(" ---  Alternativa Obtida: " + str(x["alternativa"]))

    system_prompt = sys_atendimento_geral_prompt_perguntas if str(x["alternativa"]) == "1" else sys_atendimento_geral_prompt

    # Criando o ChatPromptTemplate com a entrada do usuário e o histórico:
    prompt = ChatPromptTemplate([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "Mensagem do usuário: {input_user}"),
    ])
    return prompt.invoke(x)


def normalizar_se_necessario(x):

    if str(x["alternativa"]) != "0":
        match = re.search(r'\b([ABCDE])\b', x["resposta"].upper())
        return {
            "resposta_original":  x["resposta"],
            "resposta_normalizada": match.group(1) if match else None
        }

    return x["resposta"]

chain_de_atendimento_geral = (RunnableParallel({"input_user": itemgetter("input_user"),
                                "history": itemgetter("history"),
                                "model_llm": itemgetter("model_llm"),
                                "alternativa": itemgetter("alternativa"),
                                "contexto_obtido": RunnableLambda(
                                    lambda x: 
                                        ""
                                        if str(x["algoritmo"]) != '0'
                                        else cria_texto_dos_documentos_retornados(
                                            db_retriever.invoke(x["input_user"])
                                        )
                                ),
                                })
                                | RunnableLambda(lambda x: {
                                    "prompt": criar_prompt(x),
                                    "model_llm": x["model_llm"],
                                    "contexto_obtido": x["contexto_obtido"],
                                    "alternativa": x["alternativa"],
                                })
                                | RunnableLambda(lambda x: {
                                    "resposta": StrOutputParser().invoke(
                                        choose_llm_model_ollama(x)
                                    ),
                                    "alternativa": x["alternativa"]
                                })
                                | RunnableLambda(normalizar_se_necessario))


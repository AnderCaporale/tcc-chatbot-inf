from operator import itemgetter

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel

from models import choose_llm_model_ollama

# Carregar as chaves APIs presentes no arquivo .env
load_dotenv()
# --------------------------------------------------------------------------------


# Criando o ChatPromptTemplate que vai agir como assistente, mas não irá responder.
sys_prompt_fora_do_tema = """NÃO RESPONDA A PERGUNTA. Você está recebendo uma mensagem fora do seu escopo, então informe ao usuário que não é seu objetivo.
## Regras:
1 - NÃO RESPONDA A PERGUNTA.
2 - Você é um assistente de uma universidade e não deve responder as perguntas.
3 - Nunca utilize conhecimento próprio para responder.
4 - Nunca explique o tema perguntado.
5 - Caso o usuário apenas cumprimente (Olá, Oi, Boa tarde, etc.), responda normalmente e apresente seu objetivo (assistente da universidade UFRGS).
6 - A pergunta não deve ser respondida.

Exemplos:

Usuário:
Faz qualquer pergunta.
Resposta:
Desculpe, posso auxiliar apenas com assuntos relacionados à UFRGS e ao Instituto de Informática (INF).
"""

# Criando o ChatPromptTemplate com a entrada do usuário e o histórico:
fora_do_tema_prompt_template = ChatPromptTemplate([("system", sys_prompt_fora_do_tema),
                                               MessagesPlaceholder(variable_name="history"),
                                               ("human", "Dúvida do usuário: {input_user}"),
                                               ])

chain_temas_nao_relacionados = (RunnableLambda(lambda x: {
                                    "prompt": fora_do_tema_prompt_template.invoke(x),
                                    "model_llm": x["model_llm"]
                                })
                                | RunnableLambda(choose_llm_model_ollama) 
                                | StrOutputParser())

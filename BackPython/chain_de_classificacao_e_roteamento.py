from operator import itemgetter

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda

from models import Rota

# Carregar as chaves APIs presentes no arquivo .env
load_dotenv()
# --------------------------------------------------------------------------------

# Instanciar um chatmodel para comunicarmos com os modelos LLMs
modelo_groq = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

# --------------------------------------------------------------------------------
# Criando o classificador da pergunta de entrada do usuário:
class Rota(BaseModel):
    opcao: int = Field(description="""Defina 1 se a mensagem do usuário for relacionado à dúvidas sobre universidade, professores ou entidades relacionadas à faculdade,
    e 0 caso contrário""")

# Criando o parser estruturado
parser_classifica = JsonOutputParser(pydantic_object=Rota)

# Criando o ChatPromptTemplate que solicitará ao LLM que ele classifique a entrada do usuário:
sys_prompt_rota = """Você é um especialista em classificação. Você receberá perguntas do usuário e precisará classificar, 
Se a mensagem do usuário for sobre as mensagens do chat, relacionado à dúvidas sobre universidade, professores ou entidades relacionadas à faculdade a 
opcao deve ser 1, caso contrário deve ser 0.
Atente-se que a mensagem pode se referir indiretamente a algum dos casos acima, então também deve ser a opção 1.
Se a mensagem for algo em relação ao histórico do chat, também responda a opção 1.
Apenas classifique, não responda à pergunta do usuário. 
Importante: Responda apenas com a resposta final, sem descrever seu raciocínio.
Pergunta Usuário: {input_user}
"""

rota_prompt_template = ChatPromptTemplate([("system", sys_prompt_rota), 
                                           MessagesPlaceholder(variable_name="history"),
                                           ("human", "{input_user}")])


# Criando a Chain que vai classificar a entrada do usuário:
chain_de_roteamento = ( RunnableLambda(lambda x: print(x) or {
                            "prompt": rota_prompt_template.invoke(x),
                            "model_llm": x["model_llm"]
                      })
                        | RunnableLambda(lambda x:tratamento_rota(x))
                      )


def tratamento_rota(entrada: dict):
    try:
        structured_llm = modelo_groq.with_structured_output(Rota)
        response = structured_llm.invoke(entrada["prompt"])

        if response is None:
            return Rota(opcao=0)
        return response

    except Exception as e:
        print("ERRO AO PARSEAR:", e)
        return Rota(opcao=0)
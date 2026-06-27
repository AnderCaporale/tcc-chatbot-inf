from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Carregar as chaves APIs presentes no arquivo .env
load_dotenv()
# --------------------------------------------------------------------------------

# Instanciar um chatmodel para comunicarmos com os modelos LLMs
modelo_groq = ChatGroq(model="openai/gpt-oss-20b", temperature=0.1)

# Criando o ChatPromptTemplate que vai agir como um personal para tirar dúvidas do usuário
sys_prompt_formatacao = """Você deve receber um texto e formatar uma saída para ser exibido em um chat.

## Regras:
1 - Não modifique o texto original, apenas sua formatação.
2 - Adicione quebras de linhas onde achar necessário. 
3 - Não enfeite o texto, deixe apenas legível.
4 - Além disso, sempre adicione a frase "FORMATADO!" no final de cada resposta.
"""

# Criando o ChatPromptTemplate com a entrada do usuário e o histórico:
formatacao_prompt_template = ChatPromptTemplate([("system", sys_prompt_formatacao),
                                               ("human", "{input_user}"),
                                               ])

chain_formatacao = formatacao_prompt_template | modelo_groq | StrOutputParser()

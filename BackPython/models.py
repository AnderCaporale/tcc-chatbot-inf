from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

load_dotenv()

# Criando o classificador da pergunta de entrada do usuário:
class Rota(BaseModel):
    opcao: int = Field(description="""Defina 1 se a mensagem do usuário for relacionado à dúvidas sobre universidade, professores ou entidades relacionadas à faculdade,
                    e 0 caso contrário""")


def choose_llm_model_groq(entrada: dict):
    #print(entrada)
    model_llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    model_code = entrada["model_llm"]

    if(model_code == '0'):
        model_llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    elif(model_code == '1'):
        model_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    elif(model_code == '2'):
        model_llm = ChatGroq(model="qwen/qwen3-32b", temperature=0)

    return model_llm.invoke(entrada["prompt"])


def choose_llm_model_ollama(entrada: dict, roteamento=False): 
    print(entrada)
    model_code = entrada["model_llm"]

    model_name = "llama3.2:3b"

    if model_code == '0':
        model_name = "llama3.2:3b"
    elif model_code == '1':
        model_name = "qwen2.5:3b"
    elif model_code == '2':
        model_name = "phi3.5:3.8b"
    elif model_code == '3':
        model_name = "smollm2:1.7b"
    elif model_code == '4':
        model_name = "mistral:7b"

    #print(model_name)
    llm = ChatOllama(
        model=model_name,
        temperature=0
    )

    if (roteamento):
        try:
            structured_llm = llm.with_structured_output(Rota)
            response = structured_llm.invoke(entrada["prompt"])

            if response is None:
                return Rota(opcao=0)
            return response

        except Exception as e:
            return Rota(opcao=0)
    
    response = llm.invoke(entrada["prompt"])    

    return response

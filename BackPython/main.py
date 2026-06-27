from chain_de_classificacao_e_roteamento import chain_de_roteamento
from chain_atendimento import chain_de_atendimento_geral
from chain_temas_nao_relacionados import chain_temas_nao_relacionados
from memoria import get_session_history, trimmer
from operator import itemgetter
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory

from models import Rota

## Definindo a função de escolha de roteamento (nó que irá classificar a pergunta do usuário e mandar para a 'rota' correspondente do fluxo):
def executa_roteamento(entrada: dict):
    print("Opção de Roteamento: ")
    print(entrada["roteamento"])
    if entrada["roteamento"].opcao == 1:
        print(f">> Opção classe Pydantic: {entrada['roteamento'].opcao} (Atendimento Geral)")
        return chain_de_atendimento_geral
    else:
        print(f">> Opção classe Pydantic: {entrada['roteamento'].opcao} (Assuntos não relacionados à academia)")
        return chain_temas_nao_relacionados


# Cria a cadeia final usando LangChain Expression Language (LCEL)
chain_principal = (RunnableParallel({"input_user": itemgetter("input_user"),
                                     "history": itemgetter("history"),
                                     "roteamento": chain_de_roteamento,
                                     "model_llm": itemgetter("model_llm"),
                                     "algoritmo": itemgetter("algoritmo"),
                                     "alternativa": RunnableLambda(lambda _: "0"),
                                     })
                   | RunnableLambda(executa_roteamento)
                  )


## Encapsulando a chain com a classe de gestão de mensagens de histórico
chain_principal_com_trimming = (
    RunnablePassthrough.assign(history=itemgetter("history") | trimmer)
    | chain_principal
)


chain_principal_com_historico = RunnableWithMessageHistory(
    chain_principal_com_trimming,
    get_session_history,
    input_messages_key="input_user",
    history_messages_key="history",
    model_llm="model_llm"
)

chain_principal_alternativas = (
    RunnableParallel({
        "input_user": itemgetter("input_user"),
        "history": RunnableLambda(lambda _: []),  # histórico vazio
        "roteamento": RunnableLambda(lambda _: Rota(opcao=1)),
        "model_llm": itemgetter("model_llm"),
        "algoritmo": itemgetter("algoritmo"),
        "alternativa": RunnableLambda(lambda _: "1"),
    })
    | RunnableLambda(executa_roteamento)
)
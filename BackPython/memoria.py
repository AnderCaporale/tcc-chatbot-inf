import sqlite3
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import trim_messages

nome_banco = "memory_history"

## Criando o gestor de memória (histórico): Função para retornar o histórico de mensagens com base no `session_id`
def get_session_history(session_id):
    return SQLChatMessageHistory(session_id, connection=f"sqlite:///{nome_banco}.db")

# Criando a função que corta o histórico e captura as 30 ultimas mensagens trocadas na conversa:
trimmer = trim_messages(strategy="last", max_tokens=30, token_counter=len)

async def limpar_banco():
   conn = sqlite3.connect(f"{nome_banco}.db")
   cursor = conn.cursor()
   
   cursor.execute("DELETE FROM message_store;")
   conn.commit()
   conn.close()
   print("Todos os históricos foram apagados (tabela message_store limpa).")

async def limpar_historico_user(userId):
   conn = sqlite3.connect(f"{nome_banco}.db")
   cursor = conn.cursor()
   
   cursor.execute(f"DELETE FROM message_store WHERE session_id = {userId};")
   conn.commit()
   conn.close()
   print(f"Todo o histórico do usuário {userId} foi apagado.")
from fastapi import FastAPI, Request
from main import *
from memoria import *

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:4200",  # Exemplo: seu frontend em localhost
    "*" # Permite todas as origens (não recomendado para produção)
]

app = FastAPI(title="Chatbot INF")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

@app.post("/chat-with-history")
async def chat(request: Request):
    body = await request.json()
    mensagem = body["input"]["input_user"]
    userId = body["config"]["id"]
    algoritmo = body["config"]["algoritmo"]
    modeloLLM = body["config"]["model_llm"]
    result = chain_principal_com_historico.invoke({"input_user": mensagem, "model_llm": modeloLLM, "algoritmo": algoritmo}, config={"configurable": {"session_id": userId}})
    return result

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    mensagem = body["input"]["input_user"]
    userId = body["config"]["id"]
    algoritmo = body["config"]["algoritmo"]
    modeloLLM = body["config"]["model_llm"]
    result = chain_principal_alternativas.invoke({"input_user": mensagem, "model_llm": modeloLLM, "algoritmo": algoritmo}, config={"configurable": {"session_id": userId}})
    return result

@app.post("/limpar-banco")
async def limpar():
    print("Limpeza do banco")
    await limpar_banco()
    return("Banco limpo")

@app.post("/limpar-historico/{userId}")
async def limpar_historico(userId: str):
    await limpar_historico_user(userId)
    return {"status": "Histórico limpo", "userId": userId}


#if __name__ == "__name__":
import uvicorn
uvicorn.run(app, host="localhost", port=8000)
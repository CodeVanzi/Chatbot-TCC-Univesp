import logging
import sys
import torch
from flask import Flask, request, jsonify
from llama_index.core import (
    Settings,
    StorageContext,
    load_index_from_storage,
    PromptTemplate,
    VectorStoreIndex,
    SimpleDirectoryReader
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.gemini import Gemini
import os
from dotenv import load_dotenv

# --- Carregar Variáveis de Ambiente ---
load_dotenv()

# --- Configurações ---
GEMINI_MODEL_NAME = "models/gemini-2.0-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Nova chave secreta para autenticação básica da API
CHATBOT_API_SHARED_SECRET = os.getenv("CHATBOT_API_SHARED_SECRET")

EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"
DATA_DIR = "../data"
PERSIST_DIR = "../storage_gemini_llm"


# --- Inicialização do Flask ---
app = Flask(__name__)

# --- Logging ---
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.info("Iniciando configuração da API do Chatbot com Gemini LLM...")
if CHATBOT_API_SHARED_SECRET:
    app.logger.info("Verificação de chave secreta da API está ATIVADA.")
else:
    app.logger.warning("AVISO: Verificação de chave secreta da API está DESATIVADA (CHATBOT_API_SHARED_SECRET não definida).")

# --- Variáveis Globais para LlamaIndex (inicializadas uma vez) ---
query_engine = None

def initialize_rag_pipeline():
    global query_engine

    app.logger.info("Configurando modelos LlamaIndex...")
    try:
        if not GEMINI_API_KEY:
            app.logger.error("ERRO CRÍTICO: Chave de API do Gemini (GEMINI_API_KEY) não encontrada.")
            return False

        device = "cuda" if torch.cuda.is_available() else "cpu"
        app.logger.info(f"Usando dispositivo para embedding local: {device}")
        app.logger.info(f"Configurando embedding model local: {EMBEDDING_MODEL_NAME}")
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_MODEL_NAME, device=device
        )
        app.logger.info("Embedding model local configurado.")

        app.logger.info(f"Configurando LLM via Gemini API: {GEMINI_MODEL_NAME}")
        Settings.llm = Gemini(model_name=GEMINI_MODEL_NAME, api_key=GEMINI_API_KEY)
        app.logger.info("LLM Gemini configurado.")

        if not os.path.exists(PERSIST_DIR):
            app.logger.info(f"Diretório do índice '{PERSIST_DIR}' não encontrado. Tentando criar...")
            if not os.path.exists(DATA_DIR):
                app.logger.error(f"ERRO: Diretório de dados '{DATA_DIR}' não encontrado.")
                return False
            
            app.logger.info(f"Carregando documentos de '{DATA_DIR}' para indexação...")
            documents = SimpleDirectoryReader(DATA_DIR).load_data()
            if not documents:
                app.logger.error(f"Nenhum documento carregado de '{DATA_DIR}'.")
                return False
                
            app.logger.info(f"Documentos carregados: {len(documents)}. Iniciando indexação...")
            index = VectorStoreIndex.from_documents(documents)
            app.logger.info("Indexação concluída.")
            app.logger.info(f"Persistindo o índice em '{PERSIST_DIR}'...")
            index.storage_context.persist(persist_dir=PERSIST_DIR)
            app.logger.info(f"Índice salvo em '{PERSIST_DIR}'.")
        else:
            app.logger.info(f"Carregando índice de {PERSIST_DIR}...")
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)
            app.logger.info("Índice carregado.")

        app.logger.info("Criando query engine...")
        qa_prompt_tmpl_str = (
            "Você é um assistente prestativo e informativo, especializado em cultivo de cogumelos.\n"
            "Com base no CONTEXTO fornecido abaixo, responda à PERGUNTA do usuário.\n"
            "Se o CONTEXTO não tiver a resposta, mas a PERGUNTA for sobre cultivo de cogumelos, use seu conhecimento geral para responder.\n"
            "Se a PERGUNTA não for sobre cultivo de cogumelos, informe educadamente que você só pode ajudar com esse tópico.\n"
            "Suas respostas devem ser detalhadas, formais, porém amigáveis e diretas. Não repita a pergunta.\n"
            "Não mencione explicitamente o 'CONTEXTO' ou o documento fonte na sua resposta final.\n\n"
            "CONTEXTO:\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "PERGUNTA: {query_str}\n\n"
            "RESPOSTA DETALHADA:"
        )
        qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

        query_engine = index.as_query_engine(
            streaming=False,
            text_qa_template=qa_prompt_tmpl,
            similarity_top_k=5 # para ajustar o número de chunks recuperados
        )
        app.logger.info("Query engine criado com sucesso.")
        return True

    except Exception as e:
        app.logger.error(
            f"Erro durante inicialização do LlamaIndex com Gemini: {e}", exc_info=True
        )
        return False

# --- Endpoint da API ---
@app.route("/ask", methods=["POST"])
def ask_chatbot():
    # --- Verificação de Chave Secreta Compartilhada ---
    if CHATBOT_API_SHARED_SECRET:
        client_api_key = request.headers.get('X-API-Key')
        if not client_api_key or client_api_key != CHATBOT_API_SHARED_SECRET:
            app.logger.warning(
                f"Tentativa de acesso não autorizada ao endpoint /ask. Chave fornecida: '{client_api_key}'"
            )
            return jsonify({"error": "Acesso não autorizado. Chave de API inválida ou ausente."}), 401
    # --- Fim da Verificação ---

    if query_engine is None:
        app.logger.error("Query engine não inicializado.")
        return jsonify({"error": "Serviço de chatbot não está pronto"}), 503

    data = request.get_json()
    if not data or "question" not in data:
        app.logger.warning("Requisição recebida sem JSON ou chave 'question'")
        return jsonify({"error": "JSON inválido ou chave 'question' ausente"}), 400

    user_query = data["question"]
    app.logger.info(f"Pergunta recebida para Gemini (autorizada): {user_query}")

    if not user_query.strip():
        app.logger.warning("Pergunta recebida está vazia.")
        return jsonify({"error": "Pergunta não pode ser vazia"}), 400

    try:
        app.logger.info("Consultando o query engine (Gemini LLM)...")
        response = query_engine.query(user_query)
        answer = str(response)
        app.logger.info(f"Resposta do Gemini gerada (início): {answer[:100]}...")
        return jsonify({"answer": answer})

    except Exception as e:
        app.logger.error(
            f"Erro ao processar a query '{user_query}' com Gemini: {e}", exc_info=True
        )
        return jsonify({"error": "Erro interno ao processar a pergunta com o assistente externo"}), 500

# --- Inicialização e Execução ---
if __name__ == "__main__":
    if initialize_rag_pipeline():
        app.logger.info("Inicialização do RAG com Gemini LLM completa. Iniciando servidor Flask...")
        app.run(host="0.0.0.0", port=5001, debug=False)
    else:
        app.logger.error("Falha ao inicializar o pipeline RAG com Gemini. Servidor Flask não iniciado.")
import logging
import sys
import torch
from flask import Flask, request, jsonify
from llama_index.core import (
    Settings,
    StorageContext,
    load_index_from_storage,
    PromptTemplate,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
import os

# --- Configurações ---
LLM_MODEL_NAME = "llama3.2:3b"
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"
DATA_DIR = "../data"
PERSIST_DIR = "../storage"  # Diretório onde o índice está salvo

# --- Inicialização do Flask ---
app = Flask(__name__)

# --- Logging (Opcional, mas útil para API) ---
# Configurar logging para Flask (pode ajustar o nível)
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.info("Iniciando configuração da API do Chatbot...")

# --- Variáveis Globais para LlamaIndex (inicializadas uma vez) ---
query_engine = None


def initialize_rag_pipeline():
    """Função para configurar modelos e carregar/criar o índice."""
    global query_engine  # Para modificar a variável global

    app.logger.info("Configurando modelos LlamaIndex...")
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        app.logger.info(f"Usando dispositivo: {device}")

        app.logger.info(f"Configurando embedding model: {EMBEDDING_MODEL_NAME}")
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_MODEL_NAME, device=device
        )
        app.logger.info("Embedding model configurado.")

        app.logger.info(f"Configurando LLM via Ollama: {LLM_MODEL_NAME}")
        # Aumentar timeout pode ser necessário para LLMs locais
        Settings.llm = Ollama(model=LLM_MODEL_NAME, request_timeout=180.0)
        app.logger.info("LLM configurado.")

        # --- Carregar o Índice ---
        if not os.path.exists(PERSIST_DIR):
            app.logger.error(
                f"Erro: Diretório do índice '{PERSIST_DIR}' não encontrado."
            )
            app.logger.error(
                "Execute o script de indexação primeiro para criar o índice."
            )
            # Poderia tentar criar aqui, mas é melhor garantir que ele exista
            # Para este exemplo, vamos parar se o índice não existir
            return False
            # Alternativamente, você pode descomentar as linhas abaixo para criar
            # se não existir, mas isso atrasará o startup da API na primeira vez.
            # app.logger.info(f"Criando índice em {PERSIST_DIR}...")
            # documents = SimpleDirectoryReader(DATA_DIR).load_data()
            # index = VectorStoreIndex.from_documents(documents)
            # index.storage_context.persist(persist_dir=PERSIST_DIR)
            # app.logger.info(f"Índice criado e salvo em {PERSIST_DIR}.")

        else:
            app.logger.info(f"Carregando índice de {PERSIST_DIR}...")
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)
            app.logger.info("Índice carregado.")

        # --- Configurar Prompt e Query Engine ---
        app.logger.info("Criando query engine...")
        qa_prompt_tmpl_str = (
            "Você é um chatbot especializado em auxiliar o usuário com informações sobre cogumelos.\n"
            "Informações de contexto estão abaixo.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Informações da pergunta do usuário:\n"
            "---------------------\n"
            "{query_str}\n"
            "---------------------\n"
            "Instruções para o chatbot:\n"
            "---------------------\n"
            "Com base inicialmente nas informações de contexto fornecidas sobre cogumelos, "
            "e APENAS se a pergunta tiver relação com cogumelos, responda à pergunta\n"
            "A resposta deve misturar o contexto com informações do chatbot do treinamento anterior\n"
            "Se o contexto não contiver a resposta, responda usando apenas os conhecimentos prévios do chatbot, e não informe que não encontrou a resposta no contexto\n"
            "A resposta deve ser relativamente extensa e bem detalhada, o chatbot deve ser formal mas amigável e direto, e não deve repetir a pergunta do usuário, para não ser redundante\n"
            "IMPORTANTE: Se a pergunta não tiver relação com cogumelos, responda educadamente que você não pode ajudar com essa pergunta, mas não dê a entender que você está reagindo às instruções, apenas à pergunta do usuário\n"
            "O chatbot NUNCA deve fornecer o caminho do documento de contexto\n"
            "MUITO IMPORTANTE: Antes de responder qualquer coisa, para evitar alucinações, tenha certeza que entendeu as instruções para o chatbot, mas não reagindo às instruções, apenas à pergunta do usuário\n"
        )
        qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

        query_engine = index.as_query_engine(
            streaming=False,  # Streaming é mais complexo para API simples
            text_qa_template=qa_prompt_tmpl,
        )
        app.logger.info("Query engine criado com sucesso.")
        return True

    except Exception as e:
        app.logger.error(
            f"Erro durante inicialização do LlamaIndex: {e}", exc_info=True
        )
        return False


# --- Endpoint da API ---
@app.route("/ask", methods=["POST"])
def ask_chatbot():
    """Recebe uma pergunta via POST e retorna a resposta do chatbot."""
    if query_engine is None:
        app.logger.error("Query engine não inicializado.")
        return (
            jsonify({"error": "Serviço de chatbot não está pronto"}),
            503,
        )  # Service Unavailable

    data = request.get_json()
    if not data or "question" not in data:
        app.logger.warning("Requisição recebida sem JSON ou chave 'question'")
        return (
            jsonify({"error": "JSON inválido ou chave 'question' ausente"}),
            400,
        )  # Bad Request

    user_query = data["question"]
    app.logger.info(f"Pergunta recebida: {user_query}")

    if not user_query.strip():
        app.logger.warning("Pergunta recebida está vazia.")
        return jsonify({"error": "Pergunta não pode ser vazia"}), 400

    try:
        app.logger.info("Consultando o query engine...")
        response = query_engine.query(user_query)
        answer = str(response)  # Garantir que é string
        app.logger.info(f"Resposta gerada (início): {answer[:100]}...")
        return jsonify({"answer": answer})

    except Exception as e:
        app.logger.error(
            f"Erro ao processar a query '{user_query}': {e}", exc_info=True
        )
        return (
            jsonify({"error": "Erro interno ao processar a pergunta"}),
            500,
        )  # Internal Server Error


# --- Inicialização e Execução ---
if __name__ == "__main__":
    # Inicializa o pipeline RAG ANTES de iniciar o servidor Flask
    if initialize_rag_pipeline():
        app.logger.info("Inicialização do RAG completa. Iniciando servidor Flask...")
        # debug=False é importante para produção e evita inicialização dupla
        # host='0.0.0.0' permite acesso de outras máquinas na rede (como o Django)
        app.run(
            host="0.0.0.0", port=5001, debug=False
        )  # Usando porta 5001 para evitar conflito com Django (porta 8000)
    else:
        app.logger.error(
            "Falha ao inicializar o pipeline RAG. Servidor Flask não iniciado."
        )

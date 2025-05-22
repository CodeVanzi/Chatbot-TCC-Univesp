import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader, PromptTemplate
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

# Configurações básicas
load_dotenv()
app = Flask(__name__)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(logging.INFO)

# Inicialização dos modelos
def initialize_services():
    try:
        # Configuração do Gemini
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente")

        # Configurar embedding e LLM do Gemini
        Settings.embed_model = GeminiEmbedding(
            model_name="models/embedding-001",
            api_key=GEMINI_API_KEY
        )
        
        Settings.llm = Gemini(
            model_name="models/gemini-1.5-flash",
            api_key=GEMINI_API_KEY
        )

        # Carregar documentos (ajuste o path conforme necessário)
        documents = SimpleDirectoryReader("data").load_data()
        app.logger.info(f"Documentos carregados: {len(documents)}")

        # Criar índice na memória
        global index
        index = VectorStoreIndex.from_documents(documents)
        app.logger.info("Índice vetorial criado com sucesso")

        return True

    except Exception as e:
        app.logger.error(f"Erro na inicialização: {str(e)}")
        return False

# Template de prompt
qa_template = PromptTemplate(

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

@app.route('/ask', methods=['POST'])
def ask_endpoint():
    if request.json and 'question' in request.json:
        try:
            query = request.json['question']
            query_engine = index.as_query_engine(
                text_qa_template=qa_template,
                similarity_top_k=3
            )
            response = query_engine.query(query)
            return jsonify({"answer": str(response)})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Requisição inválida"}), 400

if __name__ == '__main__':
    if initialize_services():
        port = int(os.environ.get("PORT", 5001))
        app.logger.info(f"Iniciando servidor na porta {port}")
        app.run(host='0.0.0.0', port=port)
    else:
        app.logger.error("Falha na inicialização do serviço")

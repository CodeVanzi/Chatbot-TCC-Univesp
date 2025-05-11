# Projeto Integrador TCC - Sistema de Apoio à Decisão para Produtores de Cogumelos

**Autores:** [Lembrar de Inserir Nomes do Grupo Aqui]
**Orientadora:** Profª Carla Dominique Silva Vasconcelos
**Instituição:** Universidade Virtual do Estado de São Paulo (UNIVESP)
**Cursos:** Ciência de Dados / Engenharia da Computação
**Período:** 2025

## 1. Introdução e Motivação

Este repositório documenta o desenvolvimento do componente "Chatbot Especializado" como parte do Projeto Integrador de Conclusão de Curso (TCC). O projeto geral visa criar um **Sistema de Apoio à Decisão para Produtores de Cogumelos**, focado nas necessidades da Fazenda Nova Esperança, conforme detalhado no Relatório Inicial do TCC.

A Fazenda enfrenta desafios específicos:
*   **Sr. Eric (Proprietário):** Dificuldade em analisar a rentabilidade de diferentes espécies de cogumelos devido à falta de tempo e dados estruturados.
*   **Sr. Victor e Equipe Técnica:** Necessidade de suporte técnico rápido e confiável sobre práticas de cultivo, manejo e solução de problemas operacionais.

Enquanto um *Dashboard Interativo* visa atender à necessidade do Sr. Eric (coletando dados via Web Scraping e ETL), este componente foca em criar um **Chatbot Especializado** para auxiliar a equipe técnica do Sr. Victor.

**Objetivo do Chatbot:** Fornecer respostas precisas e contextuais sobre o cultivo de cogumelos, utilizando como base de conhecimento principal o documento técnico da Embrapa: *"Produção de Cogumelos por Meio de Tecnologia Chinesa Modificada"*.

**Restrições do Projeto:**
*   Curto prazo de execução (TCC).
*   Recursos limitados (computacionais e financeiros).
*   Necessidade de uma solução funcional e demonstrável.

---

## 2. Diário de Bordo do Desenvolvimento do Chatbot

Esta seção narra a jornada de desenvolvimento, as decisões tomadas e as evoluções do chatbot.

### Fase 1: Pesquisa Inicial e Definição da Abordagem (RAG)

*   **Desafio:** Como criar um chatbot que responda perguntas técnicas específicas sobre cultivo de cogumelos, baseado em um documento PDF extenso, dentro das restrições do projeto?
*   **Opções Consideradas:**
    *   **Sistemas Baseados em Regras/Intenções (NLU Tradicional):** Exigiria mapear manualmente muitas intenções e entidades, criar fluxos de diálogo e uma base de conhecimento estruturada. Considerado **inviável** pelo tempo e complexidade de cobrir todo o conteúdo do PDF da Embrapa.
    *   **Fine-tuning de LLMs:** Treinar um LLM especificamente sobre o PDF seria computacionalmente caro e exigiria um dataset de perguntas/respostas considerável. **Inviável** pelos recursos limitados.
    *   **Retrieval-Augmented Generation (RAG):** Abordagem que combina a busca de informações relevantes em uma base de dados (no nosso caso, o PDF da Embrapa) com a capacidade de geração de texto de um Large Language Model (LLM). O LLM usa os trechos recuperados do PDF como contexto para formular a resposta.
*   **Decisão:** **Adotar a abordagem RAG.**
    *   **Justificativa:**
        *   Permite usar o PDF da Embrapa diretamente como fonte de conhecimento, sem necessidade de curadoria manual extensa.
        *   Aproveita o poder de LLMs pré-treinados para gerar respostas coesas e naturais.
        *   Mais rápido de implementar um protótipo funcional com ferramentas modernas (LlamaIndex, LangChain).
        *   Alinhado com as restrições de tempo e recursos.

### Fase 2: Escolha da Pilha Tecnológica e Ambiente Local

*   **Ferramentas RAG:** Avaliamos `LangChain` e `LlamaIndex`. Optamos por **`LlamaIndex`** pela sua abstração focada em RAG e facilidade percebida para conectar fontes de dados, embeddings e LLMs.
*   **Execução do LLM:** Dada a restrição de custo (evitar APIs pagas sempre que possível) e o desejo de explorar tecnologias open source, decidimos rodar o LLM localmente.
    *   **Ferramenta:** Escolhemos **`Ollama`** pela facilidade de instalação e gerenciamento de diversos LLMs open source no Windows.
    *   `[INSERIR IMAGEM: Captura de tela do Ollama rodando no terminal ou da lista de modelos baixados (ollama list). Placeholder: "Ollama rodando com modelo X baixado"]`
*   **Modelo LLM Inicial:** Começamos considerando modelos menores para garantir a execução em hardware limitado.
*   **Modelo de Embedding Inicial:** A qualidade da recuperação (achar a parte certa do PDF) é crucial no RAG. Precisávamos de um modelo de embedding.
*   **API vs. Script:** Inicialmente, desenvolvemos a lógica RAG como um script Python (`chatbot_rag.py`) para testes rápidos e iteração no terminal.

### Fase 3: Iteração nos Modelos de Embedding (Desafio Multilíngue)

*   **Primeira Tentativa (Embedding):** Seguindo sugestões e benchmarks de retrieval, testamos inicialmente o `Snowflake/snowflake-arctic-embed-m`.
    *   **Observação:** Embora funcional, a qualidade da recuperação para perguntas em português sobre o PDF da Embrapa (também em português) não foi ideal. Respostas frequentemente indicavam que a informação não estava no contexto, mesmo quando estava.
    *   **Hipótese:** O modelo Arctic Embed, apesar de ter alguma capacidade multilíngue, é primariamente otimizado para inglês, não capturando bem as nuances semânticas do português brasileiro para a tarefa de retrieval.
*   **Segunda Tentativa (Embedding):** Pesquisamos modelos de embedding explicitamente **multilíngues** e bem avaliados em benchmarks de retrieval.
    *   **Modelo Escolhido:** **`intfloat/multilingual-e5-large`**. É um modelo maior, mas reconhecido pelo bom desempenho multilíngue.
    *   **Ação:** Modificamos o script para usar `HuggingFaceEmbedding` com este modelo. **Crucial:** Apagamos o índice antigo e o recriamos do zero, pois os embeddings são específicos do modelo.
    *   `[INSERIR IMAGEM: Trecho de código mostrando a configuração do Settings.embed_model com 'intfloat/multilingual-e5-large'. Placeholder: "Configuração do embedding E5-Large no LlamaIndex"]`
    *   **Resultado:** **Melhora significativa!** A recuperação dos trechos relevantes do PDF melhorou consideravelmente, levando a respostas mais precisas e contextuais do LLM.

### Fase 4: Escolha e Teste do LLM Local

*   **Modelo LLM:** Precisávamos de um LLM que rodasse localmente via Ollama, tivesse bom desempenho em português e fosse capaz de seguir instruções (para usar o contexto recuperado).
    *   **Modelo Escolhido:** **`llama3.1:8b`**. A versão 3.1 do Llama é recente, tem bom suporte multilíngue e a versão 8B é um bom compromisso entre capacidade e requisitos de hardware para rodar localmente (especialmente com quantização via Ollama).
    *   **Observação:** Usamos a versão quantizada padrão fornecida pelo Ollama para otimizar o uso de RAM/VRAM.
*   **Prompt Engineering:** A forma como instruímos o LLM a usar o contexto é vital no RAG. Iteramos no template de prompt (`qa_prompt_tmpl`) passado para o `query_engine` do LlamaIndex.
    *   **Objetivos do Prompt:**
        *   Definir o papel do chatbot (especialista em cultivo de cogumelos).
        *   Instruir a usar **APENAS** o contexto do PDF quando a pergunta for relevante.
        *   Permitir resposta com conhecimento geral **SE** a pergunta for sobre cogumelos mas a info não estiver no PDF (decisão de design para ser mais útil, mas com cuidado para não alucinar).
        *   Instruir a recusar educadamente perguntas fora do tópico.
        *   Definir o tom (formal, amigável, detalhado).
    *   `[INSERIR IMAGEM: O template de prompt (qa_prompt_tmpl_str) usado no código. Placeholder: "Template de Prompt para o LLM Llama 3.1"]`
*   **Resultado:** A combinação `intfloat/multilingual-e5-large` (embedding) + `llama3.1:8b` (LLM via Ollama) + Prompt Refinado entregou resultados satisfatórios nos testes locais via script.

### Fase 5: Transformando o Script em uma API (Flask)

*   **Necessidade:** Para que a aplicação Django pudesse interagir com o chatbot, a lógica RAG precisava ser exposta como um serviço web (API).
*   **Framework Escolhido:** **`Flask`**. Optamos pelo Flask por ser um microframework Python leve, fácil de aprender e rápido para criar uma API REST simples, ideal para o escopo do TCC.
*   **Estrutura da API (`chatbot_rag.py`):**
    *   Inicialização única: Os modelos (embedding e LLM) e o índice LlamaIndex são carregados **uma única vez** quando a API Flask inicia, para evitar recarregamentos a cada requisição (otimização de performance e recursos).
    *   Endpoint `/ask`: Uma rota foi criada para receber perguntas via método POST, com o corpo da requisição contendo um JSON `{"question": "sua pergunta"}`.
    *   Processamento: O endpoint extrai a pergunta, chama o `query_engine.query()` configurado na inicialização.
    *   Resposta: Retorna a resposta do chatbot em formato JSON `{"answer": "resposta do chatbot"}`.
    *   Tratamento de Erros: Adicionados blocos try/except e retornos de erro HTTP (400, 500, 503) para lidar com requisições inválidas ou falhas internas.
    *   `[INSERIR IMAGEM: Trecho de código mostrando a definição da rota @app.route('/ask') no Flask. Placeholder: "Endpoint /ask na API Flask"]`
*   **Teste:** A API foi testada localmente usando o Postman, enviando requisições POST para `http://127.0.0.1:5001/ask` e verificando as respostas JSON.
    *   `[INSERIR IMAGEM: Captura de tela do Postman mostrando um teste bem-sucedido da API local. Placeholder: "Teste da API com Postman"]`

### Fase 6: Considerações sobre Exposição e Segurança

*   **Dilema:** A API local funciona, mas como permitir que a aplicação Django (e potencialmente avaliadores) a acesse sem comprometer a segurança da máquina de desenvolvimento?
*   **Opção 1: Exposição Direta (Descartada):** Abrir portas no roteador (port forwarding) para expor a API diretamente na internet foi considerado **muito arriscado** por questões de segurança.
*   **Opção 2: Tunelamento (Ngrok/Cloudflare Tunnel):** Permite criar uma URL pública temporária que redireciona para a API local de forma mais segura que a exposição direta.
    *   **Vantagem:** Permite demonstração remota temporária.
    *   **Desvantagem:** Depende da máquina local estar online; URL pode mudar (tier gratuito).
*   **Opção 3: Deploy em Nuvem:** Hospedar a API Flask em serviços como PythonAnywhere, Render, etc.
    *   **Vantagem:** API sempre online, mais profissional.
    *   **Desvantagem:** Tiers gratuitos provavelmente **não suportam** rodar Ollama + LLMs pesados. Exigiria **reverter para APIs pagas (OpenAI, etc.)**, aumentando custo e perdendo o aspecto "local" do processamento.
*   **Decisão Atual:** Para a fase de desenvolvimento e demonstração inicial/defesa do TCC, optou-se por **manter a execução local** (Opção 1 da Fase 2) e, se estritamente necessário para avaliação remota, usar **Tunelamento Temporário** (Opção 2) com Ngrok, ativando-o apenas durante a demonstração. A segurança da máquina local é prioritária.

---

## 3. Status Atual

*   Pipeline RAG implementado localmente usando LlamaIndex.
*   Base de conhecimento: PDF da Embrapa sobre produção de cogumelos.
*   Modelo de Embedding: `intfloat/multilingual-e5-large` (via HuggingFace).
*   Modelo LLM: `llama3.1:8b` (via Ollama).
*   API REST simples criada com Flask, rodando localmente na porta 5001 e acessível na rede local (via IP e regra de firewall).
*   API testada com sucesso via Postman.
*   O chatbot demonstra capacidade de responder perguntas técnicas sobre o cultivo de cogumelos com base no documento fornecido.

---

## 4. Desafios e Aprendizados

*   **Seleção de Modelo de Embedding:** A performance de modelos otimizados para inglês (como Arctic Embed) pode ser subótima para documentos em outras línguas como o português. Modelos multilíngues (E5-Large) mostraram-se cruciais para a qualidade da recuperação.
*   **Recursos Computacionais Locais:** Rodar LLMs e modelos de embedding localmente exige RAM e, idealmente, uma GPU. Modelos quantizados (via Ollama) são essenciais para viabilizar a execução em hardware não especializado, mas a performance (velocidade) pode ser um gargalo.
*   **Prompt Engineering:** A qualidade da resposta final depende fortemente de como o LLM é instruído a usar o contexto recuperado. Prompts claros e específicos são necessários para evitar respostas genéricas ou fora do contexto.
*   **Segurança vs. Acessibilidade:** Expor um serviço rodando localmente requer cuidado. Ferramentas de tunelamento são uma alternativa mais segura que a exposição direta para demonstrações temporárias.
*   **Complexidade do RAG:** Embora mais simples que treinar/fine-tuning, RAG ainda envolve múltiplas etapas (chunking, embedding, retrieval, generation) que precisam ser configuradas e otimizadas.

---

## 5. Próximos Passos

*   **Integração com Django:** Desenvolver a interface do chatbot no frontend Django e conectar as requisições do usuário à API Flask (`http://<IP_DA_API_FLASK>:5001/ask`).
*   **Testes de Usabilidade:** Realizar testes com potenciais usuários (simulando a equipe técnica) para avaliar a qualidade das respostas e a fluidez da interação.
*   **Refinamento do Prompt:** Ajustar o prompt do LLM com base no feedback dos testes.
*   **Otimização (Opcional):** Explorar diferentes estratégias de chunking ou o parâmetro `similarity_top_k` se a qualidade da recuperação ainda precisar de ajustes.
*   **Documentação Final:** Finalizar a documentação do projeto para o TCC.
*   **Preparação da Demonstração:** Definir a estratégia de demonstração (local ou via tunelamento).

---

## 6. Como Rodar Localmente (Instruções)

1.  **Clonar o Repositório:**
    ```bash
    git clone [https://github.com/CodeVanzi/Chatbot-TCC-Univesp]
    cd [Chatbot-TCC-Univesp]
    ```
2.  **Configurar Ambiente Virtual:**
    ```bash
    python -m venv venv
    # Linux/macOS:
    source venv/bin/activate
    # Windows:
    .\venv\Scripts\activate
    ```
3.  **Instalar Dependências:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Instalar e Configurar Ollama:**
    *   Siga as instruções em [https://ollama.com/](https://ollama.com/).
    *   Baixe o modelo LLM necessário: `ollama pull llama3.2:3b` (ou o configurado em `chatbot_rag.py`).
    *   Garanta que o serviço Ollama esteja rodando.
5.  **Preparar Dados e Índice:**
    *   Crie a pasta `data` e coloque o PDF da Embrapa dentro dela.
    *   Execute o script de indexação (se for separado) ou execute a API Flask pela primeira vez (se ela criar o índice). Isso irá baixar o modelo de embedding e processar o PDF, salvando na pasta `storage`. **Este passo pode demorar bastante.**
6.  **Configurar Firewall (se acessando de outra máquina na rede):**
     Permitindo Acesso pela Rede (Configuração do Firewall do Windows)
    Por padrão, o Firewall do Windows provavelmente bloqueará conexões vindas de outros dispositivos da sua rede para a porta 5001 no seu computador. Precisamos criar uma regra para permitir isso:
    Abrir o Firewall do Windows com Segurança Avançada:
    Pressione a tecla Windows, digite "Firewall" e selecione "Windows Defender Firewall com Segurança Avançada". (Pode pedir permissão de administrador).
    Criar Nova Regra de Entrada:
    No painel esquerdo, clique em "Regras de Entrada".
    No painel direito (Ações), clique em "Nova Regra...".
    Assistente de Nova Regra:
    Tipo de Regra: Selecione "Porta" e clique em "Avançar".
    Protocolo e Portas:
    Selecione "TCP".
    Selecione "Portas locais específicas:" e digite 5001 (a porta que sua API Flask está usando). Clique em "Avançar".
    Ação: Selecione "Permitir a conexão" e clique em "Avançar".
    Perfil: Aqui você decide onde a regra se aplica. Para testes em casa/escritório seguro:
    Marque "Particular" (Redes domésticas ou de trabalho).
    Desmarque "Público" (Redes não seguras como Wi-Fi de aeroporto/café) a menos que você saiba o que está fazendo e precise testar em uma rede pública (não recomendado para desenvolvimento).
    Marque "Domínio" se seu computador estiver em um domínio de rede corporativo e você precisar de acesso a partir dele.
    Clique em "Avançar".
    Nome: Dê um nome descritivo para a regra, por exemplo, API Chatbot Flask (Porta 5001) ou Permitir Acesso Chatbot Cogumelos. Clique em "Concluir".
7.  **Rodar a API Flask:**
    ```bash
    python chatbot_rag.py
    ```
    *   Mantenha este terminal aberto.
8.  **Testar/Usar:**
    *   A API estará acessível em `http://127.0.0.1:5001/ask` (da mesma máquina) ou `http://<IP_DA_MAQUINA>:5001/ask` (de outras máquinas na rede).
    *   Use Postman, curl, ou a aplicação Django para enviar requisições POST com `{"question": "Sua pergunta aqui"}`.

---

*Este diário será atualizado conforme o projeto evolui.*
# Projeto Integrador TCC - Sistema de Apoio à Decisão para Produtores de Cogumelos

**Autores:** 
CAIO VINÍCIUS CONSTANTE DA SILVA, 
FABIO HIDEO HATAE, 
GABRIELLA FERREIRA, 
GRACIEL COVANZI DE SOUSA, 
RICHARD HATANAKA, 
RODRIGO TROSKAITIS SANTOS, 
ROGERIO NASCIMENTO CAVALIERI, 
VALDEMIR DAMAS DA SILVA, 

**Orientadora:** Profª Carla Dominique Silva Vasconcelos
**Instituição:** Universidade Virtual do Estado de São Paulo (UNIVESP)
**Cursos:** Ciência de Dados / Engenharia da Computação
**Ano:** 2025

## 1. Introdução e Motivação

Este repositório documenta o desenvolvimento de componentes chave como parte do Trabalho de Conclusão de Curso (TCC). O projeto geral visa criar um **Sistema de Apoio à Decisão para Produtores de Cogumelos**, focado nas necessidades da Fazenda Nova Esperança, conforme detalhado no Relatório Inicial do TCC.

A Fazenda enfrenta desafios específicos:
*   **Sr. Eric (Proprietário):** Dificuldade em analisar a rentabilidade de diferentes espécies de cogumelos devido à falta de tempo e dados estruturados.
*   **Sr. Victor e Equipe Técnica:** Necessidade de suporte técnico rápido e confiável sobre práticas de cultivo, manejo e solução de problemas operacionais.

Este projeto foca em dois componentes principais para atender a essas necessidades:
1.  Um **Chatbot Especializado** para auxiliar a equipe técnica do Sr. Victor.
2.  Um **Dashboard de Análise de Mercado** para fornecer insights ao Sr. Eric.

**Objetivo do Chatbot:** Fornecer respostas precisas e contextuais sobre o cultivo de cogumelos, utilizando como base de conhecimento principal o documento técnico da Embrapa: *"Produção de Cogumelos por Meio de Tecnologia Chinesa Modificada"*.

**Objetivo do Dashboard:** Apresentar uma análise visual de preços de mercado para diferentes espécies de cogumelos medicinais e suas apresentações, auxiliando na tomada de decisão sobre quais espécies cultivar.

**Restrições do Projeto:**
*   Curto prazo de execução (TCC).
*   Recursos limitados (computacionais e financeiros).
*   Necessidade de uma solução funcional e demonstrável.

---

## 2. Diário de Bordo do Desenvolvimento

Esta seção narra a jornada de desenvolvimento, as decisões tomadas e as evoluções dos componentes.

### Fase 1: Pesquisa Inicial e Definição da Abordagem para o Chatbot (RAG)

*   **Desafio:** Como criar um chatbot que responda perguntas técnicas específicas sobre cultivo de cogumelos, baseado em um documento PDF extenso, dentro das restrições do projeto?
*   **Opções Consideradas (Chatbot):**
    *   Sistemas Baseados em Regras/Intenções: Inviável pelo tempo e complexidade.
    *   Fine-tuning de LLMs: Inviável pelos recursos limitados.
    *   **Retrieval-Augmented Generation (RAG):** Escolhido por permitir uso direto do PDF, aproveitar LLMs pré-treinados e ser mais rápido para prototipagem.
*   **Decisão:** Adotar a abordagem RAG para o Chatbot.

### Fase 2: Escolha da Pilha Tecnológica Inicial (Foco Local)

*   **Ferramentas RAG (Chatbot):** `LlamaIndex` escolhido pela sua abstração focada em RAG.
*   **Execução do LLM (Chatbot):** Inicialmente, optou-se por rodar o LLM localmente via `Ollama` para controle de custos e exploração de tecnologias open source.
*   **Backend da API do Chatbot:** Um script Python foi desenvolvido para a lógica RAG, evoluindo para uma API `Flask` para permitir a comunicação com outros serviços.

### Fase 3: Iteração em Modelos de Embedding e LLM (Chatbot)

*   **Embedding:**
    *   Testes iniciais com `Snowflake/snowflake-arctic-embed-m` mostraram limitações para o português.
    *   Mudança para **`intfloat/multilingual-e5-large`** resultou em melhora significativa na recuperação de informações do PDF em português.
*   **LLM Local:**
    *   Utilização do modelo **`llama3.2:3b`** (uma variante do Llama 3) via Ollama, buscando um equilíbrio entre capacidade e recursos locais.
*   **Prompt Engineering:** Iterações no template de prompt para guiar o LLM a fornecer respostas contextuais e úteis.


### Fase 4: Desenvolvimento da API do Chatbot e Transição para API Externa (LLM)

*   **API Flask:** A lógica RAG foi encapsulada em uma API Flask para ser consumida pela aplicação Django.
    *   Endpoint `/ask` para receber perguntas e retornar respostas JSON.
    *   Testes com Postman validaram o funcionamento.
    
*   **Considerações de Performance e Custo:** Para aliviar a carga no hardware local e visando uma futura hospedagem, decidiu-se migrar a parte do LLM para uma API externa.
    *   **LLM via API Externa:** A API Flask foi adaptada para usar a **API do Gemini (Google)**, especificamente o modelo `gemini-2.0-flash`, para a geração de respostas. O embedding continua sendo feito localmente com `intfloat/multilingual-e5-large` para manter essa parte sem custo de API.
    *   **Gerenciamento de Chaves:** Implementado o uso de arquivos `.env` e `python-dotenv` para gerenciar a `GEMINI_API_KEY` de forma segura.

### Fase 5: Segurança da API e Exposição para Desenvolvimento

*   **Proteção da API Flask:** Adicionada uma camada básica de segurança com uma chave secreta compartilhada (`CHATBOT_API_SHARED_SECRET`) via header `X-API-Key` para proteger o endpoint quando exposto.
*   **Exposição Temporária com Ngrok:** Para permitir que a aplicação Django (rodando localmente ou em outro ambiente de desenvolvimento) consuma a API Flask (rodando localmente), utilizou-se `Ngrok` para criar um túnel seguro e uma URL pública temporária.


### Fase 6: Integração do Chatbot na Aplicação Django https://github.com/CodeVanzi/Django-Marketplace-Sitio

*   **Nova App Django (`chatbot_app`):** Criada uma app dedicada no projeto Django para toda a lógica da interface do chatbot.
*   **URLs e Views:** Definidas URLs e views na `chatbot_app` para:
    *   Renderizar a página da interface do chat (`chat_interface.html`).
    *   Uma API interna do Django (`send_message_api`) que recebe a mensagem do usuário via AJAX, chama a API Flask (exposta pelo Ngrok ou localmente) e retorna a resposta para o frontend.
*   **Template da Interface do Chat:**
    *   Desenvolvido `db_cogumelos.html` com Tailwind CSS para a interface de chat.
    *   Implementado JavaScript para enviar a mensagem do usuário para a view Django via `fetch`, exibir a mensagem do usuário e a resposta do bot na interface, e lidar com o estado de carregamento e erros.
    *   Estilização das bolhas de chat para diferenciar usuário e bot, e para correta formatação de quebras de linha (`white-space: pre-wrap;`).
    *   Ajustes de cores para melhor legibilidade e adaptação aos temas claro/escuro.
*   **Acesso Condicional no Navbar:** Adicionado um link para a página do "Assistente Virtual" no navbar principal do Django, visível apenas para usuários `staff` ou `superuser`.

### Fase 7: Desenvolvimento do Dashboard de Análise de Mercado

*   **Objetivo:** Criar uma visualização de dados para o Sr. Eric, baseada na pesquisa de mercado de cogumelos medicinais.
*   **Tecnologia:** Utilização de **Django** para a estrutura e **Bokeh** para a geração dos gráficos.
*   **Estrutura do Dashboard:**
    *   Layout com sidebar para filtros (por espécie de cogumelo) e área de conteúdo principal para gráficos e tabelas.
    *   Proporção da sidebar de 1/5 e conteúdo de 4/5 em telas maiores.
*   **Dados:** Os dados da pesquisa de mercado (preço médio, desvio padrão, etc., para Cordyceps, Reishi, Agaricus e Juba de Leão em diferentes apresentações) foram "hardcoded" na view Django para esta fase do TCC, baseado em gráficos elaborados pela equipe de ETL do projeto.
*   **Gráficos e Tabelas:**
    *   A view Django gera 6 gráficos Bokeh comparativos quando "Todas as Espécies" é selecionado.
    *   A view gera 6 gráficos Bokeh individuais quando uma espécie específica é selecionada na sidebar.
    *   Tabelas de resumo de preços são geradas em HTML diretamente no template.
*   **Interatividade com HTMX:**
    *   A sidebar permite selecionar uma espécie.
    *   Ao clicar em uma espécie, o HTMX faz uma requisição para a mesma view Django, que então renderiza um template parcial contendo apenas os gráficos e tabelas da espécie selecionada (ou os comparativos).
    *   Este template parcial é então inserido na área de conteúdo principal, atualizando a visualização sem recarregar a página inteira.
*   **Estilização e Tema:** O dashboard e os gráficos Bokeh foram estilizados para serem responsivos e se adaptarem aos temas claro/escuro da aplicação.

---

## 3. Status Atual

*   **Chatbot:**
    *   API Flask funcional usando RAG com LlamaIndex, embedding local (`intfloat/multilingual-e5-large`) e LLM via API Gemini (`gemini-2.0-flash`).
    *   API Flask protegida por chave secreta e exposta temporariamente via Ngrok.
    *   Interface do chatbot integrada à aplicação Django (`chatbot_app`), permitindo interação do usuário e exibição de respostas formatadas.
    *   Acesso à interface do chatbot restrito a administradores no navbar.
*   **Dashboard de Análise de Mercado:**
    *   Implementado em Django com visualizações Bokeh.
    *   Apresenta gráficos de preço médio e desvio padrão para 4 espécies de cogumelos em 3 apresentações.
    *   Inclui tabelas de resumo.
    *   Sidebar com filtros por espécie, utilizando HTMX para atualização dinâmica da área de conteúdo.
    *   Estilizado com Tailwind CSS e adaptado para temas claro/escuro.

---

## 4. Desafios e Aprendizados

*   **Seleção de Modelos (Chatbot):** A importância de modelos multilíngues para conteúdo em português foi um aprendizado chave.
*   **Recursos Computacionais:** Rodar LLMs localmente apresentou desafios de performance, motivando a transição para a API do Gemini para o LLM.
*   **Prompt Engineering (Chatbot):** Essencial para guiar o LLM e obter respostas relevantes.
*   **Segurança e Exposição de APIs:** A necessidade de proteger APIs e as diferentes abordagens (chave secreta, Ngrok) foram exploradas.
*   **Integração Frontend-Backend (Chatbot):** Uso de AJAX/Fetch para criar uma interface de chat dinâmica no Django.
*   **Visualização de Dados (Dashboard):** Geração de gráficos com Bokeh e integração com Django. A reatividade de gráficos Bokeh a temas CSS dinâmicos requer atenção.
*   **HTMX (Dashboard):** Utilizado para criar uma experiência de usuário mais fluida no dashboard, atualizando apenas partes da página.
*   **Gerenciamento de Estado de UI (Dashboard):** Manter o estado ativo do filtro na sidebar após atualizações HTMX.

---

## 5. Próximos Passos

*   **Chatbot - Hospedagem no Railway (API Flask):**
    *   Adaptar a API Flask do chatbot (que usa Gemini e embedding local) para ser completamente baseada em APIs (LLM Gemini e, potencialmente, Embedding Gemini).
    *   Configurar o deploy da API Flask no Railway.
    *   Atualizar a aplicação Django para consumir a API Flask hospedada no Railway.
*   **Dashboard - Refinamentos:**
    *   Melhorar a interatividade dos gráficos Bokeh (se possível, sem recarga total para mudanças de tema).
    *   Adicionar mais opções de filtro se relevante (ex: período).
*   **Geral:**
    *   Testes de usabilidade abrangentes para ambos os componentes.
    *   Refinamento final da documentação e preparação da apresentação do TCC.
    *   Coleta de feedback da equipe da Fazenda Nova Esperança.

---

## 6. Como Rodar (Configuração Atual com API Flask Local + Ngrok)

0. (para processamento de Linguagem Natural (LLM) local com Ollama):

*   **Instalar Ollama:**
    *   Acesse [ollama.com](https://ollama.com/) e baixe o instalador para seu sistema operacional (Windows, macOS, Linux).
    *   Execute o instalador. O Ollama geralmente roda como um serviço em segundo plano.
*   **Baixar o Modelo LLM:**
    *   Abra seu terminal ou prompt de comando.
    *   Execute o comando para baixar o modelo configurado para uso local na API Flask (ex: `llama3.2:3b`):
        ```bash
        ollama pull llama3.2:3b
        ```
    *   Aguarde o download. O serviço Ollama deve estar em execução quando a API Flask for iniciada.

1  **Clonar o Repositório Django:**
    ```bash
    git clone [https://github.com/CodeVanzi/Django-Marketplace-Sitio]
    cd [caminho-do-repositorio]
    ```
2.  **Configurar Ambiente Virtual e Instalar Dependências (Django):**
    ```bash
    python -m venv venv
    # Ativar venv
    pip install -r requirements.txt 
    ```
3.  **Configurar Arquivo `.env` (Django):** Crie um arquivo `.env` na raiz do projeto Django com:
    ```env
    ENVIRONMENT=development
    SECRET_KEY=(gerar uma chave secreta)
    ENCRYPT_KEY=(gerar uma chave de criptografia)
    STRIPE_API_KEY_PUBLISHABLE= (para pagamentos)
    STRIPE_API_KEY_HIDDEN= (para pagamentos)
    DATABASE_URL=(para banco de dados)
    CLOUD_NAME=(para upload de imagens)
    CLOUD_API_KEY=(para upload de imagens)
    CLOUD_API_SECRET=(para upload de imagens)
    EMAIL_HOST=(ex: smtp.gmail.com)
    EMAIL_HOST_ADDRESS=(ex: seuemail@gmail.com)
    EMAIL_HOST_PASSWORD=(ex: sua_senha_app_google)
    CHATBOT_API_URL=(ex: http://localhost:5000/ask)
    CHATBOT_API_SHARED_SECRET=(mesma chave definida no .env da API Flask)

    ```
4.  **Rodar Migrations Django:** `python manage.py migrate`


5.  **Clonar/Configurar Repositório da API Flask (Chatbot):**
    ```bash
    git clone https://github.com/CodeVanzi/Chatbot-TCC-Univesp
    cd [caminho-do-repositório-da-api-flask]
    # Configurar venv e instalar requirements.txt da API Flask

    python -m venv venv 
    # Ativar venv
    pip install -r requirements.txt 

    ```
6.  **Configurar Arquivo `.env` (API Flask):** Na raiz do projeto da API Flask:
    ```env
    GEMINI_API_KEY="SUA_CHAVE_API_GEMINI"
    CHATBOT_API_SHARED_SECRET="DEFINI_UMA_CHAVE_SECRETA_A_SER_INFORMADA_NO_DJANGO"
    ```
7.  **Rodar a API Flask:**
    ```bash
    # No terminal da API Flask, com venv ativo
    python geminichatbot.py (para rodar a API Flask usando a chave do gemini e embbeding localmente)
    python localchatbot.py (para rodar a API Flask usando a ollama localmente e embbeding localmente)
    ```
    (Ela deve rodar na porta 5001)
    (o arquivo geminichatbot_railway.py é o que seria utilizado para fazer tanto o embbeding quanto o LLM do gemini na nuvem, usando API externa, por isso o requirements é diferente, mas não está sendo utilizado no momento)

8.  **Rodar Ngrok para a API Flask:**
    ```bash
    # Em outro terminal
    ngrok http 5001 
    ```
    Copie a URL HTTPS fornecida e atualize `CHATBOT_API_URL` no `.env` do Django.
9.  **Rodar o Servidor Django:**
    ```bash
    # No terminal do projeto Django, com venv ativo
    python manage.py runserver
    ```
10. **Acessar:**
    *   Aplicação Django: `http://127.0.0.1:8000/`
    *   PARA AVALIADORES DO TCC: https://sitionovaesperanca.up.railway.app/ * 
    *   Chatbot (se staff/admin): `http://127.0.0.1:8000/assistente-virtual/`
    *   Dashboard de Cogumelos (se staff/admin): `http://127.0.0.1:8000/caminho/para/seu/dashboard_cogumelos/`

---


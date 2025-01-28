Aqui está o `README.md` completo com as atualizações incluindo o uso do modelo **deepseek-r1:8b** no Ollama server:

---

# repo-insight-bot

**repo-insight-bot** é uma aplicação que utiliza inteligência artificial para gerar insights sobre repositórios do GitHub. Ele processa dados de repositórios, gera embeddings utilizando Sentence Transformers, armazena os dados no QdrantDB, e permite consultas interativas para responder perguntas sobre o repositório.

---

## **Recursos**

- **Análise de Repositórios GitHub**: Processa dados do repositório e extrai informações relevantes.
- **Geração de Embeddings**: Utiliza Sentence Transformers para criar embeddings semânticos de texto.
- **Armazenamento Vetorial**: Armazena embeddings no QdrantDB para consultas eficientes.
- **Integração com Ollama**: Suporte opcional para modelos generativos locais, como **LLaMA** ou **deepseek-r1:8b**.

---

## **Configuração do Projeto**

### **Dependências**

Certifique-se de ter as seguintes ferramentas instaladas:

- **Docker**
- **Docker Compose**
- **Python** (versão 3.10.12)
- **Poetry** (para gerenciar dependências Python)

### **Instalação**

1. Clone o repositório:
   ```bash
   git clone https://github.com/GoLogann/repo-insight-bot.git
   cd repo-insight-bot
   ```

2. Instale as dependências do projeto usando o Poetry:
   ```bash
   poetry install
   ```

3. Configure os contêineres Docker:
   ```bash
   sudo docker compose -f docker-compose.yml -p repo-insight-bot up -d
   ```

   Esse comando iniciará os serviços:
   - **Qdrant**: Banco de dados vetorial para armazenar embeddings.
   - **Ollama** (opcional): Para usar modelos locais como LLaMA ou **deepseek-r1:8b**.

4. **Configuração do Modelo deepseek-r1:8b no Ollama**:
   Para utilizar o modelo **deepseek-r1:8b** no Ollama, execute o seguinte comando no terminal do contêiner do Ollama:
   ```bash
   docker exec -it <nome_do_container_ollama> ollama run deepseek-r1:8b
   ```
   Substitua `<nome_do_container_ollama>` pelo nome do contêiner do Ollama em execução.

---

## **Como Usar**

### **1. Endpoint para perguntas**

O endpoint principal é:

```http
POST /repo-insight-bot/ask
```

**Request Body:**

```json
{
  "repo_url": "https://github.com/GoLogann/phishing-quest-api",
  "question": "Qual é o objetivo deste repositório?"
}
```

**Exemplo de Resposta:**

```json
{
  "response": "O repositório é uma API para um game estilo quizz"
}
```

---

### **Notas Adicionais**

- O modelo **deepseek-r1:8b** é uma opção poderosa para gerar respostas contextualizadas e pode ser integrado ao Ollama para uso local.
- Certifique-se de que o contêiner do Ollama esteja em execução antes de configurar o modelo.

---

Se precisar de mais ajustes ou tiver dúvidas, é só avisar! 😊
# Projeto Banco Digital API (Nome do Seu Projeto)

![Badge de Linguagem](https://img.shields.io/badge/Python-3.11-blue.svg)
![Badge de Framework](https://img.shields.io/badge/Django-5.2-green.svg)
![Badge de DRF](https://img.shields.io/badge/DRF-3.15-red.svg)
Uma API RESTful desenvolvida em Django e Django REST Framework para simular as operações básicas de um sistema bancário, incluindo gerenciamento de contas, transações com despósito, saque e transferência.

## Funcionalidades Principais

* Criação de Clientes (usuários)
* Autenticação de Clientes (geração de Token)
* Criação automática de Conta Bancária ao registrar Cliente
* Operações de Depósito
* Operações de Saque 
* Transferência de valores entre Contas
* Consulta de Saldo
* Consulta de Extrato de Transações

## Tecnologias Utilizadas (Tech Stack)

* **Backend:**
    * Python 3.11+
    * Django 5.2+
    * Django REST Framework (DRF)
    * SQLite (para desenvolvimento - pode ser substituído por PostgreSQL para produção)
    * Autenticação por Token (DRF `authtoken`)
* **Testes:**
    * Pytest
    * pytest-django
    * Postman (para testes manuais/exploratórios da API)

## Pré-requisitos

* Python 3.11 ou superior
* Pip (gerenciador de pacotes Python)
* Git

## Como Configurar e Rodar o Projeto Localmente

1. **Clone o repositório:**
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO_GITHUB]
    cd nome-do-seu-projeto
    ```

2. **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # No Windows
    venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente (se aplicável):**
    * Se você estiver usando um arquivo `.env` (com `python-decouple`, por exemplo), crie-o na raiz do projeto e adicione as variáveis necessárias (ex: `SECRET_KEY`, `DEBUG`).
    * Exemplo de `.env`:
        ```
        SECRET_KEY=sua_secret_key_aqui
        DEBUG=True
        ```

5.  **Aplique as migrações do banco de dados:**
    ```bash
    python manage.py migrate
    ```

6.  **Crie um superusuário (opcional, para acesso ao Django Admin):**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Rode o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```
    A API estará acessível em `http://127.0.0.1:8000/api/`.

## Estrutura do Projeto (Simplificada)

```text
projeto-banco/
├── banco_project/     # Configurações principais do projeto Django
│   ├── settings.py
│   └── urls.py        # URLs globais
├── contas/            # App principal da API bancária
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py        # URLs específicas do app 'contas'
│   ├── services/      # Lógica de negócios
│   └── tests/         # Testes automatizados (Pytest)
│       ├── test_services.py
│       └── test_views.py
├── manage.py          # Utilitário de linha de comando do Django
├── pytest.ini         # Configuração do Pytest
├── requirements.txt   # Dependências do Python
└── README.md          # Este arquivo
```

## Endpoints da API

Aqui estão os principais endpoints disponíveis.

**Autenticação e Registro**

* **`POST /api/registrar/`**
    * Registra um novo cliente e cria sua conta bancária.
    * **Corpo da Requisição (Exemplo):**
        ```json
        {
          "cpf": "12345678901",
          "nome": "Nome Completo",
          "email": "usuario@example.com",
          "data_nascimento": "YYYY-MM-DD",
          "password": "suasenhaforte"
        }
        ```
    * **Resposta de Sucesso (201 CREATED):**
        ```json
        {
          "mensagem": "Cliente criado com sucesso!",
          "cliente": {
            "id": 1,
            "cpf": "12345678901",
            "nome": "Nome Completo",
            "email": "usuario@example.com",
            "data_nascimento": "YYYY-MM-DD",
            "date_joined": "..."
          },
          "numero_conta": "NUMERO_DA_CONTA",
          "token": "SEU_TOKEN_DE_AUTENTICACAO"
        }
        ```

* **`POST /api/login/`**
    * Autentica um cliente existente e retorna um token.
    * **Corpo da Requisição (Exemplo):**
        ```json
        {
          "cpf": "12345678901",
          "senha": "suasenhaforte"
        }
        ```
    * **Resposta de Sucesso (200 OK):**
        ```json
        {
          "mensagem": "Autenticado com sucesso!",
          "token": "SEU_TOKEN_DE_AUTENTICACAO",
          "usuario": { /* ... dados do usuário ... */ }
        }
        ```

**Operações de Conta (Requer Autenticação - Header: `Authorization: Token SEU_TOKEN`)**

* **`POST /api/deposito/`**
    * Realiza um depósito na conta do usuário autenticado (ou na conta especificada, se sua lógica permitir).
    * **Corpo da Requisição (Exemplo):**
        ```json
        {
          "numero_conta": "NUMERO_DA_CONTA_DO_USUARIO_LOGADO",
          "valor": "100.50"
        }
        ```
    * **Resposta de Sucesso (200 OK):**
        ```json
        {
          "mensagem": "Depósito de R$100.50 realizado com sucesso.",
          "conta": { /* ... dados atualizados da conta ... */ }
        }
        ```

* **`POST /api/saque/`**
    * Realiza um saque da conta do usuário autenticado.
    * **Corpo da Requisição (Exemplo):**
        ```json
        {
          "numero_conta": "NUMERO_DA_CONTA_DO_USUARIO_LOGADO",
          "valor": "50.00"
        }
        ```
    * **Resposta de Sucesso (200 OK):** (Similar ao depósito)

* **`POST /api/transferencia/`**
    * Realiza uma transferência da conta do usuário autenticado para outra conta.
    * **Corpo da Requisição (Exemplo):**
        ```json
        {
          "conta_origem": "NUMERO_DA_CONTA_DO_USUARIO_LOGADO",
          "conta_destino": "NUMERO_DA_CONTA_DESTINO",
          "valor": "25.00"
        }
        ```
    * **Resposta de Sucesso (200 OK):** (Mensagem de sucesso)

**Consultas (Requer Autenticação)**

* **`GET /api/saldo/`**
    * Retorna o saldo da conta do usuário autenticado.
    * **Resposta de Sucesso (200 OK):**
        ```json
        {
          "numero_conta": "NUMERO_DA_CONTA",
          "saldo": "VALOR_DO_SALDO.DD"
        }
        ```

* **`GET /api/extrato/`**
    * Retorna o extrato de transações da conta do usuário autenticado.
    * **Resposta de Sucesso (200 OK):**
        ```json
        {
          "conta": {
            "numero_conta": "...",
            "saldo_atual": "..."
          },
          "extrato": [
            {
              "tipo_codigo": "D",
              "tipo_descricao": "Depósito",
              "valor": "100.00",
              "data": "DD/MM/YYYY HH:MM:SS"
            },
            // ... outras transações
          ]
        }
        ```

## Como Rodar os Testes Automatizados

1.  Certifique-se de que as dependências de teste estão instaladas (`pytest`, `pytest-django`).
2.  Na raiz do projeto, execute:
    ```bash
    pytest
    ```
    Ou para ver mais detalhes:
    ```bash
    pytest -v
    ```

## Autor

* **[Pedro Henrique Vital Guimarães]**
* GitHub: `[@PHVital](https://github.com/PHVital)`
* LinkedIn: `[Pedro Henrique Vital Guimarães](https://www.linkedin.com/in/pedro-henrique-vital-guimar%C3%A3es/)`
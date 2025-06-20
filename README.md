# Projeto Banco Digital API

[![Django CI Banco Project](https://github.com/PHVital/projeto-banco/actions/workflows/django-ci.yml/badge.svg)](https://github.com/PHVital/projeto-banco/actions/workflows/django-ci.yml)
![Badge de Linguagem](https://img.shields.io/badge/Python-3.11-blue.svg)
![Badge de Framework](https://img.shields.io/badge/Django-5.2-green.svg)
![Badge de DRF](https://img.shields.io/badge/DRF-3.15-red.svg)
> Uma API RESTful desenvolvida em Django e Django REST Framework para simular as operações básicas de um sistema bancário, incluindo gerenciamento de contas, transações com depósito, saque e transferência.

## 📑 Sumário

- [Funcionalidades](#funcionalidades-principais)
- [Tech Stack](#tecnologias-utilizadas-tech-stack)
- [Como Rodar Localmente](#como-configurar-e-rodar-o-projeto-localmente)
- [Estrutura do Projeto](#estrutura-do-projeto-simplificada)
- [Endpoints da API](#endpoints-da-api)
- [Rodar Testes](#como-rodar-os-testes-automatizados)
- [Autor](#autor)

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
    * Autenticação por Token (DRF `authtoken`)
* **Banco de Dados:**
    * SQLite (para testes locais sem Docker)
    * PostgreSQL (em produção e desenvolvimento com Docker)
* **Testes:**
    * Pytest
    * pytest-django
    * Postman (para testes manuais/exploratórios da API)
* **Deploy e Infraestrutura:**
    * Docker e Docker Compose
    * Gunicorn (Servidor WSGI)
    * WhiteNoise (Servir arquivos estáticos)
    * Render (Plataforma de Cloud para deploy)
    * GitHub Actions (Integração Contínua - CI)

## Pré-requisitos

* Python 3.11 ou superior
* Pip (gerenciador de pacotes Python)
* Git
* Docker e Docker Compose

## Como Configurar e Rodar o Projeto Localmente

Este projeto é totalmente containerizado, então a maneira mais fácil de rodá-lo é com o Docker.

1. **Clone o repositório:**
    ```bash
    git clone https://github.com/PHVital/projeto-banco.git
    cd projeto-banco
    ```

2. **Crie o arquivo de variáveis de ambiente:**
    * Copie o arquivo de exemplo `.env.example` para um novo arquivo chamado `.env`.
    * (Se você não tiver um `.env.example`, apenas crie um `.env` na raiz do projeto).
    * Adicione as seguintes variáveis:
        ```
        SECRET_KEY=sua_secret_key_super_secreta_aqui
        DEBUG=True
        ```

3.  **Suba os containers:**
    ```bash
    docker-compose up --build
    ```
    Este comando irá construir a imagem da aplicação, baixar a imagem do PostgreSQL e iniciar ambos os containers.

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
│   ├── viewsets.py
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

* **`POST /api/contas/{id}/deposito/`**
    * Realiza um depósito em uma conta específica.
    * **Corpo da Requisição (Exemplo):**
        ```json
        {
          "valor": "100.50"
        }
        ```

* **`POST /api/contas/{id}/saque/`**
    * Realiza um saque de uma conta específica.
    * **Corpo da Requisição (Exemplo):**
        ```json
        {
          "valor": "50.00"
        }
        ```

* **`POST /api/contas/{id}/transferencia/`**
    * Realiza uma transferência da conta especificada ({id}) para outra conta.
    * **Corpo da Requisição (Exemplo):**
        ```json
        {
          "conta_destino": "NUMERO_DA_CONTA_DESTINO",
          "valor": "25.00"
        }
        ```

**Consultas (Requer Autenticação)**

* **`GET /api/contas/`**
    * Lista todas as contas bancárias pertencentes ao usuário autenticado.

* **`GET /api/contas/{id}/`**
    * Retorna os detalhes (incluindo saldo) de uma conta específica do usuário.

* **`GET /api/contas/{id}/extrato/`**
    * Retorna o extrato de transações de uma conta específica.

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

## API em Produção

A API está disponível em: `https://api-banco-phvital.onrender.com/api/`

### Documentação Interativa (Swagger UI)
`https://api-banco-phvital.onrender.com/api/docs/swagger/`

### Documentação (ReDoc)
`https://api-banco-phvital.onrender.com/api/docs/redoc/`

## Autor

* **Pedro Henrique Vital Guimarães**
* GitHub: [@PHVital](https://github.com/PHVital)
* LinkedIn: [Pedro Henrique Vital Guimarães](https://www.linkedin.com/in/pedro-henrique-vital-guimar%C3%A3es/)
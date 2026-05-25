# Catálogo de Filmes

Projeto full stack para gerenciamento de um catálogo de filmes, desenvolvido com Flask, Flet e uma landing page estática.

## Tecnologias

- **Backend**: Flask + Flask-RESTX (Swagger automático) + Pydantic
- **Frontend**: Flet (interface desktop em Python)
- **Landing Page**: HTML + Tailwind CSS

## Como rodar

### 1. Instalar dependências

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Backend

```bash
cd backend
python app.py
```

API disponível em `http://127.0.0.1:5000/api`  
Swagger UI em `http://127.0.0.1:5000/api/docs`

### 3. Frontend

Em outro terminal:

```bash
cd frontend
flet run main.py
```

### 4. Landing Page

Abra o arquivo `landing/index.html` diretamente no navegador.

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/movies` | Lista todos os filmes |
| GET | `/api/movies/<id>` | Retorna um filme pelo ID |
| POST | `/api/movies` | Cadastra um novo filme (valida com Pydantic) |

## Estrutura

```
catalogo-filmes/
├── backend/
│   ├── app.py          # Factory da aplicação Flask
│   ├── data.py         # Dados em memória
│   └── api/
│       ├── routes.py   # Endpoints e documentação Swagger
│       └── schemas.py  # Modelos Pydantic
├── frontend/
│   └── main.py         # Interface desktop Flet
├── landing/
│   └── index.html      # Landing page estática
└── requirements.txt
```

# Catálogo de Filmes

Aplicação full stack com backend Flask, frontend em Flet e landing page estática em HTML + Tailwind CSS. O projeto simula um pequeno catálogo de filmes com listagem, consulta e cadastro de novos títulos.

## Requisitos atendidos

- Backend Flask organizado com Blueprint
- Dois endpoints GET documentados com Swagger/Docstring
- Um endpoint POST com validação usando Pydantic
- Frontend Flet consumindo GET e POST com feedback ao usuário
- Landing page estática com Tailwind CSS, descrição do projeto e instruções de execução

## Stack

- Backend: Flask, Flask-RESTX e Pydantic
- Frontend: Flet e Requests
- Landing page: HTML e Tailwind CSS via CDN

## Como executar

### 1. Instale as dependências

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Inicie o backend

Você pode executar pela raiz do projeto:

```bash
python -m backend.app
```

Ou, se preferir:

```bash
cd backend
python app.py
```

API base: `http://127.0.0.1:5000/api`  
Swagger UI: `http://127.0.0.1:5000/api/docs`

### 3. Inicie o frontend Flet

Em outro terminal, com o backend já rodando:

```bash
flet run frontend/main.py
```

### 4. Abra a landing page

Abra [landing/index.html](/C:/catalogo-filmes/landing/index.html) no navegador.

## Endpoints principais

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/movies` | Lista todos os filmes cadastrados |
| GET | `/api/movies/<id>` | Retorna os detalhes de um filme pelo ID |
| POST | `/api/movies` | Cadastra um novo filme com validação Pydantic |

### Exemplo de payload para POST

```json
{
  "title": "Matrix",
  "genre": "Ficção científica",
  "year": 1999,
  "rating": 8.7
}
```

## Estrutura

```text
catalogo-filmes/
├── backend/
│   ├── app.py
│   ├── data.py
│   └── api/
│       ├── routes.py
│       └── schemas.py
├── frontend/
│   └── main.py
├── landing/
│   └── index.html
├── .gitignore
├── README.md
└── requirements.txt
```

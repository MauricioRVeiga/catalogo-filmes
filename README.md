# Catálogo de Filmes

Aplicação full stack com backend Flask, frontend em Flet e landing page estática em HTML + Tailwind CSS. O projeto simula um catálogo de filmes com listagem, consulta por ID e cadastro de novos títulos.

## Requisitos atendidos

- Backend Flask organizado com Blueprint
- Dois endpoints GET documentados com Swagger/Docstring
- Um endpoint POST com validação usando Pydantic
- Frontend Flet consumindo GET e POST com feedback ao usuário
- Landing page estática com Tailwind CSS, nome, descrição e instruções de execução

## Stack

- Backend: Flask, Flask-RESTX e Pydantic
- Frontend: Flet e Requests
- Landing page: HTML e Tailwind CSS via CDN

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

## Como executar

### 1. Criar e ativar o ambiente virtual

```powershell
python -m venv .venv
```

Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& .\.venv\Scripts\Activate.ps1
```

Windows CMD:

```bat
.venv\Scripts\activate.bat
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 2. Instalar as dependências

```powershell
pip install -r requirements.txt
```

### 3. Iniciar o backend

Na raiz do projeto:

```powershell
python -m backend.app
```

Ou, se você já estiver dentro da pasta `backend`:

```powershell
python app.py
```

API base: `http://127.0.0.1:5000/api`  
Swagger UI: `http://127.0.0.1:5000/api/docs`

### 4. Iniciar o frontend Flet

Com o backend já rodando, abra outro terminal e ative a mesma `.venv`.

Na raiz do projeto:

```powershell
& .\.venv\Scripts\flet.exe run frontend/main.py
```

Se você já estiver dentro da pasta `frontend`:

```powershell
& ..\.venv\Scripts\flet.exe run main.py
```

Observação: em alguns ambientes o comando `flet run ...` não é reconhecido diretamente no PowerShell. Nesses casos, use o executável da `.venv`, como mostrado acima.

### 5. Abrir a landing page

Abra `landing/index.html` no navegador.

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

## Observações de implementação

- O backend pode ser executado tanto pela raiz do projeto quanto pela pasta `backend`.
- O frontend foi ajustado para a versão de Flet instalada na `.venv` do projeto.
- As respostas do backend preservam acentuação em JSON.
- O endpoint `GET /api/movies/<id>` retorna `404` com mensagem de erro quando o filme não existe.

## Solução de problemas

### `ModuleNotFoundError` ao subir o backend

Garanta que a `.venv` está ativada antes de executar:

```powershell
& .\.venv\Scripts\Activate.ps1
python -m backend.app
```

Se estiver dentro da pasta `backend`, use:

```powershell
python app.py
```

### `flet` não é reconhecido no PowerShell

Use o executável da virtualenv:

```powershell
& .\.venv\Scripts\flet.exe run frontend/main.py
```

Ou, dentro da pasta `frontend`:

```powershell
& ..\.venv\Scripts\flet.exe run main.py
```

### Erros visuais ou de compatibilidade no Flet

O frontend já foi ajustado para a versão atual do Flet instalada no projeto. Se ainda houver erro, confirme que você está usando a `.venv` local e não uma instalação global do Python.

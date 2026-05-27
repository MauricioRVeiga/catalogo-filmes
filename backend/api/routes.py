from flask import Blueprint, request
from flask_restx import Api, Resource, fields
from pydantic import ValidationError

if __package__ == "backend.api":
    from ..data import movies
    from .schemas import MovieCreate, MovieUpdate
else:
    from data import movies
    from api.schemas import MovieCreate, MovieUpdate

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(
    api_bp,
    version="1.0",
    title="Catálogo de Filmes",
    description=(
        "API REST para gerenciamento CRUD de um catálogo de filmes. "
        "Permite listar, consultar, cadastrar, atualizar e remover títulos."
    ),
    doc="/docs",
)

movie_model = api.model("Movie", {
    "id": fields.Integer(readonly=True, description="Identificador único do filme"),
    "title": fields.String(required=True, description="Título do filme"),
    "genre": fields.String(required=True, description="Gênero cinematográfico"),
    "year": fields.Integer(required=True, description="Ano de lançamento"),
    "rating": fields.Float(required=True, description="Nota do filme (0.0 a 10.0)"),
})

movie_input_model = api.model("MovieInput", {
    "title": fields.String(required=True, description="Título do filme (1–100 caracteres)", example="Matrix"),
    "genre": fields.String(required=True, description="Gênero do filme (1–60 caracteres)", example="Ficção científica"),
    "year": fields.Integer(required=True, description="Ano de lançamento (1888–2100)", example=1999),
    "rating": fields.Float(required=True, description="Nota de 0.0 a 10.0", example=8.7),
})

error_model = api.model("Error", {
    "error": fields.Raw(description="Mensagem ou lista de erros de validação"),
})

message_model = api.model("Message", {
    "message": fields.String(description="Mensagem de retorno da operação"),
})


def get_json_payload():
    payload = request.get_json(silent=True)
    return payload if isinstance(payload, dict) else None


def find_movie(movie_id: int):
    return next((movie for movie in movies if movie["id"] == movie_id), None)


def next_movie_id() -> int:
    return max((movie["id"] for movie in movies), default=0) + 1


@api.route("/movies")
class MovieList(Resource):
    @api.doc("listar_filmes")
    @api.marshal_list_with(movie_model)
    @api.response(200, "Lista de filmes retornada com sucesso")
    def get(self):
        """Lista todos os filmes do catálogo.

        Retorna um array com todos os filmes cadastrados.
        Cada registro contém id, título, gênero, ano de lançamento e nota.
        """
        return movies, 200

    @api.doc("criar_filme")
    @api.expect(movie_input_model)
    @api.response(201, "Filme criado com sucesso", movie_model)
    @api.response(400, "Dados inválidos — falha na validação Pydantic", error_model)
    def post(self):
        """Cadastra um novo filme com validação via Pydantic.

        Campos obrigatórios e regras de validação:
        - **title**: string de 1 a 100 caracteres
        - **genre**: string de 1 a 60 caracteres
        - **year**: inteiro entre 1888 e 2100
        - **rating**: float entre 0.0 e 10.0

        Retorna 400 com detalhes dos erros caso a validação falhe.
        """
        payload = get_json_payload()
        if payload is None:
            return {"error": "Envie um corpo JSON válido."}, 400

        try:
            movie = MovieCreate(**payload)
        except ValidationError as e:
            return {"error": e.errors()}, 400

        new_movie = {"id": next_movie_id(), **movie.model_dump()}
        movies.append(new_movie)
        return new_movie, 201


@api.route("/movies/<int:movie_id>")
@api.param("movie_id", "Identificador único do filme")
class MovieDetail(Resource):
    @api.doc("detalhar_filme")
    @api.response(200, "Filme encontrado com sucesso", movie_model)
    @api.response(404, "Filme não encontrado", error_model)
    def get(self, movie_id):
        """Retorna os detalhes de um filme específico pelo ID.

        Realiza busca pelo identificador único (id) do filme.
        Retorna 404 caso o ID não exista no catálogo.
        """
        movie = find_movie(movie_id)
        if not movie:
            return {"error": "Filme não encontrado"}, 404
        return movie, 200

    @api.doc("atualizar_filme")
    @api.expect(movie_input_model)
    @api.response(200, "Filme atualizado com sucesso", movie_model)
    @api.response(400, "Dados inválidos — falha na validação Pydantic", error_model)
    @api.response(404, "Filme não encontrado", error_model)
    def put(self, movie_id):
        """Atualiza um filme existente com validação via Pydantic.

        Requer o envio completo do objeto filme no corpo da requisição:
        - **title**: string de 1 a 100 caracteres
        - **genre**: string de 1 a 60 caracteres
        - **year**: inteiro entre 1888 e 2100
        - **rating**: float entre 0.0 e 10.0

        Retorna 404 caso o filme informado não exista.
        """
        movie = find_movie(movie_id)
        if not movie:
            return {"error": "Filme não encontrado"}, 404

        payload = get_json_payload()
        if payload is None:
            return {"error": "Envie um corpo JSON válido."}, 400

        try:
            movie_data = MovieUpdate(**payload)
        except ValidationError as e:
            return {"error": e.errors()}, 400

        movie.update(movie_data.model_dump())
        return movie, 200

    @api.doc("remover_filme")
    @api.response(200, "Filme removido com sucesso", message_model)
    @api.response(404, "Filme não encontrado", error_model)
    def delete(self, movie_id):
        """Remove um filme do catálogo pelo ID.

        Exclui permanentemente o filme correspondente ao identificador informado.
        Retorna 404 caso o filme não exista.
        """
        movie = find_movie(movie_id)
        if not movie:
            return {"error": "Filme não encontrado"}, 404

        movies.remove(movie)
        return {"message": "Filme removido com sucesso"}, 200

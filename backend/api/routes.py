from flask import Blueprint, request
from flask_restx import Api, Resource, fields
from pydantic import ValidationError

try:
    from backend.data import movies
    from backend.api.schemas import MovieCreate
except ModuleNotFoundError:
    from data import movies
    from api.schemas import MovieCreate

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(
    api_bp,
    version="1.0",
    title="Catálogo de Filmes",
    description=(
        "API REST para gerenciamento de um catálogo de filmes. "
        "Permite listar todos os filmes, consultar por ID e cadastrar novos títulos."
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


def get_json_payload():
    payload = request.get_json(silent=True)
    return payload if isinstance(payload, dict) else None


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

        new_movie = {"id": len(movies) + 1, **movie.model_dump()}
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
        movie = next((m for m in movies if m["id"] == movie_id), None)
        if not movie:
            return {"error": "Filme não encontrado"}, 404
        return movie, 200

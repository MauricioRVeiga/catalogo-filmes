from flask import Blueprint, request
from flask_restx import Api, Resource, fields
from pydantic import ValidationError
from data import movies
from api.schemas import MovieCreate

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(
    api_bp,
    version="1.0",
    title="Catálogo de Filmes",
    description="API do projeto de catálogo de filmes",
    doc="/docs"
)

movie_model = api.model("Movie", {
    "id": fields.Integer,
    "title": fields.String,
    "genre": fields.String,
    "year": fields.Integer,
    "rating": fields.Float
})

movie_input_model = api.model("MovieInput", {
    "title": fields.String(required=True),
    "genre": fields.String(required=True),
    "year": fields.Integer(required=True),
    "rating": fields.Float(required=True)
})

@api.route("/movies")
class MovieList(Resource):
    @api.doc("listar_filmes")
    @api.marshal_list_with(movie_model)
    def get(self):
        """Lista todos os filmes do catálogo."""
        return movies, 200

    @api.doc("criar_filme")
    @api.expect(movie_input_model)
    def post(self):
        """Cria um novo filme com validação via Pydantic."""
        try:
            payload = request.get_json(force=True)
            movie = MovieCreate(**payload)
        except ValidationError as e:
            return {"error": e.errors()}, 400

        new_movie = {
            "id": len(movies) + 1,
            **movie.model_dump()
        }
        movies.append(new_movie)
        return new_movie, 201

@api.route("/movies/<int:movie_id>")
class MovieDetail(Resource):
    @api.doc("detalhar_filme")
    @api.marshal_with(movie_model)
    def get(self, movie_id):
        """Retorna um filme específico pelo ID."""
        movie = next((m for m in movies if m["id"] == movie_id), None)
        if not movie:
            return {"error": "Filme não encontrado"}, 404
        return movie, 200
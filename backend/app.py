from flask import Flask

try:
    from backend.api.routes import api_bp
except ModuleNotFoundError:
    from api.routes import api_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.register_blueprint(api_bp)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

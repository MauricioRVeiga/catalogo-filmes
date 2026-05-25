import flet as ft
import requests

API_URL = "http://127.0.0.1:5000/api"

def main(page: ft.Page):
    page.title = "Catálogo de Filmes"
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    movies_list = ft.Column(spacing=10)
    feedback = ft.Text("")

    title_field = ft.TextField(label="Título", width=400)
    genre_field = ft.TextField(label="Gênero", width=400)
    year_field = ft.TextField(label="Ano", width=400)
    rating_field = ft.TextField(label="Nota", width=400)

    def load_movies():
        movies_list.controls.clear()
        try:
            response = requests.get(f"{API_URL}/movies", timeout=10)
            data = response.json()
            for movie in data:
                movies_list.controls.append(
                    ft.Container(
                        content=ft.Text(
                            f'{movie["id"]}. {movie["title"]} — {movie["genre"]} ({movie["year"]}) | Nota: {movie["rating"]}'
                        ),
                        padding=10,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        border_radius=8
                    )
                )
            feedback.value = "Filmes carregados com sucesso."
        except Exception as e:
            feedback.value = f"Erro ao carregar filmes: {e}"
        page.update()

    def submit_movie(e):
        try:
            payload = {
                "title": title_field.value,
                "genre": genre_field.value,
                "year": int(year_field.value),
                "rating": float(rating_field.value)
            }
            response = requests.post(f"{API_URL}/movies", json=payload, timeout=10)
            if response.status_code == 201:
                feedback.value = "Filme cadastrado com sucesso."
                title_field.value = ""
                genre_field.value = ""
                year_field.value = ""
                rating_field.value = ""
                load_movies()
            else:
                feedback.value = f"Erro: {response.json()}"
        except Exception as e:
            feedback.value = f"Falha no envio: {e}"
        page.update()

    page.add(
        ft.Text("Catálogo de Filmes", size=28, weight=ft.FontWeight.BOLD),
        ft.ElevatedButton("Atualizar lista", on_click=lambda e: load_movies()),
        movies_list,
        ft.Divider(),
        ft.Text("Cadastrar novo filme", size=22, weight=ft.FontWeight.BOLD),
        title_field,
        genre_field,
        year_field,
        rating_field,
        ft.ElevatedButton("Salvar filme", on_click=submit_movie),
        feedback
    )

    load_movies()

ft.app(target=main)
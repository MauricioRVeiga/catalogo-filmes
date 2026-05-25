import flet as ft
import requests

API_URL = "http://127.0.0.1:5000/api"


def make_field(label: str, keyboard_type=None) -> ft.TextField:
    return ft.TextField(
        label=label,
        width=400,
        bgcolor=ft.Colors.GREY_800,
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=ft.Colors.GREY_400),
        border_color=ft.Colors.GREY_600,
        focused_border_color=ft.Colors.AMBER_400,
        cursor_color=ft.Colors.AMBER_400,
        keyboard_type=keyboard_type,
    )


def main(page: ft.Page):
    page.title = "Catálogo de Filmes"
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.GREY_900
    page.padding = 32

    movies_list = ft.Column(spacing=8)
    feedback = ft.Text("", size=13, weight=ft.FontWeight.W_500)

    title_field = make_field("Título")
    genre_field = make_field("Gênero")
    year_field = make_field("Ano", keyboard_type=ft.KeyboardType.NUMBER)
    rating_field = make_field("Nota (0.0 – 10.0)", keyboard_type=ft.KeyboardType.NUMBER)

    def set_feedback(msg: str, success: bool):
        feedback.value = msg
        feedback.color = ft.Colors.GREEN_400 if success else ft.Colors.RED_400
        page.update()

    def movie_card(movie: dict) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("🎬", size=22),
                    ft.Column(
                        controls=[
                            ft.Text(
                                movie["title"],
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.AMBER_300,
                            ),
                            ft.Text(
                                f'{movie["genre"]}  •  {movie["year"]}  •  ⭐ {movie["rating"]}',
                                size=12,
                                color=ft.Colors.GREY_400,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                spacing=12,
            ),
            padding=14,
            border_radius=10,
            bgcolor=ft.Colors.GREY_800,
        )

    def load_movies(e=None):
        movies_list.controls.clear()
        try:
            response = requests.get(f"{API_URL}/movies", timeout=10)
            data = response.json()
            if not data:
                movies_list.controls.append(
                    ft.Text(
                        "Nenhum filme no catálogo ainda.",
                        italic=True,
                        color=ft.Colors.GREY_500,
                    )
                )
            else:
                for movie in data:
                    movies_list.controls.append(movie_card(movie))
            set_feedback("Catálogo atualizado com sucesso.", True)
        except Exception as exc:
            set_feedback(f"Erro ao carregar filmes: {exc}", False)
        page.update()

    def submit_movie(e):
        try:
            payload = {
                "title": title_field.value.strip(),
                "genre": genre_field.value.strip(),
                "year": int(year_field.value),
                "rating": float(rating_field.value),
            }
        except ValueError:
            set_feedback("Ano deve ser inteiro e Nota deve ser número decimal.", False)
            return

        try:
            response = requests.post(f"{API_URL}/movies", json=payload, timeout=10)
            if response.status_code == 201:
                set_feedback(f'"{payload["title"]}" adicionado ao catálogo!', True)
                title_field.value = ""
                genre_field.value = ""
                year_field.value = ""
                rating_field.value = ""
                load_movies()
            else:
                erros = response.json().get("error", response.text)
                set_feedback(f"Erro de validação: {erros}", False)
        except Exception as exc:
            set_feedback(f"Falha na conexão: {exc}", False)
        page.update()

    page.add(
        # Cabeçalho
        ft.Text(
            "🎬  Catálogo de Filmes",
            size=30,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.AMBER_400,
        ),
        ft.Text(
            "Seu acervo pessoal de filmes favoritos",
            size=13,
            color=ft.Colors.GREY_500,
        ),
        ft.Divider(height=28, color=ft.Colors.GREY_700),

        # Seção: lista de filmes
        ft.Row(
            controls=[
                ft.Text(
                    "Em cartaz no seu catálogo",
                    size=17,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.WHITE,
                ),
                ft.ElevatedButton(
                    "Atualizar",
                    icon="refresh",
                    on_click=load_movies,
                    bgcolor=ft.Colors.GREY_700,
                    color=ft.Colors.WHITE,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            width=420,
        ),
        movies_list,
        ft.Divider(height=28, color=ft.Colors.GREY_700),

        # Seção: formulário
        ft.Text(
            "🎟️  Adicionar novo filme",
            size=17,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.WHITE,
        ),
        title_field,
        genre_field,
        year_field,
        rating_field,
        ft.ElevatedButton(
            "Salvar filme",
            icon="save",
            on_click=submit_movie,
            width=400,
            bgcolor=ft.Colors.AMBER_700,
            color=ft.Colors.BLACK,
        ),
        feedback,
    )

    load_movies()


ft.app(target=main)

import flet as ft
import requests

API_URL = "http://127.0.0.1:5000/api"
REQUEST_TIMEOUT = 10


def make_border(color: str, width: int = 1) -> ft.border.Border:
    return ft.border.Border.all(width=width, color=color)


def make_padding(horizontal: int = 0, vertical: int = 0) -> ft.padding.Padding:
    return ft.padding.Padding.symmetric(horizontal=horizontal, vertical=vertical)


def make_field(label: str, keyboard_type=None) -> ft.TextField:
    return ft.TextField(
        label=label,
        filled=True,
        expand=True,
        height=56,
        bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_GREY_200),
        border_color=ft.Colors.with_opacity(0.12, ft.Colors.WHITE),
        focused_border_color=ft.Colors.AMBER_400,
        cursor_color=ft.Colors.AMBER_400,
        keyboard_type=keyboard_type,
    )


def parse_api_error(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text or "Não foi possível processar a resposta da API."

    error = payload.get("error")
    if isinstance(error, list):
        messages = []
        for item in error:
            field = ".".join(str(part) for part in item.get("loc", [])) or "campo"
            message = item.get("msg", "valor inválido")
            messages.append(f"{field}: {message}")
        return " | ".join(messages)

    if isinstance(error, str):
        return error

    return payload.get("message", "Ocorreu um erro inesperado.")


def main(page: ft.Page):
    page.title = "Catálogo de Filmes"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0b1120"
    page.padding = 24
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_min_width = 420
    page.window_min_height = 700

    movies_list = ft.Column(spacing=10)
    catalog_summary = ft.Text("Carregando catálogo...", color=ft.Colors.BLUE_GREY_200)
    feedback_text = ft.Text(size=13, weight=ft.FontWeight.W_500)
    feedback_box = ft.Container(
        visible=False,
        padding=12,
        border_radius=12,
        content=feedback_text,
    )

    title_field = make_field("Título")
    genre_field = make_field("Gênero")
    year_field = make_field("Ano", keyboard_type=ft.KeyboardType.NUMBER)
    rating_field = make_field("Nota (0.0 a 10.0)", keyboard_type=ft.KeyboardType.NUMBER)

    refresh_button = ft.ElevatedButton(
        "Atualizar catálogo",
        icon=ft.Icons.REFRESH,
        bgcolor="#1e293b",
        color=ft.Colors.WHITE,
    )
    submit_button = ft.ElevatedButton(
        "Salvar filme",
        icon=ft.Icons.SAVE,
        bgcolor="#f59e0b",
        color="#111827",
        width=220,
    )

    def set_feedback(message: str, success: bool):
        feedback_text.value = message
        feedback_text.color = "#d1fae5" if success else "#fee2e2"
        feedback_box.bgcolor = "#14532d" if success else "#7f1d1d"
        feedback_box.border = make_border("#22c55e" if success else "#ef4444")
        feedback_box.visible = True
        page.update()

    def set_buttons_busy(is_busy: bool):
        refresh_button.disabled = is_busy
        submit_button.disabled = is_busy
        submit_button.text = "Salvando..." if is_busy else "Salvar filme"
        page.update()

    def clear_form():
        title_field.value = ""
        genre_field.value = ""
        year_field.value = ""
        rating_field.value = ""

    def movie_card(movie: dict) -> ft.Container:
        return ft.Container(
            padding=16,
            border_radius=18,
            bgcolor="#111827",
            border=make_border("#1f2937"),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(
                                width=42,
                                height=42,
                                border_radius=12,
                                bgcolor="#1d4ed8",
                                alignment=ft.alignment.Alignment.CENTER,
                                content=ft.Text("🎬", size=18),
                            ),
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(
                                        movie["title"],
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                    ),
                                    ft.Text(
                                        f'{movie["genre"]} • {movie["year"]}',
                                        size=12,
                                        color=ft.Colors.BLUE_GREY_200,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Container(
                        padding=make_padding(horizontal=12, vertical=8),
                        border_radius=999,
                        bgcolor="#3f2b05",
                        content=ft.Text(
                            f'⭐ {movie["rating"]}',
                            size=12,
                            weight=ft.FontWeight.W_600,
                            color="#fcd34d",
                        ),
                    ),
                ],
            ),
        )

    def load_movies(e=None):
        set_buttons_busy(True)
        movies_list.controls[:] = [ft.ProgressRing(color=ft.Colors.AMBER_400)]
        catalog_summary.value = "Sincronizando com a API..."
        page.update()

        try:
            response = requests.get(f"{API_URL}/movies", timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            movies_list.controls.clear()

            if not data:
                movies_list.controls.append(
                    ft.Container(
                        padding=20,
                        border_radius=16,
                        bgcolor="#111827",
                        border=make_border("#1f2937"),
                        content=ft.Text(
                            "Nenhum filme cadastrado ainda. Use o formulário para criar o primeiro item.",
                            color=ft.Colors.BLUE_GREY_200,
                        ),
                    )
                )
            else:
                for movie in data:
                    movies_list.controls.append(movie_card(movie))

            catalog_summary.value = f"{len(data)} filme(s) carregado(s) do endpoint GET /api/movies."
            set_feedback("Catálogo atualizado com sucesso.", True)
        except requests.RequestException as exc:
            movies_list.controls.clear()
            catalog_summary.value = "Não foi possível carregar o catálogo."
            set_feedback(f"Erro ao consultar a API: {exc}", False)
        finally:
            set_buttons_busy(False)
            page.update()

    def submit_movie(e):
        raw_title = (title_field.value or "").strip()
        raw_genre = (genre_field.value or "").strip()
        raw_year = (year_field.value or "").strip()
        raw_rating = (rating_field.value or "").strip()

        if not all([raw_title, raw_genre, raw_year, raw_rating]):
            set_feedback("Preencha título, gênero, ano e nota antes de salvar.", False)
            return

        try:
            payload = {
                "title": raw_title,
                "genre": raw_genre,
                "year": int(raw_year),
                "rating": float(raw_rating),
            }
        except ValueError:
            set_feedback("Ano deve ser inteiro e nota deve ser um número decimal.", False)
            return

        set_buttons_busy(True)
        try:
            response = requests.post(
                f"{API_URL}/movies",
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )
            if response.status_code == 201:
                clear_form()
                set_feedback(f'"{payload["title"]}" foi adicionado ao catálogo.', True)
                load_movies()
            else:
                set_feedback(parse_api_error(response), False)
        except requests.RequestException as exc:
            set_feedback(f"Falha ao enviar dados para a API: {exc}", False)
        finally:
            set_buttons_busy(False)
            page.update()

    refresh_button.on_click = load_movies
    submit_button.on_click = submit_movie

    header = ft.Container(
        width=960,
        padding=24,
        border_radius=24,
        bgcolor="#111827",
        border=make_border("#1f2937"),
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            padding=make_padding(horizontal=12, vertical=6),
                            border_radius=999,
                            bgcolor="#172554",
                            content=ft.Text(
                                "Flask + Flet + Pydantic",
                                size=12,
                                color="#93c5fd",
                            ),
                        )
                    ]
                ),
                ft.Text(
                    "Catálogo de Filmes",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(
                    "Consuma os endpoints GET da API e cadastre novos filmes com validação Pydantic pelo formulário.",
                    size=14,
                    color=ft.Colors.BLUE_GREY_200,
                ),
            ],
        ),
    )

    list_card = ft.Container(
        width=560,
        padding=22,
        border_radius=24,
        bgcolor="#0f172a",
        border=make_border("#1e293b"),
        content=ft.Column(
            spacing=18,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(
                                    "Filmes cadastrados",
                                    size=20,
                                    weight=ft.FontWeight.W_600,
                                    color=ft.Colors.WHITE,
                                ),
                                catalog_summary,
                            ],
                        ),
                        refresh_button,
                    ],
                ),
                movies_list,
            ],
        ),
    )

    form_card = ft.Container(
        width=360,
        padding=22,
        border_radius=24,
        bgcolor="#0f172a",
        border=make_border("#1e293b"),
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text(
                    "Novo filme",
                    size=20,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(
                    "Os dados enviados são validados pelo endpoint POST /api/movies.",
                    size=13,
                    color=ft.Colors.BLUE_GREY_200,
                ),
                title_field,
                genre_field,
                year_field,
                rating_field,
                submit_button,
                feedback_box,
            ],
        ),
    )

    page.add(
        ft.Container(
            width=960,
            content=ft.Column(
                spacing=20,
                controls=[
                    header,
                    ft.Row(
                        wrap=True,
                        spacing=20,
                        run_spacing=20,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[list_card, form_card],
                    ),
                ],
            ),
        )
    )

    load_movies()


ft.app(target=main)

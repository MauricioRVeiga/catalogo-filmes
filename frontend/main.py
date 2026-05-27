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
        return response.text or "Nao foi possivel processar a resposta da API."

    error = payload.get("error")
    if isinstance(error, list):
        messages = []
        for item in error:
            field = ".".join(str(part) for part in item.get("loc", [])) or "campo"
            message = item.get("msg", "valor invalido")
            messages.append(f"{field}: {message}")
        return " | ".join(messages)

    if isinstance(error, str):
        return error

    return payload.get("message", "Ocorreu um erro inesperado.")


def main(page: ft.Page):
    page.title = "Catalogo de Filmes"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0b1120"
    page.padding = 24
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_min_width = 420
    page.window_min_height = 700

    ui_state = {"editing_id": None}
    movies_list = ft.Column(spacing=10)
    catalog_summary = ft.Text("Carregando catalogo...", color=ft.Colors.BLUE_GREY_200)
    form_mode_text = ft.Text("Modo criacao", size=12, color="#93c5fd")
    feedback_text = ft.Text(size=13, weight=ft.FontWeight.W_500)
    feedback_box = ft.Container(
        visible=False,
        padding=12,
        border_radius=12,
        content=feedback_text,
    )

    title_field = make_field("Titulo")
    genre_field = make_field("Genero")
    year_field = make_field("Ano", keyboard_type=ft.KeyboardType.NUMBER)
    rating_field = make_field("Nota (0.0 a 10.0)", keyboard_type=ft.KeyboardType.NUMBER)

    refresh_button = ft.ElevatedButton(
        "Atualizar catalogo",
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
    cancel_button = ft.ElevatedButton(
        "Cancelar edicao",
        icon=ft.Icons.CLOSE,
        bgcolor="#334155",
        color=ft.Colors.WHITE,
        visible=False,
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
        cancel_button.disabled = is_busy
        submit_button.text = "Salvando..." if is_busy else (
            "Atualizar filme" if ui_state["editing_id"] is not None else "Salvar filme"
        )
        page.update()

    def set_form_mode(editing_movie=None):
        if editing_movie is None:
            ui_state["editing_id"] = None
            form_mode_text.value = "Modo criacao"
            submit_button.text = "Salvar filme"
            submit_button.icon = ft.Icons.SAVE
            cancel_button.visible = False
        else:
            ui_state["editing_id"] = editing_movie["id"]
            form_mode_text.value = f'Modo edicao - ID {editing_movie["id"]}'
            submit_button.text = "Atualizar filme"
            submit_button.icon = ft.Icons.EDIT
            cancel_button.visible = True
        page.update()

    def clear_form(reset_mode: bool = True):
        title_field.value = ""
        genre_field.value = ""
        year_field.value = ""
        rating_field.value = ""
        if reset_mode:
            set_form_mode()

    def build_payload():
        raw_title = (title_field.value or "").strip()
        raw_genre = (genre_field.value or "").strip()
        raw_year = (year_field.value or "").strip()
        raw_rating = (rating_field.value or "").strip()

        if not all([raw_title, raw_genre, raw_year, raw_rating]):
            set_feedback("Preencha titulo, genero, ano e nota antes de salvar.", False)
            return None

        try:
            return {
                "title": raw_title,
                "genre": raw_genre,
                "year": int(raw_year),
                "rating": float(raw_rating),
            }
        except ValueError:
            set_feedback("Ano deve ser inteiro e nota deve ser decimal.", False)
            return None

    def start_edit(movie: dict):
        title_field.value = movie["title"]
        genre_field.value = movie["genre"]
        year_field.value = str(movie["year"])
        rating_field.value = str(movie["rating"])
        set_form_mode(movie)
        set_feedback(f'Editando "{movie["title"]}". Atualize os campos e salve.', True)

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
                                content=ft.Text("FILM", size=12, color=ft.Colors.WHITE),
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
                                        f'{movie["genre"]} | {movie["year"]}',
                                        size=12,
                                        color=ft.Colors.BLUE_GREY_200,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=8,
                        controls=[
                            ft.Container(
                                padding=make_padding(horizontal=12, vertical=8),
                                border_radius=999,
                                bgcolor="#3f2b05",
                                content=ft.Text(
                                    f'Nota {movie["rating"]}',
                                    size=12,
                                    weight=ft.FontWeight.W_600,
                                    color="#fcd34d",
                                ),
                            ),
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.ElevatedButton(
                                        "Editar",
                                        icon=ft.Icons.EDIT,
                                        bgcolor="#1d4ed8",
                                        color=ft.Colors.WHITE,
                                        on_click=lambda e, selected_movie=movie: start_edit(selected_movie),
                                    ),
                                    ft.ElevatedButton(
                                        "Excluir",
                                        icon=ft.Icons.DELETE,
                                        bgcolor="#991b1b",
                                        color=ft.Colors.WHITE,
                                        on_click=lambda e, selected_id=movie["id"], selected_title=movie["title"]: delete_movie(selected_id, selected_title),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        )

    def load_movies(e=None, success_message="Catalogo atualizado com sucesso."):
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
                            "Nenhum filme cadastrado ainda. Use o formulario para criar o primeiro item.",
                            color=ft.Colors.BLUE_GREY_200,
                        ),
                    )
                )
            else:
                for movie in data:
                    movies_list.controls.append(movie_card(movie))

            if ui_state["editing_id"] is not None and not any(movie["id"] == ui_state["editing_id"] for movie in data):
                clear_form()

            catalog_summary.value = f"{len(data)} filme(s) carregado(s) do catalogo."
            if success_message:
                set_feedback(success_message, True)
        except requests.RequestException as exc:
            movies_list.controls.clear()
            catalog_summary.value = "Nao foi possivel carregar o catalogo."
            set_feedback(f"Erro ao consultar a API: {exc}", False)
        finally:
            set_buttons_busy(False)
            page.update()

    def submit_movie(e):
        payload = build_payload()
        if payload is None:
            return

        set_buttons_busy(True)
        try:
            editing_id = ui_state["editing_id"]
            if editing_id is None:
                response = requests.post(
                    f"{API_URL}/movies",
                    json=payload,
                    timeout=REQUEST_TIMEOUT,
                )
                expected_status = 201
                success_message = f'"{payload["title"]}" foi adicionado ao catalogo.'
            else:
                response = requests.put(
                    f"{API_URL}/movies/{editing_id}",
                    json=payload,
                    timeout=REQUEST_TIMEOUT,
                )
                expected_status = 200
                success_message = f'"{payload["title"]}" foi atualizado com sucesso.'

            if response.status_code == expected_status:
                clear_form()
                load_movies(success_message=None)
                set_feedback(success_message, True)
            else:
                set_feedback(parse_api_error(response), False)
        except requests.RequestException as exc:
            set_feedback(f"Falha ao enviar dados para a API: {exc}", False)
        finally:
            set_buttons_busy(False)
            page.update()

    def delete_movie(movie_id: int, title: str):
        set_buttons_busy(True)
        try:
            response = requests.delete(
                f"{API_URL}/movies/{movie_id}",
                timeout=REQUEST_TIMEOUT,
            )
            if response.status_code == 200:
                if ui_state["editing_id"] == movie_id:
                    clear_form()
                load_movies(success_message=None)
                set_feedback(f'"{title}" foi removido do catalogo.', True)
            else:
                set_feedback(parse_api_error(response), False)
        except requests.RequestException as exc:
            set_feedback(f"Falha ao remover filme: {exc}", False)
        finally:
            set_buttons_busy(False)
            page.update()

    refresh_button.on_click = load_movies
    submit_button.on_click = submit_movie
    cancel_button.on_click = lambda e: clear_form()

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
                    "Catalogo de Filmes",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(
                    "Gerencie filmes com operacoes de criacao, leitura, edicao e remocao integradas a API Flask.",
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
                    "Formulario",
                    size=20,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.WHITE,
                ),
                form_mode_text,
                ft.Text(
                    "Crie um novo filme ou edite um item existente selecionando o botao Editar na lista.",
                    size=13,
                    color=ft.Colors.BLUE_GREY_200,
                ),
                title_field,
                genre_field,
                year_field,
                rating_field,
                submit_button,
                cancel_button,
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

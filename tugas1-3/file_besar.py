def score_card(value, theme, global_score=False):
    return ft.Container(
        width=150,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        bgcolor=theme["card"],
        border_radius=12,
        border=ft.border.all(1, theme["border_color"]),
        content=ft.Column(
            spacing=2,
            controls=[
                ft.Text("USER SCORE" if not global_score else "GLOBAL SCORE", size=10, color=theme["text_secondary"],
                        weight=ft.FontWeight.W_600),
                ft.Text(value, size=26, color=theme["primary"] if not global_score else theme["stat_gold"],
                        weight=ft.FontWeight.W_700),
                ft.Text("Your Rating" if not global_score else "Community Average Score", size=10,
                        color=theme["text_secondary"])
            ]
        )
    )


def tag(text, theme, meta=False):
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        bgcolor=theme["card"] if not meta else theme["primary"],
        border=ft.border.all(1, theme["border_color"]) if not meta else None,
        border_radius=20,
        content=ft.Text(
            text, size=11,
            color=theme["text_main"] if not meta else theme["card"],
            weight=ft.FontWeight.W_600
        )
    )


def legend_dot(color):
    return ft.Container(width=12, height=12, bgcolor=color, border_radius=6)


def _section_card(theme: dict, title: str, content: ft.Control) -> ft.Container:
    """Card dengan header bertitle dan konten — dipakai bersama oleh LeftPanel & RightPanel."""
    return ft.Container(
        bgcolor=theme["card"],
        border=ft.border.all(1.5, theme["border_color"]),
        border_radius=12,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Column([
            ft.Container(
                content=ft.Text(title, size=11, weight=ft.FontWeight.W_800,
                                color=theme["text_main"],
                                style=ft.TextStyle(letter_spacing=1.1)),
                bgcolor=theme["bg_secondary"],
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                border=ft.border.only(bottom=ft.BorderSide(1, theme["border_color"])),
                width=float("inf"),
            ),
            ft.Container(
                content=content,
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
            ),
        ], spacing=0, tight=True),
    )


class LeftPanel(ft.Container):
    def __init__(self, detail_anime: dict, data_manager, screen_manager, theme, anime_id):
        self.detail_anime = detail_anime
        self.data_manager = data_manager
        self.screen_manager = screen_manager
        self._theme = theme
        self.anime_id = anime_id
        self.user_id = data_manager.baca_sesi()

        cover = detail_anime.get("cover_path_abs") or os.path.join(ROOT_DIR, detail_anime.get("cover_path", ""))
        gendres = detail_anime.get("genre", [])
        self.is_fav = self.data_manager.cek_is_favorit(self.user_id, self.anime_id)
        self.fav_button = self._build_fav_button()

        super().__init__(
            alignment=ft.Alignment(0, 0),
            width=268,
            content=ft.Column(
                spacing=16,
                controls=[
                    self._build_poster(cover, self._theme),
                    ft.Text(self.detail_anime.get("title", "Anime Detail"), size=22,
                            weight=ft.FontWeight.W_800, color=self._theme["text_main"]),
                    self._build_genre_tags(gendres),
                    self._build_detail_info(),
                    ft.Container(height=24),
                ]
            )
        )
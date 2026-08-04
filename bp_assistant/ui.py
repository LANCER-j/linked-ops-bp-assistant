from __future__ import annotations

from datetime import datetime
from fractions import Fraction
import math
from pathlib import Path
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import uuid

from .core import (
    MatchConfig,
    MatchRules,
    MatchState,
    Operator,
    PLAYER_A,
    PLAYER_B,
    PlayerSubmission,
    RuleError,
    build_auction_round,
)
from .storage import (
    export_results_csv,
    load_config,
    load_state,
    load_submission,
    operator_values,
    save_config,
    save_state,
    save_submission,
)


BG = "#0A1016"
HEADER_BG = "#070C11"
PANEL = "#111B25"
PANEL_2 = "#1A2733"
FG = "#F2F0E8"
MUTED = "#93A0AA"
ACCENT = "#E2B45B"
ACCENT_HOVER = "#F3CB78"
BLUE = "#54A0E8"
RED = "#E56B66"
GREEN = "#58B98A"
SURFACE = "#0D151D"
SURFACE_RAISED = "#18232E"
LINE = "#2A3946"
FOCUS = "#F0C56B"
CONTROL_HOVER = "#233441"
CONTROL_SELECTED = "#304657"
BAN_CARD = "#39252A"
BAN_BORDER = "#D76E70"
BAN_BADGE = "#F08A72"
HOST_RARITY_COLORS = {
    6: ("#34262A", "#F7E9EC"),
    5: ("#302D23", "#F1E7C8"),
    4: ("#29263A", "#E8E0F6"),
    3: ("#202D3B", "#DDEBFA"),
    2: ("#202A34", "#E5EBF1"),
    1: ("#202A34", "#E5EBF1"),
}
AUCTION_RARITY_ACCENTS = {
    6: "#C96B70",
    5: "#C7A553",
    4: "#8573C4",
    3: "#5D91BE",
    2: "#A6B0B8",
    1: "#A6B0B8",
}

PROFESSION_ICONS = {
    "先锋": "⚑",
    "近卫": "⚔",
    "狙击": "◉",
    "术师": "⬡",
    "医疗": "✚",
    "重装": "◆",
    "特种": "⌁",
    "辅助": "✦",
}

PROFESSION_ICON_NAMES = {
    "先锋": "vanguard",
    "近卫": "guard",
    "狙击": "sniper",
    "术师": "caster",
    "医疗": "medic",
    "重装": "defender",
    "特种": "specialist",
    "辅助": "supporter",
}

PROFESSION_COLORS = {
    "先锋": "#4cb8a8",
    "近卫": "#ef6c62",
    "狙击": "#5da9e9",
    "重装": "#e2ae4e",
    "医疗": "#62c58f",
    "辅助": "#ad7ce5",
    "术师": "#8b7ee8",
    "特种": "#d67dac",
}


def card_operator_name(name: str, limit: int = 18) -> str:
    """Keep operator names on one line inside compact catalogue cards."""
    return name if len(name) <= limit else f"{name[: limit - 1]}…"


def card_operator_name_size(name: str, normal: int, compact: int, minimum: int) -> int:
    length = len(name)
    if length <= 6:
        return normal
    if length <= 11:
        return compact
    return minimum


def draw_shadowed_card_name(
    canvas: tk.Canvas,
    x: float,
    y: float,
    *,
    text: str,
    font: tuple[str, int, str],
    fill: str,
    anchor: str,
    tags: tuple[str, ...],
) -> int:
    """Draw a compact dark edge shadow before the foreground card name."""
    for offset_x, offset_y in ((-1, 1), (1, 1), (0, 2)):
        canvas.create_text(
            x + offset_x,
            y + offset_y,
            text=text,
            font=font,
            fill="#03070B",
            anchor=anchor,
            tags=tags,
        )
    return canvas.create_text(
        x,
        y,
        text=text,
        font=font,
        fill=fill,
        anchor=anchor,
        tags=tags,
    )


BRANCH_ICON_NAMES = {
    "craftsman": "artificer",
    "blessing": "abjurer",
    "slower": "decel-binder",
    "ritualist": "ritualist",
    "underminer": "hexer",
    "bard": "bard",
    "supportiveranger": "supporter",
    "summoner": "summoner",
    "primguard": "primal-fighter",
    "fighter": "fighter",
    "hammer": "earthshaker",
    "sword": "swordmaster",
    "instructor": "instructor",
    "librator": "liberator",
    "lord": "lord",
    "centurion": "centurion",
    "reaper": "reaper",
    "artsfghter": "arts-fighter",
    "fearless": "dreadnought",
    "musha": "soloblade",
    "mercenary": "mercenary",
    "crusher": "crusher",
    "siegesniper": "besieger",
    "loopshooter": "loopshooter",
    "hunter": "hunter",
    "skybreaker": "skybreaker",
    "aoesniper": "artilleryman",
    "reaperrange": "spreadshooter",
    "longrange": "deadeye",
    "fastshot": "marksman",
    "bombarder": "flinger",
    "closerange": "heavyshooter",
    "primcaster": "primal",
    "blastcaster": "blast",
    "splashcaster": "splash",
    "chain": "chain",
    "mystic": "mystic",
    "soulcaster": "shaper",
    "funnel": "mech-accord",
    "phalanx": "phalanx",
    "corecaster": "core",
    "executor": "executor",
    "stalker": "ambusher",
    "hookmaster": "hookmaster",
    "geek": "geek",
    "dollkeeper": "dollkeeper",
    "alchemist": "alchemist",
    "pusher": "push-stroker",
    "traper": "trapmaster",
    "merchant": "merchant",
    "skywalker": "skyranger",
    "counsellor": "strategist",
    "charger": "charger",
    "pioneer": "pioneer",
    "agent": "agent",
    "tactician": "tactician",
    "bearer": "standard-bearer",
    "chainhealer": "chain-healer",
    "healer": "therapist",
    "ringhealer": "multi-target",
    "watchman": "watchman",
    "wandermedic": "wandering",
    "physician": "physician",
    "incantationmedic": "incantation",
    "primprotector": "primal-protector",
    "unyield": "juggernaut",
    "duelist": "duelist",
    "shotprotector": "sentry-protector",
    "guardian": "guardian",
    "protector": "protector",
    "fortress": "fortress",
    "artsprotector": "arts-protector",
}

BRANCH_ICON_CODEPOINTS = {
    name: 0xE900 + index
    for index, name in enumerate(
        (
            "abjurer agent alchemist ambusher artificer artilleryman arts-fighter "
            "arts-protector bard besieger blast caster centurion chain chain-healer "
            "charger core crusher deadeye decel-binder defender dollkeeper dreadnought "
            "duelist earthshaker executor fighter flinger fortress geek guard guardian "
            "heavyshooter hexer hookmaster hunter incantation instructor juggernaut "
            "liberator loopshooter lord marksman mech-accord medic merchant multi-target "
            "mystic phalanx physician pioneer primal primal-fighter primal-protector "
            "protector push-stroker reaper ritualist sentry-protector shaper skyranger "
            "sniper soloblade specialist splash spreadshooter standard-bearer summoner "
            "supporter swordmaster tactician therapist trapmaster vanguard wandering "
            "strategist skybreaker watchman mercenary"
        ).split()
    )
}


def short_match_id() -> str:
    return datetime.now().strftime("%Y%m%d") + "-" + uuid.uuid4().hex[:6].upper()


def safe_file_name(value: str) -> str:
    return "".join(char for char in value if char not in '\\/:*?"<>|').strip() or "未命名"


class AssetManager:
    def __init__(self, master: tk.Misc, root: Path):
        self.master = master
        self.root = root
        self.avatar_dir = root / "avatars"
        self.avatar_cache: dict[tuple[str, int], tk.PhotoImage] = {}
        self.placeholder_cache: dict[tuple[str, int], tk.PhotoImage] = {}
        self.logo_cache: dict[int, tk.PhotoImage] = {}
        self.profession_icon_cache: dict[str, tk.PhotoImage] = {}
        self._profession_source: tk.PhotoImage | None = None
        self.branch_font_family = "Segoe UI Symbol"
        self.branch_font_available = False
        self._load_branch_font()

    def _load_branch_font(self) -> None:
        font_path = self.root / "ui" / "ak-class-icons-solid.ttf"
        if not font_path.exists():
            return
        try:
            import ctypes

            add_font = ctypes.windll.gdi32.AddFontResourceExW
            add_font.argtypes = [ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_void_p]
            added = add_font(str(font_path), 0x10, None)
            if added:
                # Must match the TTF's internal family name exactly.  Using the
                # shorter "ak-class-icons" name makes Tk fall back to a system
                # font, so the private-use codepoints render as unrelated icons.
                self.branch_font_family = "ak-class-icons-solid"
                self.branch_font_available = True
        except (AttributeError, ImportError, OSError, TypeError, tk.TclError):
            return

    def branch_glyph(self, branch_id: str) -> str:
        icon_name = BRANCH_ICON_NAMES.get(branch_id)
        codepoint = BRANCH_ICON_CODEPOINTS.get(icon_name or "")
        if self.branch_font_available and codepoint is not None:
            return chr(codepoint)
        return "◇"

    def profession_glyph(self, profession: str) -> str:
        icon_name = PROFESSION_ICON_NAMES.get(profession)
        codepoint = BRANCH_ICON_CODEPOINTS.get(icon_name or "")
        if self.branch_font_available and codepoint is not None:
            return chr(codepoint)
        return PROFESSION_ICONS.get(profession, "◇")

    def logo(self, size: int = 64) -> tk.PhotoImage:
        if size in self.logo_cache:
            return self.logo_cache[size]
        sized_path = self.root / "ui" / f"linked_ops_logo_{size}.png"
        path = sized_path if sized_path.exists() else self.root / "ui" / "linked_ops_logo.png"
        try:
            image = tk.PhotoImage(master=self.master, file=str(path))
        except tk.TclError:
            image = tk.PhotoImage(master=self.master, width=size, height=size)
            image.put(ACCENT, to=(size // 5, size // 5, size * 4 // 5, size * 4 // 5))
        self.logo_cache[size] = image
        return image

    def avatar(self, operator: Operator, size: int = 88) -> tk.PhotoImage:
        key = (operator.operator_id, size)
        if key in self.avatar_cache:
            return self.avatar_cache[key]
        path = self.avatar_dir / f"{operator.operator_id}.png"
        if path.exists():
            try:
                source = tk.PhotoImage(master=self.master, file=str(path))
                largest_side = max(source.width(), source.height())
                ratio = Fraction(size, max(1, largest_side)).limit_denominator(4)
                image = source.zoom(ratio.numerator, ratio.numerator).subsample(
                    ratio.denominator, ratio.denominator
                )
                self.avatar_cache[key] = image
                return image
            except tk.TclError:
                pass
        return self.placeholder(operator.profession, size)

    def placeholder(self, profession: str, size: int = 88) -> tk.PhotoImage:
        key = (profession, size)
        if key in self.placeholder_cache:
            return self.placeholder_cache[key]
        image = tk.PhotoImage(master=self.master, width=size, height=size)
        image.put(PROFESSION_COLORS.get(profession, PANEL_2), to=(0, 0, size, size))
        inset = max(5, size // 12)
        image.put(PANEL, to=(inset, inset, size - inset, size - inset))
        self.placeholder_cache[key] = image
        return image

    def profession_icon(self, profession: str) -> tk.PhotoImage | None:
        if profession in self.profession_icon_cache:
            return self.profession_icon_cache[profession]
        if profession == "全部职业":
            image = tk.PhotoImage(master=self.master, width=98, height=98)
            image.put("#f6f6f4", to=(0, 0, 98, 98))
            for x1, y1, x2, y2 in (
                (16, 16, 45, 45),
                (53, 16, 82, 45),
                (16, 53, 45, 82),
                (53, 53, 82, 82),
            ):
                image.put("#16191e", to=(x1, y1, x2, y2))
            self.profession_icon_cache[profession] = image
            return image
        source_path = self.root / "ui" / "profession_reference.png"
        if not source_path.exists():
            return None
        if self._profession_source is None:
            try:
                self._profession_source = tk.PhotoImage(master=self.master, file=str(source_path))
            except tk.TclError:
                return None
        crops = {
            "先锋": (273, 40, 351, 118),
            "近卫": (273, 193, 351, 271),
            "狙击": (265, 346, 343, 424),
            "术师": (265, 499, 343, 577),
            "医疗": (265, 652, 343, 730),
            "重装": (265, 805, 343, 883),
            "特种": (265, 958, 343, 1036),
            "辅助": (265, 1111, 343, 1189),
        }
        if profession not in crops:
            return None
        x1, y1, x2, y2 = crops[profession]
        image = tk.PhotoImage(master=self.master, width=x2 - x1, height=y2 - y1)
        image.tk.call(
            str(image),
            "copy",
            str(self._profession_source),
            "-from",
            x1,
            y1,
            x2,
            y2,
            "-to",
            0,
            0,
        )
        image = image.zoom(5, 5).subsample(4, 4)
        self.profession_icon_cache[profession] = image
        return image


class OperatorClassFilter(tk.Frame):
    """Compact main-class rail with an expandable subclass icon matrix."""

    def __init__(
        self,
        parent: tk.Misc,
        app: "BpApplication",
        profession_var: tk.StringVar,
        branch_var: tk.StringVar,
        on_change,
    ):
        super().__init__(parent, bg=PANEL)
        self.app = app
        self.profession_var = profession_var
        self.branch_var = branch_var
        self.on_change = on_change
        self.branch_panel_visible = False
        self._branch_animation_job: str | None = None
        self._branch_layout_job: str | None = None
        self._branch_last_width = 0
        self.main_cells: dict[str, tuple[tk.Frame, tk.Label, tk.Label]] = {}
        self.branch_cells: dict[str, tuple[tk.Frame, tk.Label, tk.Label]] = {}
        self.branch_cell_widths: dict[str, int] = {}
        self.branches_by_profession: dict[str, list[tuple[str, str]]] = {}
        for operator in app.operators.values():
            values = self.branches_by_profession.setdefault(
                operator.profession, []
            )
            pair = (operator.branch, operator.branch_id)
            if pair not in values:
                values.append(pair)
        for values in self.branches_by_profession.values():
            values.sort(key=lambda item: item[0])

        self.main_rail = tk.Frame(self, bg=PANEL)
        self.main_rail.pack(fill="x")
        for profession in ["全部职业"] + list(PROFESSION_ICONS):
            self._build_main_cell(profession)

        self.branch_panel = tk.Frame(
            self,
            bg=SURFACE,
            highlightthickness=0,
            padx=0,
            pady=0,
        )
        self.branch_viewport = tk.Canvas(
            self.branch_panel,
            bg=SURFACE,
            height=0,
            highlightthickness=0,
            bd=0,
        )
        self.branch_viewport.pack(fill="x")
        self.branch_grid = tk.Frame(self.branch_viewport, bg=SURFACE, height=0)
        self.branch_window = self.branch_viewport.create_window(
            0,
            0,
            anchor="nw",
            window=self.branch_grid,
        )
        self.branch_mask = self.branch_viewport.create_rectangle(
            0,
            0,
            0,
            0,
            fill=SURFACE,
            outline=SURFACE,
            state="hidden",
        )
        self._branch_reveal_height = 0.0
        self.bind("<Configure>", self._filter_resized, add="+")
        self.refresh_selection()

    @staticmethod
    def _bind_click(widget: tk.Misc, callback) -> None:
        widget.bind("<Button-1>", callback)
        widget.configure(cursor="hand2")
        for child in widget.winfo_children():
            child.bind("<Button-1>", callback)
            child.configure(cursor="hand2")

    def _build_main_cell(self, profession: str) -> None:
        cell = tk.Frame(
            self.main_rail,
            bg=SURFACE_RAISED,
            width=76,
            height=78,
            highlightthickness=1,
            highlightbackground=LINE,
        )
        cell.pack(side="left", padx=(0, 6))
        cell.pack_propagate(False)
        if profession == "全部职业":
            glyph = "⊞"
            icon_font = ("Segoe UI Symbol", 22)
            title = "全部"
        else:
            glyph = self.app.assets.profession_glyph(profession)
            icon_font = (self.app.assets.branch_font_family, 25)
            title = profession
        icon = tk.Label(
            cell,
            text=glyph,
            font=icon_font,
            fg=MUTED,
            bg=SURFACE_RAISED,
        )
        icon.pack(pady=(7, 0))
        label = tk.Label(
            cell,
            text=title,
            font=("Microsoft YaHei UI", 9, "bold"),
            fg=MUTED,
            bg=SURFACE_RAISED,
        )
        label.pack(pady=(1, 6))
        callback = lambda _event, value=profession: self.select_profession(value)
        self._bind_click(cell, callback)
        cell.bind(
            "<Enter>",
            lambda _event, value=profession: self._set_main_hover(value, True),
        )
        cell.bind(
            "<Leave>",
            lambda _event, value=profession: self._set_main_hover(value, False),
        )
        self.main_cells[profession] = (cell, icon, label)

    def _set_main_hover(self, profession: str, hovering: bool) -> None:
        if self.profession_var.get() == profession:
            return
        color = CONTROL_HOVER if hovering else SURFACE_RAISED
        cell, icon, label = self.main_cells[profession]
        for widget in (cell, icon, label):
            widget.configure(bg=color)

    def select_profession(self, profession: str) -> None:
        same_profession = self.profession_var.get() == profession
        if profession == "全部职业":
            self.profession_var.set(profession)
            self.branch_var.set("全部分支")
            self.hide_branches()
        elif same_profession:
            if self.branch_panel_visible:
                self.hide_branches()
            else:
                self.show_branches(profession)
        else:
            self.profession_var.set(profession)
            self.branch_var.set("全部分支")
            self.show_branches(profession)
        self.refresh_selection()
        self.on_change()

    def show_branches(self, profession: str) -> None:
        self._cancel_branch_animation()
        self._cancel_branch_layout()
        for widget in self.branch_grid.winfo_children():
            widget.destroy()
        self.branch_cells.clear()
        self.branch_cell_widths.clear()
        values = [("全部分支", "")] + self.branches_by_profession.get(
            profession, []
        )
        for branch, branch_id in values:
            cell = tk.Frame(
                self.branch_grid,
                bg=SURFACE_RAISED,
                height=64,
                highlightthickness=1,
                highlightbackground=LINE,
            )
            cell.pack_propagate(False)
            glyph = "□" if branch == "全部分支" else self.app.assets.branch_glyph(
                branch_id
            )
            icon_font = (
                ("Segoe UI Symbol", 18, "bold")
                if branch == "全部分支"
                else (
                    self.app.assets.branch_font_family,
                    24 if profession == "先锋" else 20,
                )
            )
            icon = tk.Label(
                cell,
                text=glyph,
                font=icon_font,
                fg=MUTED,
                bg=SURFACE_RAISED,
            )
            icon.pack(side="left", padx=(10, 5), pady=8)
            title = "全部" if branch == "全部分支" else branch
            label = tk.Label(
                cell,
                text=title,
                font=("Microsoft YaHei UI", 10, "bold"),
                fg=FG,
                bg=SURFACE_RAISED,
                anchor="w",
            )
            label.pack(side="left", padx=(0, 11), pady=8)
            callback = lambda _event, value=branch: self.select_branch(value)
            self._bind_click(cell, callback)
            self.branch_cells[branch] = (cell, icon, label)
            content_width = (
                icon.winfo_reqwidth()
                + label.winfo_reqwidth()
                + 36
            )
            self.branch_cell_widths[branch] = max(
                124,
                min(210, content_width),
            )
        if not self.branch_panel_visible:
            self.branch_panel.pack(fill="x", pady=0)
        self.branch_panel_visible = True
        self.branch_viewport.configure(height=0)
        self.branch_viewport.coords(self.branch_window, 0, 0)
        self._branch_reveal_height = 0.0
        self._branch_layout_job = self.after_idle(
            lambda: self._layout_branch_cells(animate=True)
        )
        self.refresh_selection()

    def hide_branches(self) -> None:
        self._cancel_branch_layout()
        if not self.branch_panel_visible:
            return

        def finish() -> None:
            self.branch_panel.pack_forget()
            self.branch_panel_visible = False
            self.branch_viewport.configure(height=0)
            self.branch_viewport.coords(self.branch_window, 0, 0)
            self.branch_viewport.itemconfigure(self.branch_mask, state="hidden")
            self._branch_reveal_height = 0.0

        self._animate_branch_reveal(
            0,
            duration_ms=130,
            on_complete=finish,
        )

    def _filter_resized(self, event: tk.Event) -> None:
        if not self.branch_panel_visible or abs(event.width - self._branch_last_width) < 4:
            return
        self._cancel_branch_layout()
        self._branch_layout_job = self.after_idle(self._layout_branch_cells)

    def _layout_branch_cells(self, animate: bool = False) -> None:
        self._branch_layout_job = None
        if not self.branch_panel_visible:
            return
        viewport_width = max(320, self.branch_viewport.winfo_width())
        available_width = viewport_width - 16
        if available_width <= 320:
            viewport_width = max(320, self.winfo_width())
            available_width = viewport_width - 16
        self._branch_last_width = self.winfo_width()
        gap = 6
        row_height = 64
        x = 8
        y = 6
        for branch, (cell, _icon, _label) in self.branch_cells.items():
            width = self.branch_cell_widths[branch]
            if x > 8 and x + width > available_width + 8:
                x = 8
                y += row_height + gap
            cell.place(x=x, y=y, width=width, height=row_height)
            x += width + gap
        target_height = y + row_height + 6
        self.branch_grid.configure(
            width=viewport_width,
            height=target_height,
        )
        self.branch_viewport.itemconfigure(
            self.branch_window,
            width=viewport_width,
            height=target_height,
        )
        self.branch_viewport.configure(height=target_height)
        if animate:
            self.branch_viewport.coords(self.branch_window, 0, 0)
            self._branch_reveal_height = 0.0
            self.branch_viewport.coords(
                self.branch_mask,
                0,
                0,
                viewport_width,
                target_height,
            )
            self.branch_viewport.itemconfigure(
                self.branch_mask,
                state="normal",
            )
            self.branch_viewport.tag_raise(self.branch_mask)
            self._animate_branch_reveal(target_height, duration_ms=200)
        else:
            self._cancel_branch_animation()
            self.branch_viewport.coords(self.branch_window, 0, 0)
            self._branch_reveal_height = float(target_height)
            self.branch_viewport.itemconfigure(self.branch_mask, state="hidden")

    def _animate_branch_reveal(
        self,
        target_height: int,
        *,
        duration_ms: int,
        on_complete=None,
    ) -> None:
        self._cancel_branch_animation()
        viewport_height = int(self.branch_viewport.cget("height"))
        window_width = self.branch_viewport.itemcget(
            self.branch_window,
            "width",
        )
        viewport_width = max(1, round(float(window_width)))
        start_height = self._branch_reveal_height
        distance = target_height - start_height
        if distance == 0:
            if on_complete:
                on_complete()
            return
        self.branch_viewport.itemconfigure(self.branch_mask, state="normal")
        self.branch_viewport.tag_raise(self.branch_mask)
        frame_ms = 15
        frames = max(1, round(duration_ms / frame_ms))

        def tick(frame: int) -> None:
            progress = min(1.0, frame / frames)
            if distance > 0:
                eased = 1.0 - (1.0 - progress) ** 3
            else:
                eased = progress**2
            reveal_height = start_height + distance * eased
            self._branch_reveal_height = reveal_height
            self.branch_viewport.coords(
                self.branch_mask,
                0,
                reveal_height,
                viewport_width,
                viewport_height,
            )
            if frame < frames:
                self._branch_animation_job = self.after(
                    frame_ms, lambda: tick(frame + 1)
                )
            else:
                self._branch_animation_job = None
                self._branch_reveal_height = float(target_height)
                if target_height >= viewport_height:
                    self.branch_viewport.itemconfigure(
                        self.branch_mask,
                        state="hidden",
                    )
                if on_complete:
                    on_complete()

        tick(1)

    def _cancel_branch_animation(self) -> None:
        if self._branch_animation_job is not None:
            self.after_cancel(self._branch_animation_job)
            self._branch_animation_job = None

    def _cancel_branch_layout(self) -> None:
        if self._branch_layout_job is not None:
            self.after_cancel(self._branch_layout_job)
            self._branch_layout_job = None

    def select_branch(self, branch: str) -> None:
        self.branch_var.set(branch)
        self.refresh_selection()
        self.on_change()

    def refresh_selection(self) -> None:
        selected_profession = self.profession_var.get()
        for profession, (cell, icon, label) in self.main_cells.items():
            selected = profession == selected_profession
            color = (
                ACCENT
                if profession == "全部职业"
                else PROFESSION_COLORS.get(profession, ACCENT)
            )
            background = CONTROL_SELECTED if selected else SURFACE_RAISED
            cell.configure(
                bg=background,
                highlightbackground=color if selected else LINE,
                highlightthickness=2 if selected else 1,
            )
            icon.configure(bg=background, fg=color if selected else MUTED)
            label.configure(bg=background, fg=FG if selected else MUTED)
        selected_branch = self.branch_var.get()
        accent = PROFESSION_COLORS.get(selected_profession, ACCENT)
        for branch, (cell, icon, label) in self.branch_cells.items():
            selected = branch == selected_branch
            background = CONTROL_SELECTED if selected else SURFACE_RAISED
            cell.configure(
                bg=background,
                highlightbackground=accent if selected else LINE,
                highlightthickness=2 if selected else 1,
            )
            icon.configure(bg=background, fg=accent if selected else MUTED)
            label.configure(bg=background, fg=FG)


class BpApplication(tk.Tk):
    def __init__(self, operators: dict[str, Operator], data_path: Path):
        super().__init__()
        self.operators = operators
        self.data_path = data_path
        self.assets = AssetManager(self, data_path.parent.parent / "assets")
        self.config: MatchConfig | None = None
        self.state: MatchState | None = None
        self._loaded_state_mode = False

        self.title("联锁对抗 BP 助手")
        self._configure_window_icon()
        self._configure_dpi_scaling()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = min(1720, max(1180, int(screen_width * 0.90)))
        height = min(1240, max(800, int(screen_height * 0.96)))
        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(1100, 720)
        self.configure(bg=BG)
        self._configure_style()

        header = tk.Frame(self, bg=HEADER_BG, height=104)
        header.pack(fill="x")
        header.pack_propagate(False)
        brand = tk.Frame(header, bg=HEADER_BG)
        brand.pack(side="left", padx=24, pady=10, fill="y")
        brand_logo = self.assets.logo(64)
        tk.Label(
            brand,
            image=brand_logo,
            bg=HEADER_BG,
            bd=0,
        ).pack(side="left", padx=(0, 12))
        brand_text = tk.Frame(brand, bg=HEADER_BG)
        brand_text.pack(side="left", fill="y")
        tk.Label(
            brand_text,
            text="LINKED OPS",
            font=("Segoe UI", 10, "bold"),
            fg=MUTED,
            bg=HEADER_BG,
        ).pack(anchor="w", pady=(3, 0))
        tk.Label(
            brand_text,
            text="联锁对抗控制台",
            font=("Microsoft YaHei UI", 20, "bold"),
            fg=ACCENT,
            bg=HEADER_BG,
        ).pack(anchor="w", pady=(2, 0))
        self.status_var = tk.StringVar(value=f"本地干员数据：{len(operators)} 名")
        tk.Label(
            header,
            textvariable=self.status_var,
            font=("Microsoft YaHei UI", 10),
            fg=MUTED,
            bg=HEADER_BG,
        ).pack(side="right", padx=24)
        analysis_rail = tk.Frame(self, bg=HEADER_BG, height=3)
        analysis_rail.pack(fill="x")
        for color, weight in ((RED, 2), (ACCENT, 3), (GREEN, 2)):
            segment = tk.Frame(analysis_rail, bg=color, height=3)
            segment.pack(side="left", fill="both", expand=weight)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(8, 12))
        self.setup_tab: SetupTab | None = None
        self.host_ban_tab: HostBanTab | None = None
        self.player_tab: PlayerTab | None = None
        self.auction_tab: AuctionTab | None = None
        self.settlement_tab: SettlementTab | None = None
        self._tab_order = ("setup", "host_ban", "player", "auction", "settlement")
        self._tab_specs = {
            "setup": (SetupTab, "  比赛  "),
            "host_ban": (HostBanTab, "  主持人 Ban  "),
            "player": (PlayerTab, "  选手 Pick  "),
            "auction": (AuctionTab, "  拍卖  "),
            "settlement": (SettlementTab, "  结算  "),
        }
        self._tab_containers: dict[str, ttk.Frame] = {}
        for key in self._tab_order:
            container = ttk.Frame(self.notebook)
            self._tab_containers[key] = container
            self.notebook.add(container, text=self._tab_specs[key][1])
        self.ensure_tab("setup")
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, _event=None) -> None:
        try:
            index = self.notebook.index(self.notebook.select())
        except tk.TclError:
            return
        if 0 <= index < len(self._tab_order):
            self.ensure_tab(self._tab_order[index])

    def ensure_tab(self, key: str):
        attribute = f"{key}_tab"
        current = getattr(self, attribute, None)
        if current is not None:
            return current
        tab_class = self._tab_specs[key][0]
        tab = tab_class(self._tab_containers[key], self)
        tab.pack(fill="both", expand=True)
        setattr(self, attribute, tab)
        if key == "setup" and self.config:
            tab.fill_from_config(self.config)
        elif key == "host_ban" and self.config:
            if self._loaded_state_mode:
                tab.load_from_state()
            else:
                tab.use_config(self.config, reset=True)
        elif key == "player" and self.config:
            tab.use_config(self.config, reset=True)
        elif key == "auction" and self.config:
            if self._loaded_state_mode:
                tab.load_from_state()
            else:
                tab.use_config(self.config)
        elif key == "settlement":
            tab.refresh()
        return tab

    def _configure_window_icon(self) -> None:
        try:
            self.iconphoto(True, self.assets.logo(64))
        except tk.TclError:
            pass
        icon_path = self.assets.root / "ui" / "linked_ops_logo.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(default=str(icon_path))
            except tk.TclError:
                pass

    def _configure_dpi_scaling(self) -> None:
        """Keep text and controls crisp and physically consistent on Windows."""
        try:
            dpi = self.winfo_fpixels("1i")
            if dpi > 0:
                self.tk.call("tk", "scaling", dpi / 72.0)
        except tk.TclError:
            pass

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=("Microsoft YaHei UI", 11))
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("Muted.TLabel", background=BG, foreground=MUTED)
        style.configure("Panel.TLabel", background=PANEL, foreground=FG)
        style.configure("Title.TLabel", background=BG, foreground=FG, font=("Microsoft YaHei UI", 18, "bold"))
        style.configure("CardTitle.TLabel", background=PANEL, foreground=ACCENT, font=("Microsoft YaHei UI", 13, "bold"))
        style.configure(
            "TButton",
            padding=(16, 10),
            background=PANEL_2,
            foreground=FG,
            borderwidth=0,
        )
        style.map(
            "TButton",
            background=[
                ("active", CONTROL_HOVER),
                ("pressed", CONTROL_SELECTED),
                ("disabled", "#151D24"),
            ],
            foreground=[("disabled", "#66727C")],
        )
        style.configure(
            "Accent.TButton",
            background=ACCENT,
            foreground=HEADER_BG,
            font=("Microsoft YaHei UI", 11, "bold"),
        )
        style.map(
            "Accent.TButton",
            background=[("active", ACCENT_HOVER), ("pressed", "#C9963F")],
        )
        style.configure("Blue.TButton", background=BLUE, foreground=HEADER_BG)
        style.configure("Red.TButton", background=RED, foreground=HEADER_BG)
        style.configure(
            "AuctionBlue.TButton",
            background=BLUE,
            foreground=HEADER_BG,
            font=("Microsoft YaHei UI", 16, "bold"),
            padding=(34, 18),
        )
        style.configure(
            "AuctionRed.TButton",
            background=RED,
            foreground=HEADER_BG,
            font=("Microsoft YaHei UI", 16, "bold"),
            padding=(34, 18),
        )
        style.configure("Green.TButton", background=GREEN, foreground=HEADER_BG)
        style.configure(
            "TEntry",
            fieldbackground=SURFACE_RAISED,
            foreground=FG,
            insertcolor=FG,
            bordercolor=LINE,
            lightcolor=LINE,
            darkcolor=LINE,
            padding=8,
        )
        style.map(
            "TEntry",
            bordercolor=[("focus", FOCUS)],
            lightcolor=[("focus", FOCUS)],
            darkcolor=[("focus", FOCUS)],
        )
        style.configure(
            "TCombobox",
            fieldbackground=PANEL_2,
            background=PANEL_2,
            foreground=FG,
            bordercolor=LINE,
            lightcolor=LINE,
            darkcolor=LINE,
            padding=(8, 7),
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", SURFACE_RAISED)],
            foreground=[("readonly", FG)],
            background=[("readonly", SURFACE_RAISED), ("active", CONTROL_HOVER)],
            arrowcolor=[("readonly", MUTED), ("active", ACCENT)],
            bordercolor=[("focus", FOCUS), ("readonly", LINE)],
        )
        style.configure(
            "Modern.Vertical.TScrollbar",
            gripcount=0,
            background="#536A7C",
            darkcolor="#536A7C",
            lightcolor="#536A7C",
            troughcolor="#14202A",
            bordercolor="#14202A",
            arrowcolor="#C4CFD6",
            relief="flat",
            borderwidth=0,
            width=14,
        )
        style.map(
            "Modern.Vertical.TScrollbar",
            background=[("active", "#7890A0"), ("pressed", ACCENT)],
        )
        style.configure(
            "Vertical.TScrollbar",
            gripcount=0,
            background="#536A7C",
            darkcolor="#536A7C",
            lightcolor="#536A7C",
            troughcolor="#14202A",
            bordercolor="#14202A",
            arrowcolor="#C4CFD6",
            relief="flat",
            borderwidth=0,
            width=15,
        )
        style.map(
            "Vertical.TScrollbar",
            background=[("active", "#7890A0"), ("pressed", ACCENT)],
        )
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=FG, rowheight=28)
        style.configure(
            "Operator.Treeview",
            background=SURFACE,
            fieldbackground=SURFACE,
            foreground=FG,
            rowheight=84,
            font=("Microsoft YaHei UI", 11),
            borderwidth=0,
        )
        style.map("Operator.Treeview", background=[("selected", CONTROL_SELECTED)])
        style.configure(
            "AuctionResult.Treeview",
            background=SURFACE,
            fieldbackground=SURFACE,
            foreground=FG,
            rowheight=76,
            font=("Microsoft YaHei UI", 10),
            borderwidth=0,
        )
        style.map(
            "AuctionResult.Treeview", background=[("selected", CONTROL_SELECTED)]
        )
        style.configure(
            "HostBan.Treeview",
            background=SURFACE,
            fieldbackground=SURFACE,
            foreground=FG,
            rowheight=88,
            font=("Microsoft YaHei UI", 12, "bold"),
            borderwidth=0,
        )
        style.map(
            "HostBan.Treeview",
            background=[("selected", CONTROL_SELECTED)],
            foreground=[("selected", FG)],
        )
        style.map("Treeview", background=[("selected", CONTROL_SELECTED)])
        style.configure("Treeview.Heading", background=PANEL_2, foreground=FG, padding=6)
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=PANEL,
            foreground=MUTED,
            padding=(24, 11),
            borderwidth=0,
            font=("Microsoft YaHei UI", 10, "bold"),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", PANEL_2), ("active", CONTROL_HOVER)],
            foreground=[("selected", ACCENT), ("active", FG)],
        )
        style.configure("TCheckbutton", background=BG, foreground=FG)
        style.map("TCheckbutton", background=[("active", BG)])
        style.configure("TLabelframe", background=BG, foreground=FG)
        style.configure("TLabelframe.Label", background=BG, foreground=ACCENT)

    def set_config(self, config: MatchConfig) -> None:
        self.config = config
        self.state = MatchState(config=config)
        self._loaded_state_mode = False
        self.state.host_banned_branches = {
            player: list(config.host_banned_branches[player])
            for player in (PLAYER_A, PLAYER_B)
        }
        self.state.host_banned_operator_ids = {
            player: list(config.host_banned_operator_ids[player])
            for player in (PLAYER_A, PLAYER_B)
        }
        self.state.ban_complete = config.bans_finalized
        if self.host_ban_tab:
            self.host_ban_tab.use_config(config, reset=True)
        if self.player_tab:
            self.player_tab.use_config(config, reset=True)
        if self.auction_tab:
            self.auction_tab.use_config(config)
        if self.settlement_tab:
            self.settlement_tab.refresh()
        self.status_var.set(f"比赛：{config.title} · {config.match_id}")

    def set_state(self, state: MatchState) -> None:
        self.config = state.config
        self.state = state
        self._loaded_state_mode = True
        self.ensure_tab("setup").fill_from_config(state.config)
        if self.host_ban_tab:
            self.host_ban_tab.load_from_state()
        if self.player_tab:
            self.player_tab.use_config(state.config, reset=True)
        if self.auction_tab:
            self.auction_tab.load_from_state()
        if self.settlement_tab:
            self.settlement_tab.refresh()
        self.status_var.set(f"已读取比赛：{state.config.title} · {state.config.match_id}")

    def show_error(self, title: str, exc: Exception) -> None:
        messagebox.showerror(title, str(exc), parent=self)


class SetupTab(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, app: BpApplication):
        super().__init__(parent, padding=0)
        self.app = app
        self.vars = {
            "match_id": tk.StringVar(value=short_match_id()),
            "title": tk.StringVar(value="联锁对抗练习赛"),
            "player_a": tk.StringVar(value="选手 A"),
            "player_b": tk.StringVar(value="选手 B"),
            "rounds": tk.IntVar(value=2),
            "picks": tk.IntVar(value=5),
            "branch_bans": tk.IntVar(value=1),
            "operator_bans": tk.IntVar(value=4),
            "increment": tk.IntVar(value=1),
            "cap": tk.IntVar(value=24),
            "auction_timer": tk.IntVar(value=20),
            "price_low": tk.IntVar(value=2),
            "price_5": tk.IntVar(value=4),
            "price_6": tk.IntVar(value=8),
            "default_bans": tk.BooleanVar(value=False),
        }
        self.global_banned_operator_ids: list[str] = []
        self.global_banned_branches: list[str] = []
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        stage = tk.Frame(self, bg=SURFACE)
        stage.grid(row=0, column=0, sticky="nsew")
        stage.columnconfigure(0, weight=1)
        stage.rowconfigure(1, weight=1)

        toolbar = tk.Frame(stage, bg=SURFACE, height=62)
        toolbar.grid(row=0, column=0, sticky="ew", padx=28, pady=(18, 0))
        tk.Label(
            toolbar,
            text="MATCH CREATION",
            font=("Segoe UI", 10, "bold"),
            fg=MUTED,
            bg=SURFACE,
        ).pack(side="left")
        tk.Button(
            toolbar,
            text="规则参数",
            font=("Microsoft YaHei UI", 10, "bold"),
            fg=FG,
            bg=PANEL_2,
            activeforeground=ACCENT,
            activebackground=CONTROL_HOVER,
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            command=self.open_rules,
        ).pack(side="right")
        tk.Button(
            toolbar,
            text="全局 Ban",
            font=("Microsoft YaHei UI", 10, "bold"),
            fg=FG,
            bg=PANEL_2,
            activeforeground=ACCENT,
            activebackground=CONTROL_HOVER,
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            command=self.open_global_bans,
        ).pack(side="right", padx=(0, 8))

        center = tk.Frame(stage, bg=SURFACE)
        center.grid(row=1, column=0)
        hero = tk.Frame(
            center,
            bg=PANEL,
            highlightbackground=LINE,
            highlightcolor=ACCENT,
            highlightthickness=1,
            padx=44,
            pady=34,
        )
        hero.pack()
        hero_title = tk.Frame(hero, bg=PANEL)
        hero_title.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        tk.Label(
            hero_title,
            image=self.app.assets.logo(96),
            bg=PANEL,
            bd=0,
        ).pack(side="left", padx=(0, 18))
        hero_title_text = tk.Frame(hero_title, bg=PANEL)
        hero_title_text.pack(side="left", anchor="center")
        tk.Label(
            hero_title_text,
            text="联锁对抗 · 创建比赛",
            font=("Microsoft YaHei UI", 28, "bold"),
            fg=FG,
            bg=PANEL,
        ).pack(anchor="w")
        tk.Label(
            hero_title_text,
            text="设定对阵双方，生成本场比赛的唯一配置文件",
            font=("Microsoft YaHei UI", 10),
            fg=MUTED,
            bg=PANEL,
        ).pack(anchor="w", pady=(3, 0))

        self._field(hero, 2, "比赛名称", "title", width=34)
        self._field(hero, 3, "比赛编号", "match_id", width=34)
        player_row = tk.Frame(hero, bg=PANEL)
        player_row.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 4))
        player_row.columnconfigure(0, weight=1)
        player_row.columnconfigure(1, weight=1)
        self._compact_field(player_row, 0, "A 方选手", "player_a", BLUE)
        self._compact_field(player_row, 1, "B 方选手", "player_b", RED)

        self.rule_summary_var = tk.StringVar()
        self.refresh_rule_summary()
        tk.Label(
            hero,
            textvariable=self.rule_summary_var,
            font=("Microsoft YaHei UI", 9),
            fg=MUTED,
            bg=PANEL,
            anchor="w",
        ).grid(row=5, column=0, columnspan=2, sticky="ew", pady=(18, 12))

        actions = tk.Frame(hero, bg=PANEL)
        actions.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(actions, text="创建并应用", style="Accent.TButton", command=self.apply).pack(
            side="left", ipadx=10
        )
        ttk.Button(actions, text="读取比赛配置", command=self.load).pack(
            side="left", padx=8
        )
        ttk.Button(actions, text="读取比赛", command=self.load_match).pack(side="left")
        tk.Label(
            stage,
            text="规则已收纳至右上角设置  ·  比赛编号用于阻止错误文件导入",
            font=("Microsoft YaHei UI", 9),
            fg="#747d89",
            bg=SURFACE,
        ).grid(row=2, column=0, pady=(0, 20))

    def _field(self, parent: tk.Widget, row: int, label: str, key: str, width: int = 28) -> None:
        tk.Label(
            parent,
            text=label,
            font=("Microsoft YaHei UI", 9, "bold"),
            fg=MUTED,
            bg=PANEL,
        ).grid(row=row, column=0, sticky="w", pady=9, padx=(0, 20))
        ttk.Entry(parent, textvariable=self.vars[key], width=width).grid(
            row=row, column=1, sticky="ew", pady=9
        )
        parent.columnconfigure(1, weight=1)

    def _compact_field(
        self, parent: tk.Widget, column: int, label: str, key: str, accent: str
    ) -> None:
        box = tk.Frame(parent, bg=SURFACE_RAISED, padx=13, pady=10)
        box.grid(row=0, column=column, sticky="ew", padx=((0, 6) if column == 0 else (6, 0)))
        tk.Label(
            box,
            text=label,
            font=("Microsoft YaHei UI", 9, "bold"),
            fg=accent,
            bg=SURFACE_RAISED,
        ).pack(anchor="w")
        entry = tk.Entry(
            box,
            textvariable=self.vars[key],
            font=("Microsoft YaHei UI", 12, "bold"),
            fg=FG,
            bg=SURFACE_RAISED,
            insertbackground=FG,
            relief="flat",
            bd=0,
        )
        entry.pack(fill="x", pady=(5, 0))

    def refresh_rule_summary(self) -> None:
        self.rule_summary_var.set(
            f"{self.vars['rounds'].get()} 轮  ·  每轮 {self.vars['picks'].get()} 人  ·  "
            f"Ban {self.vars['branch_bans'].get()} 分支 + {self.vars['operator_bans'].get()} 干员  ·  "
            f"全局 Ban {len(self.global_banned_operator_ids)} 人 / "
            f"{len(self.global_banned_branches)} 分支  ·  封顶 {self.vars['cap'].get()} 点  ·  "
            f"拍卖计时 {self.vars['auction_timer'].get()} 秒"
        )

    def open_global_bans(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("全局 Ban 设置")
        dialog.configure(bg=SURFACE)
        dialog.transient(self.app)
        dialog.resizable(True, True)
        width = min(1240, max(980, self.app.winfo_screenwidth() - 120))
        height = min(860, max(680, self.app.winfo_screenheight() - 120))
        dialog.geometry(f"{width}x{height}")
        dialog.minsize(900, 620)
        dialog.grab_set()

        local_ids = set(self.global_banned_operator_ids)
        local_branches = set(self.global_banned_branches)
        search_var = tk.StringVar()
        profession_var = tk.StringVar(value="全部职业")
        branch_var = tk.StringVar(value="全部分支")
        ban_branch_var = tk.StringVar()
        summary_var = tk.StringVar()

        header = tk.Frame(dialog, bg=SURFACE)
        header.pack(fill="x", padx=24, pady=(20, 12))
        tk.Label(
            header,
            text="全局 Ban",
            font=("Microsoft YaHei UI", 22, "bold"),
            fg=FG,
            bg=SURFACE,
        ).pack(side="left")
        tk.Label(
            header,
            textvariable=summary_var,
            font=("Microsoft YaHei UI", 11),
            fg=ACCENT,
            bg=SURFACE,
        ).pack(side="left", padx=16)
        ttk.Button(
            header,
            text="清空全部",
            command=lambda: clear_all(),
        ).pack(side="right")

        branch_bar = tk.Frame(
            dialog,
            bg=PANEL,
            highlightbackground=LINE,
            highlightthickness=1,
            padx=14,
            pady=10,
        )
        branch_bar.pack(fill="x", padx=24, pady=(0, 10))
        tk.Label(
            branch_bar,
            text="一键禁用整个分支",
            font=("Microsoft YaHei UI", 10, "bold"),
            fg=MUTED,
            bg=PANEL,
        ).pack(side="left")
        branch_icon = tk.Label(
            branch_bar,
            text="◇",
            font=(self.app.assets.branch_font_family, 28),
            fg=ACCENT,
            bg=PANEL,
            width=2,
        )
        branch_icon.pack(side="left", padx=(12, 6))
        branches = operator_values(self.app.operators.values(), "branch")
        ban_branch_combo = ttk.Combobox(
            branch_bar,
            textvariable=ban_branch_var,
            values=branches,
            state="readonly",
            width=22,
        )
        ban_branch_combo.pack(side="left")

        def update_branch_icon(_event: tk.Event | None = None) -> None:
            branch = ban_branch_var.get()
            branch_id = next(
                (
                    operator.branch_id
                    for operator in self.app.operators.values()
                    if operator.branch == branch
                ),
                "",
            )
            branch_icon.configure(text=self.app.assets.branch_glyph(branch_id))

        ban_branch_combo.bind("<<ComboboxSelected>>", update_branch_icon)
        ttk.Button(
            branch_bar,
            text="禁用该分支全部干员",
            style="Accent.TButton",
            command=lambda: ban_entire_branch(),
        ).pack(side="left", padx=8)

        filters = tk.Frame(dialog, bg=SURFACE)
        filters.pack(fill="x", padx=24, pady=(0, 8))
        ttk.Entry(filters, textvariable=search_var, width=24).pack(side="left")
        profession_combo = ttk.Combobox(
            filters,
            textvariable=profession_var,
            values=["全部职业"] + list(PROFESSION_ICONS),
            state="readonly",
            width=12,
        )
        profession_combo.pack(side="left", padx=6)
        branch_filter_combo = ttk.Combobox(
            filters,
            textvariable=branch_var,
            values=["全部分支"] + branches,
            state="readonly",
            width=18,
        )
        branch_filter_combo.pack(side="left")
        tk.Label(
            filters,
            text="全局 Ban 数量不限；双击干员可快速加入或移除",
            fg=MUTED,
            bg=SURFACE,
        ).pack(side="right")

        body = ttk.Panedwindow(dialog, orient="horizontal")
        body.pack(fill="both", expand=True, padx=24)
        available_panel = ttk.LabelFrame(body, text=" 可选干员 ", padding=8)
        selected_panel = ttk.LabelFrame(body, text=" 已全局 Ban ", padding=8)
        for panel in (available_panel, selected_panel):
            panel.columnconfigure(0, weight=1)
            panel.rowconfigure(0, weight=1)
        available_tree = ttk.Treeview(
            available_panel,
            columns=("rarity", "profession", "branch"),
            show="tree headings",
            style="Operator.Treeview",
            selectmode="browse",
            height=2,
        )
        selected_tree = ttk.Treeview(
            selected_panel,
            columns=("profession", "branch"),
            show="tree headings",
            style="Operator.Treeview",
            selectmode="browse",
            height=2,
        )
        for tree in (available_tree, selected_tree):
            tree.heading("#0", text="干员")
            tree.column("#0", width=230, minwidth=170, stretch=True)
        available_tree.heading("rarity", text="星级")
        available_tree.heading("profession", text="职业")
        available_tree.heading("branch", text="分支")
        available_tree.column("rarity", width=62, anchor="center", stretch=False)
        available_tree.column("profession", width=82, anchor="center", stretch=False)
        available_tree.column("branch", width=130, anchor="center", stretch=True)
        selected_tree.heading("profession", text="职业")
        selected_tree.heading("branch", text="分支")
        selected_tree.column("profession", width=82, anchor="center", stretch=False)
        selected_tree.column("branch", width=140, anchor="center", stretch=True)
        for panel, tree in (
            (available_panel, available_tree),
            (selected_panel, selected_tree),
        ):
            scroll = ttk.Scrollbar(panel, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scroll.set)
            tree.grid(row=0, column=0, sticky="nsew")
            scroll.grid(row=0, column=1, sticky="ns")
        body.add(available_panel, weight=3)
        body.add(selected_panel, weight=2)

        def refresh_lists() -> None:
            available_tree.delete(*available_tree.get_children())
            selected_tree.delete(*selected_tree.get_children())
            search = search_var.get().strip().lower()
            rows = sorted(
                self.app.operators.values(),
                key=lambda operator: (
                    -operator.rarity,
                    operator.profession,
                    operator.name,
                ),
            )
            for operator in rows:
                if operator.operator_id in local_ids:
                    selected_tree.insert(
                        "",
                        "end",
                        iid=operator.operator_id,
                        text=f"  {operator.name}",
                        image=self.app.assets.avatar(operator, 80),
                        values=(operator.profession, operator.branch),
                    )
                    continue
                if search and search not in operator.name.lower() and search not in operator.operator_id.lower():
                    continue
                if profession_var.get() != "全部职业" and operator.profession != profession_var.get():
                    continue
                if branch_var.get() != "全部分支" and operator.branch != branch_var.get():
                    continue
                available_tree.insert(
                    "",
                    "end",
                    iid=operator.operator_id,
                    text=f"  {operator.name}",
                    image=self.app.assets.avatar(operator, 80),
                    values=(f"{operator.rarity}★", operator.profession, operator.branch),
                )
            summary_var.set(
                f"{len(local_ids)} 名干员  ·  {len(local_branches)} 个整分支"
            )

        def add_selected() -> None:
            selection = available_tree.selection()
            if selection:
                local_ids.add(selection[0])
                refresh_lists()

        def remove_selected() -> None:
            selection = selected_tree.selection()
            if not selection:
                return
            operator = self.app.operators[selection[0]]
            local_ids.discard(operator.operator_id)
            if operator.branch in local_branches:
                local_branches.discard(operator.branch)
            refresh_lists()

        def ban_entire_branch() -> None:
            branch = ban_branch_var.get()
            if not branch:
                return
            local_branches.add(branch)
            local_ids.update(
                operator.operator_id
                for operator in self.app.operators.values()
                if operator.branch == branch
            )
            refresh_lists()

        def clear_all() -> None:
            local_ids.clear()
            local_branches.clear()
            refresh_lists()

        def save_global_bans() -> None:
            self.global_banned_operator_ids = sorted(local_ids)
            self.global_banned_branches = sorted(local_branches)
            self.refresh_rule_summary()
            dialog.destroy()

        available_tree.bind("<Double-1>", lambda _event: add_selected())
        selected_tree.bind("<Double-1>", lambda _event: remove_selected())
        search_var.trace_add("write", lambda *_args: refresh_lists())
        for widget in (profession_combo, branch_filter_combo):
            widget.bind("<<ComboboxSelected>>", lambda _event: refresh_lists())

        footer = tk.Frame(dialog, bg=SURFACE)
        footer.pack(fill="x", padx=24, pady=(12, 20))
        ttk.Button(footer, text="取消", command=dialog.destroy).pack(side="right")
        ttk.Button(
            footer,
            text="保存全局 Ban",
            style="Accent.TButton",
            command=save_global_bans,
        ).pack(side="right", padx=(0, 8))
        refresh_lists()

    def open_rules(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("规则参数")
        dialog.configure(bg=SURFACE)
        dialog.transient(self.app)
        dialog.resizable(True, True)
        width = min(620, max(520, self.app.winfo_screenwidth() - 80))
        height = min(900, max(660, self.app.winfo_screenheight() - 100))
        dialog.minsize(min(520, width), min(620, height))
        self.app.update_idletasks()
        x = self.app.winfo_rootx() + self.app.winfo_width() - width - 40
        y = self.app.winfo_rooty() + 110
        x = max(0, min(x, self.app.winfo_screenwidth() - width))
        y = max(0, min(y, self.app.winfo_screenheight() - height))
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.grab_set()

        tk.Label(
            dialog,
            text="规则参数",
            font=("Microsoft YaHei UI", 20, "bold"),
            fg=FG,
            bg=SURFACE,
        ).pack(anchor="w", padx=28, pady=(24, 2))
        tk.Label(
            dialog,
            text="作为二级设置保存到本场比赛配置",
            font=("Microsoft YaHei UI", 9),
            fg=MUTED,
            bg=SURFACE,
        ).pack(anchor="w", padx=28, pady=(0, 16))

        scroll_wrap = tk.Frame(dialog, bg=SURFACE)
        scroll_wrap.pack(fill="both", expand=True, padx=22)
        scroll_wrap.columnconfigure(0, weight=1)
        scroll_wrap.rowconfigure(0, weight=1)
        settings_canvas = tk.Canvas(
            scroll_wrap,
            bg=PANEL,
            highlightthickness=0,
            bd=0,
            yscrollincrement=36,
        )
        settings_scroll = ttk.Scrollbar(
            scroll_wrap, orient="vertical", command=settings_canvas.yview
        )
        settings_canvas.configure(yscrollcommand=settings_scroll.set)
        settings_canvas.grid(row=0, column=0, sticky="nsew")
        settings_scroll.grid(row=0, column=1, sticky="ns")
        body = tk.Frame(settings_canvas, bg=PANEL, padx=24, pady=18)
        body_window = settings_canvas.create_window(0, 0, anchor="nw", window=body)
        body.bind(
            "<Configure>",
            lambda _event: settings_canvas.configure(
                scrollregion=settings_canvas.bbox("all")
            ),
        )
        settings_canvas.bind(
            "<Configure>",
            lambda event: settings_canvas.itemconfigure(body_window, width=event.width),
        )
        settings_canvas.bind(
            "<MouseWheel>",
            lambda event: settings_canvas.yview_scroll(
                -max(-5, min(5, int(event.delta / 120))), "units"
            ),
        )
        keys = [
            ("Pick 轮数", "rounds"),
            ("每轮每方 Pick 数", "picks"),
            ("每方分支 Ban 数", "branch_bans"),
            ("每方干员 Ban 数", "operator_bans"),
            ("每次加价", "increment"),
            ("价格上限", "cap"),
            ("拍卖倒计时（秒）", "auction_timer"),
            ("4 星及以下起拍", "price_low"),
            ("5 星起拍", "price_5"),
            ("6 星起拍", "price_6"),
        ]
        local_vars: dict[str, tk.Variable] = {}
        for row, (label, key) in enumerate(keys):
            local = tk.StringVar(value=str(self.vars[key].get()))
            local_vars[key] = local
            tk.Label(
                body,
                text=label,
                font=("Microsoft YaHei UI", 9),
                fg=MUTED,
                bg=PANEL,
            ).grid(row=row, column=0, sticky="w", pady=6)
            ttk.Entry(body, textvariable=local, width=12).grid(
                row=row, column=1, sticky="e", pady=6
            )
        local_default = tk.BooleanVar(value=self.vars["default_bans"].get())
        ttk.Checkbutton(
            body,
            text="启用默认 Ban",
            variable=local_default,
        ).grid(row=len(keys), column=0, columnspan=2, sticky="w", pady=(12, 4))
        body.columnconfigure(0, weight=1)

        def save_and_close() -> None:
            try:
                for _label, key in keys:
                    self.vars[key].set(int(str(local_vars[key].get()).strip()))
                self.vars["default_bans"].set(local_default.get())
                self.make_config()
                self.refresh_rule_summary()
                dialog.destroy()
            except (ValueError, tk.TclError, RuleError) as exc:
                messagebox.showerror("规则无效", str(exc), parent=dialog)

        footer = tk.Frame(dialog, bg=SURFACE)
        footer.pack(fill="x", padx=22, pady=(14, 20))
        ttk.Button(footer, text="取消", command=dialog.destroy).pack(side="right")
        ttk.Button(
            footer, text="保存规则", style="Accent.TButton", command=save_and_close
        ).pack(side="right", padx=(0, 8))

    def make_config(self) -> MatchConfig:
        prices = {
            1: self.vars["price_low"].get(),
            2: self.vars["price_low"].get(),
            3: self.vars["price_low"].get(),
            4: self.vars["price_low"].get(),
            5: self.vars["price_5"].get(),
            6: self.vars["price_6"].get(),
        }
        rules = MatchRules(
            branch_bans_per_player=self.vars["branch_bans"].get(),
            operator_bans_per_player=self.vars["operator_bans"].get(),
            rounds=self.vars["rounds"].get(),
            picks_per_round=self.vars["picks"].get(),
            max_picks_per_round=7,
            min_increment=self.vars["increment"].get(),
            price_cap=self.vars["cap"].get(),
            auction_timer_seconds=self.vars["auction_timer"].get(),
            starting_prices=prices,
            enable_default_bans=self.vars["default_bans"].get(),
        )
        config = MatchConfig(
            match_id=self.vars["match_id"].get().strip(),
            title=self.vars["title"].get().strip(),
            player_a_name=self.vars["player_a"].get().strip(),
            player_b_name=self.vars["player_b"].get().strip(),
            rules=rules,
            global_banned_operator_ids=list(self.global_banned_operator_ids),
            global_banned_branches=list(self.global_banned_branches),
        )
        config.validate()
        return config

    def apply(self) -> None:
        try:
            config = self.make_config()
            if self.app.state and self.app.state.auction_items:
                if not messagebox.askyesno(
                    "替换当前比赛",
                    "当前比赛已有拍卖数据。应用新配置会清空当前进度，是否继续？",
                    parent=self,
                ):
                    return
            self.app.set_config(config)
            messagebox.showinfo(
                "已创建",
                "比赛与全局 Ban 已应用。\n请进入“主持人 Ban”页完成双方 Ban，之后再导出选手配置。",
                parent=self,
            )
        except (RuleError, tk.TclError) as exc:
            self.app.show_error("无法创建比赛", exc)

    def load(self) -> None:
        path = filedialog.askopenfilename(
            parent=self,
            title="读取比赛配置",
            filetypes=[("比赛配置", "*.bpmatch"), ("所有文件", "*.*")],
        )
        if not path:
            return
        try:
            config = load_config(Path(path))
            config.validate()
            self.fill_from_config(config)
            self.app.set_config(config)
            messagebox.showinfo("读取成功", "比赛配置已应用。", parent=self)
        except (RuleError, OSError, ValueError) as exc:
            self.app.show_error("读取失败", exc)

    def load_match(self) -> None:
        path = filedialog.askopenfilename(
            parent=self,
            title="读取比赛",
            filetypes=[("完整比赛存档", "*.bprace"), ("所有文件", "*.*")],
        )
        if not path:
            return
        try:
            state = load_state(Path(path))
            state.config.validate()
            self.app.set_state(state)
        except (RuleError, OSError, ValueError, KeyError) as exc:
            self.app.show_error("读取失败", exc)

    def fill_from_config(self, config: MatchConfig) -> None:
        rules = config.rules
        values = {
            "match_id": config.match_id,
            "title": config.title,
            "player_a": config.player_a_name,
            "player_b": config.player_b_name,
            "rounds": rules.rounds,
            "picks": rules.picks_per_round,
            "branch_bans": rules.branch_bans_per_player,
            "operator_bans": rules.operator_bans_per_player,
            "increment": rules.min_increment,
            "cap": rules.price_cap,
            "auction_timer": rules.auction_timer_seconds,
            "price_low": rules.starting_prices[4],
            "price_5": rules.starting_prices[5],
            "price_6": rules.starting_prices[6],
            "default_bans": rules.enable_default_bans,
        }
        self.global_banned_operator_ids = list(config.global_banned_operator_ids)
        self.global_banned_branches = list(config.global_banned_branches)
        for key, value in values.items():
            self.vars[key].set(value)
        self.refresh_rule_summary()


class HostBanTab(ttk.Frame):
    """主持人使用的公开 Ban 工作台；干员 Ban 按 A、B 顺序交替进行。"""

    def __init__(self, parent: ttk.Notebook, app: BpApplication):
        super().__init__(parent, padding=12)
        self.app = app
        self.search_var = tk.StringVar()
        self.rarity_var = tk.StringVar(value="全部星级")
        self.profession_var = tk.StringVar(value="全部职业")
        self.branch_filter_var = tk.StringVar(value="全部分支")
        self.turn_var = tk.StringVar(value="请先创建或读取比赛")
        self.progress_var = tk.StringVar(value="主持人 Ban 尚未开始")
        self.catalog_count_var = tk.StringVar()
        self.selected_summary_var = tk.StringVar(value="尚未选择干员")
        self.branch_vars = {
            PLAYER_A: tk.StringVar(),
            PLAYER_B: tk.StringVar(),
        }
        self.branch_result_vars = {
            PLAYER_A: tk.StringVar(value="尚未设置分支 Ban"),
            PLAYER_B: tk.StringVar(value="尚未设置分支 Ban"),
        }
        self.branch_icon_labels: dict[str, tk.Label] = {}
        self.ban_trees: dict[str, ttk.Treeview] = {}
        self.ban_count_vars = {
            PLAYER_A: tk.StringVar(value="0 名"),
            PLAYER_B: tk.StringVar(value="0 名"),
        }
        self.ban_history: list[tuple[str, str]] = []
        self.filtered_ids: list[str] = []
        self.selected_operator_id: str | None = None
        self.card_frames: dict[str, int] = {}
        self.card_columns = 4
        self.card_width = 168.0
        self.card_row_height = 196
        self.visible_row_range = (-1, -1)
        self._catalog_refresh_job: str | None = None
        self._catalog_render_job: str | None = None
        self._catalog_scroll_job: str | None = None
        self._catalog_scroll_velocity = 0.0

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = tk.Frame(self, bg=BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        tk.Label(
            header,
            text="主持人 BAN",
            font=("Microsoft YaHei UI", 19, "bold"),
            fg=FG,
            bg=BG,
        ).pack(side="left")
        tk.Label(
            header,
            textvariable=self.progress_var,
            font=("Microsoft YaHei UI", 9),
            fg=MUTED,
            bg=BG,
        ).pack(side="left", padx=14)
        ttk.Button(
            header,
            text="确认 Ban 完成",
            style="Green.TButton",
            command=self.confirm_ban,
        ).pack(side="right")
        ttk.Button(
            header,
            text="导出选手配置",
            style="Accent.TButton",
            command=self.export_player_config,
        ).pack(side="right", padx=(0, 8))
        ttk.Button(
            header,
            text="撤销上一步",
            command=self.undo_last,
        ).pack(side="right", padx=(0, 8))

        filters = tk.Frame(
            self,
            bg=PANEL,
            highlightbackground=LINE,
            highlightthickness=1,
            padx=12,
            pady=9,
        )
        filters.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        filter_controls = tk.Frame(filters, bg=PANEL)
        filter_controls.pack(fill="x", pady=(0, 8))
        tk.Label(
            filter_controls,
            text="SEARCH",
            font=("Segoe UI", 9, "bold"),
            fg=MUTED,
            bg=PANEL,
        ).pack(side="left")
        ttk.Entry(filter_controls, textvariable=self.search_var, width=24).pack(
            side="left", padx=(7, 10)
        )
        rarity = ttk.Combobox(
            filter_controls,
            textvariable=self.rarity_var,
            values=["全部星级", "6 星", "5 星", "4 星及以下"],
            state="readonly",
            width=11,
        )
        rarity.pack(side="left", padx=4)
        rarity.bind("<<ComboboxSelected>>", lambda _event: self.refresh_catalog())
        self.search_var.trace_add(
            "write", lambda *_args: self.schedule_catalog_refresh()
        )
        tk.Label(
            filter_controls,
            textvariable=self.catalog_count_var,
            fg=MUTED,
            bg=PANEL,
            font=("Microsoft YaHei UI", 9),
        ).pack(side="right")
        self.class_filter = OperatorClassFilter(
            filters,
            app,
            self.profession_var,
            self.branch_filter_var,
            self.refresh_catalog,
        )
        self.class_filter.pack(fill="x")

        content = tk.PanedWindow(
            self,
            orient="horizontal",
            bg=LINE,
            sashwidth=7,
            sashrelief="flat",
            bd=0,
            relief="flat",
        )
        content.grid(row=2, column=0, sticky="nsew")

        catalog_panel = tk.Frame(
            content,
            bg=PANEL,
            highlightbackground=LINE,
            highlightthickness=1,
        )
        catalog_header = tk.Frame(catalog_panel, bg=PANEL, padx=12, pady=10)
        catalog_header.pack(fill="x")
        tk.Label(
            catalog_header,
            text="干员档案",
            font=("Microsoft YaHei UI", 16, "bold"),
            fg=FG,
            bg=PANEL,
        ).pack(side="left")
        tk.Label(
            catalog_header,
            text="单击选择 · 双击执行当前方 Ban",
            font=("Microsoft YaHei UI", 9),
            fg=MUTED,
            bg=PANEL,
        ).pack(side="right")
        canvas_wrap = tk.Frame(catalog_panel, bg=PANEL)
        canvas_wrap.pack(fill="both", expand=True, padx=(8, 5))
        self.catalog_canvas = tk.Canvas(
            canvas_wrap,
            bg=PANEL,
            highlightthickness=0,
            bd=0,
            yscrollincrement=1,
        )
        self.catalog_scroll = ttk.Scrollbar(
            canvas_wrap,
            orient="vertical",
            command=self._catalog_yview,
            style="Modern.Vertical.TScrollbar",
        )
        self.catalog_canvas.configure(
            yscrollcommand=self._catalog_scroll_changed
        )
        self.catalog_canvas.pack(side="left", fill="both", expand=True)
        self.catalog_scroll.pack(side="right", fill="y", padx=(4, 0))
        self.catalog_canvas.bind("<Configure>", self._catalog_resized)
        self.catalog_canvas.bind("<MouseWheel>", self._smooth_catalog_mousewheel)

        catalog_footer = tk.Frame(catalog_panel, bg=SURFACE, padx=10, pady=9)
        catalog_footer.pack(fill="x", padx=8, pady=8)
        tk.Label(
            catalog_footer,
            textvariable=self.selected_summary_var,
            font=("Microsoft YaHei UI", 9),
            fg=FG,
            bg=SURFACE,
            anchor="w",
        ).pack(side="left", fill="x", expand=True)
        tk.Button(
            catalog_footer,
            text="BAN 当前选中干员",
            command=self.ban_selected,
            bg=ACCENT,
            fg=HEADER_BG,
            activebackground=ACCENT_HOVER,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Microsoft YaHei UI", 10, "bold"),
            padx=14,
            pady=8,
        ).pack(side="right")
        content.add(catalog_panel, minsize=560, stretch="always")

        board = tk.Frame(
            content,
            bg=PANEL,
            highlightbackground=LINE,
            highlightthickness=1,
            padx=12,
            pady=10,
        )
        board.columnconfigure(0, weight=1, uniform="host-ban-sides")
        board.columnconfigure(1, weight=1, uniform="host-ban-sides")
        board.rowconfigure(3, weight=1)
        tk.Label(
            board,
            text="主持人 BAN 看板",
            font=("Microsoft YaHei UI", 17, "bold"),
            fg=FG,
            bg=PANEL,
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            board,
            textvariable=self.turn_var,
            font=("Microsoft YaHei UI", 12, "bold"),
            fg=ACCENT,
            bg=PANEL,
        ).grid(row=0, column=1, sticky="e")

        branch_values = operator_values(app.operators.values(), "branch")
        for column, (player, color, title) in enumerate(
            (
                (PLAYER_A, BLUE, "蓝方分支 BAN"),
                (PLAYER_B, RED, "红方分支 BAN"),
            )
        ):
            branch_panel = tk.Frame(
                board,
                bg=SURFACE,
                highlightbackground=color,
                highlightthickness=1,
                padx=9,
                pady=8,
            )
            branch_panel.grid(
                row=1,
                column=column,
                sticky="nsew",
                padx=((0, 5) if column == 0 else (5, 0)),
                pady=(10, 8),
            )
            branch_panel.columnconfigure(1, weight=1)
            icon = tk.Label(
                branch_panel,
                text="◇",
                font=(self.app.assets.branch_font_family, 28),
                fg=color,
                bg=SURFACE,
                width=2,
            )
            icon.grid(row=0, column=0, rowspan=3, padx=(0, 6))
            self.branch_icon_labels[player] = icon
            tk.Label(
                branch_panel,
                text=title,
                font=("Microsoft YaHei UI", 9, "bold"),
                fg=color,
                bg=SURFACE,
                anchor="w",
            ).grid(row=0, column=1, columnspan=2, sticky="ew")
            ttk.Combobox(
                branch_panel,
                textvariable=self.branch_vars[player],
                values=branch_values,
                state="readonly",
                width=11,
            ).grid(row=1, column=1, sticky="ew", pady=(5, 0))
            ttk.Button(
                branch_panel,
                text="设置",
                command=lambda value=player: self.add_branch_ban(value),
            ).grid(row=1, column=2, padx=(6, 0), pady=(5, 0))
            tk.Label(
                branch_panel,
                textvariable=self.branch_result_vars[player],
                font=("Microsoft YaHei UI", 9, "bold"),
                fg=FG,
                bg=SURFACE,
                anchor="w",
            ).grid(row=2, column=1, columnspan=2, sticky="ew", pady=(5, 0))

            ban_panel = tk.Frame(
                board,
                bg=SURFACE,
                highlightbackground=color,
                highlightthickness=2,
                padx=7,
                pady=7,
            )
            ban_panel.grid(
                row=3,
                column=column,
                sticky="nsew",
                padx=((0, 5) if column == 0 else (5, 0)),
            )
            ban_panel.columnconfigure(0, weight=1)
            ban_panel.rowconfigure(1, weight=1)
            panel_head = tk.Frame(ban_panel, bg=SURFACE)
            panel_head.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
            tk.Label(
                panel_head,
                text="蓝方 BAN" if player == PLAYER_A else "红方 BAN",
                font=("Microsoft YaHei UI", 13, "bold"),
                fg=color,
                bg=SURFACE,
            ).pack(side="left")
            tk.Label(
                panel_head,
                textvariable=self.ban_count_vars[player],
                font=("Microsoft YaHei UI", 10),
                fg=MUTED,
                bg=SURFACE,
            ).pack(side="right")
            tree = ttk.Treeview(
                ban_panel,
                show="tree",
                selectmode="browse",
                style="HostBan.Treeview",
            )
            tree.column("#0", width=245, minwidth=150, stretch=True)
            tree.grid(row=1, column=0, sticky="nsew")
            for rarity_value, (
                background,
                foreground,
            ) in HOST_RARITY_COLORS.items():
                tree.tag_configure(
                    f"rarity-{rarity_value}",
                    background=background,
                    foreground=foreground,
                    font=("Microsoft YaHei UI", 12, "bold"),
                )
            scroll = ttk.Scrollbar(
                ban_panel,
                orient="vertical",
                command=tree.yview,
                style="Modern.Vertical.TScrollbar",
            )
            tree.configure(yscrollcommand=scroll.set)
            scroll.grid(row=1, column=1, sticky="ns")
            self.ban_trees[player] = tree
        content.add(board, minsize=520, stretch="always")
        self.after_idle(
            lambda: content.sash_place(0, int(self.winfo_width() * 0.52), 0)
        )
        self.refresh_catalog()
        self.refresh()

    def use_config(self, _config: MatchConfig, reset: bool = False) -> None:
        if reset:
            self.ban_history.clear()
        self.refresh_catalog()
        self.refresh()

    def load_from_state(self) -> None:
        self.ban_history.clear()
        self.refresh_catalog()
        self.refresh()

    def schedule_catalog_refresh(self) -> None:
        if self._catalog_refresh_job:
            self.after_cancel(self._catalog_refresh_job)
        self._catalog_refresh_job = self.after(120, self._run_catalog_refresh)

    def _run_catalog_refresh(self) -> None:
        self._catalog_refresh_job = None
        self.refresh_catalog()

    def refresh_catalog(self) -> None:
        if not hasattr(self, "catalog_canvas"):
            return
        search = self.search_var.get().strip().lower()
        rows = []
        for operator in self.app.operators.values():
            if search and search not in operator.name.lower() and search not in operator.operator_id.lower():
                continue
            if self.rarity_var.get() == "6 星" and operator.rarity != 6:
                continue
            if self.rarity_var.get() == "5 星" and operator.rarity != 5:
                continue
            if self.rarity_var.get() == "4 星及以下" and operator.rarity > 4:
                continue
            if self.profession_var.get() != "全部职业" and operator.profession != self.profession_var.get():
                continue
            if (
                self.branch_filter_var.get() != "全部分支"
                and operator.branch != self.branch_filter_var.get()
            ):
                continue
            rows.append(operator)
        rows.sort(key=lambda operator: (-operator.rarity, operator.profession, operator.name))
        self.filtered_ids = [operator.operator_id for operator in rows]
        self.catalog_count_var.set(
            f"显示 {len(self.filtered_ids)} / {len(self.app.operators)} 名"
        )
        self._update_catalog_scrollregion()
        self._schedule_catalog_render(force=True)

    def _catalog_status(self, operator: Operator) -> tuple[str, str, str]:
        if self.app.config and (
            operator.operator_id in self.app.config.global_banned_operator_ids
            or operator.branch in self.app.config.global_banned_branches
        ):
            return "全局 BAN", "#30343a", "#858b94"
        if self.app.state:
            if operator.operator_id in self.app.state.host_banned_operator_ids.get(
                PLAYER_A, []
            ):
                return "蓝方 BAN", "#26384a", BLUE
            if operator.operator_id in self.app.state.host_banned_operator_ids.get(
                PLAYER_B, []
            ):
                return "红方 BAN", "#472f33", RED
        return "", SURFACE_RAISED, LINE

    def _catalog_yview(self, *args) -> None:
        self.catalog_canvas.yview(*args)
        self._schedule_catalog_render()

    def _catalog_scroll_changed(self, first: str, last: str) -> None:
        self.catalog_scroll.set(first, last)
        self._schedule_catalog_render()

    def _smooth_catalog_mousewheel(self, event: tk.Event) -> str:
        steps = -event.delta / 120 if event.delta else 0
        self._catalog_scroll_velocity += steps * 105
        self._catalog_scroll_velocity = max(
            -480.0, min(480.0, self._catalog_scroll_velocity)
        )
        if self._catalog_scroll_job is None:
            self._catalog_scroll_job = self.after(0, self._animate_catalog_scroll)
        return "break"

    def _animate_catalog_scroll(self) -> None:
        self._catalog_scroll_job = None
        region = str(self.catalog_canvas.cget("scrollregion")).split()
        if len(region) < 4:
            self._catalog_scroll_velocity = 0.0
            return
        total_height = max(1.0, float(region[3]))
        viewport = max(1.0, float(self.catalog_canvas.winfo_height()))
        maximum = max(0.0, total_height - viewport)
        current = max(0.0, float(self.catalog_canvas.canvasy(0)))
        step = self._catalog_scroll_velocity * 0.24
        target = max(0.0, min(maximum, current + step))
        if maximum > 0:
            self.catalog_canvas.yview_moveto(target / total_height)
        self._catalog_scroll_velocity *= 0.72
        self._schedule_catalog_render()
        if (
            abs(self._catalog_scroll_velocity) >= 0.7
            and target not in (0.0, maximum)
        ):
            self._catalog_scroll_job = self.after(16, self._animate_catalog_scroll)
        else:
            self._catalog_scroll_velocity = 0.0

    def _catalog_resized(self, event: tk.Event) -> None:
        width = max(1, event.width)
        columns = max(3, width // 154)
        card_width = (width - 8 * (columns + 1)) / columns
        avatar_size = 106 if card_width >= 158 else 94
        row_height = avatar_size + 76
        changed = (
            columns != self.card_columns
            or abs(card_width - self.card_width) > 1
            or row_height != self.card_row_height
        )
        self.card_columns = columns
        self.card_width = card_width
        self.card_row_height = row_height
        if changed:
            self._update_catalog_scrollregion()
            self._schedule_catalog_render(force=True)

    def _update_catalog_scrollregion(self) -> None:
        columns = max(3, self.card_columns)
        rows = math.ceil(len(self.filtered_ids) / columns) if self.filtered_ids else 0
        total_height = max(
            self.catalog_canvas.winfo_height(),
            rows * self.card_row_height + 8,
        )
        self.catalog_canvas.configure(
            scrollregion=(
                0,
                0,
                max(1, self.catalog_canvas.winfo_width()),
                total_height,
            )
        )

    def _schedule_catalog_render(self, force: bool = False) -> None:
        if force:
            self.visible_row_range = (-1, -1)
        if self._catalog_render_job is None:
            self._catalog_render_job = self.after_idle(
                self._render_visible_catalog
            )

    def _render_visible_catalog(self) -> None:
        self._catalog_render_job = None
        if not self.filtered_ids or self.card_columns < 1:
            self.catalog_canvas.delete("host-card")
            self.card_frames.clear()
            if not self.filtered_ids:
                self.catalog_canvas.create_text(
                    max(1, self.catalog_canvas.winfo_width()) // 2,
                    100,
                    text="没有符合当前筛选条件的干员",
                    fill=MUTED,
                    font=("Microsoft YaHei UI", 11),
                    tags=("host-card",),
                )
            return
        top = max(0.0, self.catalog_canvas.canvasy(0))
        bottom = top + max(1, self.catalog_canvas.winfo_height())
        first_row = max(0, int(top // self.card_row_height) - 1)
        last_row = min(
            math.ceil(len(self.filtered_ids) / self.card_columns),
            int(bottom // self.card_row_height) + 2,
        )
        row_range = (first_row, last_row)
        if row_range == self.visible_row_range:
            return
        self.visible_row_range = row_range
        self.catalog_canvas.delete("host-card")
        self.card_frames.clear()
        start = first_row * self.card_columns
        end = min(len(self.filtered_ids), last_row * self.card_columns)
        for index in range(start, end):
            operator = self.app.operators[self.filtered_ids[index]]
            row, column = divmod(index, self.card_columns)
            self._draw_catalog_card(operator, row, column)

    def _draw_catalog_card(
        self,
        operator: Operator,
        row: int,
        column: int,
    ) -> None:
        status, fill, border = self._catalog_status(operator)
        selected = operator.operator_id == self.selected_operator_id
        if selected:
            border = ACCENT
        gap = 8
        x1 = gap + column * (self.card_width + gap)
        y1 = gap + row * self.card_row_height
        x2 = x1 + self.card_width
        y2 = y1 + self.card_row_height - gap
        tag = f"host-operator::{operator.operator_id}"
        tags = ("host-card", tag)
        rectangle = self.catalog_canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill=fill,
            outline=border,
            width=3 if selected else 2 if status else 1,
            tags=tags,
        )
        self.card_frames[operator.operator_id] = rectangle
        avatar_size = 106 if self.card_width >= 158 else 94
        self.catalog_canvas.create_image(
            (x1 + x2) / 2,
            y1 + 5,
            image=self.app.assets.avatar(operator, avatar_size),
            anchor="n",
            tags=tags,
        )
        if status:
            badge_color = (
                "#858b94"
                if status == "全局 BAN"
                else BLUE
                if status == "蓝方 BAN"
                else RED
            )
            badge_width = 72
            self.catalog_canvas.create_rectangle(
                x2 - badge_width - 4,
                y1 + 4,
                x2 - 4,
                y1 + 28,
                fill=badge_color,
                outline="",
                tags=tags,
            )
            self.catalog_canvas.create_text(
                x2 - badge_width / 2 - 4,
                y1 + 16,
                text=status,
                fill="#11151a",
                font=("Microsoft YaHei UI", 8, "bold"),
                tags=tags,
            )
        name_size = card_operator_name_size(operator.name, 10, 9, 8)
        draw_shadowed_card_name(
            self.catalog_canvas,
            (x1 + x2) / 2,
            y2 - 31,
            text=card_operator_name(operator.name),
            font=("Microsoft YaHei UI", name_size, "bold"),
            fill=FG,
            anchor="s",
            tags=tags,
        )
        self.catalog_canvas.create_text(
            (x1 + x2) / 2,
            y2 - 8,
            text=operator.branch,
            fill=PROFESSION_COLORS.get(operator.profession, MUTED),
            font=("Microsoft YaHei UI", 8),
            anchor="s",
            width=max(70, self.card_width - 12),
            tags=tags,
        )
        self.catalog_canvas.tag_bind(
            tag,
            "<Button-1>",
            lambda _event, oid=operator.operator_id: self.select_catalog_operator(
                oid
            ),
        )
        self.catalog_canvas.tag_bind(
            tag,
            "<Double-Button-1>",
            lambda _event, oid=operator.operator_id: self.ban_operator_by_id(oid),
        )

    def select_catalog_operator(self, operator_id: str) -> None:
        old_id = self.selected_operator_id
        self.selected_operator_id = operator_id
        operator = self.app.operators[operator_id]
        self.selected_summary_var.set(
            f"已选择：{operator.name} · {operator.rarity}★ · "
            f"{operator.profession} / {operator.branch}"
        )
        if old_id and old_id in self.card_frames:
            old_operator = self.app.operators[old_id]
            old_status, _fill, old_border = self._catalog_status(old_operator)
            self.catalog_canvas.itemconfigure(
                self.card_frames[old_id],
                outline=old_border,
                width=2 if old_status else 1,
            )
        if operator_id in self.card_frames:
            self.catalog_canvas.itemconfigure(
                self.card_frames[operator_id],
                outline=ACCENT,
                width=3,
            )

    def add_branch_ban(self, player: str) -> None:
        if not self.app.state:
            messagebox.showwarning("需要比赛", "请先创建或读取比赛。", parent=self)
            return
        if self.app.state.ban_complete:
            messagebox.showinfo(
                "Ban 已确认", "已确认的 Ban 不能直接修改，请先撤销干员 Ban。", parent=self
            )
            return
        branch = self.branch_vars[player].get()
        if not branch:
            return
        if branch in self.app.state.config.global_banned_branches:
            messagebox.showinfo(
                "已经全局禁用",
                "该分支已经在赛前全局 Ban，无需占用主持人 Ban 位。",
                parent=self,
            )
            return
        values = self.app.state.host_banned_branches[player]
        limit = self.app.state.config.rules.branch_bans_per_player
        if branch in values:
            return
        if len(values) >= limit:
            if limit == 1:
                values[:] = [branch]
            else:
                messagebox.showwarning(
                    "数量已满", f"{player} 方最多 Ban {limit} 个分支。", parent=self
                )
                return
        else:
            values.append(branch)
        self.app.state.ban_complete = False
        self.refresh()

    def ban_selected(self) -> None:
        if not self.selected_operator_id:
            return
        self.ban_operator_by_id(self.selected_operator_id)

    def ban_operator_by_id(self, operator_id: str) -> None:
        if not self.app.state:
            messagebox.showwarning("需要比赛", "请先创建或读取比赛。", parent=self)
            return
        state = self.app.state
        if state.ban_complete:
            messagebox.showinfo(
                "Ban 已确认", "如需修改，请先撤销上一步。", parent=self
            )
            return
        operator = self.app.operators.get(operator_id)
        if not operator:
            return
        if (
            operator_id in state.config.global_banned_operator_ids
            or operator.branch in state.config.global_banned_branches
        ):
            messagebox.showinfo(
                "已被全局禁用",
                "该干员已在赛前全局 Ban 中，不能再次占用主持人 Ban 位。",
                parent=self,
            )
            return
        player = state.ban_turn
        limit = state.config.rules.operator_bans_per_player
        if len(state.host_banned_operator_ids[player]) >= limit:
            player = PLAYER_B if player == PLAYER_A else PLAYER_A
            state.ban_turn = player
        if any(
            operator_id in state.host_banned_operator_ids[value]
            for value in (PLAYER_A, PLAYER_B)
        ):
            return
        if len(state.host_banned_operator_ids[player]) >= limit:
            messagebox.showinfo("Ban 已满", "双方干员 Ban 均已完成。", parent=self)
            return
        state.host_banned_operator_ids[player].append(operator_id)
        self.ban_history.append((player, operator_id))
        other = PLAYER_B if player == PLAYER_A else PLAYER_A
        state.ban_turn = (
            other
            if len(state.host_banned_operator_ids[other]) < limit
            else player
        )
        self.refresh()
        self._schedule_catalog_render(force=True)

    def undo_last(self) -> None:
        if not self.app.state:
            return
        if self.ban_history:
            player, operator_id = self.ban_history.pop()
        else:
            player = next(
                (
                    value
                    for value in (PLAYER_B, PLAYER_A)
                    if self.app.state.host_banned_operator_ids[value]
                ),
                "",
            )
            if not player:
                return
            operator_id = self.app.state.host_banned_operator_ids[player][-1]
        values = self.app.state.host_banned_operator_ids[player]
        if operator_id in values:
            values.remove(operator_id)
        self.app.state.ban_turn = player
        self.app.state.ban_complete = False
        self.refresh_catalog()
        self.refresh()

    def confirm_ban(self) -> None:
        try:
            if not self.app.state:
                raise RuleError("请先创建或读取比赛")
            state = self.app.state
            rules = state.config.rules
            for player in (PLAYER_A, PLAYER_B):
                if len(state.host_banned_branches[player]) != rules.branch_bans_per_player:
                    raise RuleError(
                        f"{player} 方需要完成 {rules.branch_bans_per_player} 个分支 Ban"
                    )
                if len(state.host_banned_operator_ids[player]) != rules.operator_bans_per_player:
                    raise RuleError(
                        f"{player} 方需要完成 {rules.operator_bans_per_player} 名干员 Ban"
                    )
            state.ban_complete = True
            state.config.host_banned_branches = {
                player: list(state.host_banned_branches[player])
                for player in (PLAYER_A, PLAYER_B)
            }
            state.config.host_banned_operator_ids = {
                player: list(state.host_banned_operator_ids[player])
                for player in (PLAYER_A, PLAYER_B)
            }
            state.config.bans_finalized = True
            self.refresh()
            player_tab = self.app.ensure_tab("player")
            player_tab.sync_host_bans()
            player_tab.refresh_selected_list()
            player_tab.refresh_summary()
            player_tab.render_pool_page()
            messagebox.showinfo(
                "Ban 已确认",
                "双方 Ban 结果已锁定，选手可进入 Pick 页面。",
                parent=self,
            )
        except RuleError as exc:
            self.app.show_error("无法确认 Ban", exc)

    def export_player_config(self) -> None:
        try:
            if not self.app.state or not self.app.state.ban_complete:
                raise RuleError("请先完成并确认双方主持人 Ban")
            state = self.app.state
            config = state.config
            config.host_banned_branches = {
                player: list(state.host_banned_branches[player])
                for player in (PLAYER_A, PLAYER_B)
            }
            config.host_banned_operator_ids = {
                player: list(state.host_banned_operator_ids[player])
                for player in (PLAYER_A, PLAYER_B)
            }
            config.bans_finalized = True
            config.validate()
            path = filedialog.asksaveasfilename(
                parent=self,
                title="导出含完整 Ban 的选手配置",
                defaultextension=".bpmatch",
                initialfile=(
                    f"{safe_file_name(config.title)}_{config.match_id}_选手配置.bpmatch"
                ),
                filetypes=[("比赛配置", "*.bpmatch"), ("所有文件", "*.*")],
            )
            if path:
                save_config(Path(path), config)
                messagebox.showinfo(
                    "导出成功",
                    "已导出选手配置，文件包含：\n"
                    "• 全局 Ban 干员与整分支\n"
                    "• A、B 双方主持人干员 Ban\n"
                    "• A、B 双方主持人分支 Ban\n\n"
                    f"{path}",
                    parent=self,
                )
        except (RuleError, OSError) as exc:
            self.app.show_error("无法导出选手配置", exc)

    def refresh(self) -> None:
        if not self.app.state:
            self.turn_var.set("请先创建或读取比赛")
            self.progress_var.set("主持人 Ban 尚未开始")
            for player in (PLAYER_A, PLAYER_B):
                tree = self.ban_trees[player]
                tree.delete(*tree.get_children())
                self.ban_count_vars[player].set("0 名")
            self._schedule_catalog_render(force=True)
            return
        state = self.app.state
        rules = state.config.rules
        for player in (PLAYER_A, PLAYER_B):
            values = state.host_banned_operator_ids[player]
            tree = self.ban_trees[player]
            tree.delete(*tree.get_children())
            for operator_id in values:
                operator = self.app.operators.get(operator_id)
                if operator:
                    tree.insert(
                        "",
                        "end",
                        iid=operator_id,
                        text=f"  {operator.name}",
                        image=self.app.assets.avatar(operator, 72),
                        tags=(
                            f"rarity-{max(1, min(6, operator.rarity))}",
                        ),
                    )
            self.ban_count_vars[player].set(f"{len(values)} 名")
            branches = state.host_banned_branches[player]
            self.branch_result_vars[player].set(
                "、".join(branches) if branches else "尚未设置分支 Ban"
            )
            branch_id = ""
            if branches:
                branch_id = next(
                    (
                        operator.branch_id
                        for operator in self.app.operators.values()
                        if operator.branch == branches[0]
                    ),
                    "",
                )
            self.branch_icon_labels[player].configure(
                text=self.app.assets.branch_glyph(branch_id)
            )
        if state.ban_complete:
            self.turn_var.set("双方 Ban 已确认")
        else:
            color_name = "蓝方" if state.ban_turn == PLAYER_A else "红方"
            self.turn_var.set(f"当前轮到：{state.ban_turn} 方（{color_name}）Ban 干员")
        self.progress_var.set(
            f"全局 Ban {len(state.config.global_banned_operator_ids)} 人 / "
            f"{len(state.config.global_banned_branches)} 分支  ·  "
            + "  |  ".join(
                f"{player} 方 {len(state.host_banned_operator_ids[player])}/{rules.operator_bans_per_player}"
                for player in (PLAYER_A, PLAYER_B)
            )
        )
        self._schedule_catalog_render(force=True)


class PlayerTab(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, app: BpApplication):
        super().__init__(parent, padding=14)
        self.app = app
        self.selected: dict[str, list[str]] = {"ban": []}
        self.branch_bans: list[str] = []
        self.filtered_ids: list[str] = []
        self.selected_operator_id: str | None = None
        self.card_columns = 5
        self.card_frames: dict[str, int] = {}
        self.selected_branch_index: int | None = None
        self.branch_by_name = {
            operator.branch: operator.branch_id for operator in app.operators.values()
        }
        self.profession_buttons: dict[str, tk.Button] = {}
        self.player_buttons: dict[str, tk.Button] = {}
        self.player_var = tk.StringVar(value=PLAYER_A)
        self.config_label = tk.StringVar(value="尚未读取比赛配置")
        self.search_var = tk.StringVar()
        self.rarity_var = tk.StringVar(value="全部星级")
        self.profession_var = tk.StringVar(value="全部职业")
        self.branch_filter_var = tk.StringVar(value="全部分支")
        self.target_var = tk.StringVar(value="第 1 轮 Pick")
        self.export_round_var = tk.StringVar(value="第 1 轮")
        self.branch_pick_var = tk.StringVar()
        self.summary_var = tk.StringVar()
        self.pool_count_var = tk.StringVar()
        self._pool_refresh_job: str | None = None
        self._pool_scroll_job: str | None = None
        self._pool_scroll_velocity = 0.0

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        top = tk.Frame(self, bg=BG)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(top, text="读取比赛配置", command=self.load_config_file).pack(side="left")
        tk.Label(
            top,
            textvariable=self.config_label,
            font=("Microsoft YaHei UI", 12),
            fg=MUTED,
            bg=BG,
        ).pack(side="left", padx=12)
        tk.Label(
            top,
            text="当前身份",
            font=("Microsoft YaHei UI", 11, "bold"),
            fg=MUTED,
            bg=BG,
        ).pack(side="right", padx=(12, 6))
        player_switch = tk.Frame(top, bg=PANEL_2)
        player_switch.pack(side="right")
        for player, color in ((PLAYER_A, BLUE), (PLAYER_B, RED)):
            player_button = tk.Button(
                player_switch,
                text=player,
                font=("Segoe UI", 12, "bold"),
                width=5,
                fg=color,
                bg=PANEL_2,
                activeforeground="#111",
                activebackground=color,
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda value=player: self.set_player(value),
            )
            player_button.pack(side="left", padx=1, pady=1)
            self.player_buttons[player] = player_button

        filters = tk.Frame(
            self,
            bg=PANEL,
            highlightbackground=LINE,
            highlightthickness=1,
            padx=16,
            pady=13,
        )
        filters.grid(row=1, column=0, sticky="ew", pady=(0, 9))
        controls = tk.Frame(filters, bg=PANEL)
        controls.pack(side="top", fill="x", pady=(0, 8))
        tk.Label(
            controls,
            text="SEARCH",
            font=("Segoe UI", 9, "bold"),
            fg=MUTED,
            bg=PANEL,
        ).pack(side="left", padx=(2, 10))
        ttk.Entry(controls, textvariable=self.search_var, width=24).pack(
            side="left", padx=(0, 6)
        )
        rarity = ttk.Combobox(
            controls,
            textvariable=self.rarity_var,
            values=["全部星级", "6 星", "5 星", "4 星及以下"],
            state="readonly",
            width=11,
        )
        rarity.pack(side="left", padx=4)
        rarity.bind(
            "<<ComboboxSelected>>", lambda _event: self.reset_pool_page()
        )
        self.class_filter = OperatorClassFilter(
            filters,
            app,
            self.profession_var,
            self.branch_filter_var,
            self.reset_pool_page,
        )
        self.class_filter.pack(fill="x")

        content = ttk.Panedwindow(self, orient="horizontal")
        content.grid(row=2, column=0, sticky="nsew")
        pool_frame = tk.Frame(
            content,
            bg=PANEL,
            highlightbackground=LINE,
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        pool_frame.columnconfigure(0, weight=1)
        pool_frame.rowconfigure(1, weight=1)
        pool_header = tk.Frame(pool_frame, bg=PANEL)
        pool_header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        tk.Label(
            pool_header,
            text="干员档案",
            font=("Microsoft YaHei UI", 15, "bold"),
            fg=FG,
            bg=PANEL,
        ).pack(side="left")
        tk.Label(
            pool_header,
            textvariable=self.pool_count_var,
            font=("Microsoft YaHei UI", 10),
            fg=MUTED,
            bg=PANEL,
        ).pack(side="left", padx=8)
        tk.Label(
            pool_header,
            text="滚轮浏览全部干员",
            font=("Microsoft YaHei UI", 10),
            fg=MUTED,
            bg=PANEL,
        ).pack(side="right", padx=8)
        canvas_wrap = tk.Frame(pool_frame, bg=PANEL)
        canvas_wrap.grid(row=1, column=0, sticky="nsew")
        canvas_wrap.columnconfigure(0, weight=1)
        canvas_wrap.rowconfigure(0, weight=1)
        self.pool_canvas = tk.Canvas(
            canvas_wrap,
            bg=PANEL,
            highlightthickness=0,
            bd=0,
            yscrollincrement=1,
        )
        pool_scroll = ttk.Scrollbar(
            canvas_wrap,
            orient="vertical",
            command=self.pool_canvas.yview,
            style="Modern.Vertical.TScrollbar",
        )
        self.pool_canvas.configure(yscrollcommand=pool_scroll.set)
        self.pool_canvas.grid(row=0, column=0, sticky="nsew")
        pool_scroll.grid(row=0, column=1, sticky="ns")
        self.pool_canvas.bind("<Configure>", self.on_pool_canvas_resize)
        self.pool_canvas.bind("<MouseWheel>", self._smooth_pool_mousewheel)

        selection_frame = tk.Frame(
            content,
            bg=PANEL,
            highlightbackground=LINE,
            highlightthickness=1,
            padx=18,
            pady=15,
        )
        selection_frame.columnconfigure(0, weight=1)
        selection_frame.rowconfigure(6, weight=1)
        tk.Label(
            selection_frame,
            text="本方提交内容",
            font=("Microsoft YaHei UI", 15, "bold"),
            fg=FG,
            bg=PANEL,
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))
        tk.Label(
            selection_frame,
            text="主持人 Ban 结果（只读）",
            font=("Microsoft YaHei UI", 11, "bold"),
            fg=MUTED,
            bg=PANEL,
        ).grid(row=1, column=0, sticky="w")
        branch_line = tk.Frame(selection_frame, bg=PANEL)
        branch_line.grid(row=1, column=0, sticky="ew", pady=(5, 10))
        branch_line.grid_configure(row=2)
        branch_line.columnconfigure(1, weight=1)
        self.branch_preview_icon = tk.Label(
            branch_line,
            text="◇",
            font=(self.app.assets.branch_font_family, 25),
            width=2,
            fg=ACCENT,
            bg=SURFACE_RAISED,
        )
        self.branch_preview_icon.grid(row=0, column=0, sticky="ns", padx=(0, 7))
        self.branch_pick = ttk.Combobox(
            branch_line,
            textvariable=self.branch_pick_var,
            values=operator_values(app.operators.values(), "branch"),
            state="disabled",
        )
        self.branch_pick.grid(row=0, column=1, sticky="ew")
        self.branch_pick.bind("<<ComboboxSelected>>", self.update_branch_preview)
        self.branch_ban_button = ttk.Button(
            branch_line,
            text="请在主持人 Ban 页设置",
            command=self.add_branch_ban,
            state="disabled",
        )
        self.branch_ban_button.grid(
            row=0, column=2, padx=(8, 0)
        )
        self.branch_ban_canvas = tk.Canvas(
            selection_frame,
            height=72,
            bg=SURFACE,
            highlightthickness=0,
            bd=0,
        )
        self.branch_ban_canvas.grid(row=3, column=0, sticky="ew")
        self.branch_ban_canvas.bind(
            "<Configure>", lambda _event: self.refresh_branch_list()
        )

        ttk.Separator(selection_frame).grid(row=4, column=0, sticky="ew", pady=10)
        action_line = tk.Frame(selection_frame, bg=PANEL)
        action_line.grid(row=5, column=0, sticky="ew", pady=(0, 8))
        self.target_combo = ttk.Combobox(
            action_line, textvariable=self.target_var, state="readonly", width=15
        )
        self.target_combo.pack(side="left")
        self.target_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_selected_list())
        ttk.Button(action_line, text="加入所选干员", style="Accent.TButton", command=self.add_operator).pack(
            side="left", padx=6
        )
        ttk.Button(action_line, text="移除", command=self.remove_selected).pack(side="left")
        self.selected_tree = ttk.Treeview(
            selection_frame,
            show="tree",
            selectmode="browse",
            height=1,
            style="Operator.Treeview",
        )
        self.selected_tree.column("#0", width=370, anchor="w")
        selected_scroll = ttk.Scrollbar(
            selection_frame, orient="vertical", command=self.selected_tree.yview
        )
        self.selected_tree.configure(yscrollcommand=selected_scroll.set)
        self.selected_tree.grid(row=6, column=0, sticky="nsew")
        selected_scroll.grid(row=6, column=1, sticky="ns")
        self.selected_tree.bind("<Double-1>", lambda _event: self.remove_selected())
        tk.Label(
            selection_frame,
            textvariable=self.summary_var,
            font=("Microsoft YaHei UI", 10),
            fg=MUTED,
            bg=PANEL,
            wraplength=360,
            justify="left",
        ).grid(row=7, column=0, sticky="ew", pady=(10, 6))
        export_line = tk.Frame(selection_frame, bg=PANEL)
        export_line.grid(row=8, column=0, sticky="ew", pady=(4, 0))
        export_line.columnconfigure(1, weight=1)
        tk.Label(
            export_line, text="导出", font=("Microsoft YaHei UI", 9), fg=MUTED, bg=PANEL
        ).grid(row=0, column=0, padx=(0, 6))
        self.export_round_combo = ttk.Combobox(
            export_line, textvariable=self.export_round_var, state="readonly", width=10
        )
        self.export_round_combo.grid(row=0, column=1, sticky="ew")
        ttk.Button(
            export_line,
            text="校验并导出本轮文件",
            style="Green.TButton",
            command=self.export_submission,
        ).grid(row=0, column=2, padx=(6, 0))
        content.add(pool_frame, weight=5)
        content.add(selection_frame, weight=3)

        self.search_var.trace_add("write", lambda *_args: self.schedule_pool_refresh())
        self.update_player_buttons()
        self.update_profession_buttons()
        self.refresh_pool()

    def set_player(self, player: str) -> None:
        self.player_var.set(player)
        self.update_player_buttons()
        self.sync_host_bans()
        self.refresh_selected_list()
        self.render_pool_page()
        self.refresh_summary()

    def update_player_buttons(self) -> None:
        for player, button in self.player_buttons.items():
            color = BLUE if player == PLAYER_A else RED
            selected = self.player_var.get() == player
            button.configure(
                bg=color if selected else PANEL_2,
                fg="#10151b" if selected else color,
            )

    def set_profession(self, profession: str) -> None:
        self.profession_var.set(profession)
        self.branch_filter_var.set("全部分支")
        self.update_profession_buttons()
        self.reset_pool_page()

    def update_profession_buttons(self) -> None:
        if hasattr(self, "class_filter"):
            self.class_filter.refresh_selection()

    def reset_pool_page(self) -> None:
        if hasattr(self, "pool_canvas"):
            self.pool_canvas.yview_moveto(0)
        self.refresh_pool()

    def schedule_pool_refresh(self) -> None:
        if self._pool_refresh_job:
            self.after_cancel(self._pool_refresh_job)
        self._pool_refresh_job = self.after(120, self._run_scheduled_pool_refresh)

    def _run_scheduled_pool_refresh(self) -> None:
        self._pool_refresh_job = None
        self.reset_pool_page()

    def _smooth_pool_mousewheel(self, event: tk.Event) -> str:
        steps = -event.delta / 120 if event.delta else 0
        self._pool_scroll_velocity += steps * 110
        self._pool_scroll_velocity = max(
            -520.0, min(520.0, self._pool_scroll_velocity)
        )
        if self._pool_scroll_job is None:
            self._pool_scroll_job = self.after(0, self._animate_pool_scroll)
        return "break"

    def _animate_pool_scroll(self) -> None:
        self._pool_scroll_job = None
        region = str(self.pool_canvas.cget("scrollregion")).split()
        if len(region) < 4:
            self._pool_scroll_velocity = 0.0
            return
        total_height = max(1.0, float(region[3]))
        viewport = max(1.0, float(self.pool_canvas.winfo_height()))
        maximum = max(0.0, total_height - viewport)
        current = max(0.0, float(self.pool_canvas.canvasy(0)))
        step = self._pool_scroll_velocity * 0.24
        target = max(0.0, min(maximum, current + step))
        if maximum > 0:
            self.pool_canvas.yview_moveto(target / total_height)
        self._pool_scroll_velocity *= 0.72
        if (
            abs(self._pool_scroll_velocity) >= 0.7
            and target not in (0.0, maximum)
        ):
            self._pool_scroll_job = self.after(16, self._animate_pool_scroll)
        else:
            self._pool_scroll_velocity = 0.0

    def on_pool_canvas_resize(self, event: tk.Event) -> None:
        columns = max(3, min(6, max(1, event.width - 8) // 190))
        if columns != self.card_columns:
            self.card_columns = columns
            self.after_idle(self.render_pool_page)

    def load_config_file(self) -> None:
        path = filedialog.askopenfilename(
            parent=self,
            title="读取比赛配置",
            filetypes=[("比赛配置", "*.bpmatch"), ("所有文件", "*.*")],
        )
        if not path:
            return
        try:
            config = load_config(Path(path))
            config.validate()
            self.app.ensure_tab("setup").fill_from_config(config)
            self.app.set_config(config)
        except (RuleError, OSError, ValueError) as exc:
            self.app.show_error("读取失败", exc)

    def use_config(self, config: MatchConfig, reset: bool) -> None:
        if reset:
            self.selected = {"ban": []}
            for index in range(config.rules.rounds):
                self.selected[f"round_{index + 1}"] = []
            self.branch_bans = []
            self.selected_branch_index = None
        self.target_combo["values"] = [
            f"第 {index + 1} 轮 Pick" for index in range(config.rules.rounds)
        ]
        self.export_round_combo["values"] = [
            f"第 {index + 1} 轮" for index in range(config.rules.rounds)
        ]
        self.export_round_var.set("第 1 轮")
        self.target_var.set("第 1 轮 Pick")
        self.config_label.set(
            f"{config.title} · 每轮 {config.rules.picks_per_round} 人 · 共 {config.rules.rounds} 轮"
        )
        self.sync_host_bans()
        self.refresh_selected_list()
        self.refresh_summary()

    def target_key(self) -> str:
        try:
            round_number = int(self.target_var.get().split()[1])
        except (IndexError, ValueError):
            return "round_1"
        return f"round_{round_number}"

    def sync_host_bans(self) -> None:
        player = self.player_var.get()
        if self.app.state:
            self.branch_bans = list(
                self.app.state.host_banned_branches.get(player, [])
            )
            self.selected["ban"] = list(
                self.app.state.host_banned_operator_ids.get(player, [])
            )
        else:
            self.branch_bans = []
            self.selected["ban"] = []
        self.selected_branch_index = None
        self.refresh_branch_list()

    def refresh_pool(self) -> None:
        rarity_filter = self.rarity_var.get()
        profession_filter = self.profession_var.get()
        branch_filter = self.branch_filter_var.get()
        search = self.search_var.get().strip().lower()
        rows = []
        for operator in self.app.operators.values():
            if search and search not in operator.name.lower() and search not in operator.operator_id.lower():
                continue
            if rarity_filter == "6 星" and operator.rarity != 6:
                continue
            if rarity_filter == "5 星" and operator.rarity != 5:
                continue
            if rarity_filter == "4 星及以下" and operator.rarity > 4:
                continue
            if profession_filter != "全部职业" and operator.profession != profession_filter:
                continue
            if branch_filter != "全部分支" and operator.branch != branch_filter:
                continue
            rows.append(operator)
        rows.sort(key=lambda op: (-op.rarity, op.profession, op.name))
        self.filtered_ids = [operator.operator_id for operator in rows]
        self.pool_count_var.set(f"{len(rows)} 名")
        self.render_pool_page()

    def render_pool_page(self) -> None:
        if not hasattr(self, "pool_canvas"):
            return
        canvas = self.pool_canvas
        canvas.delete("all")
        self.card_frames.clear()
        canvas_width = max(600, canvas.winfo_width())
        gap = 12
        card_width = max(
            165, (canvas_width - gap * (self.card_columns + 1)) // self.card_columns
        )
        card_height = 218

        if not self.filtered_ids:
            canvas.create_text(
                canvas_width // 2,
                120,
                text="没有符合当前筛选条件的干员",
                fill=MUTED,
                font=("Microsoft YaHei UI", 12),
            )
            canvas.configure(scrollregion=(0, 0, canvas_width, 260))
            return

        effective_banned_ids: set[str] = set()
        effective_banned_branches: set[str] = set()
        if self.app.config:
            effective_banned_ids.update(self.app.config.global_banned_operator_ids)
            effective_banned_branches.update(self.app.config.global_banned_branches)
        if self.app.state:
            for player in (PLAYER_A, PLAYER_B):
                effective_banned_ids.update(
                    self.app.state.host_banned_operator_ids.get(player, [])
                )
                effective_banned_branches.update(
                    self.app.state.host_banned_branches.get(player, [])
                )

        for index, operator_id in enumerate(self.filtered_ids):
            operator = self.app.operators[operator_id]
            row, column = divmod(index, self.card_columns)
            selected = operator_id == self.selected_operator_id
            is_banned = (
                operator_id in effective_banned_ids
                or operator.branch in effective_banned_branches
            )
            border = ACCENT if selected else (BAN_BORDER if is_banned else LINE)
            card_fill = BAN_CARD if is_banned else SURFACE_RAISED
            x1 = gap + column * (card_width + gap)
            y1 = gap + row * (card_height + gap)
            x2 = x1 + card_width
            y2 = y1 + card_height
            tag = f"operator::{operator_id}"
            rectangle = canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill=card_fill,
                outline=border,
                width=3 if selected or is_banned else 1,
                tags=(tag, "operator_card"),
            )
            self.card_frames[operator_id] = rectangle
            image = self.app.assets.avatar(operator, 118)
            canvas.create_image(
                (x1 + x2) // 2,
                y1 + 8,
                image=image,
                anchor="n",
                tags=(tag, "operator_card"),
            )
            marks: list[str] = []
            if is_banned:
                marks.append("BAN")
            for selected_key, selected_ids in self.selected.items():
                if selected_key.startswith("round_") and operator_id in selected_ids:
                    marks.append("R" + selected_key.rsplit("_", 1)[-1])
            if marks:
                badge_text = " / ".join(marks)
                badge_width = max(
                    46 if is_banned else 32,
                    len(badge_text) * (9 if is_banned else 7)
                    + (14 if is_banned else 10),
                )
                badge_height = 27 if is_banned else 19
                canvas.create_rectangle(
                    x2 - badge_width - 4,
                    y1 + 4,
                    x2 - 4,
                    y1 + 4 + badge_height,
                    fill=BAN_BADGE if is_banned else ACCENT,
                    outline="",
                    tags=(tag, "operator_card"),
                )
                canvas.create_text(
                    x2 - badge_width / 2 - 4,
                    y1 + 4 + badge_height / 2,
                    text=badge_text,
                    font=("Segoe UI", 10 if is_banned else 7, "bold"),
                    fill="#121212",
                    tags=(tag, "operator_card"),
                )
            name_font_size = card_operator_name_size(operator.name, 11, 10, 8)
            draw_shadowed_card_name(
                canvas,
                (x1 + x2) // 2,
                y2 - 39,
                text=card_operator_name(operator.name),
                font=("Microsoft YaHei UI", name_font_size, "bold"),
                fill=FG,
                anchor="s",
                tags=(tag, "operator_card"),
            )
            canvas.create_text(
                (x1 + x2) // 2,
                y2 - 20,
                text=operator.branch,
                font=("Microsoft YaHei UI", 8),
                fill=PROFESSION_COLORS.get(operator.profession, MUTED),
                tags=(tag, "operator_card"),
            )
            canvas.tag_bind(
                tag,
                "<Button-1>",
                lambda _event, oid=operator_id: self.select_operator_card(oid),
            )
            canvas.tag_bind(
                tag,
                "<Double-Button-1>",
                lambda _event, oid=operator_id: self.add_operator_by_id(oid),
            )

        total_rows = math.ceil(len(self.filtered_ids) / self.card_columns)
        total_height = gap + total_rows * (card_height + gap)
        canvas.configure(scrollregion=(0, 0, canvas_width, total_height))

    def select_operator_card(self, operator_id: str) -> None:
        old_id = self.selected_operator_id
        self.selected_operator_id = operator_id
        effective_banned_ids: set[str] = set()
        effective_banned_branches: set[str] = set()
        if self.app.config:
            effective_banned_ids.update(self.app.config.global_banned_operator_ids)
            effective_banned_branches.update(self.app.config.global_banned_branches)
        if self.app.state:
            for player in (PLAYER_A, PLAYER_B):
                effective_banned_ids.update(
                    self.app.state.host_banned_operator_ids.get(player, [])
                )
                effective_banned_branches.update(
                    self.app.state.host_banned_branches.get(player, [])
                )
        if old_id and old_id in self.card_frames and old_id in self.app.operators:
            old_operator = self.app.operators[old_id]
            old_banned = (
                old_id in effective_banned_ids
                or old_operator.branch in effective_banned_branches
            )
            self.pool_canvas.itemconfigure(
                self.card_frames[old_id],
                outline=BAN_BORDER if old_banned else LINE,
                width=3 if old_banned else 1,
            )
        if operator_id in self.card_frames:
            self.pool_canvas.itemconfigure(
                self.card_frames[operator_id],
                outline=ACCENT,
                width=3,
            )

    def add_branch_ban(self) -> None:
        messagebox.showinfo(
            "只读区域",
            "比赛 Ban 由主持人在“主持人 Ban”页面统一操作。",
            parent=self,
        )

    def update_branch_preview(self, _event: tk.Event | None = None) -> None:
        branch_id = self.branch_by_name.get(self.branch_pick_var.get(), "")
        self.branch_preview_icon.configure(text=self.app.assets.branch_glyph(branch_id))

    def refresh_branch_list(self) -> None:
        canvas = self.branch_ban_canvas
        canvas.delete("all")
        width = max(360, canvas.winfo_width())
        if not self.branch_bans:
            canvas.create_text(
                18,
                43,
                anchor="w",
                text="尚未选择子职业 Ban",
                fill=MUTED,
                font=("Microsoft YaHei UI", 11),
            )
            return
        gap = 10
        card_width = min(250, max(170, (width - gap * (len(self.branch_bans) + 1)) // len(self.branch_bans)))
        for index, branch in enumerate(self.branch_bans):
            x1 = gap + index * (card_width + gap)
            x2 = x1 + card_width
            tag = f"branch-ban-{index}"
            selected = self.selected_branch_index == index
            canvas.create_rectangle(
                x1,
                8,
                x2,
                78,
                fill=SURFACE_RAISED,
                outline=ACCENT if selected else LINE,
                width=3 if selected else 1,
                tags=(tag,),
            )
            branch_id = self.branch_by_name.get(branch, "")
            canvas.create_text(
                x1 + 36,
                43,
                text=self.app.assets.branch_glyph(branch_id),
                fill=ACCENT,
                font=(self.app.assets.branch_font_family, 27),
                tags=(tag,),
            )
            canvas.create_text(
                x1 + 68,
                43,
                anchor="w",
                text=branch,
                fill=FG,
                font=("Microsoft YaHei UI", 12, "bold"),
                tags=(tag,),
            )

    def select_branch_card(self, index: int) -> None:
        self.selected_branch_index = index
        self.refresh_branch_list()

    def remove_branch_at(self, index: int) -> None:
        return

    def add_operator(self) -> None:
        if not self.app.config:
            messagebox.showwarning("需要配置", "请先读取比赛配置。", parent=self)
            return
        if not self.selected_operator_id:
            return
        self.add_operator_by_id(self.selected_operator_id)

    def add_operator_by_id(self, operator_id: str) -> None:
        if not self.app.config:
            messagebox.showwarning("需要配置", "请先读取比赛配置。", parent=self)
            return
        operator = self.app.operators[operator_id]
        key = self.target_key()
        limit = self.app.config.rules.picks_per_round
        banned_operator_ids = set()
        banned_branches = set()
        if self.app.state:
            for player in (PLAYER_A, PLAYER_B):
                banned_operator_ids.update(
                    self.app.state.host_banned_operator_ids.get(player, [])
                )
                banned_branches.update(
                    self.app.state.host_banned_branches.get(player, [])
                )
        banned_operator_ids.update(self.app.config.global_banned_operator_ids)
        banned_branches.update(self.app.config.global_banned_branches)
        if operator_id in banned_operator_ids:
            messagebox.showwarning("不可选择", "该干员已在主持人台被 Ban。", parent=self)
            return
        if operator.branch in banned_branches:
            messagebox.showwarning("不可选择", "该干员所属分支已在主持人台被 Ban。", parent=self)
            return
        all_picks = [
            op_id
            for selected_key, ids in self.selected.items()
            if selected_key.startswith("round_")
            for op_id in ids
        ]
        if operator_id in all_picks:
            messagebox.showwarning("不可重复", "同一选手不能跨轮重复 Pick 干员。", parent=self)
            return
        if operator_id in self.selected[key]:
            return
        if len(self.selected[key]) >= limit:
            messagebox.showwarning("数量已满", f"当前分组最多选择 {limit} 名干员。", parent=self)
            return
        self.selected[key].append(operator_id)
        self.refresh_selected_list()
        self.refresh_summary()
        self.render_pool_page()

    def remove_selected(self) -> None:
        selected_items = self.selected_tree.selection()
        if selected_items:
            key = self.target_key()
            operator_id = selected_items[0]
            if operator_id in self.selected.get(key, []):
                self.selected[key].remove(operator_id)
            self.refresh_selected_list()
            self.refresh_summary()
            self.render_pool_page()
            return
        if self.selected_branch_index is not None:
            self.remove_branch_at(self.selected_branch_index)

    def refresh_selected_list(self) -> None:
        self.selected_tree.delete(*self.selected_tree.get_children())
        for operator_id in self.selected.get(self.target_key(), []):
            operator = self.app.operators[operator_id]
            self.selected_tree.insert(
                "",
                "end",
                iid=operator_id,
                text=f"  {operator.name}    {operator.rarity}★  ·  {operator.branch}",
                image=self.app.assets.avatar(operator, 80),
            )

    def refresh_summary(self) -> None:
        if not self.app.config:
            self.summary_var.set("读取比赛配置后开始选择。")
            return
        rules = self.app.config.rules
        parts = [
            f"全局 Ban {len(self.app.config.global_banned_operator_ids)} 人/"
            f"{len(self.app.config.global_banned_branches)} 分支",
            f"分支 Ban {len(self.branch_bans)}/{rules.branch_bans_per_player}",
            f"干员 Ban {len(self.selected.get('ban', []))}/{rules.operator_bans_per_player}",
        ]
        for index in range(rules.rounds):
            parts.append(
                f"第 {index + 1} 轮 {len(self.selected.get(f'round_{index + 1}', []))}/{rules.picks_per_round}"
            )
        name = (
            self.app.config.player_a_name
            if self.player_var.get() == PLAYER_A
            else self.app.config.player_b_name
        )
        self.summary_var.set(f"{self.player_var.get()} 方 · {name}\n" + "  |  ".join(parts))

    def make_submission(self) -> PlayerSubmission:
        if not self.app.config:
            raise RuleError("请先读取比赛配置")
        if not self.app.state or not self.app.state.ban_complete:
            raise RuleError("主持人尚未确认双方 Ban，请先完成主持人 Ban 流程")
        player = self.player_var.get()
        self.sync_host_bans()
        name = (
            self.app.config.player_a_name if player == PLAYER_A else self.app.config.player_b_name
        )
        try:
            round_index = int(self.export_round_var.get().split()[1])
        except (IndexError, ValueError) as exc:
            raise RuleError("请选择要导出的轮次") from exc
        submission = PlayerSubmission(
            match_id=self.app.config.match_id,
            player=player,
            player_name=name,
            round_index=round_index,
            banned_branches=list(self.branch_bans),
            banned_operator_ids=list(self.selected.get("ban", [])),
            picks=list(self.selected.get(f"round_{round_index}", [])),
        )
        submission.validate(self.app.config, self.app.operators)
        return submission

    def export_submission(self) -> None:
        try:
            submission = self.make_submission()
            path = filedialog.asksaveasfilename(
                parent=self,
                title="导出选手文件",
                defaultextension=".bpselect",
                initialfile=(
                    f"{self.app.config.match_id}_{submission.player}_"
                    f"{safe_file_name(submission.player_name)}_R{submission.round_index}.bpselect"
                ),
                filetypes=[("选手 BP 文件", "*.bpselect"), ("所有文件", "*.*")],
            )
            if path:
                save_submission(Path(path), submission)
                messagebox.showinfo(
                    "导出成功",
                    "选手文件已生成。请将该文件单独发送给主办方，不要转发给对手。",
                    parent=self,
                )
        except (RuleError, OSError) as exc:
            self.app.show_error("无法导出", exc)


class AuctionTab(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, app: BpApplication):
        super().__init__(parent, padding=12)
        self.app = app
        self.submissions: dict[str, PlayerSubmission] = {}
        self.config_var = tk.StringVar(value="尚未载入比赛")
        self.round_import_var = tk.StringVar(value="当前等待：第 1 轮选手文件")
        self.a_file_var = tk.StringVar(value="蓝方：未导入")
        self.b_file_var = tk.StringVar(value="红方：未导入")
        self.seed_var = tk.StringVar(value=str(random.SystemRandom().randint(100000, 999999999)))
        self.progress_var = tk.StringVar(value="等待生成拍卖池")
        self.current_name_var = tk.StringVar(value="—")
        self.current_meta_var = tk.StringVar(value="请先导入双方选手文件")
        self.price_var = tk.StringVar(value="—")
        self.leader_var = tk.StringVar(value="尚无出价")
        self.a_bid_var = tk.StringVar(value="蓝方出价")
        self.b_bid_var = tk.StringVar(value="红方出价")
        self.a_pass_var = tk.StringVar(value="蓝方放弃")
        self.b_pass_var = tk.StringVar(value="红方放弃")
        self.timer_var = tk.StringVar(value="20")
        self.timer_context_var = tk.StringVar(value="等待首次出价")
        self.result_title_vars = {
            PLAYER_A: tk.StringVar(value="蓝方获得 · 0"),
            PLAYER_B: tk.StringVar(value="红方获得 · 0"),
            "unsold": tk.StringVar(value="流拍 · 0"),
        }
        self.result_canvases: dict[str, tk.Canvas] = {}
        self.result_scrollbars: dict[str, ttk.Scrollbar] = {}
        self.bid_frames: dict[str, tk.Frame] = {}
        self.bid_buttons: dict[str, tk.Button] = {}
        self.selected_result_operator_id: str | None = None
        self._result_render_job: str | None = None
        self._timer_job: str | None = None
        self._timer_operator_id: str | None = None
        self._timer_remaining = 20

        self.columnconfigure(0, weight=0, minsize=300)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1, minsize=470)

        control = ttk.LabelFrame(self, text=" 文件与进度 ", padding=12)
        control.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 8))
        control.columnconfigure(0, weight=1)
        ttk.Label(control, textvariable=self.config_var, style="CardTitle.TLabel", wraplength=320).grid(
            row=0, column=0, sticky="ew", pady=(0, 12)
        )
        ttk.Label(
            control,
            textvariable=self.round_import_var,
            foreground=ACCENT,
            wraplength=300,
            justify="left",
        ).grid(
            row=1, column=0, sticky="w", pady=(0, 8)
        )
        ttk.Button(control, text="读取比赛配置", command=self.load_config_file).grid(
            row=2, column=0, sticky="ew", pady=3
        )
        self.a_import_button = ttk.Button(
            control,
            text="导入蓝方选手文件",
            command=lambda: self.import_submission(PLAYER_A),
        )
        self.a_import_button.grid(row=3, column=0, sticky="ew", pady=3)
        ttk.Label(control, textvariable=self.a_file_var, style="Muted.TLabel", wraplength=300).grid(
            row=4, column=0, sticky="w", pady=(2, 6)
        )
        self.b_import_button = ttk.Button(
            control,
            text="导入红方选手文件",
            command=lambda: self.import_submission(PLAYER_B),
        )
        self.b_import_button.grid(row=5, column=0, sticky="ew", pady=3)
        ttk.Label(control, textvariable=self.b_file_var, style="Muted.TLabel", wraplength=300).grid(
            row=6, column=0, sticky="w", pady=(2, 12)
        )
        ttk.Label(control, text="本轮随机种子").grid(row=7, column=0, sticky="w")
        ttk.Entry(control, textvariable=self.seed_var).grid(row=8, column=0, sticky="ew", pady=(4, 8))
        ttk.Button(
            control, text="校验并生成本轮拍卖池", style="Accent.TButton", command=self.prepare_auction
        ).grid(row=9, column=0, sticky="ew", pady=(2, 14))
        ttk.Separator(control).grid(row=10, column=0, sticky="ew", pady=8)
        ttk.Button(control, text="保存完整比赛", command=self.save_match).grid(
            row=11, column=0, sticky="ew", pady=3
        )
        control.rowconfigure(12, weight=1)

        auction = ttk.Frame(self, style="Panel.TFrame", padding=(20, 14))
        auction.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        auction.columnconfigure(0, weight=1)
        auction.columnconfigure(1, weight=1)
        tk.Label(
            auction,
            textvariable=self.progress_var,
            font=("Microsoft YaHei UI", 11, "bold"),
            fg=MUTED,
            bg=PANEL,
        ).grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )
        timer_head = tk.Frame(auction, bg=PANEL)
        timer_head.grid(row=0, column=1, sticky="e", pady=(0, 8))
        tk.Label(
            timer_head,
            textvariable=self.timer_context_var,
            font=("Microsoft YaHei UI", 10, "bold"),
            fg=MUTED,
            bg=PANEL,
        ).pack(side="left", padx=(0, 10))
        self.timer_value_label = tk.Label(
            timer_head,
            textvariable=self.timer_var,
            font=("Segoe UI", 20, "bold"),
            fg=FG,
            bg=SURFACE_RAISED,
            width=3,
            padx=4,
            pady=2,
        )
        self.timer_value_label.pack(side="left")

        current = tk.Frame(auction, bg=PANEL)
        current.grid(row=1, column=0, columnspan=2, sticky="ew")
        current.columnconfigure(1, weight=1)
        avatar_stage = tk.Frame(
            current,
            bg=SURFACE_RAISED,
            width=142,
            height=132,
            highlightbackground=LINE,
            highlightthickness=1,
        )
        avatar_stage.grid(row=0, column=0, rowspan=4, sticky="w", padx=(0, 18))
        avatar_stage.grid_propagate(False)
        self.current_avatar_label = tk.Label(
            avatar_stage,
            bg=SURFACE_RAISED,
            fg=LINE,
            text="◇",
            font=("Segoe UI Symbol", 34),
            bd=0,
        )
        self.current_avatar_label.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(
            current,
            textvariable=self.current_name_var,
            font=("Microsoft YaHei UI", 24, "bold"),
            fg=FG,
            bg=PANEL,
            anchor="w",
        ).grid(row=0, column=1, sticky="w")
        tk.Label(
            current,
            textvariable=self.current_meta_var,
            font=("Microsoft YaHei UI", 11),
            fg=MUTED,
            bg=PANEL,
            anchor="w",
        ).grid(row=1, column=1, sticky="w", pady=(2, 0))
        tk.Label(
            current,
            textvariable=self.price_var,
            font=("Microsoft YaHei UI", 34, "bold"),
            fg=ACCENT,
            bg=PANEL,
            anchor="w",
        ).grid(row=2, column=1, sticky="w", pady=(8, 2))
        self.leader_label = tk.Label(
            current,
            textvariable=self.leader_var,
            font=("Microsoft YaHei UI", 12, "bold"),
            fg=FG,
            bg=SURFACE_RAISED,
            anchor="w",
            padx=14,
            pady=6,
        )
        self.leader_label.grid(row=3, column=1, sticky="ew", pady=(4, 0))

        bids = tk.Frame(auction, bg=PANEL)
        bids.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 4))
        bids.columnconfigure(0, weight=1)
        bids.columnconfigure(1, weight=1)
        for column, (player, color, bid_var, pass_var) in enumerate(
            (
                (PLAYER_A, BLUE, self.a_bid_var, self.a_pass_var),
                (PLAYER_B, RED, self.b_bid_var, self.b_pass_var),
            )
        ):
            side = tk.Frame(
                bids,
                bg=PANEL,
                highlightbackground=LINE,
                highlightthickness=1,
                padx=4,
                pady=4,
            )
            side.grid(
                row=0,
                column=column,
                sticky="ew",
                padx=((0, 7) if column == 0 else (7, 0)),
            )
            side.columnconfigure(0, weight=1)
            bid_button = tk.Button(
                side,
                textvariable=bid_var,
                command=lambda value=player: self.bid(value),
                bg=color,
                fg=HEADER_BG,
                activebackground=color,
                activeforeground=HEADER_BG,
                font=("Microsoft YaHei UI", 15, "bold"),
                relief="flat",
                bd=0,
                cursor="hand2",
                pady=12,
            )
            bid_button.grid(row=0, column=0, sticky="ew")
            tk.Button(
                side,
                textvariable=pass_var,
                command=lambda value=player: self.pass_bid(value),
                bg=SURFACE_RAISED,
                fg=FG,
                activebackground=CONTROL_HOVER,
                activeforeground=FG,
                font=("Microsoft YaHei UI", 10, "bold"),
                relief="flat",
                bd=0,
                cursor="hand2",
                pady=7,
            ).grid(row=1, column=0, sticky="ew", pady=(4, 0))
            self.bid_frames[player] = side
            self.bid_buttons[player] = bid_button

        finish = ttk.Frame(auction, style="Panel.TFrame")
        finish.grid(row=3, column=0, columnspan=2, pady=(6, 0))
        ttk.Button(finish, text="确认成交", command=self.award).pack(side="left", padx=4)
        ttk.Button(finish, text="标记流拍", command=self.unsold).pack(side="left", padx=4)

        history = tk.Frame(
            self,
            bg=PANEL,
            highlightbackground=LINE,
            highlightthickness=1,
            padx=12,
            pady=10,
        )
        history.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(10, 0))
        history.rowconfigure(1, weight=1)
        history.columnconfigure(0, weight=2, uniform="auction_result")
        history.columnconfigure(1, weight=2, uniform="auction_result")
        history.columnconfigure(2, weight=1, uniform="auction_result")
        tk.Label(
            history,
            text="已完成拍卖",
            font=("Microsoft YaHei UI", 16, "bold"),
            fg=FG,
            bg=PANEL,
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.reauction_button = tk.Button(
            history,
            text="重新拍卖选中干员",
            command=self.reauction_selected,
            state="disabled",
            bg=SURFACE_RAISED,
            fg=MUTED,
            activebackground=CONTROL_HOVER,
            activeforeground=FG,
            disabledforeground="#66727D",
            font=("Microsoft YaHei UI", 10, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=14,
            pady=7,
        )
        self.reauction_button.grid(
            row=0,
            column=1,
            columnspan=2,
            sticky="e",
            pady=(0, 8),
        )
        for column, (key, title, color) in enumerate(
            (
                (PLAYER_A, "蓝方获得", BLUE),
                (PLAYER_B, "红方获得", RED),
                ("unsold", "流拍区", MUTED),
            )
        ):
            panel = tk.Frame(
                history,
                bg=SURFACE,
                highlightbackground=color,
                highlightthickness=2,
                padx=6,
                pady=6,
            )
            panel.grid(
                row=1,
                column=column,
                sticky="nsew",
                padx=((0, 5) if column == 0 else ((5, 0) if column == 2 else 5)),
            )
            panel.columnconfigure(0, weight=1)
            panel.rowconfigure(1, weight=1)
            tk.Label(
                panel,
                textvariable=self.result_title_vars[key],
                font=("Microsoft YaHei UI", 12, "bold"),
                fg=color,
                bg=SURFACE,
            ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 7))
            canvas = tk.Canvas(
                panel,
                bg=SURFACE,
                highlightthickness=0,
                bd=0,
                yscrollincrement=24,
            )
            result_scroll = ttk.Scrollbar(
                panel,
                orient="vertical",
                command=canvas.yview,
            )
            canvas.configure(yscrollcommand=result_scroll.set)
            canvas.grid(row=1, column=0, sticky="nsew")
            result_scroll.grid(row=1, column=1, sticky="ns")
            canvas.bind(
                "<Configure>",
                lambda _event: self.schedule_result_render(),
            )
            canvas.bind(
                "<MouseWheel>",
                lambda event, target=canvas: target.yview_scroll(
                    -1 if event.delta > 0 else 1,
                    "units",
                ),
            )
            self.result_canvases[key] = canvas
            self.result_scrollbars[key] = result_scroll

        self.refresh_team_labels()

    def team_name(self, player: str) -> str:
        if player not in (PLAYER_A, PLAYER_B):
            return player
        config = self.app.config
        if not config:
            return "蓝方" if player == PLAYER_A else "红方"
        name = (
            config.player_a_name
            if player == PLAYER_A
            else config.player_b_name
        ).strip()
        return name or ("蓝方" if player == PLAYER_A else "红方")

    def refresh_team_labels(self) -> None:
        blue_name = self.team_name(PLAYER_A)
        red_name = self.team_name(PLAYER_B)
        self.a_import_button.configure(text=f"导入 {blue_name} 选手文件")
        self.b_import_button.configure(text=f"导入 {red_name} 选手文件")
        self.a_pass_var.set(f"{blue_name} 放弃")
        self.b_pass_var.set(f"{red_name} 放弃")
        self.result_title_vars[PLAYER_A].set(f"蓝方 · {blue_name} · 0")
        self.result_title_vars[PLAYER_B].set(f"红方 · {red_name} · 0")

    def schedule_result_render(self) -> None:
        if self._result_render_job is not None:
            return
        self._result_render_job = self.after_idle(self.refresh_auction_results)

    def use_config(self, config: MatchConfig) -> None:
        self.submissions = {}
        self.config_var.set(f"{config.title}\n{config.match_id}")
        self.round_import_var.set("当前等待：第 1 轮选手文件")
        self.refresh_team_labels()
        self.a_file_var.set(f"{self.team_name(PLAYER_A)}：未导入")
        self.b_file_var.set(f"{self.team_name(PLAYER_B)}：未导入")
        self.progress_var.set("等待生成拍卖池")
        self.update_current()

    def load_config_file(self) -> None:
        path = filedialog.askopenfilename(
            parent=self,
            title="读取比赛配置",
            filetypes=[("比赛配置", "*.bpmatch"), ("所有文件", "*.*")],
        )
        if not path:
            return
        try:
            config = load_config(Path(path))
            config.validate()
            self.app.ensure_tab("setup").fill_from_config(config)
            self.app.set_config(config)
        except (RuleError, OSError, ValueError) as exc:
            self.app.show_error("读取失败", exc)

    def import_submission(self, expected_player: str) -> None:
        if not self.app.config:
            messagebox.showwarning("需要配置", "请先读取比赛配置。", parent=self)
            return
        path = filedialog.askopenfilename(
            parent=self,
            title=f"导入 {self.team_name(expected_player)} 选手文件",
            filetypes=[("选手 BP 文件", "*.bpselect"), ("所有文件", "*.*")],
        )
        if not path:
            return
        try:
            submission = load_submission(Path(path))
            if submission.player != expected_player:
                raise RuleError(
                    f"选择的是 {self.team_name(submission.player)} 文件，"
                    f"并非 {self.team_name(expected_player)} 文件"
                )
            expected_round = self.next_round_to_prepare()
            if submission.round_index != expected_round:
                raise RuleError(
                    f"当前应导入第 {expected_round} 轮文件，选择的是第 {submission.round_index} 轮"
                )
            submission.validate(self.app.config, self.app.operators)
            self.submissions[expected_player] = submission
            if self.app.state:
                self.app.state.host_banned_branches[expected_player] = list(
                    submission.banned_branches
                )
                self.app.state.host_banned_operator_ids[expected_player] = list(
                    submission.banned_operator_ids
                )
                rules = self.app.state.config.rules
                self.app.state.ban_complete = all(
                    len(self.app.state.host_banned_branches[player])
                    == rules.branch_bans_per_player
                    and len(self.app.state.host_banned_operator_ids[player])
                    == rules.operator_bans_per_player
                    for player in (PLAYER_A, PLAYER_B)
                )
                self.app.ensure_tab("host_ban").load_from_state()
            label = f"{self.team_name(expected_player)}：{submission.player_name} · 已校验"
            (self.a_file_var if expected_player == PLAYER_A else self.b_file_var).set(label)
        except (RuleError, OSError, ValueError) as exc:
            self.app.show_error("导入失败", exc)

    def prepare_auction(self) -> None:
        try:
            if not self.app.config:
                raise RuleError("请先读取比赛配置")
            if PLAYER_A not in self.submissions or PLAYER_B not in self.submissions:
                raise RuleError(
                    f"请先分别导入 {self.team_name(PLAYER_A)}、"
                    f"{self.team_name(PLAYER_B)} 的选手文件"
                )
            state = self.app.state or MatchState(config=self.app.config)
            if not state.ban_complete:
                raise RuleError("双方主持人 Ban 尚未完成或未随选手文件导入")
            duplicate_bans = set(
                state.host_banned_operator_ids[PLAYER_A]
            ) & set(state.host_banned_operator_ids[PLAYER_B])
            if duplicate_bans:
                names = "、".join(
                    self.app.operators[operator_id].name
                    for operator_id in duplicate_bans
                    if operator_id in self.app.operators
                )
                raise RuleError(f"双方不能重复 Ban 同一干员：{names}")
            global_banned_ids = set(
                state.host_banned_operator_ids[PLAYER_A]
                + state.host_banned_operator_ids[PLAYER_B]
            )
            global_banned_ids.update(state.config.global_banned_operator_ids)
            global_banned_branches = set(
                state.host_banned_branches[PLAYER_A]
                + state.host_banned_branches[PLAYER_B]
            )
            global_banned_branches.update(state.config.global_banned_branches)
            invalid_picks = {
                operator_id
                for submission in self.submissions.values()
                for operator_id in submission.picks
                if operator_id in global_banned_ids
                or self.app.operators[operator_id].branch in global_banned_branches
            }
            if invalid_picks:
                names = "、".join(
                    self.app.operators[operator_id].name
                    for operator_id in sorted(invalid_picks)
                )
                raise RuleError(f"Pick 中包含主持人 Ban 的干员或分支：{names}")
            round_index = self.next_round_to_prepare()
            if self.submissions[PLAYER_A].round_index != round_index:
                raise RuleError(f"当前应准备第 {round_index} 轮")
            if round_index > 1:
                previous_round_items = [
                    item
                    for item in (self.app.state.auction_items if self.app.state else [])
                    if item.round_index == round_index - 1
                ]
                if not previous_round_items or any(
                    item.status not in ("sold", "unsold") for item in previous_round_items
                ):
                    raise RuleError("必须完成上一轮拍卖后，才能导入并生成下一轮")
            seed = int(self.seed_var.get())
            previous_ids = {
                item.operator_id for item in (self.app.state.auction_items if self.app.state else [])
            }
            items = build_auction_round(
                self.app.config,
                self.submissions[PLAYER_A],
                self.submissions[PLAYER_B],
                self.app.operators,
                seed=seed,
                previous_operator_ids=previous_ids,
            )
            duplicates = self.app.config.rules.picks_per_round * 2 - len(items)
            if any(item.round_index == round_index for item in state.auction_items):
                raise RuleError(f"第 {round_index} 轮拍卖池已经生成")
            state.submissions[f"R{round_index}:A"] = self.submissions[PLAYER_A]
            state.submissions[f"R{round_index}:B"] = self.submissions[PLAYER_B]
            state.auction_items.extend(items)
            state.auction_seed = state.auction_seed or seed
            state.auction_seeds[str(round_index)] = seed
            state.advance()
            self.app.state = state
            self.submissions = {}
            self.a_file_var.set(f"{self.team_name(PLAYER_A)}：未导入")
            self.b_file_var.set(f"{self.team_name(PLAYER_B)}：未导入")
            self.round_import_var.set(f"正在拍卖：第 {round_index} 轮")
            self.app.ensure_tab("settlement").refresh()
            self.update_current()
            messagebox.showinfo(
                f"第 {round_index} 轮拍卖池已生成",
                f"本轮共 {len(items)} 名干员；双方重复选择合并 {duplicates} 次。\n"
                "随机顺序已经固化到比赛存档中。",
                parent=self,
            )
        except (RuleError, ValueError) as exc:
            self.app.show_error("无法生成拍卖池", exc)

    def get_item(self):
        if not self.app.state:
            raise RuleError("尚未生成拍卖池")
        item = self.app.state.current_item()
        if not item:
            raise RuleError("所有干员均已完成拍卖")
        return item

    def next_price(self) -> int:
        item = self.get_item()
        rules = self.app.state.config.rules
        return item.starting_price if item.current_price is None else item.current_price + rules.min_increment

    def bid(self, player: str) -> None:
        try:
            item = self.get_item()
            item.place_bid(player, self.next_price(), self.app.state.config.rules)
            if item.status == "sold":
                self._advance_completed_item()
            else:
                self.update_current(reset_timer=True)
        except RuleError as exc:
            self.app.show_error("无法出价", exc)

    def pass_bid(self, player: str) -> None:
        try:
            item = self.get_item()
            ended = item.pass_bid(player)
            if ended:
                self._advance_completed_item()
            else:
                self.update_current(reset_timer=True)
        except RuleError as exc:
            self.app.show_error("无法放弃", exc)

    def award(self) -> None:
        try:
            self.get_item().award()
            self._advance_completed_item()
        except RuleError as exc:
            self.app.show_error("无法成交", exc)

    def unsold(self) -> None:
        try:
            self.get_item().mark_unsold()
            self._advance_completed_item()
        except RuleError as exc:
            self.app.show_error("无法流拍", exc)

    def next_item(self) -> None:
        try:
            item = self.get_item()
            if item.status not in ("sold", "unsold"):
                raise RuleError("请先完成当前干员的拍卖")
            self._advance_completed_item()
        except RuleError as exc:
            self.app.show_error("无法继续", exc)

    def _advance_completed_item(self) -> None:
        state = self.app.state
        if not state:
            raise RuleError("尚未生成拍卖池")
        self._cancel_timer()
        state.current_index += 1
        state.advance()
        self.update_current()
        self.app.ensure_tab("settlement").refresh()
        if state.auction_complete:
            messagebox.showinfo(
                "拍卖完成",
                "所有干员拍卖结束，可以进入阵容结算。",
                parent=self,
            )
        elif state.current_item() is None:
            next_round = self.next_round_to_prepare()
            self.round_import_var.set(f"当前等待：第 {next_round} 轮选手文件")
            self.seed_var.set(str(random.SystemRandom().randint(100000, 999999999)))
            messagebox.showinfo(
                "本轮完成",
                f"第 {next_round - 1} 轮拍卖已结束。"
                f"请双方完成第 {next_round} 轮选取并导入新文件。",
                parent=self,
            )

    def update_current(self, reset_timer: bool = False) -> None:
        self.schedule_result_render()
        state = self.app.state
        if not state or not state.auction_items:
            self._cancel_timer()
            self.current_avatar_label.configure(image="", text="◇")
            self.current_avatar_label.image = None
            self.current_name_var.set("—")
            self.current_meta_var.set("请先导入双方文件并生成拍卖池")
            self.price_var.set("—")
            self.leader_var.set("尚无出价")
            self.leader_label.grid()
            self.progress_var.set("等待生成拍卖池")
            self._update_leader_visual(None)
            return
        item = state.current_item()
        if not item:
            self._cancel_timer()
            self.current_avatar_label.configure(image="", text="◇")
            self.current_avatar_label.image = None
            if state.auction_complete:
                self.current_name_var.set("拍卖完成")
                self.current_meta_var.set("请进入“阵容结算”登记实际上场干员")
                self.price_var.set("✓")
                self.leader_var.set("")
                self.progress_var.set(f"已完成 {len(state.auction_items)}/{len(state.auction_items)}")
            else:
                next_round = self.next_round_to_prepare()
                self.current_name_var.set(f"等待第 {next_round} 轮选取")
                self.current_meta_var.set("双方分别导出本轮选手文件后，由主办方导入")
                self.price_var.set("—")
                self.leader_var.set("")
                self.progress_var.set(f"已完成前 {next_round - 1} 轮")
            self.leader_label.grid_remove()
            self._update_leader_visual(None)
            return
        operator = self.app.operators[item.operator_id]
        self.leader_label.grid()
        avatar = self.app.assets.avatar(operator, 120)
        self.current_avatar_label.configure(image=avatar, text="")
        self.current_avatar_label.image = avatar
        self.progress_var.set(
            f"第 {item.round_index} 轮 · 第 {state.current_index + 1}/{len(state.auction_items)} 名"
        )
        self.current_name_var.set(operator.name)
        self.current_meta_var.set(
            f"{operator.rarity}★ · {operator.profession}/{operator.branch} · "
            f"起拍 {item.starting_price} 点"
        )
        if item.status == "sold":
            self.price_var.set(f"{item.final_price} 点")
            self.leader_var.set(f"成交给 {self.team_name(item.winner)}")
        elif item.status == "unsold":
            self.price_var.set("流拍")
            self.leader_var.set("无人获得")
        else:
            self.price_var.set(
                f"{item.current_price} 点" if item.current_price is not None else f"{item.starting_price} 点"
            )
            self.leader_var.set(
                f"领先 · {self.team_name(item.leader)}"
                if item.leader
                else "等待首次出价"
            )
        self._update_leader_visual(item.leader)
        try:
            next_price = self.next_price()
            cap = state.config.rules.price_cap
            self.a_bid_var.set(
                f"{self.team_name(PLAYER_A)} · 出价 {next_price} 点"
                if next_price <= cap
                else f"{self.team_name(PLAYER_A)} · 已达封顶"
            )
            self.b_bid_var.set(
                f"{self.team_name(PLAYER_B)} · 出价 {next_price} 点"
                if next_price <= cap
                else f"{self.team_name(PLAYER_B)} · 已达封顶"
            )
        except RuleError:
            self.a_bid_var.set(f"{self.team_name(PLAYER_A)} · 出价")
            self.b_bid_var.set(f"{self.team_name(PLAYER_B)} · 出价")
        self._start_timer(item, force=reset_timer)

    def _update_leader_visual(self, leader: str | None) -> None:
        for player, frame in self.bid_frames.items():
            color = BLUE if player == PLAYER_A else RED
            leading = player == leader
            frame.configure(
                bg=color if leading else PANEL,
                highlightbackground=color if leading else LINE,
                highlightthickness=4 if leading else 1,
            )
            self.bid_buttons[player].configure(
                relief="sunken" if leading else "flat",
            )
        if leader == PLAYER_A:
            self.leader_label.configure(bg=BLUE, fg=HEADER_BG)
        elif leader == PLAYER_B:
            self.leader_label.configure(bg=RED, fg=HEADER_BG)
        else:
            self.leader_label.configure(bg=SURFACE_RAISED, fg=FG)

    def _start_timer(self, item, *, force: bool = False) -> None:
        if item.status not in ("pending", "active"):
            self._cancel_timer()
            return
        token = f"{item.operator_id}:{item.attempt}"
        if (
            not force
            and token == self._timer_operator_id
            and self._timer_job is not None
        ):
            self._update_timer_context(item)
            return
        is_new_attempt = token != self._timer_operator_id
        self._cancel_timer(clear_token=False)
        self._timer_operator_id = token
        timer_seconds = self.auction_timer_seconds()
        self._timer_remaining = timer_seconds
        if is_new_attempt:
            item.record_event("start", detail=f"{timer_seconds}s countdown")
        self._update_timer_context(item)
        self._render_timer()
        self._timer_job = self.after(1000, self._timer_tick)

    def _update_timer_context(self, item) -> None:
        if item.leader:
            waiting = PLAYER_B if item.leader == PLAYER_A else PLAYER_A
            self.timer_context_var.set(f"等待 {self.team_name(waiting)} 响应")
        else:
            self.timer_context_var.set("等待首次出价")

    def _render_timer(self) -> None:
        self.timer_var.set(f"{self._timer_remaining:02d}")
        color = (
            RED
            if self._timer_remaining <= 5
            else ACCENT
            if self._timer_remaining <= 10
            else FG
        )
        self.timer_value_label.configure(fg=color)

    def _timer_tick(self) -> None:
        self._timer_job = None
        state = self.app.state
        item = state.current_item() if state else None
        if not item or item.status not in ("pending", "active"):
            self._cancel_timer()
            return
        token = f"{item.operator_id}:{item.attempt}"
        if token != self._timer_operator_id:
            self._start_timer(item, force=True)
            return
        self._timer_remaining -= 1
        self._render_timer()
        if self._timer_remaining <= 0:
            self._handle_timeout(item)
            return
        self._timer_job = self.after(1000, self._timer_tick)

    def _handle_timeout(self, item) -> None:
        waiting = None
        if item.leader:
            waiting = PLAYER_B if item.leader == PLAYER_A else PLAYER_A
        item.record_event(
            "timeout",
            player=waiting,
            detail=f"{self.auction_timer_seconds()}s no action",
        )
        if item.leader:
            item.award()
        else:
            item.mark_unsold()
        self._advance_completed_item()

    def _cancel_timer(self, *, clear_token: bool = True) -> None:
        if self._timer_job is not None:
            self.after_cancel(self._timer_job)
            self._timer_job = None
        if clear_token:
            self._timer_operator_id = None
        self._timer_remaining = self.auction_timer_seconds()
        self.timer_var.set(f"{self._timer_remaining:02d}")
        self.timer_context_var.set("计时暂停")

    def auction_timer_seconds(self) -> int:
        config = self.app.state.config if self.app.state else self.app.config
        if config is None:
            return 20
        return max(1, int(config.rules.auction_timer_seconds))

    def refresh_auction_results(self) -> None:
        self._result_render_job = None
        buckets = {PLAYER_A: [], PLAYER_B: [], "unsold": []}
        state = self.app.state
        if state:
            for item in state.auction_items:
                if item.status not in ("sold", "unsold"):
                    continue
                operator = self.app.operators.get(item.operator_id)
                if operator is None:
                    continue
                key = item.winner if item.status == "sold" and item.winner else "unsold"
                buckets[key].append((item, operator))

        blue_name = self.team_name(PLAYER_A)
        red_name = self.team_name(PLAYER_B)
        self.result_title_vars[PLAYER_A].set(
            f"蓝方 · {blue_name} · {len(buckets[PLAYER_A])}"
        )
        self.result_title_vars[PLAYER_B].set(
            f"红方 · {red_name} · {len(buckets[PLAYER_B])}"
        )
        self.result_title_vars["unsold"].set(
            f"流拍 · {len(buckets['unsold'])}"
        )
        for key, canvas in self.result_canvases.items():
            self._render_result_canvas(key, canvas, buckets[key])

    def _render_result_canvas(self, key: str, canvas: tk.Canvas, entries) -> None:
        canvas.delete("all")
        canvas.image_refs = []
        width = max(150, canvas.winfo_width())
        padding = 8
        gap = 8
        card_height = 90
        columns = 2 if key != "unsold" and width >= 460 else 1
        card_width = max(
            134,
            (width - padding * 2 - gap * (columns - 1)) // columns,
        )
        if not entries:
            canvas.create_text(
                width / 2,
                70,
                text="暂无记录",
                fill=MUTED,
                font=("Microsoft YaHei UI", 11),
            )
            content_height = 150
        else:
            entries_by_round: dict[int, list[tuple]] = {}
            for item, operator in entries:
                entries_by_round.setdefault(item.round_index, []).append(
                    (item, operator)
                )
            section_accent = (
                BLUE
                if key == PLAYER_A
                else RED
                if key == PLAYER_B
                else MUTED
            )
            y_cursor = padding
            for round_index in sorted(entries_by_round):
                round_entries = entries_by_round[round_index]
                header_height = 34
                canvas.create_rectangle(
                    padding,
                    y_cursor,
                    width - padding,
                    y_cursor + header_height,
                    fill=CONTROL_SELECTED,
                    outline=section_accent,
                    width=1,
                )
                canvas.create_rectangle(
                    padding,
                    y_cursor,
                    padding + 5,
                    y_cursor + header_height,
                    fill=section_accent,
                    outline=section_accent,
                )
                canvas.create_text(
                    padding + 14,
                    y_cursor + header_height / 2,
                    anchor="w",
                    text=f"第 {round_index} 轮",
                    fill=FG,
                    font=("Microsoft YaHei UI", 11, "bold"),
                )
                canvas.create_text(
                    width - padding - 10,
                    y_cursor + header_height / 2,
                    anchor="e",
                    text=f"{len(round_entries)} 名",
                    fill=section_accent,
                    font=("Microsoft YaHei UI", 9, "bold"),
                )
                y_cursor += header_height + gap

                for index, (item, operator) in enumerate(round_entries):
                    row, column = divmod(index, columns)
                    x1 = padding + column * (card_width + gap)
                    y1 = y_cursor + row * (card_height + gap)
                    x2 = x1 + card_width
                    y2 = y1 + card_height
                    tag = f"result-{item.operator_id}"
                    selected = item.operator_id == self.selected_result_operator_id
                    background, _foreground = HOST_RARITY_COLORS.get(
                        operator.rarity,
                        HOST_RARITY_COLORS[1],
                    )
                    accent = AUCTION_RARITY_ACCENTS.get(
                        operator.rarity,
                        AUCTION_RARITY_ACCENTS[1],
                    )
                    canvas.create_rectangle(
                        x1,
                        y1,
                        x2,
                        y2,
                        fill=background,
                        outline=FOCUS if selected else LINE,
                        width=3 if selected else 1,
                        tags=(tag,),
                    )
                    canvas.create_rectangle(
                        x1,
                        y1,
                        x1 + 5,
                        y2,
                        fill=accent,
                        outline=accent,
                        tags=(tag,),
                    )
                    avatar = self.app.assets.avatar(operator, 64)
                    canvas.image_refs.append(avatar)
                    canvas.create_image(
                        x1 + 42,
                        y1 + card_height / 2,
                        image=avatar,
                        tags=(tag,),
                    )
                    canvas.create_text(
                        x1 + 82,
                        y1 + 34,
                        anchor="w",
                        text=card_operator_name(
                            operator.name,
                            7 if card_width < 230 else 10,
                        ),
                        fill=FG,
                        font=("Microsoft YaHei UI", 13, "bold"),
                        tags=(tag,),
                    )
                    price = (
                        f"{item.final_price} 点"
                        if item.final_price is not None
                        else "流拍"
                    )
                    canvas.create_text(
                        x2 - 10,
                        y1 + 20,
                        anchor="ne",
                        text=price,
                        fill=accent,
                        font=("Microsoft YaHei UI", 12, "bold"),
                        tags=(tag,),
                    )
                    if item.attempt > 1:
                        canvas.create_text(
                            x1 + 82,
                            y1 + 65,
                            anchor="w",
                            text=f"重新拍卖 × {item.attempt}",
                            fill=MUTED,
                            font=("Microsoft YaHei UI", 8, "bold"),
                            tags=(tag,),
                        )
                    canvas.tag_bind(
                        tag,
                        "<Button-1>",
                        lambda _event, operator_id=item.operator_id: self.select_result_operator(
                            operator_id
                        ),
                    )
                    canvas.tag_bind(
                        tag,
                        "<Enter>",
                        lambda _event, target=canvas: target.configure(cursor="hand2"),
                    )
                    canvas.tag_bind(
                        tag,
                        "<Leave>",
                        lambda _event, target=canvas: target.configure(cursor=""),
                    )
                rows = math.ceil(len(round_entries) / columns)
                y_cursor += (
                    rows * card_height
                    + max(0, rows - 1) * gap
                    + 14
                )
            content_height = y_cursor + padding
        canvas.configure(scrollregion=(0, 0, width, content_height))
        scrollbar = self.result_scrollbars[key]
        if content_height <= max(1, canvas.winfo_height()):
            scrollbar.grid_remove()
            canvas.yview_moveto(0)
        else:
            scrollbar.grid()

    def select_result_operator(self, operator_id: str) -> None:
        self.selected_result_operator_id = operator_id
        self.reauction_button.configure(
            state="normal",
            fg=FG,
            bg=CONTROL_HOVER,
        )
        self.refresh_auction_results()

    def reauction_selected(self) -> None:
        state = self.app.state
        operator_id = self.selected_result_operator_id
        if not state or not operator_id:
            return
        index = next(
            (
                position
                for position, item in enumerate(state.auction_items)
                if item.operator_id == operator_id
                and item.status in ("sold", "unsold")
            ),
            None,
        )
        if index is None:
            return
        item = state.auction_items[index]
        operator = self.app.operators.get(operator_id)
        name = operator.name if operator else operator_id
        previous = (
            f"{self.team_name(item.winner)} · {item.final_price} 点"
            if item.winner
            else "流拍"
        )
        if not messagebox.askyesno(
            "重新拍卖",
            f"确定重新拍卖“{name}”吗？\n"
            f"原结果：{previous}\n\n"
            "旧出价与时间轴会保留，本次计价将从起拍价重新开始。",
            parent=self,
        ):
            return
        self._cancel_timer()
        item.reset_for_reauction()
        for player in (PLAYER_A, PLAYER_B):
            state.used_operator_ids[player] = [
                value
                for value in state.used_operator_ids.get(player, [])
                if value != operator_id
            ]
        state.current_index = index
        state.advance()
        self.selected_result_operator_id = None
        self.reauction_button.configure(
            state="disabled",
            fg=MUTED,
            bg=SURFACE_RAISED,
        )
        self.update_current(reset_timer=True)
        self.app.ensure_tab("settlement").refresh()

    def save_match(self) -> None:
        if not self.app.state:
            messagebox.showwarning("没有比赛", "当前没有可保存的比赛。", parent=self)
            return
        path = filedialog.asksaveasfilename(
            parent=self,
            title="保存完整比赛",
            defaultextension=".bprace",
            initialfile=f"{safe_file_name(self.app.state.config.title)}_{self.app.state.config.match_id}.bprace",
            filetypes=[("完整比赛存档", "*.bprace"), ("所有文件", "*.*")],
        )
        if not path:
            return
        try:
            save_state(Path(path), self.app.state)
            messagebox.showinfo("保存成功", f"完整比赛已保存：\n{path}", parent=self)
        except OSError as exc:
            self.app.show_error("保存失败", exc)

    def load_from_state(self) -> None:
        if not self.app.state:
            return
        state = self.app.state
        self.submissions = {}
        self.config_var.set(f"{state.config.title}\n{state.config.match_id}")
        next_round = self.next_round_to_prepare()
        self.round_import_var.set(
            "所有轮次已完成" if state.auction_complete else f"当前等待：第 {next_round} 轮选手文件"
        )
        self.seed_var.set(str(random.SystemRandom().randint(100000, 999999999)))
        self.refresh_team_labels()
        self.a_file_var.set(f"{self.team_name(PLAYER_A)}：未导入")
        self.b_file_var.set(f"{self.team_name(PLAYER_B)}：未导入")
        self.update_current()

    def next_round_to_prepare(self) -> int:
        if not self.app.state or not self.app.state.auction_items:
            return 1
        prepared = {item.round_index for item in self.app.state.auction_items}
        for round_index in range(1, self.app.state.config.rules.rounds + 1):
            if round_index not in prepared:
                return round_index
        return self.app.state.config.rules.rounds


class SettlementTab(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, app: BpApplication):
        super().__init__(parent, padding=18)
        self.app = app
        self.a_clear = tk.BooleanVar(value=False)
        self.b_clear = tk.BooleanVar(value=False)
        self.score_adjustment_vars = {
            PLAYER_A: tk.StringVar(value="0"),
            PLAYER_B: tk.StringVar(value="0"),
        }
        self.result_var = tk.StringVar(value="拍卖结束后，在这里登记实际上场阵容。")
        self.player_canvases: dict[str, tk.Canvas] = {}
        self.player_title_vars = {
            PLAYER_A: tk.StringVar(value="A SIDE"),
            PLAYER_B: tk.StringVar(value="B SIDE"),
        }

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, minsize=76)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(1, weight=1)
        title_bar = tk.Frame(self, bg=BG)
        title_bar.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 14))
        title_bar.columnconfigure(0, weight=1)
        settlement_brand = tk.Frame(title_bar, bg=BG)
        settlement_brand.grid(row=0, column=0)
        tk.Label(
            settlement_brand,
            image=self.app.assets.logo(64),
            bg=BG,
            bd=0,
        ).pack(side="left", padx=(0, 12))
        settlement_title = tk.Frame(settlement_brand, bg=BG)
        settlement_title.pack(side="left")
        tk.Label(
            settlement_title,
            text="联锁对抗 · 最终阵容",
            font=("Microsoft YaHei UI", 22, "bold"),
            fg=FG,
            bg=BG,
        ).pack(anchor="w")
        tk.Label(
            settlement_title,
            text="点击获得干员可切换“上场 / 未使用”",
            font=("Microsoft YaHei UI", 10),
            fg=MUTED,
            bg=BG,
        ).pack(anchor="w", pady=(3, 0))

        self._build_player_panel(PLAYER_A, 0, BLUE, self.a_clear)
        versus = tk.Frame(self, bg=BG)
        versus.grid(row=1, column=1, sticky="ns")
        versus.rowconfigure(0, weight=1)
        versus.rowconfigure(2, weight=1)
        tk.Frame(versus, bg=LINE, width=2).grid(row=0, column=0, sticky="ns", padx=37)
        tk.Label(
            versus,
            text="VS",
            font=("Segoe UI", 23, "bold"),
            fg=ACCENT,
            bg=BG,
        ).grid(row=1, column=0, pady=12)
        tk.Frame(versus, bg=LINE, width=2).grid(row=2, column=0, sticky="ns", padx=37)
        self._build_player_panel(PLAYER_B, 2, RED, self.b_clear)

        result = ttk.Frame(self, style="Panel.TFrame", padding=18)
        result.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(14, 0))
        result.columnconfigure(0, weight=1)
        ttk.Label(
            result,
            textvariable=self.result_var,
            style="Panel.TLabel",
            font=("Microsoft YaHei UI", 13, "bold"),
            wraplength=1050,
            justify="left",
        ).grid(row=0, column=0, sticky="w")
        actions = ttk.Frame(result, style="Panel.TFrame")
        actions.grid(row=0, column=1, sticky="e", padx=(12, 0))
        ttk.Button(actions, text="重新计算", style="Accent.TButton", command=self.calculate).pack(
            side="left", padx=4
        )
        ttk.Button(actions, text="导出 CSV 汇总", command=self.export_csv).pack(side="left", padx=4)
        ttk.Button(
            actions,
            text="保存比赛",
            command=self.save_match,
        ).pack(
            side="left", padx=4
        )

    def _build_player_panel(
        self, player: str, column: int, color: str, clear_var: tk.BooleanVar
    ) -> None:
        panel = tk.Frame(
            self,
            bg=PANEL,
            highlightbackground=color,
            highlightthickness=2,
            padx=12,
            pady=12,
        )
        panel.grid(row=1, column=column, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)
        header = tk.Frame(panel, bg=PANEL)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        tk.Label(
            header,
            text=player,
            font=("Segoe UI", 24, "bold"),
            fg="#111820",
            bg=color,
            padx=16,
            pady=4,
        ).pack(side="left")
        tk.Label(
            header,
            textvariable=self.player_title_vars[player],
            font=("Microsoft YaHei UI", 15, "bold"),
            fg=FG,
            bg=PANEL,
        ).pack(side="left", padx=12)
        score_controls = tk.Frame(header, bg=PANEL)
        score_controls.pack(side="right")
        tk.Label(
            score_controls,
            text="分数修正",
            font=("Microsoft YaHei UI", 9, "bold"),
            fg=MUTED,
            bg=PANEL,
        ).grid(row=0, column=0, padx=(0, 6))
        adjustment_entry = ttk.Entry(
            score_controls,
            textvariable=self.score_adjustment_vars[player],
            width=7,
            justify="center",
        )
        adjustment_entry.grid(row=0, column=1, padx=(0, 14))
        adjustment_entry.bind(
            "<Return>", lambda _event: self.apply_score_adjustments()
        )
        tk.Label(
            score_controls,
            text="完美通关",
            font=("Microsoft YaHei UI", 10, "bold"),
            fg=MUTED,
            bg=PANEL,
        ).grid(row=0, column=2, padx=(0, 6))
        ttk.Checkbutton(
            score_controls,
            variable=clear_var,
            command=self.sync_clear,
        ).grid(row=0, column=3)

        canvas = tk.Canvas(
            panel,
            bg=SURFACE,
            highlightthickness=0,
            bd=0,
            yscrollincrement=44,
        )
        settlement_scroll = ttk.Scrollbar(panel, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=settlement_scroll.set)
        canvas.grid(row=1, column=0, sticky="nsew")
        settlement_scroll.grid(row=1, column=1, sticky="ns")
        canvas.bind(
            "<MouseWheel>",
            lambda event, target=canvas: target.yview_scroll(
                -max(-5, min(5, int(event.delta / 120))), "units"
            ),
        )
        canvas.bind("<Configure>", lambda _event, p=player: self.render_player_panel(p))
        self.player_canvases[player] = canvas

    def refresh(self) -> None:
        state = self.app.state
        if state:
            self.a_clear.set(state.perfect_clear.get(PLAYER_A, False))
            self.b_clear.set(state.perfect_clear.get(PLAYER_B, False))
            for player in (PLAYER_A, PLAYER_B):
                value = state.score_adjustments.get(player, 0.0)
                self.score_adjustment_vars[player].set(f"{value:g}")
            self.player_title_vars[PLAYER_A].set(f"A SIDE · {state.config.player_a_name}")
            self.player_title_vars[PLAYER_B].set(f"B SIDE · {state.config.player_b_name}")
        else:
            self.a_clear.set(False)
            self.b_clear.set(False)
            self.score_adjustment_vars[PLAYER_A].set("0")
            self.score_adjustment_vars[PLAYER_B].set("0")
            self.player_title_vars[PLAYER_A].set("A SIDE")
            self.player_title_vars[PLAYER_B].set("B SIDE")
        for player in (PLAYER_A, PLAYER_B):
            self.render_player_panel(player)
        self.update_preview()

    def _player_bp_records(self, player: str) -> tuple[list[str], list[str]]:
        if not self.app.state:
            return [], []
        branches: list[str] = []
        operator_ids: list[str] = []
        for submission in self.app.state.submissions.values():
            if submission.player != player:
                continue
            for branch in submission.banned_branches:
                if branch not in branches:
                    branches.append(branch)
            for operator_id in submission.banned_operator_ids:
                if operator_id not in operator_ids:
                    operator_ids.append(operator_id)
        return branches, operator_ids

    def render_player_panel(self, player: str) -> None:
        canvas = self.player_canvases.get(player)
        if canvas is None:
            return
        canvas.delete("all")
        state = self.app.state
        width = max(470, canvas.winfo_width())
        accent = BLUE if player == PLAYER_A else RED
        padding = 18
        y = 18

        def section_title(title: str, count: int) -> None:
            nonlocal y
            canvas.create_text(
                padding,
                y,
                anchor="nw",
                text=f"{title}   {count}",
                fill=accent,
                font=("Segoe UI", 11, "bold"),
            )
            canvas.create_line(padding, y + 25, width - padding, y + 25, fill=LINE)
            y += 38

        if not state:
            canvas.create_text(
                width // 2,
                110,
                text="尚未载入比赛",
                fill=MUTED,
                font=("Microsoft YaHei UI", 13),
            )
            canvas.configure(scrollregion=(0, 0, width, 260))
            return

        branches, banned_operator_ids = self._player_bp_records(player)
        section_title("SUBCLASS BAN", len(branches))
        if branches:
            branch_width = min(230, max(160, (width - padding * 2 - 10) // max(1, len(branches))))
            for index, branch in enumerate(branches):
                x1 = padding + index * (branch_width + 10)
                branch_id = next(
                    (
                        operator.branch_id
                        for operator in self.app.operators.values()
                        if operator.branch == branch
                    ),
                    "",
                )
                canvas.create_rectangle(
                    x1,
                    y,
                    x1 + branch_width,
                    y + 66,
                    fill=SURFACE_RAISED,
                    outline=accent,
                )
                canvas.create_text(
                    x1 + 34,
                    y + 33,
                    text=self.app.assets.branch_glyph(branch_id),
                    fill=accent,
                    font=(self.app.assets.branch_font_family, 26),
                )
                canvas.create_text(
                    x1 + 65,
                    y + 33,
                    anchor="w",
                    text=branch,
                    fill=FG,
                    font=("Microsoft YaHei UI", 11, "bold"),
                )
            y += 82
        else:
            canvas.create_text(
                padding,
                y + 18,
                anchor="w",
                text="暂无子职业 Ban 记录",
                fill=MUTED,
                font=("Microsoft YaHei UI", 10),
            )
            y += 48

        banned_operators = [
            self.app.operators[operator_id]
            for operator_id in banned_operator_ids
            if operator_id in self.app.operators
        ]
        section_title("OPERATOR BAN", len(banned_operators))
        ban_columns = max(3, min(5, (width - padding * 2) // 96))
        for index, operator in enumerate(banned_operators):
            row, column = divmod(index, ban_columns)
            x = padding + column * ((width - padding * 2) / ban_columns)
            top = y + row * 100
            canvas.create_image(
                x + 40,
                top + 4,
                image=self.app.assets.avatar(operator, 76),
                anchor="n",
            )
            canvas.create_text(
                x + 40,
                top + 82,
                text=operator.name,
                fill=FG,
                font=("Microsoft YaHei UI", 9, "bold"),
            )
        y += max(52, math.ceil(len(banned_operators) / ban_columns) * 100) + 10

        won_items = [item for item in state.auction_items if item.winner == player]
        section_title("AUCTION ROSTER", len(won_items))
        roster_columns = 2 if width >= 560 else 1
        roster_gap = 12
        roster_width = (
            width - padding * 2 - roster_gap * (roster_columns - 1)
        ) / roster_columns
        roster_height = 126
        used_ids = set(state.used_operator_ids.get(player, []))
        for index, item in enumerate(won_items):
            operator = self.app.operators.get(item.operator_id)
            if operator is None:
                continue
            row, column = divmod(index, roster_columns)
            x1 = padding + column * (roster_width + roster_gap)
            y1 = y + row * (roster_height + roster_gap)
            x2 = x1 + roster_width
            y2 = y1 + roster_height
            used = item.operator_id in used_ids
            tag = f"settlement-{player}-{item.operator_id}"
            canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill="#253541" if used else SURFACE_RAISED,
                outline=accent if used else LINE,
                width=3 if used else 1,
                tags=(tag,),
            )
            canvas.create_image(
                x1 + 56,
                y1 + 63,
                image=self.app.assets.avatar(operator, 98),
                tags=(tag,),
            )
            canvas.create_text(
                x1 + 112,
                y1 + 30,
                anchor="w",
                text=operator.name,
                fill=FG,
                font=("Microsoft YaHei UI", 12, "bold"),
                tags=(tag,),
            )
            canvas.create_text(
                x1 + 112,
                y1 + 59,
                anchor="w",
                text=f"{operator.rarity}★ · {operator.branch}",
                fill=PROFESSION_COLORS.get(operator.profession, MUTED),
                font=("Microsoft YaHei UI", 9),
                tags=(tag,),
            )
            canvas.create_text(
                x1 + 112,
                y1 + 93,
                anchor="w",
                text=f"{item.final_price} 点  ·  第 {item.round_index} 轮",
                fill=ACCENT,
                font=("Microsoft YaHei UI", 10, "bold"),
                tags=(tag,),
            )
            canvas.create_text(
                x2 - 12,
                y1 + 18,
                anchor="ne",
                text="上场" if used else "未使用",
                fill=GREEN if used else MUTED,
                font=("Microsoft YaHei UI", 9, "bold"),
                tags=(tag,),
            )
            canvas.tag_bind(
                tag,
                "<Button-1>",
                lambda _event, p=player, operator_id=item.operator_id: self.toggle_used(
                    p, operator_id
                ),
            )
        roster_rows = math.ceil(len(won_items) / roster_columns)
        total_height = y + max(90, roster_rows * (roster_height + roster_gap)) + 18
        canvas.configure(scrollregion=(0, 0, width, total_height))

    def toggle_used(self, player: str, operator_id: str) -> None:
        if not self.app.state:
            return
        if not self.apply_score_adjustments(show_error=False):
            return
        used = self.app.state.used_operator_ids.setdefault(player, [])
        if operator_id in used:
            used.remove(operator_id)
        else:
            used.append(operator_id)
        self.refresh()

    def sync_clear(self) -> None:
        if self.app.state:
            self.app.state.perfect_clear[PLAYER_A] = self.a_clear.get()
            self.app.state.perfect_clear[PLAYER_B] = self.b_clear.get()
            self.apply_score_adjustments(show_error=False)
        self.update_preview()

    def apply_score_adjustments(self, show_error: bool = True) -> bool:
        if not self.app.state:
            return True
        parsed: dict[str, float] = {}
        try:
            for player in (PLAYER_A, PLAYER_B):
                raw = self.score_adjustment_vars[player].get().strip()
                value = float(raw or "0")
                if not math.isfinite(value):
                    raise ValueError
                parsed[player] = value
        except ValueError:
            if show_error:
                messagebox.showwarning(
                    "分数修正无效",
                    "分数修正必须是有限数字，可填写正数、负数或 0。",
                    parent=self,
                )
            return False
        self.app.state.score_adjustments.update(parsed)
        self.update_preview()
        return True

    def update_preview(self) -> None:
        state = self.app.state
        if not state or not state.auction_items:
            self.result_var.set("拍卖结束后，在这里登记实际上场阵容。")
            return
        a = state.calculate_score(PLAYER_A)
        b = state.calculate_score(PLAYER_B)
        self.result_var.set(
            f"A 方：使用 {a['used_cost']:g} + 未使用折算 {a['bench_weighted_cost']:g} "
            f"+ 修正 {a['adjustment']:+g} = {a['total']:g} 点\n"
            f"B 方：使用 {b['used_cost']:g} + 未使用折算 {b['bench_weighted_cost']:g} "
            f"+ 修正 {b['adjustment']:+g} = {b['total']:g} 点"
        )

    def calculate(self) -> None:
        try:
            if not self.app.state or not self.app.state.auction_complete:
                raise RuleError("必须先完成全部干员的拍卖")
            if not self.apply_score_adjustments():
                return
            self.sync_clear()
            result = self.app.state.result()
            winner_text = f"{result['winner']} 方获胜" if result["winner"] else "无胜者 / 平局"
            a, b = result[PLAYER_A], result[PLAYER_B]
            self.result_var.set(
                f"{winner_text}：{result['reason']}。\n"
                f"A 方：{a['base_total']:g} {a['adjustment']:+g} = {a['total']:g} 点\n"
                f"B 方：{b['base_total']:g} {b['adjustment']:+g} = {b['total']:g} 点"
            )
        except RuleError as exc:
            self.app.show_error("无法结算", exc)

    def export_csv(self) -> None:
        try:
            if not self.app.state or not self.app.state.auction_complete:
                raise RuleError("必须先完成全部干员的拍卖")
            if not self.apply_score_adjustments():
                return
            self.sync_clear()
            path = filedialog.asksaveasfilename(
                parent=self,
                title="导出赛后汇总",
                defaultextension=".csv",
                initialfile=(
                    f"{safe_file_name(self.app.state.config.title)}_"
                    f"{self.app.state.config.match_id}_结果.csv"
                ),
                filetypes=[("CSV 表格", "*.csv"), ("所有文件", "*.*")],
            )
            if path:
                export_results_csv(Path(path), self.app.state, self.app.operators)
                messagebox.showinfo("导出成功", f"赛后汇总已保存：\n{path}", parent=self)
        except (RuleError, OSError) as exc:
            self.app.show_error("导出失败", exc)

    def save_match(self) -> None:
        if not self.apply_score_adjustments():
            return
        self.sync_clear()
        self.app.ensure_tab("auction").save_match()

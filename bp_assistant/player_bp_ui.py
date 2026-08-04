from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .core import MatchConfig, Operator, RuleError
from .pre_match_bp import MODE_BAN, MODE_BLUE, MODE_RED, PreMatchBpState
from .storage import load_config, operator_values, save_config
from .ui import (
    ACCENT,
    AssetManager,
    BAN_BADGE,
    BAN_BORDER,
    BAN_CARD,
    BG,
    BLUE,
    FG,
    LINE,
    MUTED,
    PANEL,
    PROFESSION_COLORS,
    RED,
    SURFACE,
    SURFACE_RAISED,
)


# Player edition design tokens: a restrained "night operations" palette.
# These intentionally override the shared host-console colors imported above so
# this application can evolve independently without changing the main program.
FONT = "Microsoft YaHei UI"
BG = "#09111B"
HEADER_BG = "#070D14"
PANEL = "#101C29"
SURFACE = "#0D1722"
SURFACE_RAISED = "#192A3A"
LINE = "#283A4D"
FG = "#F3F7FC"
MUTED = "#91A3B7"
ACCENT = "#F0B44C"
ACCENT_HOVER = "#FFD173"
ACCENT_SOFT = "#6B542C"
BLUE = "#5AAEFF"
RED = "#FF737B"
BAN_BADGE = "#FF8B72"
BAN_CARD = "#35232A"
BAN_BORDER = "#E26F72"
GLOBAL_CARD = "#202B37"
GLOBAL_BORDER = "#718399"
BLUE_CARD = "#142E45"
BLUE_BORDER = "#5AAEFF"
RED_CARD = "#3A222A"
RED_BORDER = "#FF737B"
HOVER_BORDER = "#A9BCD0"
CONTROL_HOVER = "#24384B"
CONTROL_SELECTED = "#31465B"
DELETE_BG = "#252C36"
DELETE_HOVER = "#41303A"
PROFESSION_COLORS = {
    "先锋": "#56C8B7",
    "近卫": "#FF817A",
    "狙击": "#69B6F2",
    "重装": "#E7B75E",
    "医疗": "#6ED09A",
    "辅助": "#B892EA",
    "术师": "#978BEF",
    "特种": "#DE8DB8",
}
RARITY_COLORS = {
    6: ("#33262B", "#F7E9EC"),
    5: ("#302D23", "#F1E7C8"),
    4: ("#29263A", "#E8E0F6"),
    3: ("#202D3B", "#DDEBFA"),
    2: ("#202A34", "#E5EBF1"),
    1: ("#202A34", "#E5EBF1"),
}


class ModernDropdown(ttk.Combobox):
    """稳定的只读下拉框，使用原生弹层避免焦点闪退。"""

    def __init__(
        self,
        parent: tk.Misc,
        values: list[str],
        value: str,
        width: int = 170,
        command=None,
    ):
        self.variable = tk.StringVar(value=value)
        self.command = command
        super().__init__(
            parent,
            values=values,
            textvariable=self.variable,
            state="readonly",
            style="Modern.TCombobox",
            width=max(10, width // 10),
            height=min(14, max(6, len(values))),
        )
        self.values = list(values)
        self.bind("<<ComboboxSelected>>", self._selected)

    def _selected(self, _event=None) -> None:
        if self.command:
            self.command(self.get())

    def set(self, value: str, invoke: bool = False) -> None:
        if value not in self.values and self.values:
            value = self.values[0]
        self.variable.set(value)
        if invoke and self.command:
            self.command(value)

    def set_values(self, values: list[str], keep_value: bool = True) -> None:
        old_value = self.get()
        self.values = list(values)
        self.configure(values=self.values, height=min(14, max(6, len(values))))
        if not keep_value or old_value not in self.values:
            self.set(self.values[0] if self.values else "")


class GlobalBanEditor(tk.Toplevel):
    """Edit global operator/branch bans from an imported match config."""

    def __init__(self, app: "PlayerBpApplication"):
        super().__init__(app)
        self.app = app
        self.operator_ids = set(app.state.global_banned_operator_ids)
        self.branches = set(app.state.global_banned_branches)
        self.title("全局 Ban 管理")
        self.configure(bg=BG)
        self.geometry("1180x760")
        self.minsize(960, 640)
        self.transient(app)
        self.grab_set()
        try:
            self.iconphoto(True, app.assets.logo(64))
        except tk.TclError:
            pass
        self._build()
        self._refresh_available()
        self._refresh_banned()

    def _build(self) -> None:
        header = tk.Frame(self, bg=HEADER_BG, padx=20, pady=14)
        header.pack(fill="x")
        tk.Label(
            header,
            text="全局 Ban 管理",
            bg=HEADER_BG,
            fg=ACCENT,
            font=(FONT, 18, "bold"),
        ).pack(side="left")
        tk.Label(
            header,
            text="修改导入配置中的全局干员与分支 Ban",
            bg=HEADER_BG,
            fg=MUTED,
            font=(FONT, 9),
        ).pack(side="left", padx=18)

        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=14, pady=12)
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=2)
        main.grid_rowconfigure(0, weight=1)

        available = tk.Frame(
            main, bg=PANEL, highlightthickness=1, highlightbackground=LINE
        )
        available.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        available_head = tk.Frame(available, bg=PANEL, padx=12, pady=10)
        available_head.pack(fill="x")
        tk.Label(
            available_head,
            text="全部干员",
            bg=PANEL,
            fg=FG,
            font=(FONT, 13, "bold"),
        ).pack(side="left")
        self.search_var = tk.StringVar()
        search = tk.Entry(
            available_head,
            textvariable=self.search_var,
            bg=SURFACE_RAISED,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            bd=0,
            width=24,
            font=(FONT, 10),
        )
        search.pack(side="right", ipady=7)
        search.bind("<KeyRelease>", lambda _e: self._refresh_available())

        available_body = tk.Frame(available, bg=PANEL)
        available_body.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.available_tree = ttk.Treeview(
            available_body,
            show="tree",
            selectmode="browse",
            style="Bp.Treeview",
        )
        available_scroll = ttk.Scrollbar(
            available_body,
            orient="vertical",
            command=self.available_tree.yview,
            style="Modern.Vertical.TScrollbar",
        )
        self.available_tree.configure(yscrollcommand=available_scroll.set)
        self.available_tree.column("#0", width=570, stretch=True)
        self.available_tree.pack(side="left", fill="both", expand=True)
        available_scroll.pack(side="right", fill="y")
        self.available_tree.tag_configure(
            "global", background="#38272E", foreground="#FFD9DC"
        )
        self.available_tree.bind("<Double-1>", lambda _e: self._add_operator())
        tk.Button(
            available,
            text="加入全局 Ban",
            command=self._add_operator,
            bg=ACCENT,
            fg=HEADER_BG,
            activebackground=ACCENT_HOVER,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(FONT, 10, "bold"),
            pady=9,
        ).pack(fill="x", padx=8, pady=(0, 8))

        selected = tk.Frame(
            main, bg=PANEL, highlightthickness=1, highlightbackground=LINE
        )
        selected.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        tk.Label(
            selected,
            text="当前全局 Ban",
            bg=PANEL,
            fg=FG,
            font=(FONT, 13, "bold"),
            padx=12,
            pady=10,
            anchor="w",
        ).pack(fill="x")

        banned_body = tk.Frame(selected, bg=PANEL)
        banned_body.pack(fill="both", expand=True, padx=8)
        self.banned_tree = ttk.Treeview(
            banned_body,
            show="tree",
            selectmode="browse",
            style="Bp.Treeview",
            height=7,
        )
        banned_scroll = ttk.Scrollbar(
            banned_body,
            orient="vertical",
            command=self.banned_tree.yview,
            style="Modern.Vertical.TScrollbar",
        )
        self.banned_tree.configure(yscrollcommand=banned_scroll.set)
        self.banned_tree.column("#0", width=400, stretch=True)
        self.banned_tree.pack(side="left", fill="both", expand=True)
        banned_scroll.pack(side="right", fill="y")
        self.banned_tree.bind("<Double-1>", lambda _e: self._remove_operator())

        tk.Button(
            selected,
            text="移除所选干员",
            command=self._remove_operator,
            bg=SURFACE_RAISED,
            fg=FG,
            activebackground=CONTROL_HOVER,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(FONT, 9),
            pady=8,
        ).pack(fill="x", padx=8, pady=8)

        branch_box = tk.Frame(
            selected, bg=SURFACE, highlightthickness=1, highlightbackground=LINE
        )
        branch_box.pack(fill="x", padx=8, pady=(0, 8))
        tk.Label(
            branch_box,
            text="全局分支 Ban",
            bg=SURFACE,
            fg=FG,
            font=(FONT, 11, "bold"),
            padx=10,
            pady=8,
            anchor="w",
        ).pack(fill="x")
        branch_controls = tk.Frame(branch_box, bg=SURFACE)
        branch_controls.pack(fill="x", padx=8, pady=(0, 8))
        all_branches = operator_values(self.app.operator_list, "branch")
        self.branch_dropdown = ModernDropdown(
            branch_controls,
            all_branches,
            all_branches[0] if all_branches else "",
            190,
        )
        self.branch_dropdown.pack(side="left", fill="x", expand=True)
        tk.Button(
            branch_controls,
            text="加入",
            command=self._add_branch,
            bg=ACCENT,
            fg=HEADER_BG,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(FONT, 9, "bold"),
            padx=12,
            pady=8,
        ).pack(side="right", padx=(8, 0))
        self.branch_list = tk.Listbox(
            branch_box,
            bg=SURFACE,
            fg=FG,
            selectbackground=CONTROL_SELECTED,
            selectforeground=FG,
            relief="flat",
            bd=0,
            highlightthickness=0,
            height=5,
            font=(FONT, 10),
        )
        self.branch_list.pack(fill="x", padx=8)
        tk.Button(
            branch_box,
            text="移除所选分支",
            command=self._remove_branch,
            bg=SURFACE_RAISED,
            fg=MUTED,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(FONT, 9),
            pady=7,
        ).pack(fill="x", padx=8, pady=8)

        actions = tk.Frame(self, bg=HEADER_BG, padx=16, pady=12)
        actions.pack(fill="x")
        tk.Button(
            actions,
            text="取消",
            command=self.destroy,
            bg=SURFACE_RAISED,
            fg=FG,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(FONT, 10),
            padx=20,
            pady=9,
        ).pack(side="right")
        tk.Button(
            actions,
            text="应用到当前 BP",
            command=self._apply,
            bg=BLUE,
            fg=HEADER_BG,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(FONT, 10, "bold"),
            padx=20,
            pady=9,
        ).pack(side="right", padx=8)
        tk.Button(
            actions,
            text="应用并重新导出配置",
            command=self._apply_and_export,
            bg=ACCENT,
            fg=HEADER_BG,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(FONT, 10, "bold"),
            padx=20,
            pady=9,
        ).pack(side="right")

    def _refresh_available(self) -> None:
        search = self.search_var.get().strip().casefold()
        self.available_tree.delete(*self.available_tree.get_children())
        for operator in self.app.operator_list:
            haystack = (
                f"{operator.name} {operator.profession} {operator.branch}".casefold()
            )
            if search and search not in haystack:
                continue
            avatar = self.app.assets.avatar(operator, 44)
            tags = ("global",) if operator.operator_id in self.operator_ids else ()
            self.available_tree.insert(
                "",
                "end",
                iid=operator.operator_id,
                image=avatar,
                text=(
                    f"  {operator.name}   {operator.rarity}★  ·  "
                    f"{operator.profession}  ·  {operator.branch}"
                ),
                tags=tags,
            )

    def _refresh_banned(self) -> None:
        self.banned_tree.delete(*self.banned_tree.get_children())
        for operator_id in sorted(
            self.operator_ids,
            key=lambda item: self.app.operators[item].name
            if item in self.app.operators
            else item,
        ):
            operator = self.app.operators.get(operator_id)
            if not operator:
                continue
            avatar = self.app.assets.avatar(operator, 44)
            self.banned_tree.insert(
                "",
                "end",
                iid=operator_id,
                image=avatar,
                text=f"  {operator.name}   {operator.rarity}★  ·  {operator.branch}",
            )
        self.branch_list.delete(0, "end")
        for branch in sorted(self.branches):
            self.branch_list.insert("end", branch)

    def _add_operator(self) -> None:
        selection = self.available_tree.selection()
        if not selection:
            return
        self.operator_ids.add(selection[0])
        self._refresh_available()
        self._refresh_banned()

    def _remove_operator(self) -> None:
        selection = self.banned_tree.selection()
        if not selection:
            return
        self.operator_ids.discard(selection[0])
        self._refresh_available()
        self._refresh_banned()

    def _add_branch(self) -> None:
        branch = self.branch_dropdown.get()
        if branch:
            self.branches.add(branch)
            self._refresh_banned()

    def _remove_branch(self) -> None:
        selection = self.branch_list.curselection()
        if not selection:
            return
        self.branches.discard(self.branch_list.get(selection[0]))
        self._refresh_banned()

    def _apply(self, close: bool = True) -> None:
        self.app.apply_global_bans(self.operator_ids, self.branches)
        if close:
            self.destroy()

    def _apply_and_export(self) -> None:
        self._apply(close=False)
        if self.app.export_modified_config():
            self.destroy()


class PlayerBpApplication(tk.Tk):
    def __init__(self, operators: dict[str, Operator], asset_root: Path):
        super().__init__()
        self.operators = operators
        self.operator_list = sorted(
            operators.values(),
            key=lambda item: (-item.rarity, item.profession, item.name),
        )
        self.assets = AssetManager(self, asset_root)
        self.state = PreMatchBpState()
        self.current_mode = MODE_BAN
        self.selected_operator_id: str | None = None
        self.config_path: Path | None = None
        self.loaded_config: MatchConfig | None = None
        self.card_columns = 0
        self.filtered_cache: list[Operator] = []
        self.card_border_items: dict[str, int] = {}
        self.card_row_height = 184
        self.card_width = 168
        self.visible_row_range = (-1, -1)
        self.scroll_velocity = 0.0
        self.scroll_animation_job: str | None = None
        self.visible_render_job: str | None = None
        self.board_trees: dict[str, ttk.Treeview] = {}
        self.board_count_vars: dict[str, tk.StringVar] = {}

        self.title("联锁对抗 · 选手赛前 BP")
        self._configure_window()
        self._configure_style()
        self._build_header()
        self._build_toolbar()
        self._build_main_area()
        self.refresh_all()

    def _configure_window(self) -> None:
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
        try:
            dpi = self.winfo_fpixels("1i")
            if dpi > 0:
                self.tk.call("tk", "scaling", dpi / 72.0)
        except tk.TclError:
            pass
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = min(1840, max(1260, int(screen_width * 0.94)))
        height = min(1260, max(800, int(screen_height * 0.95)))
        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(1180, 760)
        self.configure(bg=BG)

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=(FONT, 10))
        style.configure(
            "Modern.Vertical.TScrollbar",
            gripcount=0,
            background="#536A82",
            darkcolor="#536A82",
            lightcolor="#536A82",
            troughcolor="#142231",
            bordercolor="#142231",
            arrowcolor="#C4D0DC",
            relief="flat",
            borderwidth=0,
            width=14,
        )
        style.map(
            "Modern.Vertical.TScrollbar",
            background=[("active", "#7890A8"), ("pressed", ACCENT)],
        )
        style.configure(
            "Modern.TCombobox",
            fieldbackground=SURFACE_RAISED,
            background=SURFACE_RAISED,
            foreground=FG,
            arrowcolor=MUTED,
            bordercolor=LINE,
            lightcolor=LINE,
            darkcolor=LINE,
            padding=(10, 8),
            arrowsize=18,
        )
        style.map(
            "Modern.TCombobox",
            fieldbackground=[("readonly", SURFACE_RAISED)],
            foreground=[("readonly", FG)],
            background=[("readonly", SURFACE_RAISED), ("active", CONTROL_HOVER)],
            arrowcolor=[("readonly", MUTED), ("active", ACCENT)],
            bordercolor=[("focus", ACCENT), ("readonly", LINE)],
        )
        self.option_add("*TCombobox*Listbox.background", SURFACE)
        self.option_add("*TCombobox*Listbox.foreground", FG)
        self.option_add("*TCombobox*Listbox.selectBackground", CONTROL_SELECTED)
        self.option_add("*TCombobox*Listbox.selectForeground", FG)
        self.option_add("*TCombobox*Listbox.font", (FONT, 10))
        style.configure(
            "Bp.Treeview",
            background=SURFACE,
            fieldbackground=SURFACE,
            foreground=FG,
            rowheight=66,
            borderwidth=0,
            relief="flat",
            font=(FONT, 11),
        )
        style.configure(
            "BpLarge.Treeview",
            background=SURFACE,
            fieldbackground=SURFACE,
            foreground=FG,
            rowheight=88,
            borderwidth=0,
            relief="flat",
            font=(FONT, 12, "bold"),
        )
        style.map(
            "BpLarge.Treeview",
            background=[("selected", CONTROL_SELECTED)],
            foreground=[("selected", FG)],
        )
        style.map(
            "Bp.Treeview",
            background=[("selected", CONTROL_SELECTED)],
            foreground=[("selected", FG)],
        )

    def _build_header(self) -> None:
        header = tk.Frame(self, bg=HEADER_BG, height=108)
        header.pack(fill="x")
        header.pack_propagate(False)
        brand = tk.Frame(header, bg=HEADER_BG)
        brand.pack(side="left", padx=24, pady=10, fill="y")
        logo = self.assets.logo(64)
        tk.Label(brand, image=logo, bg=HEADER_BG, bd=0).pack(
            side="left", padx=(0, 14)
        )
        text = tk.Frame(brand, bg=HEADER_BG)
        text.pack(side="left", anchor="center")
        tk.Label(
            text,
            text="LINKED OPS",
            font=("Segoe UI", 10, "bold"),
            fg=MUTED,
            bg=HEADER_BG,
        ).pack(anchor="w")
        tk.Label(
            text,
            text="选手赛前 BP",
            font=(FONT, 20, "bold"),
            fg=ACCENT,
            bg=HEADER_BG,
        ).pack(anchor="w", pady=(1, 0))
        tk.Label(
            text,
            text="红蓝双方即时共用 · Ban / Pick 数量不限",
            font=(FONT, 9),
            fg=MUTED,
            bg=HEADER_BG,
        ).pack(anchor="w", pady=(2, 0))

        info = tk.Frame(header, bg=HEADER_BG)
        info.pack(side="right", padx=24, pady=16)
        self.match_var = tk.StringVar(value="尚未导入比赛配置")
        self.players_var = tk.StringVar(value="蓝方  —    VS    —  红方")
        tk.Label(
            info,
            textvariable=self.match_var,
            font=(FONT, 10, "bold"),
            fg=FG,
            bg=HEADER_BG,
            anchor="e",
        ).pack(anchor="e")
        tk.Label(
            info,
            textvariable=self.players_var,
            font=(FONT, 10),
            fg=MUTED,
            bg=HEADER_BG,
            anchor="e",
        ).pack(anchor="e", pady=(6, 0))
        tk.Frame(self, bg=ACCENT, height=3).pack(fill="x")

    def _build_toolbar(self) -> None:
        toolbar = tk.Frame(
            self,
            bg=PANEL,
            padx=16,
            pady=12,
            highlightthickness=1,
            highlightbackground=LINE,
        )
        toolbar.pack(fill="x", padx=14, pady=(12, 8))
        tk.Button(
            toolbar,
            text="导入比赛配置",
            command=self.import_match_config,
            bg=ACCENT,
            fg=HEADER_BG,
            activebackground=ACCENT_HOVER,
            activeforeground=HEADER_BG,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(FONT, 11, "bold"),
            padx=18,
            pady=9,
        ).pack(side="left", padx=(0, 16))
        tk.Button(
            toolbar,
            text="全局 Ban 管理",
            command=self.open_global_ban_editor,
            bg=SURFACE_RAISED,
            fg=ACCENT,
            activebackground=CONTROL_HOVER,
            activeforeground=ACCENT_HOVER,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(FONT, 10, "bold"),
            padx=14,
            pady=9,
        ).pack(side="left", padx=(0, 14))

        tk.Label(toolbar, text="搜索", bg=PANEL, fg=MUTED, font=(FONT, 9)).pack(
            side="left", padx=(0, 6)
        )
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            toolbar,
            textvariable=self.search_var,
            bg=SURFACE_RAISED,
            fg=FG,
            insertbackground=FG,
            selectbackground=CONTROL_SELECTED,
            highlightthickness=1,
            highlightbackground=LINE,
            highlightcolor=ACCENT,
            relief="flat",
            bd=0,
            font=(FONT, 10),
            width=18,
        )
        search_entry.pack(side="left", ipady=10, padx=(0, 12))
        search_entry.bind("<KeyRelease>", lambda _e: self.refresh_cards())

        rarities = ["全部星级"] + [
            f"{item} 星"
            for item in sorted(
                {operator.rarity for operator in self.operator_list}, reverse=True
            )
        ]
        professions = ["全部职业"] + operator_values(
            self.operator_list, "profession"
        )
        branches = ["全部分支"] + operator_values(self.operator_list, "branch")
        self.rarity_dropdown = ModernDropdown(
            toolbar, rarities, "全部星级", 138, lambda _v: self.refresh_cards()
        )
        self.rarity_dropdown.pack(side="left", padx=5)
        self.profession_dropdown = ModernDropdown(
            toolbar, professions, "全部职业", 150, self._profession_changed
        )
        self.profession_dropdown.pack(side="left", padx=5)
        self.branch_dropdown = ModernDropdown(
            toolbar, branches, "全部分支", 190, lambda _v: self.refresh_cards()
        )
        self.branch_dropdown.pack(side="left", padx=5)

        self.filter_count_var = tk.StringVar()
        tk.Label(
            toolbar,
            textvariable=self.filter_count_var,
            bg=PANEL,
            fg=MUTED,
            font=(FONT, 9),
        ).pack(side="right", padx=8)

    def _build_main_area(self) -> None:
        main = tk.PanedWindow(
            self,
            orient="horizontal",
            bg="#1A2B3C",
            sashwidth=7,
            sashrelief="flat",
            bd=0,
            relief="flat",
        )
        main.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.left_panel = tk.Frame(
            main, bg=PANEL, bd=0, highlightthickness=1, highlightbackground=LINE
        )
        self.right_panel = tk.Frame(
            main,
            bg=PANEL,
            bd=0,
            width=620,
            highlightthickness=1,
            highlightbackground=LINE,
        )
        main.add(self.left_panel, minsize=610, stretch="always")
        main.add(self.right_panel, minsize=500, stretch="always")
        self.after_idle(
            lambda: main.sash_place(0, int(self.winfo_width() * 0.46), 0)
        )
        self._build_operator_archive()
        self._build_bp_board()

    def _build_operator_archive(self) -> None:
        head = tk.Frame(self.left_panel, bg=PANEL, padx=14, pady=12)
        head.pack(fill="x")
        tk.Label(
            head,
            text="干员档案",
            bg=PANEL,
            fg=FG,
            font=(FONT, 17, "bold"),
        ).pack(side="left")
        tk.Label(
            head,
            text="单击选择 · 双击加入当前 BP 模式",
            bg=PANEL,
            fg=MUTED,
            font=(FONT, 9),
        ).pack(side="right")

        body = tk.Frame(self.left_panel, bg=PANEL)
        body.pack(fill="both", expand=True, padx=(10, 6), pady=(0, 10))
        self.card_canvas = tk.Canvas(body, bg=PANEL, highlightthickness=0, bd=0)
        self.card_scrollbar = ttk.Scrollbar(
            body,
            orient="vertical",
            command=self._card_yview,
            style="Modern.Vertical.TScrollbar",
        )
        self.card_canvas.configure(yscrollcommand=self._card_scroll_changed)
        self.card_canvas.pack(side="left", fill="both", expand=True)
        self.card_scrollbar.pack(side="right", fill="y", padx=(5, 0))
        self.card_canvas.bind("<Configure>", self._cards_canvas_resized)
        self.card_canvas.bind("<MouseWheel>", self._smooth_mousewheel)
        self.card_canvas.bind("<Button-4>", lambda _e: self._queue_scroll(-90))
        self.card_canvas.bind("<Button-5>", lambda _e: self._queue_scroll(90))

        footer = tk.Frame(
            self.left_panel,
            bg=SURFACE,
            padx=12,
            pady=10,
            highlightthickness=1,
            highlightbackground=LINE,
        )
        footer.pack(fill="x", padx=10, pady=(0, 10))
        self.selection_var = tk.StringVar(value="尚未选择干员")
        tk.Label(
            footer,
            textvariable=self.selection_var,
            bg=SURFACE,
            fg=FG,
            font=(FONT, 10),
            anchor="w",
        ).pack(side="left", fill="x", expand=True)
        tk.Button(
            footer,
            text="加入当前模式",
            command=self.add_selected_operator,
            bg=ACCENT,
            fg=HEADER_BG,
            activebackground=ACCENT_HOVER,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(FONT, 10, "bold"),
            padx=18,
            pady=8,
        ).pack(side="right")

    def _build_bp_board(self) -> None:
        head = tk.Frame(self.right_panel, bg=PANEL, padx=16, pady=10)
        head.pack(fill="x", pady=(4, 0))
        tk.Label(
            head,
            text="赛前 BP 看板",
            bg=PANEL,
            fg=FG,
            font=(FONT, 18, "bold"),
        ).pack(side="left")

        modes = tk.Frame(self.right_panel, bg=PANEL, padx=14, pady=4)
        modes.pack(fill="x")
        self.mode_buttons: dict[str, tk.Button] = {}
        for mode, text, color in (
            (MODE_BLUE, "蓝方 PICK", BLUE),
            (MODE_BAN, "选手 BAN", BAN_BADGE),
            (MODE_RED, "红方 PICK", RED),
        ):
            button = tk.Button(
                modes,
                text=text,
                command=lambda target=mode: self.set_mode(target),
                bg=SURFACE_RAISED,
                fg=color,
                activebackground=CONTROL_HOVER,
                activeforeground=color,
                relief="flat",
                bd=0,
                cursor="hand2",
                font=(FONT, 11, "bold"),
                padx=14,
                pady=12,
            )
            button.pack(side="left", fill="x", expand=True, padx=4)
            self.mode_buttons[mode] = button

        imported = tk.Frame(
            self.right_panel,
            bg=SURFACE,
            highlightthickness=1,
            highlightbackground=LINE,
        )
        imported.pack(fill="x", padx=18, pady=(10, 8))
        tk.Frame(imported, bg=ACCENT_SOFT, height=2).pack(fill="x")
        self.branch_ban_var = tk.StringVar(value="配置分支 Ban：无")
        tk.Label(
            imported,
            textvariable=self.branch_ban_var,
            bg=SURFACE,
            fg=MUTED,
            font=(FONT, 9),
            justify="left",
            anchor="w",
            padx=12,
            pady=9,
            wraplength=530,
        ).pack(fill="x")

        board = tk.Frame(self.right_panel, bg=PANEL)
        board.pack(fill="both", expand=True, padx=14, pady=(0, 8))
        for column in range(3):
            board.grid_columnconfigure(column, weight=1, uniform="bp-strips")
        board.grid_rowconfigure(0, weight=1)
        self._build_board_section(
            board, MODE_BLUE, "蓝方 PICK", BLUE, 0, 0, 1
        )
        self._build_board_section(
            board, MODE_BAN, "选手 BAN", BAN_BADGE, 0, 1, 1
        )
        self._build_board_section(
            board, MODE_RED, "红方 PICK", RED, 0, 2, 1
        )

    def _build_board_section(
        self,
        parent: tk.Frame,
        mode: str,
        title: str,
        color: str,
        row: int,
        column: int,
        columnspan: int,
    ) -> None:
        section = tk.Frame(
            parent,
            bg=SURFACE,
            highlightthickness=1,
            highlightbackground=color,
        )
        section.grid(
            row=row,
            column=column,
            columnspan=columnspan,
            sticky="nsew",
            padx=4,
            pady=4,
        )
        tk.Frame(section, bg=color, height=3).pack(fill="x")
        head = tk.Frame(section, bg=SURFACE, padx=10, pady=8)
        head.pack(fill="x")
        tk.Label(
            head,
            text=title,
            bg=SURFACE,
            fg=color,
            font=(FONT, 12, "bold"),
        ).pack(side="left")
        tk.Button(
            head,
            text="清空",
            command=lambda target=mode: self.clear_board_group(target),
            bg=DELETE_BG,
            fg="#FFB8B5" if mode == MODE_BAN else color,
            activebackground=DELETE_HOVER,
            activeforeground=FG,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(FONT, 8, "bold"),
            padx=9,
            pady=4,
        ).pack(side="left", padx=(8, 0))
        count_var = tk.StringVar(value="0 名")
        self.board_count_vars[mode] = count_var
        tk.Label(
            head,
            textvariable=count_var,
            bg=SURFACE,
            fg=MUTED,
            font=(FONT, 9),
        ).pack(side="right")

        tree_body = tk.Frame(section, bg=SURFACE)
        tree_body.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        tree = ttk.Treeview(
            tree_body,
            show="tree",
            selectmode="browse",
            style="BpLarge.Treeview",
        )
        scrollbar = ttk.Scrollbar(
            tree_body,
            orient="vertical",
            command=tree.yview,
            style="Modern.Vertical.TScrollbar",
        )
        tree.configure(yscrollcommand=scrollbar.set)
        tree.column("#0", minwidth=120, width=250, stretch=True)
        for rarity, (background, foreground) in RARITY_COLORS.items():
            tree.tag_configure(
                f"rarity-{rarity}",
                background=background,
                foreground=foreground,
                font=(FONT, 12, "bold"),
            )
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y", padx=(4, 0))
        tree.bind(
            "<Double-1>", lambda _e, target=mode: self.remove_board_item(target)
        )
        self._bind_mousewheel(tree, tree)
        self.board_trees[mode] = tree

    def _bind_mousewheel(self, widget: tk.Misc, target) -> None:
        def scroll(event):
            delta = -1 if event.delta > 0 else 1
            target.yview_scroll(delta, "units")
            return "break"

        widget.bind("<MouseWheel>", scroll)

    def _card_yview(self, *args) -> None:
        self.card_canvas.yview(*args)
        self._schedule_visible_render()

    def _card_scroll_changed(self, first: str, last: str) -> None:
        self.card_scrollbar.set(first, last)
        self._schedule_visible_render()

    def _smooth_mousewheel(self, event) -> str:
        steps = -event.delta / 120 if event.delta else 0
        self._queue_scroll(steps * 105)
        return "break"

    def _queue_scroll(self, pixels: float) -> str:
        self.scroll_velocity += pixels
        self.scroll_velocity = max(-480.0, min(480.0, self.scroll_velocity))
        if self.scroll_animation_job is None:
            self.scroll_animation_job = self.after(0, self._animate_scroll)
        return "break"

    def _animate_scroll(self) -> None:
        self.scroll_animation_job = None
        total_height = max(
            1.0,
            float(self.card_canvas.cget("scrollregion").split()[3])
            if self.card_canvas.cget("scrollregion")
            else 1.0,
        )
        viewport = max(1.0, float(self.card_canvas.winfo_height()))
        maximum = max(0.0, total_height - viewport)
        current = max(0.0, float(self.card_canvas.canvasy(0)))
        step = self.scroll_velocity * 0.24
        target = max(0.0, min(maximum, current + step))
        if maximum > 0:
            self.card_canvas.yview_moveto(target / total_height)
        self.scroll_velocity *= 0.72
        self._schedule_visible_render()
        if abs(self.scroll_velocity) >= 0.7 and target not in (0.0, maximum):
            self.scroll_animation_job = self.after(16, self._animate_scroll)
        else:
            self.scroll_velocity = 0.0

    def _schedule_visible_render(self, force: bool = False) -> None:
        if force:
            self.visible_row_range = (-1, -1)
        if self.visible_render_job is None:
            self.visible_render_job = self.after_idle(self._render_visible_cards)

    def _cards_canvas_resized(self, event) -> None:
        width = max(1, event.width)
        columns = max(3, width // 158)
        card_width = (width - 8 * (columns + 1)) / columns
        avatar_size = 118 if card_width >= 168 else 104 if card_width >= 148 else 92
        # Reserve an independent two-line name band and a metadata band.
        # Long Chinese operator names must never collide with profession text.
        row_height = avatar_size + 94
        geometry_changed = (
            columns != self.card_columns
            or abs(card_width - self.card_width) > 1
            or row_height != self.card_row_height
        )
        self.card_columns = columns
        self.card_width = card_width
        self.card_row_height = row_height
        if geometry_changed:
            self._update_card_scrollregion()
            self._schedule_visible_render(force=True)

    def _profession_changed(self, _value: str) -> None:
        profession = self.profession_dropdown.get()
        branches = ["全部分支"]
        branches.extend(
            sorted(
                {
                    operator.branch
                    for operator in self.operator_list
                    if profession == "全部职业"
                    or operator.profession == profession
                }
            )
        )
        self.branch_dropdown.set_values(branches, keep_value=True)
        self.refresh_cards()

    def filtered_operators(self) -> list[Operator]:
        search = self.search_var.get().strip().casefold()
        rarity = self.rarity_dropdown.get()
        profession = self.profession_dropdown.get()
        branch = self.branch_dropdown.get()
        result = []
        for operator in self.operator_list:
            if search and search not in operator.name.casefold():
                continue
            if rarity != "全部星级" and operator.rarity != int(rarity[0]):
                continue
            if profession != "全部职业" and operator.profession != profession:
                continue
            if branch != "全部分支" and operator.branch != branch:
                continue
            result.append(operator)
        return result

    def refresh_cards(self) -> None:
        self.filtered_cache = self.filtered_operators()
        self.filter_count_var.set(
            f"显示 {len(self.filtered_cache)} / {len(self.operators)} 名"
        )
        self.card_canvas.yview_moveto(0)
        self._update_card_scrollregion()
        self._schedule_visible_render(force=True)

    def _update_card_scrollregion(self) -> None:
        columns = max(3, self.card_columns or 3)
        rows = (len(self.filtered_cache) + columns - 1) // columns
        total_height = max(
            self.card_canvas.winfo_height(),
            rows * self.card_row_height + 8,
        )
        self.card_canvas.configure(
            scrollregion=(0, 0, max(1, self.card_canvas.winfo_width()), total_height)
        )

    def _render_visible_cards(self) -> None:
        self.visible_render_job = None
        if not self.filtered_cache or self.card_columns < 1:
            self.card_canvas.delete("operator-card")
            self.card_border_items.clear()
            return
        top = max(0.0, self.card_canvas.canvasy(0))
        bottom = top + max(1, self.card_canvas.winfo_height())
        first_row = max(0, int(top // self.card_row_height) - 1)
        last_row = min(
            (len(self.filtered_cache) + self.card_columns - 1)
            // self.card_columns,
            int(bottom // self.card_row_height) + 2,
        )
        row_range = (first_row, last_row)
        if row_range == self.visible_row_range:
            return
        self.visible_row_range = row_range
        self.card_canvas.delete("operator-card")
        self.card_border_items.clear()
        start = first_row * self.card_columns
        end = min(len(self.filtered_cache), last_row * self.card_columns)
        for index in range(start, end):
            operator = self.filtered_cache[index]
            row, column = divmod(index, self.card_columns)
            self._draw_operator_card(operator, row, column)

    def _operator_status(self, operator: Operator) -> tuple[str, str, str]:
        operator_id = operator.operator_id
        if self.state.is_global_banned(operator):
            return "全局 BAN", GLOBAL_CARD, GLOBAL_BORDER
        if self.state.is_player_banned(operator):
            return "BAN", BAN_CARD, BAN_BORDER
        if operator_id in self.state.blue_pick_ids:
            return "蓝方 PICK", BLUE_CARD, BLUE_BORDER
        if operator_id in self.state.red_pick_ids:
            return "红方 PICK", RED_CARD, RED_BORDER
        return "", SURFACE_RAISED, LINE

    def _draw_operator_card(
        self, operator: Operator, row: int, column: int
    ) -> None:
        status, bg, border = self._operator_status(operator)
        selected = operator.operator_id == self.selected_operator_id
        if selected:
            border = ACCENT
        gap = 8
        x1 = gap + column * (self.card_width + gap)
        y1 = gap + row * self.card_row_height
        x2 = x1 + self.card_width
        y2 = y1 + self.card_row_height - gap
        tag = f"operator:{operator.operator_id}"
        common_tags = ("operator-card", tag)
        border_item = self.card_canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill=bg,
            outline=border,
            width=3 if selected else 2 if status else 1,
            tags=common_tags,
        )
        self.card_border_items[operator.operator_id] = border_item
        avatar_size = (
            118 if self.card_width >= 168 else 104 if self.card_width >= 148 else 92
        )
        avatar = self.assets.avatar(operator, avatar_size)
        self.card_canvas.create_image(
            (x1 + x2) / 2,
            y1 + 5,
            image=avatar,
            anchor="n",
            tags=common_tags,
        )
        if status:
            badge_color = (
                GLOBAL_BORDER
                if status == "全局 BAN"
                else BLUE
                if status == "蓝方 PICK"
                else RED
                if status == "红方 PICK"
                else BAN_BADGE
            )
            badge_width = 78 if len(status) > 3 else 50
            self.card_canvas.create_rectangle(
                x2 - badge_width - 5,
                y1 + 5,
                x2 - 5,
                y1 + 31,
                fill=badge_color,
                outline="",
                tags=common_tags,
            )
            self.card_canvas.create_text(
                x2 - badge_width / 2 - 5,
                y1 + 18,
                text=status,
                fill=HEADER_BG,
                font=(FONT, 8, "bold"),
                tags=common_tags,
            )
        name_length = len(operator.name)
        name_font_size = 10 if name_length <= 5 else 9 if name_length <= 8 else 8
        self.card_canvas.create_text(
            (x1 + x2) / 2,
            y2 - 56,
            text=operator.name,
            fill=FG,
            font=(FONT, name_font_size, "bold"),
            width=max(70, self.card_width - 14),
            anchor="center",
            tags=common_tags,
        )
        self.card_canvas.create_text(
            (x1 + x2) / 2,
            y2 - 11,
            text=operator.branch,
            fill=PROFESSION_COLORS.get(operator.profession, MUTED),
            font=(FONT, 8),
            width=max(70, self.card_width - 14),
            anchor="s",
            tags=common_tags,
        )
        self.card_canvas.tag_bind(
            tag,
            "<Button-1>",
            lambda _e, target=operator.operator_id: self.select_operator(target),
        )
        self.card_canvas.tag_bind(
            tag,
            "<Double-Button-1>",
            lambda _e, target=operator.operator_id: self.add_operator(target),
        )
        self.card_canvas.tag_bind(
            tag,
            "<Enter>",
            lambda _e, target=operator.operator_id: self._set_card_hover(
                target, True
            ),
        )
        self.card_canvas.tag_bind(
            tag,
            "<Leave>",
            lambda _e, target=operator.operator_id: self._set_card_hover(
                target, False
            ),
        )

    def _set_card_hover(self, operator_id: str, hovering: bool) -> None:
        self.card_canvas.configure(cursor="hand2" if hovering else "")
        if operator_id == self.selected_operator_id:
            return
        border_item = self.card_border_items.get(operator_id)
        operator = self.operators.get(operator_id)
        if border_item is None or operator is None:
            return
        status, _background, border = self._operator_status(operator)
        self.card_canvas.itemconfigure(
            border_item,
            outline=HOVER_BORDER if hovering else border,
            width=2 if hovering or status else 1,
        )

    def select_operator(self, operator_id: str) -> None:
        old_id = self.selected_operator_id
        self.selected_operator_id = operator_id
        operator = self.operators[operator_id]
        self.selection_var.set(
            f"已选择：{operator.name}  ·  {operator.rarity}★  ·  "
            f"{operator.profession} / {operator.branch}"
        )
        if old_id and old_id in self.card_border_items:
            old_operator = self.operators[old_id]
            old_status, _bg, old_border = self._operator_status(old_operator)
            self.card_canvas.itemconfigure(
                self.card_border_items[old_id],
                outline=old_border,
                width=2 if old_status else 1,
            )
        if operator_id in self.card_border_items:
            self.card_canvas.itemconfigure(
                self.card_border_items[operator_id],
                outline=ACCENT,
                width=3,
            )

    def add_selected_operator(self) -> None:
        if not self.selected_operator_id:
            messagebox.showinfo(
                "请选择干员", "请先在左侧选择一名干员。", parent=self
            )
            return
        self.add_operator(self.selected_operator_id)

    def add_operator(self, operator_id: str) -> None:
        operator = self.operators[operator_id]
        try:
            self.state.add(self.current_mode, operator)
        except RuleError as exc:
            messagebox.showwarning("无法加入", str(exc), parent=self)
            return
        self.refresh_all()

    def set_mode(self, mode: str) -> None:
        self.current_mode = mode
        colors = {MODE_BAN: BAN_BADGE, MODE_BLUE: BLUE, MODE_RED: RED}
        active_backgrounds = {
            MODE_BAN: "#3A282D",
            MODE_BLUE: "#173652",
            MODE_RED: "#40242C",
        }
        for target, button in self.mode_buttons.items():
            selected = target == mode
            button.configure(
                bg=active_backgrounds[target] if selected else SURFACE_RAISED,
                fg=colors[target],
                activebackground=(
                    active_backgrounds[target] if selected else CONTROL_HOVER
                ),
            )

    def remove_board_item(self, mode: str) -> None:
        tree = self.board_trees[mode]
        selection = tree.selection()
        if not selection:
            return
        operator_id = selection[0]
        if mode == MODE_BAN:
            operator = self.operators.get(operator_id)
            if operator and operator.branch in self.state.player_banned_branches:
                self.state.player_banned_branches.discard(operator.branch)
            self.state.remove(mode, operator_id)
        else:
            self.state.remove(mode, operator_id)
        self.refresh_all()

    def clear_picks(self) -> None:
        if not self.state.blue_pick_ids and not self.state.red_pick_ids:
            return
        if not messagebox.askyesno(
            "清空红蓝 Pick",
            "确认清空双方当前全部 Pick？选手 Ban 和导入配置会保留。",
            parent=self,
        ):
            return
        self.state.clear_draft(keep_imported_bans=True)
        self.refresh_all()

    def clear_board_group(self, mode: str) -> None:
        if mode == MODE_BLUE:
            self.state.blue_pick_ids = []
        elif mode == MODE_BAN:
            self.state.player_banned_operator_ids = []
            self.state.player_banned_branches = set()
        elif mode == MODE_RED:
            self.state.red_pick_ids = []
        else:
            return
        self.refresh_all()

    def clear_current_bp(self) -> None:
        has_current_bp = (
            self.state.player_banned_operator_ids
            or self.state.player_banned_branches
            or self.state.blue_pick_ids
            or self.state.red_pick_ids
        )
        if not has_current_bp:
            return
        if not messagebox.askyesno(
            "清空当前 BAN / PICK",
            "确认清空当前全部选手 Ban、分支 Ban以及红蓝双方 Pick？\n\n"
            "全局 Ban 将完整保留，不会受到影响。",
            parent=self,
        ):
            return
        self.state.clear_draft(keep_imported_bans=False)
        self.selected_operator_id = None
        self.selection_var.set("尚未选择干员")
        self.refresh_all()

    def open_global_ban_editor(self) -> None:
        if self.loaded_config is None:
            messagebox.showinfo(
                "请先导入比赛配置",
                "请先使用“导入之前比赛配置”读取一个 .bpmatch 文件，"
                "再修改其中的全局 Ban。",
                parent=self,
            )
            return
        GlobalBanEditor(self)

    def apply_global_bans(
        self,
        operator_ids: set[str],
        branches: set[str],
    ) -> None:
        valid_branches = {
            operator.branch for operator in self.operator_list
        }
        self.state.global_banned_operator_ids = {
            operator_id
            for operator_id in operator_ids
            if operator_id in self.operators
        }
        self.state.global_banned_branches = set(branches) & valid_branches

        def available(operator_id: str) -> bool:
            operator = self.operators.get(operator_id)
            return bool(operator and not self.state.is_global_banned(operator))

        self.state.player_banned_operator_ids = [
            operator_id
            for operator_id in self.state.player_banned_operator_ids
            if available(operator_id)
        ]
        self.state.player_banned_branches -= self.state.global_banned_branches
        self.state.blue_pick_ids = [
            operator_id
            for operator_id in self.state.blue_pick_ids
            if available(operator_id)
        ]
        self.state.red_pick_ids = [
            operator_id
            for operator_id in self.state.red_pick_ids
            if available(operator_id)
        ]
        if self.loaded_config is not None:
            self.loaded_config.global_banned_operator_ids = sorted(
                self.state.global_banned_operator_ids
            )
            self.loaded_config.global_banned_branches = sorted(
                self.state.global_banned_branches
            )
        self.refresh_all()

    def export_modified_config(self) -> bool:
        if self.loaded_config is None:
            return False
        safe_title = "".join(
            character
            for character in (self.loaded_config.title or "比赛配置")
            if character not in '\\/:*?"<>|'
        ).strip() or "比赛配置"
        path = filedialog.asksaveasfilename(
            parent=self,
            title="重新导出修改后的比赛配置",
            defaultextension=".bpmatch",
            initialfile=f"{safe_title}_全局Ban修改.bpmatch",
            filetypes=[("联锁对抗比赛配置", "*.bpmatch")],
        )
        if not path:
            return False
        try:
            self.loaded_config.validate()
            save_config(Path(path), self.loaded_config)
        except (OSError, ValueError, RuleError) as exc:
            messagebox.showerror(
                "导出失败",
                f"无法导出修改后的比赛配置：\n{exc}",
                parent=self,
            )
            return False
        messagebox.showinfo(
            "导出完成",
            f"修改后的比赛配置已保存：\n{path}",
            parent=self,
        )
        return True

    def import_match_config(self) -> None:
        path = filedialog.askopenfilename(
            parent=self,
            title="导入之前的比赛配置",
            filetypes=[
                ("联锁对抗比赛配置", "*.bpmatch"),
                ("JSON 配置", "*.json"),
                ("所有文件", "*.*"),
            ],
        )
        if not path:
            return
        has_draft = (
            self.state.player_banned_operator_ids
            or self.state.blue_pick_ids
            or self.state.red_pick_ids
        )
        if has_draft and not messagebox.askyesno(
            "覆盖当前 BP",
            "导入比赛配置会清空当前红蓝 Pick，并以配置中的主持人 Ban "
            "重建选手 Ban。是否继续？",
            parent=self,
        ):
            return
        try:
            config = load_config(Path(path))
            config.validate()
            self.state.apply_config(config, self.operators)
        except (OSError, ValueError, KeyError, TypeError, RuleError) as exc:
            messagebox.showerror(
                "配置导入失败",
                f"无法读取该比赛配置：\n{exc}",
                parent=self,
            )
            return
        self.loaded_config = config
        self.config_path = Path(path)
        self.selected_operator_id = None
        self.match_var.set(
            f"{self.state.match_title or '未命名比赛'}  ·  {self.state.match_id}"
        )
        self.players_var.set(
            f"蓝方  {self.state.blue_name}    VS    {self.state.red_name}  红方"
        )
        self.refresh_all()

    def refresh_board(self) -> None:
        expanded_player_bans = list(self.state.player_banned_operator_ids)
        expanded_player_ban_set = set(expanded_player_bans)
        for operator in self.operator_list:
            if (
                operator.branch in self.state.player_banned_branches
                and not self.state.is_global_banned(operator)
                and operator.operator_id not in expanded_player_ban_set
            ):
                expanded_player_bans.append(operator.operator_id)
                expanded_player_ban_set.add(operator.operator_id)
        groups = {
            MODE_BAN: expanded_player_bans,
            MODE_BLUE: self.state.blue_pick_ids,
            MODE_RED: self.state.red_pick_ids,
        }
        for mode, operator_ids in groups.items():
            tree = self.board_trees[mode]
            tree.delete(*tree.get_children())
            for operator_id in operator_ids:
                operator = self.operators.get(operator_id)
                if not operator:
                    continue
                avatar = self.assets.avatar(operator, 72)
                tree.insert(
                    "",
                    "end",
                    iid=operator_id,
                    image=avatar,
                    text=f"  {operator.name}",
                    tags=(f"rarity-{min(6, max(1, operator.rarity))}",),
                )
            self.board_count_vars[mode].set(f"{len(operator_ids)} 名")
        branches = sorted(self.state.player_banned_branches)
        global_count = len(self.state.global_banned_operator_ids)
        global_branch_count = len(self.state.global_banned_branches)
        branch_text = "、".join(branches) if branches else "无"
        self.branch_ban_var.set(
            f"配置分支 Ban：{branch_text}    ·    "
            f"全局 Ban：{global_count} 名干员 / {global_branch_count} 个分支"
        )

    def refresh_all(self) -> None:
        self.set_mode(self.current_mode)
        self.refresh_board()
        if self.filtered_cache:
            self._schedule_visible_render(force=True)
        else:
            self.refresh_cards()

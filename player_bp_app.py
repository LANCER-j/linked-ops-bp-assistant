from __future__ import annotations

from pathlib import Path
import os
import sys
import traceback
import tkinter as tk
from tkinter import messagebox

from bp_assistant.player_bp_ui import PlayerBpApplication
from bp_assistant.storage import load_operators


FROZEN = bool(getattr(sys, "frozen", False))
RESOURCE_ROOT = (
    Path(getattr(sys, "_MEIPASS")).resolve()
    if FROZEN
    else Path(__file__).resolve().parent
)
APP_ROOT = Path(sys.executable).resolve().parent if FROZEN else RESOURCE_ROOT
OPERATOR_DATA = RESOURCE_ROOT / "data" / "operators.csv"
ERROR_LOG = APP_ROOT / "选手赛前BP_启动错误.log"


def enable_high_dpi() -> None:
    """让 Tk 在 Windows 高分屏上按真实像素渲染。"""
    dll_directory = None
    try:
        if hasattr(os, "add_dll_directory"):
            dll_directory = os.add_dll_directory(
                str(Path(sys.executable).resolve().parent)
            )
        import ctypes
    except (ImportError, OSError):
        return
    try:
        if hasattr(ctypes, "windll"):
            try:
                set_app_id = (
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID
                )
                set_app_id.argtypes = [ctypes.c_wchar_p]
                set_app_id("LinkedOps.PlayerPreMatchBP")
            except (AttributeError, OSError, TypeError):
                pass
            try:
                ctypes.windll.user32.SetProcessDpiAwarenessContext(
                    ctypes.c_void_p(-4)
                )
            except (AttributeError, OSError):
                try:
                    ctypes.windll.shcore.SetProcessDpiAwareness(2)
                except (AttributeError, OSError):
                    ctypes.windll.user32.SetProcessDPIAware()
    finally:
        try:
            if dll_directory is not None:
                dll_directory.close()
        except OSError:
            pass


def show_startup_error(exc: BaseException) -> None:
    details = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    try:
        ERROR_LOG.write_text(details, encoding="utf-8")
    except OSError:
        pass
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "选手赛前 BP 无法启动",
        f"{exc}\n\n详细信息已写入：\n{ERROR_LOG}",
    )
    root.destroy()


def main() -> None:
    try:
        enable_high_dpi()
        operators = load_operators(OPERATOR_DATA)
        if not operators:
            raise RuntimeError("干员数据为空")
        app = PlayerBpApplication(operators, RESOURCE_ROOT / "assets")
        try:
            ERROR_LOG.unlink(missing_ok=True)
        except OSError:
            pass
        app.mainloop()
    except BaseException as exc:
        show_startup_error(exc)


if __name__ == "__main__":
    main()

"""Windows 无控制台启动入口。"""

from __future__ import annotations

import os
from pathlib import Path
import sys
import traceback


ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))


try:
    from app import main

    main()
except BaseException as exc:
    log_path = ROOT / "启动错误.log"
    details = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    try:
        log_path.write_text(details, encoding="utf-8")
    except OSError:
        pass
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "联锁对抗 BP 助手无法启动",
            f"{exc}\n\n详细信息已写入：\n{log_path}",
        )
        root.destroy()
    except BaseException:
        pass


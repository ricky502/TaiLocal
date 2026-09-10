#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TaiLocal 最台繁 · Taiwan + Localization
简体中文 → 台湾繁体中文 批量转换工具（GUI版）
- 双击/命令行均可运行
- 图形界面选择任意位置的 Excel，输出保存在原文件旁
- 术语库：terms.csv（公共）+ terms_private.csv（个人，可选）
"""
import os
import sys
import threading
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))

TERMS = [os.path.join(BASE, "terms.csv"), os.path.join(BASE, "terms_private.csv")]
POST_FIX = os.path.join(BASE, "post_fix.csv")

APP_NAME = "TaiLocal 最台繁"


def run_convert(input_file, status_cb):
    """执行转换，返回输出文件路径"""
    import pandas as pd
    from tailocal_core import convert_excel

    log_rows = []
    df, loaded, n_terms, n_fix = convert_excel(input_file, TERMS, POST_FIX, log_rows)

    out_dir = os.path.dirname(os.path.abspath(input_file))
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    ts = datetime.now().strftime("%m%d_%H%M%S")
    out_file = os.path.join(out_dir, f"{base_name}_tw_{ts}.xlsx")
    df.to_excel(out_file, index=False)

    # log（debug用）
    try:
        log_file = os.path.join(out_dir, f"{base_name}_twlog_{ts}.xlsx")
        pd.DataFrame(log_rows).to_excel(log_file, index=False)
    except Exception:
        pass

    msg = "\n".join([f"✅ 术语表 {n}: {c} 条" for n, c in loaded]) + f"\n🎯 生效术语 {n_terms} 条 · post_fix {n_fix} 条"
    return out_file, len(df), msg


def run_cli(argv):
    if not argv or not argv[0].endswith(".xlsx") or not os.path.exists(argv[0]):
        print(f"用法: python {os.path.basename(__file__)} <文件.xlsx> [--debug]")
        sys.exit(1)
    out, n, msg = run_convert(argv[0], print)
    print(msg)
    print(f"✅ 完成 {n} 条 → {out}")


def run_gui():
    import tkinter as tk
    from tkinter import filedialog, font as tkfont

    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry("460x360")
    root.resizable(False, False)
    root.configure(bg="#F7F3EE")

    try:
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=11)
    except Exception:
        pass

    frame = tk.Frame(root, bg="#F7F3EE")
    frame.pack(expand=True, fill="both", padx=24, pady=20)

    tk.Label(frame, text="最台繁", font=("PingFang TC", 26, "bold"),
             bg="#F7F3EE", fg="#2C6E49").pack(pady=(6, 0))
    tk.Label(frame, text="TaiLocal · 簡體中文 → 台灣繁體中文", font=("PingFang TC", 11),
             bg="#F7F3EE", fg="#8A8A8A").pack(pady=(0, 18))

    status = tk.Label(frame, text="選一個 Excel，剩下的交給我。",
                      font=("PingFang TC", 11), bg="#F7F3EE", fg="#555555", wraplength=400, justify="left")
    status.pack(pady=(0, 14))

    btn = tk.Button(frame, text="選擇待翻譯的 Excel 檔案", font=("PingFang TC", 13, "bold"),
                    bg="#2C6E49", fg="white", relief="flat", cursor="hand2",
                    padx=24, pady=10, command=lambda: None)
    btn.pack()

    def on_close():
        root.destroy()
        os._exit(0)

    root.protocol("WM_DELETE_WINDOW", on_close)

    def pick():
        path = filedialog.askopenfilename(
            title="選擇 Excel 檔案",
            filetypes=[("Excel", "*.xlsx"), ("All files", "*.*")])
        if not path:
            return
        btn.configure(state="disabled", text="翻譯中…")
        status.configure(text=f"正在翻譯：{os.path.basename(path)}\n請稍候…", fg="#2C6E49")

        def worker():
            try:
                out, n, msg = run_convert(path, None)
                root.after(0, lambda: status.configure(
                    text=f"✅ 翻譯完成！共 {n} 條\n{msg}\n已輸出至：{out}", fg="#2C6E49"))
            except Exception as e:
                root.after(0, lambda: status.configure(text=f"❌ 出錯：{e}", fg="#C0392B"))
            finally:
                root.after(0, lambda: btn.configure(state="normal", text="再翻一個檔案"))

        threading.Thread(target=worker, daemon=True).start()

    btn.configure(command=pick)
    tk.Label(frame, text="輸出檔案會自動存在原檔案旁邊\n術語庫：terms.csv（可自行增刪詞條）",
             font=("PingFang TC", 9), bg="#F7F3EE", fg="#AAAAAA", justify="center").pack(side="bottom", pady=(10, 0))

    root.mainloop()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a.endswith(".xlsx")]
    if args:
        run_cli(args)
    else:
        run_gui()

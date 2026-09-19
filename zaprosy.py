#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЗАПРОСЫ — маленькое окно-шпаргалка поверх браузера.

Каждая строка = отдельный запрос.
Кнопка справа от строки — скопировать запрос в буфер обмена.
Крестик рядом — удалить эту строку (возврат по Cmd+Z).
Тумблер «Вырезать» — удалять ли запрос после копирования.
Кнопка «+» внизу — быстро добавить одну строку.
Карандаш — редактор всего списка.
Солнце/месяц — светлая и тёмная тема.

Запуск: в IDLE нажать Fn+F5, либо `python3 zaprosy.py` в терминале.
"""

import json
import os
import re
import shutil
import shlex
import subprocess
import sys
import tempfile
import threading
import urllib.request
import tkinter as tk
from tkinter import font as tkfont

APP_NAME = "Запросы"

# ---------- где храним состояние ----------
STATE_DIR = os.path.join(
    os.path.expanduser("~"), "Library", "Application Support", "ZaprosyPad"
)
STATE_FILE = os.path.join(STATE_DIR, "state.json")

DEFAULT_GEOM = "330x520+80+80"

# ---------- обновления ----------
APP_VERSION = "1.0.3"
GITHUB_REPO = "pingujonathan7/zaprosy"

# иконка приложения (PNG в base64)
ICON_B64 = "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"

# ---------- темы ----------
THEMES = {
    "dark": {
        "bg": "#1c1d21",
        "bar": "#26282d",
        "row": "#2c2f35",
        "row_hover": "#363a42",
        "flash": "#2f6b46",
        "fg": "#e8e9ec",
        "muted": "#8b8f98",
        "accent": "#4c8dff",
        "danger": "#e2645c",
        "off": "#4a4e57",
        "border": "#34373e",
        "field": "#32363d",
    },
    "light": {
        "bg": "#f1f2f4",
        "bar": "#e5e7eb",
        "row": "#ffffff",
        "row_hover": "#e6eefb",
        "flash": "#bde7c8",
        "fg": "#1d1f24",
        "muted": "#767c86",
        "accent": "#2f6fe0",
        "danger": "#d24b42",
        "off": "#c3c8d0",
        "border": "#d2d6dc",
        "field": "#ffffff",
    },
}

# живая палитра — обновляется на месте при смене темы
C = dict(THEMES["dark"])

ROW_PARTS = ("frame", "text", "num", "del", "btn")


def copy_to_clipboard(root, text):
    """Кладём в буфер обмена так, чтобы текст жил и после закрытия программы.

    Приложению, запущенному из Finder, система не передаёт LANG, и pbcopy
    принимает входящий текст за однобайтовую кодировку — кириллица
    превращается в мусор. Поэтому кодировку задаём явно.
    """
    try:
        env = dict(os.environ)
        env["LANG"] = "en_US.UTF-8"
        env["LC_ALL"] = "en_US.UTF-8"
        env["LC_CTYPE"] = "UTF-8"
        subprocess.run(
            ["pbcopy"], input=text.encode("utf-8"), env=env, check=True
        )
        return
    except Exception:
        pass
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update_idletasks()
    except Exception:
        pass


def paste_from_clipboard(root):
    """Читаем буфер обмена с явной кодировкой — по той же причине, что и pbcopy."""
    try:
        env = dict(os.environ)
        env["LANG"] = "en_US.UTF-8"
        env["LC_ALL"] = "en_US.UTF-8"
        env["LC_CTYPE"] = "UTF-8"
        out = subprocess.run(["pbpaste"], capture_output=True, env=env, check=True)
        return out.stdout.decode("utf-8", "replace")
    except Exception:
        pass
    try:
        return root.clipboard_get()
    except Exception:
        return ""


def pick_icons(root):
    """Старые сборки Tk на macOS не умеют символы вне BMP (эмодзи).
    Проверяем и при необходимости подставляем безопасные значки."""
    try:
        root.tk.call("string", "length", "\U0001F4CB")
        return {"copy": "\U0001F4CB", "pin_on": "\U0001F4CC", "pin_off": "\U0001F4CD"}
    except Exception:
        return {"copy": "⧉", "pin_on": "▲", "pin_off": "△"}


def set_app_icon(root):
    """Иконка в Dock и в переключателе приложений."""
    try:
        img = tk.PhotoImage(data=ICON_B64)
        root.iconphoto(True, img)
        root._app_icon = img  # держим ссылку, иначе картинку соберёт GC
    except Exception:
        pass


def version_tuple(text):
    parts = []
    for chunk in re.split(r"[.\-+_]", (text or "").lstrip("vV")):
        if chunk.isdigit():
            parts.append(int(chunk))
        else:
            break
    return tuple(parts) or (0,)


def app_bundle_path():
    """Путь к .app, если программа запущена как собранное приложение."""
    if not getattr(sys, "frozen", False):
        return None
    parts = os.path.abspath(sys.executable).split(os.sep)
    for i in range(len(parts) - 1, -1, -1):
        if parts[i].endswith(".app"):
            return os.sep.join(parts[: i + 1])
    return None


def fetch_latest_release():
    """Возвращает (тег, ссылка на zip) последнего релиза на GitHub."""
    url = "https://api.github.com/repos/%s/releases/latest" % GITHUB_REPO
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ZaprosyPad",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    tag = data.get("tag_name") or ""
    link = None
    for asset in data.get("assets") or []:
        name = (asset.get("name") or "").lower()
        if name.endswith(".zip"):
            link = asset.get("browser_download_url")
            break
    return tag, link


def install_update(zip_url, bundle):
    """Качает архив релиза и подменяет .app на месте."""
    work = tempfile.mkdtemp(prefix="zaprosy-update-")
    archive = os.path.join(work, "update.zip")
    req = urllib.request.Request(zip_url, headers={"User-Agent": "ZaprosyPad"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        with open(archive, "wb") as f:
            shutil.copyfileobj(resp, f)

    unpacked = os.path.join(work, "unpacked")
    os.makedirs(unpacked, exist_ok=True)
    # ditto, а не zipfile: сохраняет права, симлинки и подпись бандла
    subprocess.run(["ditto", "-x", "-k", archive, unpacked], check=True)

    new_app = None
    for root_dir, dirs, _files in os.walk(unpacked):
        for name in dirs:
            if name.endswith(".app"):
                new_app = os.path.join(root_dir, name)
                break
        if new_app:
            break
    if new_app is None:
        raise RuntimeError("в архиве нет .app")

    # Старую версию не удаляем сразу: её файлы ещё открыты процессом.
    # Отодвигаем рядом (тот же диск — переименование мгновенное),
    # а сносим уже после выхода, отдельным процессом.
    parked = bundle + ".old"
    if os.path.exists(parked):
        shutil.rmtree(parked, ignore_errors=True)
    os.rename(bundle, parked)
    try:
        subprocess.run(["ditto", new_app, bundle], check=True)
    except Exception:
        if not os.path.exists(bundle):
            os.rename(parked, bundle)
        raise

    subprocess.Popen(
        ["/bin/sh", "-c", "sleep 8; rm -rf %s" % shlex.quote(parked)],
        start_new_session=True,
    )
    shutil.rmtree(work, ignore_errors=True)
    return bundle


class ToggleSwitch(tk.Canvas):
    """Маленький ползунок вкл/выкл."""

    def __init__(self, master, value=False, command=None, **kw):
        super().__init__(
            master, width=36, height=20, bg=C["bar"], highlightthickness=0, bd=0, **kw
        )
        self.value = bool(value)
        self.command = command
        self.bind("<Button-1>", self._click)
        self.configure(cursor="pointinghand")
        self._draw()

    def _draw(self):
        self.delete("all")
        self.configure(bg=C["bar"])
        fill = C["accent"] if self.value else C["off"]
        self.create_oval(1, 2, 17, 18, fill=fill, outline=fill)
        self.create_oval(19, 2, 35, 18, fill=fill, outline=fill)
        self.create_rectangle(9, 2, 27, 18, fill=fill, outline=fill)
        x = 26 if self.value else 10
        self.create_oval(x - 7, 3, x + 7, 17, fill="#ffffff", outline="#ffffff")

    def _click(self, _e=None):
        self.value = not self.value
        self._draw()
        if self.command:
            self.command(self.value)

    def set(self, value):
        self.value = bool(value)
        self._draw()

    def restyle(self):
        self._draw()


class IconButton(tk.Label):
    """Кнопка-иконка (на macOS у tk.Button нельзя красить фон, поэтому Label)."""

    def __init__(self, master, text, command, bg=None, fg=None, font=None,
                 pad=(6, 2), **kw):
        bg = bg if bg is not None else C["bar"]
        fg = fg if fg is not None else C["fg"]
        super().__init__(
            master, text=text, bg=bg, fg=fg, font=font,
            padx=pad[0], pady=pad[1], cursor="pointinghand", **kw
        )
        self._bg = bg
        self._command = command
        self.bind("<Button-1>", lambda e: self._command())
        self.bind("<Enter>", lambda e: self.configure(bg=C["row_hover"]))
        self.bind("<Leave>", lambda e: self.configure(bg=self._bg))

    def restyle(self, bg, fg):
        self._bg = bg
        self.configure(bg=bg, fg=fg)


class App:
    def __init__(self, root):
        self.root = root
        self.queries = []
        self.cut_mode = False
        self.pinned = True
        self.theme = "dark"
        self.undo_stack = []
        self.rows = []
        self.add_visible = False
        self._upd_busy = False
        self._upd_pending = None
        self._save_job = None
        self._flash_jobs = {}

        state = self.load_state()
        self.theme = state.get("theme", "dark")
        if self.theme not in THEMES:
            self.theme = "dark"
        C.update(THEMES[self.theme])

        root.title(APP_NAME)
        root.configure(bg=C["bg"])
        root.geometry(state.get("geometry", DEFAULT_GEOM))
        root.minsize(250, 180)
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        if not getattr(sys, "frozen", False):
            set_app_icon(root)

        self.f_ui = tkfont.Font(family="Helvetica", size=12)
        self.f_small = tkfont.Font(family="Helvetica", size=10)
        self.f_row = tkfont.Font(family="Helvetica", size=12)
        self.f_icon = tkfont.Font(family="Helvetica", size=13)
        self.f_del = tkfont.Font(family="Helvetica", size=14)
        self.icons = pick_icons(root)

        self.build_toolbar()
        self.build_list()

        self.queries = list(state.get("queries", []))
        self.cut_mode = bool(state.get("cut_mode", False))
        self.pinned = bool(state.get("pinned", True))
        self.sw_cut.set(self.cut_mode)
        self.update_pin_look()
        self.update_theme_look()
        self.render()

        # Tk привязывает Cmd-сочетания к латинским буквам, и при русской
        # раскладке они перестают срабатывать. Ловим обе раскладки сами.
        root.bind_all("<Command-KeyPress>", self.on_command_key)
        root.bind("<Control-z>", self.undo)
        root.bind("<Escape>", lambda e: self.hide_add())

        # На macOS «поверх всех» применяется только к уже показанному окну,
        # поэтому ставим флаг после отрисовки и затем поддерживаем его.
        root.after(300, self.apply_pin)
        root.after(1500, self.topmost_keepalive)
        root.after(4000, self.silent_update_check)
        root.bind("<Configure>", self.on_configure)

    # ---------- интерфейс ----------
    def build_toolbar(self):
        bar = tk.Frame(self.root, bg=C["bar"])
        bar.pack(side="top", fill="x")
        self.bar = bar

        self.btn_pin = IconButton(
            bar, self.icons["pin_on"], self.toggle_pin, font=self.f_icon, pad=(7, 4)
        )
        self.btn_pin.pack(side="left", padx=(4, 2), pady=3)

        self.lbl_cut = tk.Label(
            bar, text="Вырезать", bg=C["bar"], fg=C["fg"], font=self.f_small
        )
        self.lbl_cut.pack(side="left", padx=(2, 4))
        self.sw_cut = ToggleSwitch(bar, value=False, command=self.set_cut)
        self.sw_cut.pack(side="left", pady=3)

        self.btn_edit = IconButton(
            bar, "✎", self.open_editor, font=self.f_icon,
            fg=C["muted"], pad=(7, 4)
        )
        self.btn_edit.pack(side="right", padx=(0, 4), pady=3)

        self.btn_undo = IconButton(
            bar, "↺", self.undo, font=self.f_icon, fg=C["muted"], pad=(7, 4)
        )
        self.btn_undo.pack(side="right", padx=0, pady=3)

        self.btn_theme = IconButton(
            bar, "☾", self.toggle_theme, font=self.f_icon,
            fg=C["muted"], pad=(7, 4)
        )
        self.btn_theme.pack(side="right", padx=0, pady=3)

        self.sep1 = tk.Frame(self.root, bg=C["border"], height=1)
        self.sep1.pack(side="top", fill="x")

        # нижняя строка состояния
        self.status = tk.Frame(self.root, bg=C["bar"])
        self.status.pack(side="bottom", fill="x")
        self.sep2 = tk.Frame(self.root, bg=C["border"], height=1)
        self.sep2.pack(side="bottom", fill="x")

        self.btn_add = IconButton(
            self.status, "+", self.toggle_add, font=self.f_icon,
            fg=C["accent"], pad=(8, 1)
        )
        self.btn_add.pack(side="left", padx=(4, 2), pady=2)

        self.lbl_count = tk.Label(
            self.status, text="", bg=C["bar"], fg=C["muted"],
            font=self.f_small, anchor="w"
        )
        self.lbl_count.pack(side="left", padx=4, pady=3)
        self.btn_ver = IconButton(
            self.status, "v" + APP_VERSION, self.updates_click,
            font=self.f_small, fg=C["muted"], pad=(7, 3)
        )
        self.btn_ver.pack(side="right", padx=(0, 4), pady=2)

        self.lbl_hint = tk.Label(
            self.status, text="", bg=C["bar"], fg=C["muted"],
            font=self.f_small, anchor="e"
        )
        self.lbl_hint.pack(side="right", padx=4, pady=3)

        # строка быстрого добавления (прячется)
        self.addbar = tk.Frame(self.root, bg=C["bar"])
        self.addbar.pack(side="bottom", fill="x")
        self.entry = tk.Entry(
            self.addbar, bg=C["field"], fg=C["fg"], insertbackground=C["fg"],
            font=self.f_row, relief="flat", highlightthickness=1,
            highlightbackground=C["border"], highlightcolor=C["accent"]
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(6, 4), pady=6)
        self.entry.bind("<Return>", self.add_from_entry)
        self.entry.bind("<Escape>", lambda e: self.hide_add())
        self.btn_add_ok = IconButton(
            self.addbar, "⏎", self.add_from_entry, font=self.f_icon,
            bg=C["accent"], fg="#ffffff", pad=(9, 3)
        )
        self.btn_add_ok.pack(side="right", padx=(0, 6), pady=6)
        self.addbar.pack_forget()

    def build_list(self):
        self.wrap = tk.Frame(self.root, bg=C["bg"])
        self.wrap.pack(side="top", fill="both", expand=True)

        self.canvas = tk.Canvas(self.wrap, bg=C["bg"], highlightthickness=0, bd=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scroll = tk.Scrollbar(
            self.wrap, orient="vertical", command=self.canvas.yview
        )
        self.scroll.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.inner = tk.Frame(self.canvas, bg=C["bg"])
        self.win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        for w in (self.canvas, self.inner):
            w.bind("<MouseWheel>", self.on_wheel)

    def on_canvas_resize(self, event):
        self.canvas.itemconfigure(self.win, width=event.width)
        wl = max(80, event.width - 92)
        for r in self.rows:
            r["text"].configure(wraplength=wl)

    def on_wheel(self, event):
        self.canvas.yview_scroll(int(-1 * event.delta), "units")

    # ---------- отрисовка списка ----------
    def render(self):
        for job in self._flash_jobs.values():
            try:
                self.root.after_cancel(job)
            except Exception:
                pass
        self._flash_jobs = {}
        for r in self.rows:
            r["frame"].destroy()
        self.rows = []
        for i, q in enumerate(self.queries):
            self.make_row(i, q)
        self.update_count()
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def make_row(self, index, text):
        wl = max(80, self.canvas.winfo_width() - 92)
        fr = tk.Frame(self.inner, bg=C["row"])
        fr.pack(fill="x", padx=4, pady=2)

        num = tk.Label(
            fr, text=str(index + 1), bg=C["row"], fg=C["muted"], font=self.f_small,
            width=3, anchor="ne", padx=0
        )
        num.pack(side="left", fill="y", pady=5)

        btn = tk.Label(
            fr, text=self.icons["copy"], bg=C["row"], fg=C["fg"], font=self.f_icon,
            padx=5, cursor="pointinghand"
        )
        btn.pack(side="right", fill="y", pady=3)

        dele = tk.Label(
            fr, text="×", bg=C["row"], fg=C["muted"], font=self.f_del,
            padx=4, cursor="pointinghand"
        )
        dele.pack(side="right", fill="y", pady=3)

        lbl = tk.Label(
            fr, text=text, bg=C["row"], fg=C["fg"], font=self.f_row, justify="left",
            anchor="w", wraplength=wl, padx=2, pady=5
        )
        lbl.pack(side="left", fill="x", expand=True)

        row = {"frame": fr, "text": lbl, "num": num, "btn": btn, "del": dele}
        self.rows.append(row)

        def on_copy(_e=None, r=row):
            self.copy_row(r)

        def on_delete(_e=None, r=row):
            self.delete_row(r)

        parts = (fr, lbl, num, btn, dele)
        for w in parts:
            w.bind("<MouseWheel>", self.on_wheel)
        btn.bind("<Button-1>", on_copy)
        lbl.bind("<Double-Button-1>", on_copy)
        dele.bind("<Button-1>", on_delete)

        def enter(_e=None, r=row):
            self.paint(r, C["row_hover"])

        def leave(_e=None, r=row):
            self.paint(r, C["row"])

        for w in parts:
            w.bind("<Enter>", enter)
            w.bind("<Leave>", leave)

        # крестик краснеет под курсором
        dele.bind("<Enter>", lambda e, d=dele: d.configure(fg=C["danger"]), add="+")
        dele.bind("<Leave>", lambda e, d=dele: d.configure(fg=C["muted"]), add="+")
        return row

    def paint(self, row, color):
        if row["frame"] in self._flash_jobs:
            return
        for k in ROW_PARTS:
            try:
                row[k].configure(bg=color)
            except tk.TclError:
                pass

    # ---------- действия ----------
    def copy_row(self, row):
        try:
            index = self.rows.index(row)
        except ValueError:
            return
        text = self.queries[index]
        copy_to_clipboard(self.root, text)

        if self.cut_mode:
            self.delete_index(index)
            self.set_hint("вырезано")
        else:
            self.flash(row)
            self.set_hint("скопировано")

    def delete_row(self, row):
        try:
            index = self.rows.index(row)
        except ValueError:
            return
        self.delete_index(index)
        self.set_hint("удалено")

    def flash(self, row):
        key = row["frame"]
        if key in self._flash_jobs:
            self.root.after_cancel(self._flash_jobs[key])
        for k in ROW_PARTS:
            try:
                row[k].configure(bg=C["flash"])
            except tk.TclError:
                return

        def restore():
            self._flash_jobs.pop(key, None)
            for k in ROW_PARTS:
                try:
                    row[k].configure(bg=C["row"])
                except tk.TclError:
                    pass

        self._flash_jobs[key] = self.root.after(650, restore)

    def delete_index(self, index):
        text = self.queries.pop(index)
        self.undo_stack.append((index, text))
        del self.undo_stack[:-100]
        row = self.rows.pop(index)
        key = row["frame"]
        if key in self._flash_jobs:
            self.root.after_cancel(self._flash_jobs.pop(key))
        row["frame"].destroy()
        for i in range(index, len(self.rows)):
            self.rows[i]["num"].configure(text=str(i + 1))
        self.update_count()
        self.schedule_save()

    def undo(self, _e=None):
        if not self.undo_stack:
            self.set_hint("нечего возвращать")
            return
        index, text = self.undo_stack.pop()
        index = min(index, len(self.queries))
        self.queries.insert(index, text)
        self.render()
        self.set_hint("возвращено")
        self.schedule_save()
        self.root.after(30, lambda: self.scroll_to(index))

    def scroll_to(self, index):
        if not self.rows or index >= len(self.rows):
            return
        self.canvas.update_idletasks()
        total = self.inner.winfo_height() or 1
        y = self.rows[index]["frame"].winfo_y()
        self.canvas.yview_moveto(max(0.0, (y - 40) / total))

    def set_cut(self, value):
        self.cut_mode = bool(value)
        self.schedule_save()

    # ---------- быстрое добавление ----------
    def toggle_add(self):
        if self.add_visible:
            self.hide_add()
        else:
            self.show_add()

    def show_add(self):
        if not self.add_visible:
            self.addbar.pack(side="bottom", fill="x", before=self.sep2)
            self.add_visible = True
        self.entry.focus_set()

    def hide_add(self, _e=None):
        if self.add_visible:
            self.addbar.pack_forget()
            self.add_visible = False

    def add_from_entry(self, _e=None):
        text = self.entry.get().strip()
        if not text:
            self.hide_add()
            return
        self.queries.append(text)
        self.make_row(len(self.queries) - 1, text)
        self.update_count()
        self.schedule_save()
        self.entry.delete(0, "end")
        self.set_hint("добавлено")
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(1.0)

    # ---------- горячие клавиши в обеих раскладках ----------
    CMD_MAP = {
        "v": "paste", "\u043c": "paste",
        "c": "copy", "\u0441": "copy",
        "x": "cut", "\u0447": "cut",
        "a": "all", "\u0444": "all",
        "z": "undo", "\u044f": "undo",
        "n": "new", "\u0442": "new",
    }
    KEYSYM_ALIAS = {
        "cyrillic_em": "\u043c",
        "cyrillic_es": "\u0441",
        "cyrillic_che": "\u0447",
        "cyrillic_ef": "\u0444",
        "cyrillic_ya": "\u044f",
        "cyrillic_te": "\u0442",
    }

    def on_command_key(self, event):
        key = (event.char or "").lower()
        if key not in self.CMD_MAP:
            ks = (event.keysym or "").lower()
            key = self.KEYSYM_ALIAS.get(ks, ks)
        action = self.CMD_MAP.get(key)
        if action is None:
            return None

        w = event.widget
        is_entry = isinstance(w, tk.Entry)
        is_text = isinstance(w, tk.Text)

        if action == "paste":
            if not (is_entry or is_text):
                return None
            data = paste_from_clipboard(self.root)
            if data:
                self.drop_selection(w, is_entry)
                w.insert("insert", data)
            return "break"

        if action in ("copy", "cut"):
            if not (is_entry or is_text):
                return None
            sel = self.get_selection(w, is_entry)
            if sel:
                copy_to_clipboard(self.root, sel)
                if action == "cut":
                    self.drop_selection(w, is_entry)
            return "break"

        if action == "all":
            if is_text:
                w.tag_add("sel", "1.0", "end-1c")
                return "break"
            if is_entry:
                w.select_range(0, "end")
                w.icursor("end")
                return "break"
            return None

        if action == "undo":
            if is_text:
                try:
                    w.edit_undo()
                except tk.TclError:
                    pass
                return "break"
            if is_entry:
                return "break"
            self.undo()
            return "break"

        if action == "new":
            self.show_add()
            return "break"
        return None

    @staticmethod
    def get_selection(w, is_entry):
        try:
            if is_entry:
                if not w.selection_present():
                    return ""
                return w.get()[w.index("sel.first"):w.index("sel.last")]
            return w.get("sel.first", "sel.last")
        except tk.TclError:
            return ""

    @staticmethod
    def drop_selection(w, is_entry):
        try:
            if is_entry:
                if w.selection_present():
                    w.delete("sel.first", "sel.last")
            else:
                w.delete("sel.first", "sel.last")
        except tk.TclError:
            pass

    # ---------- поверх всех окон ----------
    def toggle_pin(self):
        self.pinned = not self.pinned
        self.apply_pin()
        self.schedule_save()

    def apply_pin(self):
        try:
            self.root.attributes("-topmost", bool(self.pinned))
        except tk.TclError:
            pass
        if self.pinned:
            try:
                self.root.lift()
            except tk.TclError:
                pass
        self.update_pin_look()

    def topmost_keepalive(self):
        """macOS иногда сбрасывает уровень окна — переставляем флаг."""
        if self.pinned:
            try:
                self.root.attributes("-topmost", True)
            except tk.TclError:
                pass
        self.root.after(1500, self.topmost_keepalive)

    def update_pin_look(self):
        self.btn_pin.restyle(C["bar"], C["accent"] if self.pinned else C["muted"])
        self.btn_pin.configure(
            text=self.icons["pin_on"] if self.pinned else self.icons["pin_off"]
        )

    # ---------- тема ----------
    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        C.update(THEMES[self.theme])
        self.apply_theme()
        self.schedule_save()

    def update_theme_look(self):
        self.btn_theme.configure(text="☾" if self.theme == "dark" else "☀")

    def apply_theme(self):
        self.root.configure(bg=C["bg"])
        self.bar.configure(bg=C["bar"])
        self.status.configure(bg=C["bar"])
        self.addbar.configure(bg=C["bar"])
        self.sep1.configure(bg=C["border"])
        self.sep2.configure(bg=C["border"])
        self.wrap.configure(bg=C["bg"])
        self.canvas.configure(bg=C["bg"])
        self.inner.configure(bg=C["bg"])
        self.lbl_cut.configure(bg=C["bar"], fg=C["fg"])
        self.lbl_count.configure(bg=C["bar"], fg=C["muted"])
        self.lbl_hint.configure(bg=C["bar"], fg=C["muted"])
        self.entry.configure(
            bg=C["field"], fg=C["fg"], insertbackground=C["fg"],
            highlightbackground=C["border"], highlightcolor=C["accent"]
        )
        self.btn_edit.restyle(C["bar"], C["muted"])
        self.btn_undo.restyle(C["bar"], C["muted"])
        self.btn_theme.restyle(C["bar"], C["muted"])
        self.btn_add.restyle(C["bar"], C["accent"])
        self.btn_ver.restyle(
            C["bar"], C["accent"] if self._upd_pending else C["muted"]
        )
        self.btn_add_ok.restyle(C["accent"], "#ffffff")
        self.sw_cut.restyle()
        self.update_pin_look()
        self.update_theme_look()
        self.render()

    def update_count(self):
        self.lbl_count.configure(text="запросов: %d" % len(self.queries))

    def set_hint(self, text):
        self.lbl_hint.configure(text=text)
        self.root.after(1200, lambda: self.lbl_hint.configure(text=""))

    # ---------- обновления ----------
    def silent_update_check(self):
        """Тихо смотрим, есть ли новый релиз. Нашли — подсвечиваем версию."""
        if app_bundle_path() is None or self._upd_busy:
            return
        self._upd_busy = True
        threading.Thread(target=self._check_worker, args=(True,), daemon=True).start()

    def updates_click(self):
        if self._upd_pending:
            tag, link = self._upd_pending
            self.offer_update(tag, link)
            return
        if app_bundle_path() is None:
            self.set_hint("только для приложения")
            return
        if self._upd_busy:
            return
        self._upd_busy = True
        self.btn_ver.configure(text="проверяю\u2026")
        threading.Thread(target=self._check_worker, args=(False,), daemon=True).start()

    def _check_worker(self, silent):
        try:
            tag, link = fetch_latest_release()
            err = None
        except Exception as exc:
            tag, link, err = None, None, str(exc)
        self.root.after(0, lambda: self._check_done(tag, link, err, silent))

    def _check_done(self, tag, link, err, silent):
        self._upd_busy = False
        self.btn_ver.configure(text="v" + APP_VERSION)
        if err is not None:
            if not silent:
                self.set_hint("сеть недоступна")
            return
        if not tag or version_tuple(tag) <= version_tuple(APP_VERSION):
            if not silent:
                self.set_hint("версия актуальна")
            return
        if not link:
            if not silent:
                self.set_hint("в релизе нет файла")
            return
        self._upd_pending = (tag, link)
        self.btn_ver.restyle(C["bar"], C["accent"])
        self.btn_ver.configure(text=tag + " \u2b07")
        if not silent:
            self.offer_update(tag, link)

    def offer_update(self, tag, link):
        win = tk.Toplevel(self.root)
        win.title("Обновление")
        win.configure(bg=C["bg"])
        win.resizable(False, False)
        win.transient(self.root)
        try:
            win.attributes("-topmost", True)
        except tk.TclError:
            pass

        body = tk.Frame(win, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=18, pady=16)

        tk.Label(
            body, text="Доступна версия " + tag, bg=C["bg"], fg=C["fg"],
            font=self.f_ui
        ).pack(anchor="w")
        state = tk.Label(
            body, text="Сейчас установлена v" + APP_VERSION,
            bg=C["bg"], fg=C["muted"], font=self.f_small
        )
        state.pack(anchor="w", pady=(4, 14))

        btns = tk.Frame(body, bg=C["bg"])
        btns.pack(fill="x")

        def start():
            state.configure(text="Загружаю\u2026", fg=C["fg"])
            for child in btns.winfo_children():
                child.destroy()
            win.update_idletasks()
            threading.Thread(
                target=self._install_worker, args=(link, win, state), daemon=True
            ).start()

        IconButton(
            btns, "  Обновить  ", start,
            bg=C["accent"], fg="#ffffff", font=self.f_ui, pad=(10, 6)
        ).pack(side="right")
        IconButton(
            btns, "  Позже  ", win.destroy,
            bg=C["bg"], fg=C["muted"], font=self.f_ui, pad=(10, 6)
        ).pack(side="right", padx=(0, 8))

    def _install_worker(self, link, win, state):
        bundle = app_bundle_path()
        try:
            install_update(link, bundle)
            err = None
        except Exception as exc:
            err = str(exc)
        self.root.after(0, lambda: self._install_done(err, bundle, win, state))

    def _install_done(self, err, bundle, win, state):
        if err is not None:
            try:
                state.configure(text="Не вышло: " + err[:60], fg=C["danger"])
            except tk.TclError:
                pass
            return
        try:
            state.configure(text="Готово, перезапускаю\u2026")
        except tk.TclError:
            pass
        self.save_state()
        try:
            subprocess.Popen(["open", "-n", bundle])
        except Exception:
            pass
        self.root.after(400, lambda: os._exit(0))

    # ---------- редактор списка ----------
    def open_editor(self):
        win = tk.Toplevel(self.root)
        win.title("Список запросов")
        win.configure(bg=C["bg"])
        win.geometry("520x460")
        win.transient(self.root)
        try:
            win.attributes("-topmost", self.pinned)
        except tk.TclError:
            pass

        tk.Label(
            win, text="Каждая новая строка — отдельный запрос",
            bg=C["bg"], fg=C["muted"], font=self.f_small, anchor="w"
        ).pack(fill="x", padx=10, pady=(10, 4))

        txt = tk.Text(
            win, bg=C["field"], fg=C["fg"], insertbackground=C["fg"], font=self.f_row,
            wrap="word", bd=0, highlightthickness=1, highlightbackground=C["border"],
            padx=8, pady=8, undo=True
        )
        txt.pack(fill="both", expand=True, padx=10)
        txt.insert("1.0", "\n".join(self.queries))
        txt.focus_set()

        btns = tk.Frame(win, bg=C["bg"])
        btns.pack(fill="x", padx=10, pady=10)

        def apply_and_close(mode):
            raw = txt.get("1.0", "end").splitlines()
            lines = [s.strip() for s in raw]
            lines = [s for s in lines if s]
            if mode == "replace":
                self.queries = lines
            else:
                self.queries = self.queries + lines
            self.undo_stack.clear()
            self.render()
            self.schedule_save()
            win.destroy()

        IconButton(
            btns, "  Заменить список  ", lambda: apply_and_close("replace"),
            bg=C["accent"], fg="#ffffff", font=self.f_ui, pad=(10, 6)
        ).pack(side="right")
        IconButton(
            btns, "  Добавить в конец  ", lambda: apply_and_close("append"),
            bg=C["row"], fg=C["fg"], font=self.f_ui, pad=(10, 6)
        ).pack(side="right", padx=(0, 8))
        IconButton(
            btns, "  Отмена  ", win.destroy,
            bg=C["bg"], fg=C["muted"], font=self.f_ui, pad=(10, 6)
        ).pack(side="left")

    # ---------- состояние ----------
    def load_state(self):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
        return {}

    def save_state(self):
        self._save_job = None
        data = {
            "geometry": self.root.winfo_geometry(),
            "queries": self.queries,
            "cut_mode": self.cut_mode,
            "pinned": self.pinned,
            "theme": self.theme,
        }
        try:
            os.makedirs(STATE_DIR, exist_ok=True)
            tmp = STATE_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
            os.replace(tmp, STATE_FILE)
        except Exception:
            pass

    def schedule_save(self):
        if self._save_job is not None:
            self.root.after_cancel(self._save_job)
        self._save_job = self.root.after(400, self.save_state)

    def on_configure(self, event):
        if event.widget is self.root:
            self.schedule_save()

    def on_close(self):
        if self._save_job is not None:
            self.root.after_cancel(self._save_job)
        self.save_state()
        self.root.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()

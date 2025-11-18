import tkinter as tk


def apply_custom_titlebar(root, theme):
    # tira a barra padrão
    root.overrideredirect(True)

    bg = theme["theme"]["panel"]
    fg = theme["theme"]["text"]

    title_bar = tk.Frame(root, bg=bg, relief="flat", bd=0, height=28)
    title_bar.pack(fill="x", side="top")

    title_label = tk.Label(
        title_bar,
        text="  StreamDeck Felitron V6",
        bg=bg,
        fg=fg,
        font=(theme["theme"]["font"], theme["theme"]["font_size"], "bold")
    )
    title_label.pack(side="left", padx=5)

    # Botão fechar
    close_btn = tk.Label(
        title_bar, text=" ✕ ",
        bg=bg, fg="#ff5555",
        font=(theme["theme"]["font"], theme["theme"]["font_size"])
    )
    close_btn.pack(side="right", padx=4)

    # Botão minimizar
    min_btn = tk.Label(
        title_bar, text=" ─ ",
        bg=bg, fg=fg,
        font=(theme["theme"]["font"], theme["theme"]["font_size"])
    )
    min_btn.pack(side="right", padx=4)

    # Eventos
    def close_window(event=None):
        root.destroy()

    def minimize_window(event=None):
        root.iconify()

    close_btn.bind("<Button-1>", close_window)
    min_btn.bind("<Button-1>", minimize_window)

    # Drag da janela
    def start_move(event):
        root.x = event.x
        root.y = event.y

    def stop_move(event):
        root.x = None
        root.y = None

    def do_move(event):
        x = event.x_root - root.x
        y = event.y_root - root.y
        root.geometry(f"+{x}+{y}")

    for widget in (title_bar, title_label):
        widget.bind("<Button-1>", start_move)
        widget.bind("<ButtonRelease-1>", stop_move)
        widget.bind("<B1-Motion>", do_move)

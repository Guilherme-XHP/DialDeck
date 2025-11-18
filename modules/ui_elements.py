import os
import tkinter as tk
from tkinter import simpledialog, filedialog
from PIL import Image, ImageTk

ASSET_DIR = os.path.join("assets", "icons")


class KeyButton(tk.Frame):
    def __init__(self, parent, key_char, keymap_manager, theme, on_mapping_changed):
        super().__init__(parent, bg=theme["theme"]["background"])

        self.key = key_char
        self.km = keymap_manager
        self.theme = theme
        self.on_mapping_changed = on_mapping_changed
        self._icon_img = None

        # Frame fixo do botão (quadrado)
        self.config(width=82, height=82)
        self.pack_propagate(False)

        # Botão interno
        self.button = tk.Button(
            self,
            text=self.key,
            bg=theme["theme"]["button"],
            fg=theme["theme"]["text"],
            activebackground=theme["theme"]["button_active"],
            activeforeground=theme["theme"]["text"],
            font=(theme["theme"]["font"], 10),
            bd=0,
            relief="flat",
            compound="top",
            width=80,
            height=80,
            padx=2,
            pady=2
        )
        self.button.pack(fill="both", expand=True)

        # Hover
        self.button.bind("<Enter>", self._on_enter)
        self.button.bind("<Leave>", self._on_leave)
        self.button.bind("<Button-3>", self._on_right_click)

        self._update_visual()

    # Hover
    def _on_enter(self, event):
        self.button.configure(bg=self.theme["theme"]["button_hover"])

    def _on_leave(self, event):
        self.button.configure(bg=self.theme["theme"]["button"])

    # Flash ao pressionar no serial
    def flash(self):
        self.button.configure(bg=self.theme["theme"]["button_active"])
        self.after(120, lambda: self.button.configure(bg=self.theme["theme"]["button"]))

    # Menu direito
    def _on_right_click(self, event):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Alterar ação…", command=self._change_action)
        menu.add_command(label="Alterar ícone…", command=self._change_icon)
        menu.add_separator()
        menu.add_command(label="Remover ícone", command=self._remove_icon)

        menu.tk_popup(event.x_root, event.y_root)

    def _change_action(self):
        current = self.km.get_action(self.key) or ""
        new = simpledialog.askstring(
            "Configurar ação", 
            f"Ação para {self.key}:", 
            initialvalue=current, 
            parent=self.winfo_toplevel()
        )
        if not new:
            return
        self.km.set_action(self.key, new.strip())
        self._update_visual()

    def _change_icon(self):
        file = filedialog.askopenfilename(
            title="Escolher ícone",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp")],
            initialdir=os.path.abspath(ASSET_DIR)
        )
        if file:
            self.km.set_icon(self.key, file)
            self._update_visual()

    def _remove_icon(self):
        self.km.set_icon(self.key, None)
        self._update_visual()

    # Atualização visual principal
    def _update_visual(self):
        action = self.km.get_action(self.key) or ""
        icon_path = self.km.get_icon(self.key)

        if icon_path is None:
            icon_path = self._guess_icon_from_action(action)

        if icon_path and os.path.exists(icon_path):
            self._apply_icon(icon_path, action)
        else:
            self._set_text(action)

    # Detecta ícones automáticos
    def _guess_icon_from_action(self, action):
        action = action.lower()
        matches = {
            "play": "play.png",
            "pause": "play.png",
            "previous": "prev.png",
            "back": "prev.png",
            "next": "next.png",
            "mute": "mute.png"
        }
        for key, icon in matches.items():
            if key in action:
                path = os.path.join(ASSET_DIR, icon)
                if os.path.exists(path):
                    return path
        return None

    # Aplica ícone e texto pequeno
    def _apply_icon(self, path, action):
        try:
            img = Image.open(path)
            w, h = img.size

            # Ícone 40px máx
            scale = 40 / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

            self._icon_img = ImageTk.PhotoImage(img)

            # Texto pequeno
            short = action if len(action) <= 12 else action[:10] + "…"

            self.button.config(
                image=self._icon_img,
                text=short,
                font=(self.theme["theme"]["font"], 8),
                compound="top"
            )

        except Exception as e:
            print("Erro ícone:", e)
            self._set_text(action)

    # Apenas texto
    def _set_text(self, action):
        short = action if len(action) <= 14 else action[:12] + "…"
        if action:
            self.button.config(image="", text=f"{self.key}\n{short}")
        else:
            self.button.config(image="", text=self.key)

import os
import serial
import tkinter as tk
from tkinter import ttk, scrolledtext
import keyboard
import yaml

from modules.serial_handler import SerialHandler
from modules.keymap_manager import KeymapManager
from modules.ui_elements import KeyButton
from modules.system_monitor import get_cpu_usage, get_ram_usage


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class StreamDeckApp:
    def __init__(self, root):
        self.root = root
        root.title("DialDeck - StreamDeck Do Paraguai")

        # FORÇA ÍCONE NA TASKBAR
        try:
            root.iconbitmap("assets/logo.ico")
        except:
            pass

        self.config_data = load_yaml("config/settings.yaml")["settings"]
        self.theme = load_yaml("config/theme.yaml")
        self.km = KeymapManager("config/keys.yaml")

        w = self.config_data.get("window_width", 780)
        h = self.config_data.get("window_height", 720)

        root.geometry(f"{w}x{h}")
        root.configure(bg=self.theme["theme"]["background"])

        # SERIAL
        baud = self.config_data.get("baud_rate", 115200)
        self.serial = SerialHandler(self.on_serial_key, baud=baud)

        # UI
        self._build_top_bar()
        self._build_main_layout()
        self._build_debug()

        # Inicializa portas
        self.refresh_ports()

        # Monitor
        self.root.after(1000, self.update_monitor)

        # Auto-detect
        if self.config_data.get("auto_connect", True):
            self.root.after(1500, self.auto_detect_loop)

    # ------------------ UI PARTS ------------------ #
    def _build_top_bar(self):
        self.top_frame = tk.Frame(self.root, bg=self.theme["theme"]["background"])
        self.top_frame.pack(fill="x", pady=(10, 8))

        tk.Label(
            self.top_frame, text="Porta:",
            bg=self.theme["theme"]["background"],
            fg=self.theme["theme"]["text"],
            font=(self.theme["theme"]["font"], self.theme["theme"]["font_size"])
        ).pack(side="left", padx=8)

        self.port_combo = ttk.Combobox(self.top_frame, width=12, state="readonly")
        self.port_combo.pack(side="left", padx=5)

        tk.Button(
            self.top_frame, text="↻",
            command=self.refresh_ports,
            bg=self.theme["theme"]["button"],
            fg=self.theme["theme"]["text"],
            bd=0
        ).pack(side="left")

        tk.Button(
            self.top_frame, text="Conectar",
            command=self.connect_clicked,
            bg=self.theme["theme"]["button"],
            fg=self.theme["theme"]["text"],
            bd=0
        ).pack(side="left", padx=4)

        tk.Button(
            self.top_frame, text="Desconectar",
            command=self.disconnect_clicked,
            bg=self.theme["theme"]["button"],
            fg=self.theme["theme"]["text"],
            bd=0
        ).pack(side="left")

        self.status_label = tk.Label(
            self.top_frame, text="Desconectado",
            bg=self.theme["theme"]["background"],
            fg="#ff5555",
            font=(self.theme["theme"]["font"], self.theme["theme"]["font_size"])
        )
        self.status_label.pack(side="left", padx=20)

    def _build_main_layout(self):
        self.main_frame = tk.Frame(self.root, bg=self.theme["theme"]["background"])
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # LEFT: keyboard
        self.left_frame = tk.Frame(self.main_frame, bg=self.theme["theme"]["background"])
        self.left_frame.pack(side="left", padx=20, pady=10)

        tk.Label(
            self.left_frame,
            text="Teclado",
            bg=self.theme["theme"]["background"],
            fg=self.theme["theme"]["text"],
            font=(self.theme["theme"]["font"], 13)
        ).pack(pady=5)

        self.keyboard_frame = tk.Frame(
            self.left_frame,
            bg=self.theme["theme"]["background"],
            width=320,
            height=400
        )
        self.keyboard_frame.pack_propagate(False)
        self.keyboard_frame.pack(pady=10)

        layout = [
            ['1','2','3'],
            ['4','5','6'],
            ['7','8','9'],
            ['*','0','#'],
            ['M','A','B','C']
        ]

        self.key_buttons = {}
        for r, row in enumerate(layout):
            for c, key in enumerate(row):
                kb = KeyButton(
                    self.keyboard_frame,
                    key_char=key,
                    keymap_manager=self.km,
                    theme=self.theme,
                    on_mapping_changed=self.on_mapping_changed
                )
                kb.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
                self.key_buttons[key] = kb

        # RIGHT: info
        self.right_frame = tk.Frame(self.main_frame, bg=self.theme["theme"]["background"])
        self.right_frame.pack(side="right", padx=20, pady=10)

        tk.Label(
            self.right_frame, text="Informações",
            bg=self.theme["theme"]["background"],
            fg=self.theme["theme"]["text"],
            font=(self.theme["theme"]["font"], 13)
        ).pack(pady=5)

        self.last_key_var = tk.StringVar(value="---")
        self.sent_key_var = tk.StringVar(value="---")

        tk.Label(
            self.right_frame, text="Última tecla:",
            bg=self.theme["theme"]["background"], fg=self.theme["theme"]["text"]
        ).pack()
        tk.Label(
            self.right_frame, textvariable=self.last_key_var,
            bg=self.theme["theme"]["background"], fg="#00d0ff",
            font=(self.theme["theme"]["font"], 14)
        ).pack(pady=4)

        tk.Label(
            self.right_frame, text="Enviada:",
            bg=self.theme["theme"]["background"], fg=self.theme["theme"]["text"]
        ).pack()
        tk.Label(
            self.right_frame, textvariable=self.sent_key_var,
            bg=self.theme["theme"]["background"], fg="#f5d300",
            font=(self.theme["theme"]["font"], 14)
        ).pack(pady=4)

        self.cpu_label = tk.Label(
            self.right_frame, text="CPU: --%",
            bg=self.theme["theme"]["background"], fg=self.theme["theme"]["text"]
        )
        self.cpu_label.pack(pady=4)

        self.ram_label = tk.Label(
            self.right_frame, text="RAM: -- MB",
            bg=self.theme["theme"]["background"], fg=self.theme["theme"]["text"]
        )
        self.ram_label.pack(pady=4)

    def _build_debug(self):
        tk.Label(
            self.root, text="Debug",
            bg=self.theme["theme"]["background"],
            fg=self.theme["theme"]["text"]
        ).pack(pady=4)

        self.debug_box = scrolledtext.ScrolledText(
            self.root,
            width=90,
            height=10,
            bg="#101010",
            fg=self.theme["theme"]["text"],
            borderwidth=0,
            insertbackground="white"
        )
        self.debug_box.pack(pady=8)

    # --------- SERIAL / PORTS --------- #
    def refresh_ports(self):
        ports = self.serial.list_ports()
        self.port_combo["values"] = ports
        if ports:
            self.port_combo.current(0)
        self.log("Portas atualizadas.")

    def connect_clicked(self):
        port = self.port_combo.get()
        if not port:
            self.log("Nenhuma porta selecionada.")
            return
        ok = self.serial.connect(port)
        if ok:
            self.status_label.config(text=f"Conectado ({port})", fg="#44ff44")
            self.log(f"Conectado em {port}")
        else:
            self.status_label.config(text="Erro ao conectar", fg="#ff5555")
            self.log(f"Falha ao conectar em {port}")

    def disconnect_clicked(self):
        self.serial.disconnect()
        self.status_label.config(text="Desconectado", fg="#ff5555")
        self.log("Desconectado.")

    def auto_detect_loop(self):
        if self.serial.is_connected():
            self.root.after(2000, self.auto_detect_loop)
            return

        ports = self.serial.list_ports()
        for p in ports:
            try:
                test = serial.Serial(p, self.config_data.get("baud_rate", 115200), timeout=0.2)
                data = test.read(32).decode(errors="ignore")
                test.close()
                if "KEY_" in data:
                    self.port_combo.set(p)
                    self.connect_clicked()
                    self.log(f"Auto-conectado em {p}")
                    break
            except Exception:
                continue

        self.root.after(2000, self.auto_detect_loop)

    # --------- SERIAL CALLBACK --------- #
    def on_serial_key(self, linha: str):
        self.last_key_var.set(linha)

        if not linha.startswith("KEY_"):
            self.log(f"Recebido desconhecido: {linha}")
            return

        key_char = linha.replace("KEY_", "")
        action = self.km.get_action(key_char)
        if not action:
            self.log(f"Sem ação configurada para {key_char}")
        else:
            try:
                keyboard.press_and_release(action)
                self.sent_key_var.set(action)
                self.log(f"{key_char} → {action}")
            except Exception as e:
                self.log(f"Erro ao enviar ação {action}: {e}")

        if key_char in self.key_buttons:
            self.key_buttons[key_char].flash()

    def on_mapping_changed(self, key, new_action):
        self.log(f"Tecla {key} agora faz: {new_action}")

    # --------- MONITOR --------- #
    def update_monitor(self):
        cpu = get_cpu_usage()
        ram = get_ram_usage()
        self.cpu_label.config(text=f"CPU: {cpu:.1f}%")
        self.ram_label.config(text=f"RAM: {ram:.1f} MB")
        self.root.after(1000, self.update_monitor)

    # -------- LOG -------- #
    def log(self, msg: str):
        self.debug_box.insert(tk.END, msg + "\n")
        self.debug_box.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = StreamDeckApp(root)
    root.mainloop()


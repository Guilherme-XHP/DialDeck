import os
import yaml

KEYMAP_FILE = os.path.join("config", "keys.yaml")


class KeymapManager:
    def __init__(self, path=KEYMAP_FILE):
        self.path = path
        self.keys = {}
        self.load()

    # ──────────────────────────────────────────────
    # Carregar YAML (suporte formato antigo e novo)
    # ──────────────────────────────────────────────
    def load(self):
        if not os.path.exists(self.path):
            self.keys = {}
            return

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            print("Erro carregando keys.yaml:", e)
            self.keys = {}
            return

        # FORMATO NOVO? ótimo.
        if all(isinstance(v, dict) for v in data.values()):
            self.keys = data
            return

        # FORMATO ANTIGO? converter.
        converted = {}
        for k, v in data.get("keys", {}).items():
            new_key = f"KEY_{k.upper()}"
            converted[new_key] = {
                "action": v,
                "icon": None
            }

        self.keys = converted
        self.save()

    # ──────────────────────────────────────────────
    # Salvar YAML no formato novo
    # ──────────────────────────────────────────────
    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                yaml.dump(self.keys, f, allow_unicode=True, sort_keys=True)
        except Exception as e:
            print("Erro salvando keys.yaml:", e)

    # ──────────────────────────────────────────────
    # AÇÕES
    # ──────────────────────────────────────────────
    def get_action(self, key):
        k = f"KEY_{key.upper()}"
        if k not in self.keys:
            return None
        return self.keys[k].get("action")

    def set_action(self, key, action):
        k = f"KEY_{key.upper()}"
        if k not in self.keys:
            self.keys[k] = {}
        self.keys[k]["action"] = action
        self.save()

    # ──────────────────────────────────────────────
    # ÍCONES
    # ──────────────────────────────────────────────
    def get_icon(self, key):
        k = f"KEY_{key.upper()}"
        if k not in self.keys:
            return None
        return self.keys[k].get("icon")

    def set_icon(self, key, icon_path):
        k = f"KEY_{key.upper()}"
        if k not in self.keys:
            self.keys[k] = {}

        if icon_path is None:
            self.keys[k]["icon"] = None
        else:
            icon_path = icon_path.replace("\\", "/")
            if "assets/icons/" in icon_path:
                icon_path = icon_path[icon_path.index("assets/icons/"):]
            self.keys[k]["icon"] = icon_path

        self.save()

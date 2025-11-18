# DialDeck — README

Um projeto open‑source que transforma um teclado telefônico Felitron S8010 em um StreamDeck customizável.

Principais tecnologias:
- NodeMCU (ESP8266)
- Matrix scan 4×4 descoberta manualmente
- Comunicação via Serial USB
- Aplicação Python + Tkinter para GUI
- Ações configuráveis (atalhos, mídia, macros, etc.)
- Ícones customizáveis por botão
- Suporte para compilação em .exe via PyInstaller

---

## 1. Hardware
Componentes:
- NodeMCU ESP-12E (ESP8266)
- Teclado/membrana Felitron S8010
- Jumpers para interligar matriz ao NodeMCU

O conector RJ-9 do teclado expõe 22 pads; 8 deles formam uma matriz 4×4 funcional. O mapeamento foi feito manualmente.

---

## 2. Descoberta da Matriz

Linhas (Row): 3, 5, 7, 9  
Colunas (Col): 1, 2, 4, 6

Mapeamento final das teclas principais:
- 7 - 4 = 1
- 7 - 2 = 2
- 7 - 1 = 3
- 3 - 6 = 4
- 3 - 4 = 5
- 3 - 2 = 6
- 3 - 1 = 7
- 5 - 6 = 8
- 5 - 4 = 9
- 5 - 1 = *
- 5 - 2 = 0
- 9 - 6 = #

Teclas extras (referência histórica; não pertencem à matriz principal):
- 7 - 6 = mute (mapeado como key_M, pois ele usa os row e col padrões)
- 5 - 2 + D23 = tone
- 7 - 6 + D22 = redial
- 18 - 9 = flash
- 16 - 17 = on/off
- 7 - 1 + D22 = vol -
- 7 - 2 + D22 = vol +

Algumas dependem de diodos ou resistores internos.

---

## 3. Firmware NodeMCU (Arduino IDE)
O firmware do ESP8266 atua como teclado serial, enviando strings como:
```
KEY_1
KEY_2
...
KEY_M
KEY_A
KEY_B
KEY_C
```

Bibliotecas: nenhuma externa — apenas suporte ESP8266 Boards.

Instalar ESP8266 no Arduino IDE:
1. Abra Arquivo → Preferências  
2. Em “URLs adicionais para Gerenciador de Placas”, adicione:
    `https://arduino.esp8266.com/stable/package_esp8266com_index.json`
3. Vá em Ferramentas → Placas → Gerenciador de Placas, pesquise por ESP8266 e instale.
4. Selecione “NodeMCU 1.0 (ESP-12E Module)”.

Upload: conectar USB e clicar em Upload.

---

## 4. Software Python (Tkinter)
Funcionalidades:
- Recebe eventos via Serial
- Mostra teclas pressionadas e comandos enviados
- Envia atalhos para o sistema
- Permite configurar ações por tecla
- Ao configurar funções das teclas, use os nomes suportados listados em [keyref.md](keyref.md) (essa lista contém os nomes válidos que podem ser usados em keys.yaml)
- Suporta ícones (PNG/JPG/WebP)
- Auto-detecção da porta serial
- Monitor CPU/RAM
- Terminal de debug
- Salva configurações em YAML

Executar manualmente:
```
python streamdeck.py
```

---

## 5. Estrutura de Pastas
```
StreamDeck/
├── streamdeck.py
├── requirements.txt
├── serialnumpad/
│   └── serialnumpad.ino
├── config/
│   ├── settings.yaml
│   ├── theme.yaml
│   ├── keys.yaml
│   └── keyref.md
├── assets/
│   ├── logo.png  / logo.ico
│   └── icons/
│       ├── play.png
│       ├── prev.png
│       ├── next.png
│       └── mute.png
└── modules/
     ├── serial_handler.py
     ├── keymap_manager.py
     ├── system_monitor.py
     └── ui_elements.py
```

---

## 6. Instalar dependências
Dentro da pasta do projeto:
```
pip install -r requirements.txt
```

requirements.txt:
```
pyserial
keyboard
psutil
pyyaml
pillow
```

---

## 7. Como compilar para .EXE (Windows)
Instalar PyInstaller:
```
pip install pyinstaller
```

Gerar .exe:
```
python -m PyInstaller --onefile --noconsole --icon=assets/logo.ico streamdeck.py
```

Flags:
- --onefile: cria um único .exe  
- --noconsole: remove janela de terminal  
- --icon: define ícone  
- streamdeck.py: entrypoint

O executável aparecerá em `dist/streamdeck.exe`. Mover o .exe para a raiz do projeto, pois o PyInstaller não copia as pastas assets/ e config/.

---

## 8. Licença

Este projeto está sob a [Licença MIT](LICENSE).

Você pode usar, modificar e distribuir livremente, desde que mantenha os créditos.



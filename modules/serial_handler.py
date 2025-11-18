import serial
import serial.tools.list_ports
import threading


class SerialHandler:
    def __init__(self, on_key_callback, baud=115200):
        """
        on_key_callback: função que recebe `linha` (ex: "KEY_1")
        """
        self.on_key_callback = on_key_callback
        self.baud = baud
        self.ser = None
        self.running = False

    # Lista portas disponíveis
    def list_ports(self):
        return [p.device for p in serial.tools.list_ports.comports()]

    # Conecta em uma porta
    def connect(self, port: str) -> bool:
        self.disconnect()
        try:
            self.ser = serial.Serial(port, self.baud, timeout=0.1)
            self.running = True
            t = threading.Thread(target=self._loop, daemon=True)
            t.start()
            return True
        except Exception:
            self.ser = None
            self.running = False
            return False

    def disconnect(self):
        self.running = False
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
        self.ser = None

    def is_connected(self):
        return self.ser is not None and self.running

    # Loop de leitura
    def _loop(self):
        while self.running and self.ser:
            try:
                if self.ser.in_waiting:
                    linha = self.ser.readline().decode(errors="ignore").strip()
                    if linha:
                        self.on_key_callback(linha)
            except Exception:
                # se der erro, desconecta silenciosamente
                self.disconnect()
                break

import snap7
from snap7.util import *
from snap7.type import *

class S7Manager:
    def __init__(self, ip="192.168.0.10", rack=0, slot=1, db_number=1):
        self.ip = ip
        self.rack = rack
        self.slot = slot
        self.db_number = db_number
        self.client = snap7.client.Client()
        self.connected = False

    def connect(self):
        """Conecta al PLC."""
        try:
            self.client.connect(self.ip, self.rack, self.slot)
            self.connected = self.client.get_connected()
            return self.connected
        except Exception as e:
            print(f"[PLC] Error al conectar: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Desconecta del PLC."""
        try:
            if self.connected:
                self.client.disconnect()
                self.connected = False
                print("[PLC] Desconectado correctamente.")
        except Exception as e:
            print(f"[PLC] Error al desconectar: {e}")

    def read_counts(self):
        """Lee los contadores RedCount y BlueCount del DB1."""
        if not self.connected:
            print("[PLC] No conectado.")
            return None

        try:
            data = self.client.db_read(self.db_number, 0, 8)
            red = get_dint(data, 0)
            blue = get_dint(data, 4)
            return {"RedCount": red, "BlueCount": blue}
        except Exception as e:
            print(f"[PLC] Error al leer: {e}")
            return None

    def set_command(self, value: int):
        """Escribe un valor en DB1.Command (1=rojo, 2=azul)."""
        if not self.connected:
            print("[PLC] No conectado.")
            return

        try:
            data = self.client.db_read(self.db_number, 8, 1)
            set_usint(data, 0, value)
            self.client.db_write(self.db_number, 8, data)
            print(f"[PLC] Command -> {value}")
        except Exception as e:
            print(f"[PLC] Error al escribir: {e}")

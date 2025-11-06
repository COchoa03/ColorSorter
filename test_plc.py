from core.plc_manager import S7Manager

plc = S7Manager(ip="192.168.0.10", rack=0, slot=1, db_number=1)

if plc.connect():
    print("✅ Conectado correctamente")
    plc.set_command(1) 
    counts = plc.read_counts()
    print("Datos leídos:", counts)
    plc.disconnect()
else:
    print("❌ No se pudo conectar")

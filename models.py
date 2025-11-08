# models.py
# ==================== 🏗️ MODELOS DE DATOS ====================

class Reserva:
    """Representa una reserva en el sistema - como un registro en FoxPRO"""
    
    def __init__(self, id, tipo, fecha, turno, cliente, telefono, tipo_cliente, usuario, timestamp):
        self.id = id
        self.tipo = tipo
        self.fecha = fecha
        self.turno = turno
        self.cliente = cliente
        self.telefono = telefono           # 🆕 NUEVO
        self.tipo_cliente = tipo_cliente   # 🆕 NUEVO
        self.usuario = usuario
        self.timestamp = timestamp

    def formato_fecha_salida_amigable(self):
        """Convierte fecha_salida YYYY-MM-DD a DD/MM/AA"""
        if hasattr(self, 'fecha_salida') and self.fecha_salida:
            return f"{self.fecha_salida[8:10]}/{self.fecha_salida[5:7]}/{self.fecha_salida[2:4]}"
        return ""
    
    def to_dict(self):
        """Convierte la reserva a diccionario - para templates"""
        return {
            'id': self.id,
            'tipo': self.tipo,
            'fecha': self.fecha,
            'turno': self.turno,
            'cliente': self.cliente,
            'telefono': self.telefono,           # 🆕 NUEVO
            'tipo_cliente': self.tipo_cliente,   # 🆕 NUEVO
            'usuario': self.usuario,
            'timestamp': self.timestamp
        }
    
    def formato_fecha_amigable(self):
        """Convierte fecha YYYY-MM-DD a DD/MM/AA"""
        if self.fecha:
            return f"{self.fecha[8:10]}/{self.fecha[5:7]}/{self.fecha[2:4]}"
        return ""
    
    def formato_timestamp_amigable(self):
        """Convierte timestamp a DD/MM/AA HH:MM"""
        if self.timestamp:
            fecha = self.timestamp.split()[0]
            hora = self.timestamp.split()[1][:5]
            return f"{fecha[8:10]}/{fecha[5:7]}/{fecha[2:4]} {hora}"
        return ""

    def calcular_costo(self):
        """Calcula el costo según tipo de cliente"""
        if self.tipo_cliente == 'municipal':
            return 0  # Sin cargo
        else:
        # Lógica de precios para particulares
            precios = {'quincho': 5000, 'casa_camping': 3000, 'fogones': 1000}
            return precios.get(self.tipo, 0)

class Usuario:
    """Representa un usuario del sistema"""
    
    def __init__(self, username):
        self.username = username


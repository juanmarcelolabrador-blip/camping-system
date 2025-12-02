# database.py
# ==================== 🗄️ MANEJO DE BASE DE DATOS ====================

import sqlite3
from models import Reserva
from datetime import datetime, timedelta

def obtener_modulo_popular(fecha_desde=None, fecha_hasta=None, modulo=None):
    """
    Encuentra qué módulo tiene más reservas según filtros
    """
    # Primero obtenemos las reservas filtradas
    filtros = {
        'buscar': '',
        'modulos': [modulo] if modulo else [],
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta
    }
    
    reservas = obtener_reservas(filtros)
    
    if not reservas:
        return "Sin datos"
    
    # Contamos por tipo de módulo
    contador = {}
    for reserva in reservas:
        tipo = reserva.tipo
        contador[tipo] = contador.get(tipo, 0) + 1
    
    # Encontramos el más popular
    modulo_popular = max(contador.items(), key=lambda x: x[1])
    
    # Traducir a nombre amigable
    nombres = {
        'casa_camping': 'Casa Camping',
        'quincho': 'Quincho', 
        'fogones': 'Fogones'
    }
    
    return nombres.get(modulo_popular[0], modulo_popular[0])

def calcular_ingresos_totales(fecha_desde=None, fecha_hasta=None, modulo=None):
    """
    Calcula ingresos totales según filtros
    """
    # Primero obtenemos las reservas filtradas (reutilizando tu función)
    filtros = {
        'buscar': '',
        'modulos': [modulo] if modulo else [],
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta
    }
    
    reservas = obtener_reservas(filtros)
    
    # Sumamos los costos (igual que tu función calcular_costo en models.py)
    ingresos_totales = 0
    for reserva in reservas:
        if reserva.tipo_cliente != 'municipal':  # Municipales no pagan
            ingresos_totales += reserva.calcular_costo()
    
    return ingresos_totales

def get_reservas_totales(fecha_desde=None, fecha_hasta=None, modulo=None):
    """
    Cuenta reservas totales según filtros
    """
    query = "SELECT COUNT(*) as total FROM reservas WHERE 1=1"
    params = []
    
    if fecha_desde:
        query += " AND fecha >= ?"
        params.append(fecha_desde)
    if fecha_hasta:
        query += " AND fecha <= ?" 
        params.append(fecha_hasta)
    if modulo:
        query += " AND tipo = ?"
        params.append(modulo)
        
    resultado = db_query(query, params)
    return resultado[0]['total'] if resultado else 0

def get_db_connection():
    """Crea y retorna conexión a la base de datos"""
    conn = sqlite3.connect('demo_camping.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Inicializa la base de datos con estructura NUEVA y datos de ejemplo"""
    conn = get_db_connection()
    c = conn.cursor()

    # Crear tabla de reservas
    c.execute('''CREATE TABLE IF NOT EXISTS reservas
                 (id INTEGER PRIMARY KEY,
                  tipo TEXT,
                  fecha TEXT,
                  fecha_entrada TEXT,
                  hora_entrada TEXT,
                  fecha_salida TEXT,
                  hora_salida TEXT,
                  turno TEXT,
                  cliente TEXT,
                  telefono TEXT,
                  tipo_cliente TEXT,
                  usuario TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # Crear tabla de ocupación rápida
    c.execute('''CREATE TABLE IF NOT EXISTS ocupacion
                 (fecha TEXT,
                  tipo TEXT,
                  status TEXT,
                  reserva_id INTEGER,
                  PRIMARY KEY (fecha, tipo))''')

    # Datos de ejemplo
    reservas_ejemplo = [
        ('quincho', '2025-10-15', 'mañana', 'Familia Pérez',
         '291-4567890', 'particular', 'admin'),
        ('casa_camping', '2025-10-16', 'completo',
         'Municipalidad', '291-1234567', 'municipal', 'admin'),
        ('fogones', '2025-10-20', 'completo', 'Escuela 123',
         '291-9876543', 'particular', 'admin')
    ]

    c.executemany('INSERT OR IGNORE INTO reservas (tipo, fecha, turno, cliente, telefono, tipo_cliente, usuario) VALUES (?,?,?,?,?,?,?)',
                  reservas_ejemplo)
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada con nueva estructura")


def verificar_disponibilidad_casa_completa(fecha_entrada, fecha_salida, hora_entrada=None, hora_salida=None):
    """Verificación inteligente para casa camping - CON HORARIOS"""
    print(f"🐛 DEBUG: INICIANDO validación para {fecha_entrada} a {fecha_salida}")
    print(f"🐛 DEBUG: Horas recibidas: entrada={hora_entrada}, salida={hora_salida}")
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # INICIALIZAR LA VARIABLE
    reserva_existente = None
    
    try:
        # Buscar reservas existentes en ese rango
        query = """
            SELECT * FROM reservas 
            WHERE tipo = 'casa_camping' 
            AND fecha_entrada <= ? AND fecha_salida >= ?
        """
        c.execute(query, (fecha_salida, fecha_entrada))
        reserva_existente = c.fetchone()
        
    except Exception as e:
        print(f"Error en verificación: {e}")
        conn.close()
        return False, "Error al verificar disponibilidad"
    
    # Si hay reserva existente, rechazar inmediatamente
    if reserva_existente:
        conn.close()
        return False, f"❌ Casa camping ya reservada del {reserva_existente['fecha_entrada']} al {reserva_existente['fecha_salida']}"
    
    # Generar rango de fechas a verificar
    fechas_a_verificar = generar_rango_fechas(fecha_entrada, fecha_salida)
    print(f"🐛 DEBUG: Fechas a verificar: {fechas_a_verificar}")

    for fecha in fechas_a_verificar:
        # Verificar en tabla de ocupación rápida
        c.execute(
            "SELECT status, reserva_id FROM ocupacion WHERE fecha = ? AND tipo = 'casa_camping'", (fecha,))
        resultado = c.fetchone()
        print(f"🐛 DEBUG: Resultado en ocupación para {fecha}: {resultado}")
        if resultado:
            status = resultado['status']
            reserva_id = resultado['reserva_id']

            # Si está OCUPADO, rechazar inmediatamente
            if status == 'OCUPADO':
                conn.close()
                return False, f"La casa está completamente ocupada el {fecha}"

            # Si es INGRESO o SALIDA, verificar horarios
            elif status in ['INGRESO', 'SALIDA']:
                # Obtener los horarios de la reserva existente
                c.execute(
                    "SELECT hora_entrada, hora_salida FROM reservas WHERE id = ?", (reserva_id,))
                reserva_existente = c.fetchone()

                if reserva_existente and hora_entrada and hora_salida:
                    # Obtener TODOS los datos de la reserva existente
                    c.execute("SELECT fecha_entrada, hora_entrada, fecha_salida, hora_salida FROM reservas WHERE id = ?", (reserva_id,))
                    existente = c.fetchone()

                    fecha_entrada_existente = existente['fecha_entrada']
                    hora_entrada_existente = existente['hora_entrada']
                    fecha_salida_existente = existente['fecha_salida'] 
                    hora_salida_existente = existente['hora_salida']

                    # 🎯 LÓGICA INTELIGENTE - SEGÚN TU VISIÓN CORRECTA:
                    print(f"🐛 DEBUG: fecha_entrada={fecha_entrada}, fecha_salida_existente={fecha_salida_existente}")
                    print(f"🐛 DEBUG: hora_entrada={hora_entrada}, hora_salida_existente={hora_salida_existente}")

                    # ESCENARIO 1: Nueva entra el mismo día que Existente sale
                    if fecha_entrada == fecha_salida_existente:
                        if hora_entrada < hora_salida_existente:
                            # ❌ BLOQUEAR - Entra ANTES de que salga el anterior
                            print(f"🐛 DEBUG: ✅ BLOQUEANDO - Entra {hora_entrada} antes de salida {hora_salida_existente}")
                            conn.close()
                            return False, f"❌ La casa está ocupada hasta las {hora_salida_existente} del {fecha_salida_existente}"

                    # ESCENARIO 2: Nueva sale el mismo día que Existente entra
                    if fecha_salida == fecha_entrada_existente:
                        if hora_salida > hora_entrada_existente:
                            # ❌ BLOQUEAR - Sale DESPUÉS de que entre el siguiente
                            conn.close()
                            return False, f"❌ La casa está ocupada desde las {hora_entrada_existente} del {fecha_entrada_existente}"

    # Si llegó hasta aquí, es porque está DISPONIBLE
    conn.close()
    return True, "Disponible"

def obtener_reservas(filtros=None):
    """Obtiene reservas de la base de datos con filtros opcionales"""
    conn = get_db_connection()
    c = conn.cursor()
    
    query = "SELECT * FROM reservas WHERE 1=1"
    params = []
    
    if filtros:
        if 'modulos' in filtros and filtros['modulos']:
            placeholders = ','.join(['?'] * len(filtros['modulos']))
            query += f" AND tipo IN ({placeholders})"
            params.extend(filtros['modulos'])
        
        if 'buscar' in filtros and filtros['buscar']:
            query += " AND cliente LIKE ?"
            params.append('%' + filtros['buscar'] + '%')
        
        if 'fecha_desde' in filtros and filtros['fecha_desde']:
            query += " AND fecha >= ?"
            params.append(filtros['fecha_desde'])
        
        if 'fecha_hasta' in filtros and filtros['fecha_hasta']:
            query += " AND fecha <= ?"
            params.append(filtros['fecha_hasta'])
    
    query += " ORDER BY fecha"
    
    c.execute(query, params)
    filas = c.fetchall()
    conn.close()
    
    reservas = []
    for fila in filas:
        reserva = Reserva(
            id=fila['id'],
            tipo=fila['tipo'],
            fecha=fila['fecha'],
            turno=fila['turno'],
            cliente=fila['cliente'],
            telefono=fila['telefono'],
            tipo_cliente=fila['tipo_cliente'],
            usuario=fila['usuario'],
            timestamp=fila['timestamp'],
            fecha_entrada=fila['fecha_entrada'] if 'fecha_entrada' in fila.keys() else None,
            hora_entrada=fila['hora_entrada'] if 'hora_entrada' in fila.keys() else None,
            fecha_salida=fila['fecha_salida'] if 'fecha_salida' in fila.keys() else None,
            hora_salida=fila['hora_salida'] if 'hora_salida' in fila.keys() else None
        )
        reservas.append(reserva)
    
    return reservas

def crear_reserva(tipo, fecha, cliente, telefono, tipo_cliente, usuario, turno='completo'):
    """Crea una nueva reserva en la base de datos"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("INSERT INTO reservas (tipo, fecha, turno, cliente, telefono, tipo_cliente, usuario) VALUES (?,?,?,?,?,?,?)",
              (tipo, fecha, 'completo', cliente, telefono, tipo_cliente, usuario))
    
    reserva_id = c.lastrowid  # 🆕 Obtener el ID de la reserva creada
    conn.commit()
    conn.close()

    return reserva_id  # 🆕 Retornar el ID

# ==================== ✅ VALIDACIONES DE NEGOCIO ====================

def verificar_turno_disponible(tipo, fecha, turno):
 
    """Verifica si un turno está disponible para reserva"""
    conn = get_db_connection()
    c = conn.cursor()
    
    if tipo == 'quincho':
        # Si alguien ya tiene "completo", nadie más puede reservar
        c.execute("SELECT COUNT(*) FROM reservas WHERE tipo = ? AND fecha = ? AND turno = 'completo'", 
                  (tipo, fecha))
        completo_count = c.fetchone()[0]
        if completo_count > 0:
            conn.close()
            return False
        
        # Si el turno solicitado es "completo", verificar que no haya ninguno
        if turno == 'completo':
            c.execute("SELECT COUNT(*) FROM reservas WHERE tipo = ? AND fecha = ?", 
                      (tipo, fecha))
            cualquier_turno_count = c.fetchone()[0]
            conn.close()
            return cualquier_turno_count == 0
        
        # Si es turno específico, verificar que no esté ocupado
        c.execute("SELECT COUNT(*) FROM reservas WHERE tipo = ? AND fecha = ? AND turno IN (?, 'completo')", 
                  (tipo, fecha, turno))
    elif tipo == 'casa_camping':
        c.execute("SELECT COUNT(*) FROM reservas WHERE tipo = ? AND fecha = ?", 
                  (tipo, fecha))
    else:  # fogones
        c.execute("SELECT COUNT(*) FROM reservas WHERE tipo = ? AND fecha = ?", 
                  (tipo, fecha))
    
    count = c.fetchone()[0]
    conn.close()
    return count == 0

def verificar_superposicion_casa(fecha):
    """Verifica superposición de fechas para casa camping"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM reservas WHERE tipo = 'casa_camping' AND fecha = ?", 
              (fecha,))
    count = c.fetchone()[0]
    conn.close()
    return count == 0

# ==================== 🚀 OCUPACIÓN RÁPIDA ====================

def generar_rango_fechas(fecha_entrada, fecha_salida):
    """Genera lista de fechas entre entrada y salida"""
    inicio = datetime.strptime(fecha_entrada, "%Y-%m-%d")
    fin = datetime.strptime(fecha_salida, "%Y-%m-%d")
    
    fechas = []
    current = inicio
    while current <= fin:
        fechas.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    
    return fechas

def verificar_fecha_rapida(fecha, tipo):
    """Verificación rápida usando tabla ocupación"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT status FROM ocupacion WHERE fecha = ? AND tipo = ?", (fecha, tipo))
    resultado = c.fetchone()
    conn.close()
    
    return resultado is None or resultado['status'] == 'DISPONIBLE'

def actualizar_tabla_ocupacion(reserva_id, fecha_entrada, fecha_salida):
    """Actualiza tabla de ocupación después de crear reserva"""
    fechas = generar_rango_fechas(fecha_entrada, fecha_salida)
    
    conn = get_db_connection()
    c = conn.cursor()
    
    for i, fecha in enumerate(fechas):
        if i == 0:
            status = 'INGRESO'
        elif i == len(fechas) - 1:
            status = 'SALIDA'
        else:
            status = 'OCUPADO'
        
        c.execute("INSERT OR REPLACE INTO ocupacion (fecha, tipo, status, reserva_id) VALUES (?, ?, ?, ?)",
                  (fecha, 'casa_camping', status, reserva_id))
    
    conn.commit()
    conn.close()

# Ejecutar inicialización al importar
if __name__ == "__main__":
    init_database()
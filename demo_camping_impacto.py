# demo_camping_impacto.py
# ==================== 🚀 APLICACIÓN PRINCIPAL FLASK ====================

from flask import Flask, render_template, request, session, redirect, send_file, jsonify
import datetime
from database import obtener_reservas, crear_reserva, get_db_connection, actualizar_tabla_ocupacion
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'demo_secret'

# PARTE DONDE DETECTA SI ES UN CELULAR O UNA PC
def es_movil():
    user_agent = request.headers.get('User-Agent', '').lower()
    movil_keywords = ['mobile', 'android', 'iphone', 'ipad']
    return any(keyword in user_agent for keyword in movil_keywords)

# ==================== 📄 GENERAR PDF ====================

def generar_pdf(filtros):
    reservas = obtener_reservas(filtros)
    
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    import io
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Cabecera
    p.drawString(100, 800, "REPORTE DE RESERVAS - CAMPING MUNICIPAL")
    p.drawString(100, 780, f"Total de reservas: {len(reservas)}")
    
    # Información de filtros
    y = 760
    if filtros['buscar']:
        p.drawString(100, y, f"Búsqueda: {filtros['buscar']}")
        y -= 20
    if filtros['fecha_desde']:
        p.drawString(100, y, f"Desde: {filtros['fecha_desde']}")
        y -= 20
    if filtros['fecha_hasta']:
        p.drawString(100, y, f"Hasta: {filtros['fecha_hasta']}")
        y -= 20
    
    # Línea separadora
    y -= 10
    p.line(100, y, 500, y)
    y -= 20
    
    # Contenido de reservas
    for reserva in reservas:
        if y < 100:  # Salto de página si queda poco espacio
            p.showPage()
            y = 800
        
        texto = f"{reserva.tipo.upper()} | {reserva.fecha_entrada} | {reserva.cliente}"
        p.drawString(100, y, texto)
        y -= 20
    
    p.save()
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name="reporte_reservas.pdf", mimetype='application/pdf')


# 🆕 INICIALIZAR BASE DE DATOS AL INICIAR
#init_database()

@app.route('/')
def home():
    # ==================== 🎯 1. VERIFICAR USUARIO ====================
    if 'usuario' not in session:
        return redirect('/login')
    
    # ==================== 🔍 2. LEER FILTROS DEL FORMULARIO ====================
    filtros = {
        'buscar': request.args.get('buscar', ''),
        'modulos': request.args.getlist('modulo'),
        'fecha_desde': request.args.get('fecha_desde', ''),
        'fecha_hasta': request.args.get('fecha_hasta', '')
    }
    
    # ==================== 🗄️ 3. OBTENER RESERVAS ====================
    reservas = obtener_reservas(filtros)
    
    # ==================== 🎨 4. RENDERIZAR TEMPLATE ====================
    return render_template('lista_reservas.html', 
                         reservas=reservas, 
                         hoy=datetime.datetime.now().strftime("%Y-%m-%d"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['usuario'] = request.form['usuario']
        return redirect('/')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🔐 Login - Sistema Camping</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial; margin: 50px; background: #f5f5f5; display: flex; justify-content: center; }
            .login-box { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 300px; width: 100%; }
            input, button { width: 100%; padding: 10px; margin: 5px 0; box-sizing: border-box; }
            button { background: #2E8B57; color: white; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>🔐 Acceso al Sistema</h2>
            <form method="post">
                <input type="text" name="usuario" placeholder="Usuario" value="admin" required>
                <button type="submit">Entrar al Sistema</button>
            </form>
            <p style="text-align: center; color: #666; margin-top: 20px;">Demo Camping Rada Tilly</p>
        </div>
    </body>
    </html>
    '''

# 📊 RUTAS DEL DASHBOARD
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# 🆕 RUTA PARA DATOS FILTRADOS DEL DASHBOARD
@app.route('/api/dashboard_data')
def api_dashboard_data():
    try:
        # Obtener parámetros de filtro
        fecha_desde = request.args.get('fecha_desde', '')
        fecha_hasta = request.args.get('fecha_hasta', '')
        modulo = request.args.get('modulo', '')
        
        print(f"🎯 Filtros recibidos: {fecha_desde} a {fecha_hasta}, módulo: {modulo}")
        
        from database import obtener_reservas, calcular_ingresos_totales
        
        # USAR EXACTAMENTE EL MISMO FORMATO QUE EN TU RUTA PRINCIPAL
        filtros = {
            'buscar': '',  # No usamos búsqueda de cliente en dashboard
            'modulos': [modulo] if modulo else [],  # Convertir a lista como en tu código
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta
        }
        
        reservas_filtradas = obtener_reservas(filtros)
        
        # Contar reservas totales
        reservas_totales = len(reservas_filtradas) if reservas_filtradas else 0
    
        # 🆕 CALCULAR INGRESOS REALES
        ingresos_reales = calcular_ingresos_totales(fecha_desde, fecha_hasta, modulo)
        
        # 🆕 OBTENER MÓDULO POPULAR REAL
        modulo_popular_real = obtener_modulo_popular(fecha_desde, fecha_hasta, modulo)


        datos_reales = {
            'reservas_totales': reservas_totales,
            'ingresos': ingresos_reales,
            'ocupacion': '78%',   # Por ahora sigue siendo ejemplo  
            'modulo_popular': modulo_popular_real  # Por ahora sigue siendo ejemplo
        }
        
        print(f"✅ Enviando datos REALES - Reservas: {reservas_totales}, Ingresos: ${ingresos_reales}, Popular: {modulo_popular_real}")
        return jsonify(datos_reales)
        
    except Exception as e:
        print(f"❌ Error en api_dashboard_data: {e}")
        # Datos de ejemplo como fallback
        datos_ejemplo = {
            'reservas_totales': 124,
            'ingresos': 458600,
            'ocupacion': '78%',
            'modulo_popular': 'Casa Camping'
        }
        return jsonify(datos_ejemplo)
    
# @app.route('/exportar_excel')
# def exportar_excel(filtros=None):  # ← AGREGÁ ESTE PARÁMETRO
#     # ==================== 📊 1. OBTENER DATOS CON FILTROS ACTUALES ====================
#     filtros = {
#         'buscar': request.args.get('buscar', ''),
#         'modulos': request.args.getlist('modulo'),
#         'fecha_desde': request.args.get('fecha_desde', ''),
#         'fecha_hasta': request.args.get('fecha_hasta', '')
#     }
    
#     reservas = obtener_reservas(filtros)
    
#     # ==================== 📋 2. CREAR EXCEL ====================
#     wb = Workbook()
#     ws = wb.active
#     ws.title = "Reservas Camping"
    
#     # ==================== 🎨 3. ENCABEZADOS (como BROWSE) ====================
#     headers = ['ID', 'Módulo', 'Fecha', 'Cliente', 'Teléfono', 'Tipo Cliente', 'Costo', 'Usuario', 'Fecha Reserva']
#     ws.append(headers)
    
#     # Estilo encabezados
#     for cell in ws[1]:
#         cell.font = Font(bold=True)
#         cell.alignment = Alignment(horizontal='center')
    
#     # ==================== 📝 4. LLENAR DATOS ====================
#     for reserva in reservas:
#         costo = 'Gratis' if reserva.tipo_cliente == 'municipal' else f"${reserva.calcular_costo()}"
#         ws.append([
#             reserva.id,
#             reserva.tipo.upper(),
#             reserva.fecha,
#             reserva.cliente,
#             reserva.telefono,
#             reserva.tipo_cliente,
#             costo,
#             reserva.usuario,
#             reserva.timestamp
#         ])
    
#     # ==================== 💾 5. GUARDAR Y ENVIAR ====================
#     from io import BytesIO
#     buffer = BytesIO()
#     wb.save(buffer)
#     buffer.seek(0)
    
#     return send_file(
#         buffer,
#         as_attachment=True,
#         download_name=f"reservas_camping.xlsx",
#         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )

@app.route('/nueva_reserva', methods=['POST'])
def nueva_reserva():
    tipo = request.form['tipo']
    cliente = request.form['cliente']
    telefono = request.form['telefono']
    tipo_cliente = request.form['tipo_cliente']
    
    # Manejar diferentes tipos de reserva
    if tipo == 'casa_camping':
        fecha_entrada = request.form['fecha_entrada']
        hora_entrada = request.form['hora_entrada']
        fecha_salida = request.form['fecha_salida']
        hora_salida = request.form['hora_salida']
        
         # 🆕 VALIDAR QUE LAS FECHAS NO SEAN PASADAS
        from datetime import datetime
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        if fecha_entrada < fecha_actual:
            return f"❌ No se pueden reservar fechas pasadas. Hoy es {fecha_actual}", 400
        if fecha_salida < fecha_actual:
            return f"❌ No se pueden reservar fechas pasadas. Hoy es {fecha_actual}", 400
        
        # Validar que fecha salida no sea anterior a entrada
        if fecha_salida < fecha_entrada:
            return "❌ Error: La fecha de salida no puede ser anterior a la de entrada", 400
        
        # 🎯 TU VALIDACIÓN INTELIGENTE
        from database import verificar_disponibilidad_casa_completa
        disponible, mensaje = verificar_disponibilidad_casa_completa(fecha_entrada, fecha_salida, hora_entrada, hora_salida)
        if not disponible:
            return f"❌ {mensaje}", 400
        
        # Crear reserva y obtener ID
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO reservas (tipo, fecha, fecha_entrada, hora_entrada, fecha_salida, hora_salida, turno, cliente, telefono, tipo_cliente, usuario) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (tipo, None, fecha_entrada, hora_entrada, fecha_salida, hora_salida, 'completo', cliente, telefono, tipo_cliente, session.get('usuario', 'demo')))
        reserva_id = c.lastrowid
        conn.commit()
        conn.close()
                
        # Actualizar tabla de ocupación
        actualizar_tabla_ocupacion(reserva_id, fecha_entrada, fecha_salida)
        
    else:
            # Para quincho y fogones
            fecha = request.form['fecha']
             # 🆕 VALIDAR QUE LA FECHA NO SEA PASADA
            from datetime import datetime
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            if fecha < fecha_actual:
                return f"❌ No se pueden reservar fechas pasadas. Hoy es {fecha_actual}", 400

            # QUINCHO necesita turno específico
            if tipo == 'quincho':
                turno = request.form.get('turno', 'mañana')  # Default a mañana si no viene
                 # 🆕 VALIDAR DISPONIBILIDAD DEL TURNO
                from database import verificar_turno_disponible
                disponible = verificar_turno_disponible(tipo, fecha, turno)
                if not disponible:
                  return f"❌ Quincho no disponible para {fecha} turno {turno}", 400
            
            else:
                turno = 'completo'  # Fogones siempre completo
  
                 # 🆕 VALIDAR DISPONIBILIDAD DE FOGONES
                from database import verificar_turno_disponible
                disponible = verificar_turno_disponible(tipo, fecha, turno)
                if not disponible:
                            return f"❌ Fogones no disponibles para {fecha}", 400
    
          #--  crear_reserva(tipo, fecha, cliente, telefono, tipo_cliente, session.get('usuario', 'demo'), turno)
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO reservas (tipo, fecha, turno, cliente, telefono, tipo_cliente, usuario) VALUES (?,?,?,?,?,?,?)",
        (tipo, fecha, turno, cliente, telefono, tipo_cliente, session.get('usuario', 'demo')))
            conn.commit()
            conn.close()


    return redirect('/')

@app.route('/eliminar_reserva/<int:id>')
def eliminar_reserva(id):
    # ==================== 🗑️ 1. CONECTAR A LA BASE DE DATOS ====================
    conn = get_db_connection()
    c = conn.cursor()
    
    # ==================== 🗑️ 2. EJECUTAR ELIMINACIÓN ====================
    c.execute("DELETE FROM reservas WHERE id = ?", (id,))
    
    # ==================== 💾 3. GUARDAR CAMBIOS ====================
    conn.commit()
    conn.close()
    
    # ==================== 🔄 4. VOLVER A LA LISTA ====================
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')



@app.route('/verificar_disponibilidad')
def verificar_disponibilidad():
    tipo = request.args.get('tipo')
    fecha = request.args.get('fecha')
    turno = request.args.get('turno', 'completo')  # Default si no viene turno
    
    from database import verificar_turno_disponible, verificar_superposicion_casa
    
    if tipo == 'quincho':
        disponible = verificar_turno_disponible(tipo, fecha, turno)
        mensaje = f'Quincho disponible turno {turno}' if disponible else f'Quincho ya reservado para {fecha} turno {turno}'
    elif tipo == 'casa_camping':
        disponible = verificar_superposicion_casa(fecha)
        mensaje = 'Casa camping disponible' if disponible else f'Casa camping ya reservada para {fecha}'
    else:
        disponible = True
        mensaje = 'Disponible'
    
    return {'disponible': disponible, 'mensaje': mensaje}

@app.route('/exportar_reporte')
def exportar_reporte():
    # Obtener filtros actuales
    filtros = {
        'buscar': request.args.get('buscar', ''),
        'modulos': request.args.getlist('modulo'),
        'fecha_desde': request.args.get('fecha_desde', ''),
        'fecha_hasta': request.args.get('fecha_hasta', '')
    }
    
    # Detectar dispositivo y generar archivo
    if es_movil():
        buffer = generar_pdf_puro(filtros)
        filename = "reporte_reservas.pdf"
        mimetype = "application/pdf"
    else:
        buffer = generar_excel_puro(filtros)
        filename = "reservas_camping.xlsx" 
        mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    # Devolver archivo
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype=mimetype)
    #== fin del coso ese de app route exportar_reporte ningo nunga==#
    
    
    # ==================== 🔧 FUNCIONES PURAS DE EXPORTACIÓN ====================

def generar_excel_puro(filtros):
    reservas = obtener_reservas(filtros)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Reservas Camping"
    
    # ENCABEZADOS UNIVERSALES
    headers = ['ID', 'Módulo', 'Cliente', 'Teléfono', 'Tipo Cliente', 'Costo', 'Usuario', 'Fecha Creación', 'Fecha/Turno', 'Detalles Especiales']
    
    ws.append(headers)
    
    for reserva in reservas:
        costo = 'Gratis' if reserva.tipo_cliente == 'municipal' else f"${reserva.calcular_costo()}"
        
        # FECHA/TURNO UNIVERSAL CON VERIFICACIÓN DE None
        if reserva.tipo == 'casa_camping':
            fecha_turno = "Estadía"
            if reserva.fecha_entrada and reserva.hora_entrada:
                detalles = f"Entrada: {reserva.fecha_entrada[8:10]}/{reserva.fecha_entrada[5:7]} {reserva.hora_entrada}"
            else:
                detalles = "Sin datos de entrada"
        elif reserva.tipo == 'quincho':
            fecha_turno = f"{reserva.fecha} ({reserva.turno})" if reserva.fecha else "Sin fecha"
            detalles = f"Turno {reserva.turno}" if reserva.turno else "Sin turno"
        else:  # fogones
            fecha_turno = reserva.fecha if reserva.fecha else "Sin fecha"
            detalles = "Día completo"
        
        fila = [
            reserva.id,
            reserva.tipo.upper(),
            reserva.cliente,
            reserva.telefono,
            reserva.tipo_cliente,
            costo,
            reserva.usuario,
            reserva.formato_timestamp_amigable(),
            fecha_turno,
            detalles
        ]
        
        ws.append(fila)
    
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def generar_pdf_puro(filtros):
    """Versión pura de generar_pdf - sin dependencias de Flask"""
    reservas = obtener_reservas(filtros)
    
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    import io
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Cabecera
    p.drawString(100, 800, "REPORTE DE RESERVAS - CAMPING MUNICIPAL")
    p.drawString(100, 780, f"Total de reservas: {len(reservas)}")
    
    # Información de filtros
    y = 760
    if filtros['buscar']:
        p.drawString(100, y, f"Búsqueda: {filtros['buscar']}")
        y -= 20
    if filtros['fecha_desde']:
        p.drawString(100, y, f"Desde: {filtros['fecha_desde']}")
        y -= 20
    if filtros['fecha_hasta']:
        p.drawString(100, y, f"Hasta: {filtros['fecha_hasta']}")
        y -= 20
    
    # Línea separadora
    y -= 10
    p.line(100, y, 500, y)
    y -= 20
    
    # Contenido de reservas
    for reserva in reservas:
        if y < 100:  # Salto de página
            p.showPage()
            y = 800
        texto = f"{reserva.tipo.upper()} | {reserva.fecha} | {reserva.cliente}"
        p.drawString(100, y, texto)
        y -= 20
    
    p.save()
    buffer.seek(0)
    return buffer
    
    #== fin funciones de exportacion


if __name__ == '__main__':
    print("🎪 SISTEMA CAMPING - ESTRUCTURA PROFESIONAL")
    print("📍 URL Local: http://localhost:5000")
    print("🌐 Para acceso externo ejecutar: ngrok http 5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
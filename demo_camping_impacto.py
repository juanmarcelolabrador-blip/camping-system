# demo_camping_impacto.py
# ==================== 🚀 APLICACIÓN PRINCIPAL FLASK ====================

from flask import Flask, render_template, request, session, redirect
import datetime
from database import obtener_reservas, crear_reserva

app = Flask(__name__)
app.secret_key = 'demo_secret'

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
        
        # Validar que fecha salida no sea anterior a entrada
        if fecha_salida < fecha_entrada:
            return "❌ Error: La fecha de salida no puede ser anterior a la de entrada", 400
        
        # 🎯 TU VALIDACIÓN INTELIGENTE
        from database import verificar_disponibilidad_casa_completa, actualizar_tabla_ocupacion
        
        disponible, mensaje = verificar_disponibilidad_casa_completa(fecha_entrada, fecha_salida)
        if not disponible:
            return f"❌ {mensaje}", 400
        
        # Crear reserva y obtener ID
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO reservas (tipo, fecha, fecha_entrada, hora_entrada, fecha_salida, hora_salida, turno, cliente, telefono, tipo_cliente, usuario) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (tipo, fecha_entrada, fecha_entrada, hora_entrada, fecha_salida, hora_salida, 'completo', cliente, telefono, tipo_cliente, session.get('usuario', 'demo')))
        reserva_id = c.lastrowid
        conn.commit()
        conn.close()
                
        # Actualizar tabla de ocupación
        actualizar_tabla_ocupacion(reserva_id, fecha_entrada, fecha_salida)
        
    else:
        # Para quincho y fogones (comportamiento actual)
        fecha = request.form['fecha']
        turno = request.form.get('turno', 'completo')
        crear_reserva(tipo, fecha, cliente, telefono, tipo_cliente, session.get('usuario', 'demo'))
    
    return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    print("🎪 SISTEMA CAMPING - ESTRUCTURA PROFESIONAL")
    print("📍 URL Local: http://localhost:5000")
    print("🌐 Para acceso externo ejecutar: ngrok http 5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)

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
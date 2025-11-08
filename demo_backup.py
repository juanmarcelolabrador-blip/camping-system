from flask import Flask, render_template_string, request, session, redirect
import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'demo_secret'

def init_demo_db():
    conn = sqlite3.connect('demo_camping.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reservas
                 (id INTEGER PRIMARY KEY, tipo TEXT, fecha TEXT, turno TEXT, 
                  cliente TEXT, usuario TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Datos de ejemplo para impresionar
    reservas_ejemplo = [
        ('quincho', '2025-10-15', 'mañana', 'Familia Pérez', 'admin'),
        ('casa_camping', '2025-10-16', 'completo', 'Municipalidad', 'admin'),
        ('fogones', '2025-10-20', 'completo', 'Escuela 123', 'admin')
    ]
    
    c.executemany('INSERT OR IGNORE INTO reservas (tipo, fecha, turno, cliente, usuario) VALUES (?,?,?,?,?)', reservas_ejemplo)
    conn.commit()
    conn.close()

@app.route('/')
def home():
    if 'usuario' not in session:
        return redirect('/login')
    
    # Leer filtros
    buscar = request.args.get('buscar', '')
    modulos_seleccionados = request.args.getlist('modulo')

    # CONEXIÓN SEGURA
    with sqlite3.connect('demo_camping.db') as conn:
        c = conn.cursor()
    
        # Construir consulta con filtros (SOLO UNA CONSULTA)
        query = "SELECT * FROM reservas WHERE 1=1"
        params = []
        
        # Filtro por módulo
        if modulos_seleccionados:
            placeholders = ','.join(['?'] * len(modulos_seleccionados))
            query += f" AND tipo IN ({placeholders})"
            params.extend(modulos_seleccionados)
        
        # Filtro por búsqueda de cliente
        if buscar:
            query += " AND cliente LIKE ?"
            params.append('%' + buscar + '%')
        
        query += " ORDER BY fecha"
        
        # EJECUTAR SOLO UNA VEZ
        c.execute(query, params)
        reservas = c.fetchall()
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🏕️ Demo Sistema Camping</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial; margin: 20px; background: #f5f5f5; }
            .header { background: linear-gradient(45deg, #2E8B57, #228B22); color: white; padding: 20px; border-radius: 10px; }
            .card { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .quincho { border-left: 4px solid #8A2BE2; }
            .casa { border-left: 4px solid #FFD700; }
            .fogones { border-left: 4px solid #228B22; }
            .btn { background: #2E8B57; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
<!--LOGO NUEVO AGREGADO ARRIBA 
    <div style="text-align: center; margin: 20px 0;">
        <img src="{{ url_for('static', filename='images/logo.jpeg') }}" 
             alt="Logo Turismo" 
             style="height: 80px;">
    </div>
    -->

       <!-- <div class="header">
            <h1>🏕️ Sistema Camping - DEMO EN VIVO</h1>
            <p>Usuario: {{ session.usuario }} | <a href="/logout" style="color: white;">Salir</a></p>
        </div>
        -->
        <!--QUI EMPIEZA LO QUE PEGO, EL HEADER NUEVO-->
        <div class="header" style="display: flex; align-items: center; justify-content: space-between; padding: 15px 20px;">
    <!-- Logo + Título a la izquierda -->
    <div style="display: flex; align-items: center;">
        <img src="{{ url_for('static', filename='images/logo.jpeg') }}" 
             style="height: 90px; margin-right: 15px; border-radius: 5px;">
        <div>
            <h1 style="margin: 0; font-size: 2.4em;">🏕️ Sistema Camping Municipal</h1>
            <p style="margin: 0; padding-left:60px ;opacity: 0.9; font-size: 1.9em;">Demo en Vivo - Rada Tilly</p>
        </div>
    </div>
    
    <!-- Usuario a la derecha -->
    <div style="text-align: right; color: white;">
        <p style="margin: 0;">👤 {{ session.usuario }}</p>
        <a href="/logout" style="color: white; text-decoration: underline;">Salir</a>
    </div>
</div>
        <!--AQUI TERMINA EL HEADER NUEVO-->

        <div class="card">
            <h3>🚀 Accesos Simultáneos Activos</h3>
              <!-- FILTRO "LOCATE FOR" -->  
   <div class="card">
    <h3>📅 Reservas Existentes</h3>
    
    <!-- FORMULARIO UNIFICADO DE FILTROS -->
    <div style="margin-bottom: 15px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
        <form action="/" method="get">
            <!-- Buscador de cliente -->
            <div style="margin-bottom: 10px;">
                <input type="text" 
                       name="buscar" 
                       placeholder="🔍 Buscar por nombre de cliente..." 
                       value="{{ request.args.get('buscar', '') }}"
                       style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            
            <!-- Filtro por módulo -->
            <div style="margin-bottom: 10px;">
                <strong>Filtrar por módulo:</strong><br>
                <label style="margin-right: 15px;">
                    <input type="checkbox" name="modulo" value="quincho" 
                           {% if 'quincho' in request.args.getlist('modulo') or not request.args.get('modulo') %}checked{% endif %}> 
                    🎪 Quincho
                </label>
                <label style="margin-right: 15px;">
                    <input type="checkbox" name="modulo" value="casa_camping" 
                           {% if 'casa_camping' in request.args.getlist('modulo') or not request.args.get('modulo') %}checked{% endif %}>
                    🏠 Casa
                </label>
                <label>
                    <input type="checkbox" name="modulo" value="fogones" 
                           {% if 'fogones' in request.args.getlist('modulo') or not request.args.get('modulo') %}checked{% endif %}>
                    🔥 Fogones
                </label>
            </div>
            
            <!-- Botones -->
            <div style="display: flex; gap: 10px; align-items: center;">
                <button type="submit" class="btn">Aplicar Filtros</button>
                {% if request.args.get('buscar') or request.args.get('modulo') %}
                    <a href="/" class="btn" style="background: #6c757d;">Limpiar Filtros</a>
                {% endif %}
            </div>
        </form>
    </div>
    
    {% if reservas %}
            <p>✅ Esta misma pantalla funciona en: PC, Celular, Tablet</p>
            <p>🌐 <strong>URL única:</strong> http://tu-demo.ngrok.io</p>
        </div>
        
        <div class="card">
            <h3>➕ Nueva Reserva Rápida</h3>
            <form action="/nueva_reserva" method="post">
                <select name="tipo">
                    <option value="quincho">🎪 Quincho</option>
                    <option value="casa_camping">🏠 Casa Camping</option>
                    <option value="fogones">🔥 Fogones</option>
                </select>
                <input type="date" name="fecha" value="{{ hoy }}">
                <input type="text" name="cliente" placeholder="Nombre cliente" required>
                <button type="submit" class="btn">Crear Reserva</button>
            </form>
        </div>
        
        <div class="card">
            <h3>📅 Reservas Existentes</h3>
                                                                          <!-- Filtro por módulo -->
<!-- Filtro por módulo -->
<div style="margin-bottom: 15px; padding: 10px; background: #e8f4fd; border-radius: 5px;">
    <strong>Filtrar por módulo:</strong><br>
    <label style="margin-right: 15px;">
        <input type="checkbox" name="modulo" value="quincho" 
               {% if 'quincho' in request.args.getlist('modulo') or not request.args.get('modulo') %}checked{% endif %}> 
        🎪 Quincho
    </label>
    <label style="margin-right: 15px;">
        <input type="checkbox" name="modulo" value="casa_camping" 
               {% if 'casa_camping' in request.args.getlist('modulo') or not request.args.get('modulo') %}checked{% endif %}>
        🏠 Casa
    </label>
    <label>
        <input type="checkbox" name="modulo" value="fogones" 
               {% if 'fogones' in request.args.getlist('modulo') or not request.args.get('modulo') %}checked{% endif %}>
        🔥 Fogones
    </label>
</div>                        
            {% if reservas %}
    {% for r in reservas %}
    <div class="card {{ r[1] }}">
        <strong>{{ r[1].upper() }}</strong> | {{ r[2] }} | {{ r[4] }}
        <br><small>Creado por: {{ r[5] }} | {{ r[6] }}</small>
    </div>
    {% endfor %}
{% else %}
    <div class="card" style="text-align: center; background: #fff3cd; border-left: 4px solid #ffc107;">
        <h3>🔍 No se encontraron reservas</h3>
        {% if request.args.get('buscar') %}
            <p>La búsqueda <strong>"{{ request.args.get('buscar') }}"</strong> no produjo resultados.</p>
        {% else %}
            <p>No hay reservas registradas en el sistema.</p>
        {% endif %}
        <a href="/" class="btn" style="background: #6c757d;">Ver todas las reservas</a>
    </div>
{% endif %}
           </div>
    </body>
    </html>
    ''', session=session, reservas=reservas, hoy=datetime.datetime.now().strftime("%Y-%m-%d"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['usuario'] = request.form['usuario']
        return redirect('/')
    return '''
    <form method="post" style="max-width: 300px; margin: 50px auto;">
        <h2>🔐 Acceso al Sistema</h2>
        <input type="text" name="usuario" placeholder="Usuario" value="admin" style="width: 100%; padding: 10px; margin: 5px 0;">
        <button type="submit" style="width: 100%; padding: 10px; background: #2E8B57; color: white; border: none;">Entrar al Sistema</button>
        <p style="text-align: center; color: #666; margin-top: 20px;">Demo Camping Rada Tilly</p>
    </form>
    '''

@app.route('/nueva_reserva', methods=['POST'])
def nueva_reserva():
    tipo = request.form['tipo']
    fecha = request.form['fecha']
    cliente = request.form['cliente']
    
    conn = sqlite3.connect('demo_camping.db')
    c = conn.cursor()
    c.execute("INSERT INTO reservas (tipo, fecha, turno, cliente, usuario) VALUES (?,?,?,?,?)", 
              (tipo, fecha, 'completo', cliente, session.get('usuario', 'demo')))
    conn.commit()
    conn.close()
    
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    init_demo_db()
    print("🎪 DEMO SISTEMA CAMPING - LISTO!")
    print("📍 URL Local: http://localhost:5000")
    print("🌐 Para acceso externo ejecutar: ngrok http 5000")
    print("📱 Luego compartir URL ngrok para demo multi-dispositivo")
    app.run(host='0.0.0.0', port=5000, debug=True)
"""  """
#!/bin/bash

# Ir a la carpeta del proyecto
cd /home/jmlsystems/camping_system

# Activar el entorno virtual
source venv/bin/activate

# Ejecutar Flask en segundo plano
python demo_camping_impacto.py &

# Esperar 2 segundos que Flask arranque
sleep 2

echo "🚀 Flask ejecutándose en: http://localhost:5000"
echo "🌐 Ngrok iniciando... La URL pública aparecerá abajo:"

# Ejecutar Ngrok
ngrok http 5000

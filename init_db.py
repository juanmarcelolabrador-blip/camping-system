#!/usr/bin/env python3
# init_db.py
# ==================== 🏗️ INICIALIZADOR DE BASE DE DATOS ====================

import sqlite3
import os

def borrar_base_antigua():
    """Elimina la base de datos anterior para empezar de cero"""
    if os.path.exists('demo_camping.db'):
        os.remove('demo_camping.db')
        print("🗑️  Base de datos anterior eliminada")

def crear_estructura_completa():
    """Crea la base de datos con la nueva estructura"""
    from database import init_database, obtener_reservas
    
    # Inicializar base de datos
    init_database()
    
    # Verificar que funcionó
    reservas = obtener_reservas()
    print(f"✅ Base de datos creada con {len(reservas)} reservas de ejemplo")
    
    # Mostrar las reservas creadas
    print("\n📋 Reservas creadas:")
    for reserva in reservas:
        costo = reserva.calcular_costo()
        print(f"   • {reserva.cliente} ({reserva.tipo_cliente}) - {reserva.tipo} - ${costo}")

if __name__ == "__main__":
    print("🏗️  INICIALIZANDO BASE DE DATOS NUEVA...")
    print("=" * 50)
    
    borrar_base_antigua()
    crear_estructura_completa()
    
    print("=" * 50)
    print("🎉 BASE DE DATOS LISTA PARA USAR!")
    print("📁 Archivo: demo_camping.db")
    print("🚀 Ejecuta: python demo_camping_impacto.py")

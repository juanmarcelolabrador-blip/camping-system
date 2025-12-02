#!/usr/bin/env python3
# browse.py - Tu BROWSE de FoxPRO pero en Python
# Para debug: python3 browse.py
# Para "asterisquear": # delante de la línea

import sqlite3
from tabulate import tabulate

def browse_reservas(tabla='reservas'):
    """BROWSE profesional - como en FoxPRO pero mejor"""
    
    conn = sqlite3.connect('demo_camping.db')
    c = conn.cursor()
    
    # Obtener estructura de la tabla
    c.execute(f"PRAGMA table_info({tabla})")
    columnas = [col[1] for col in c.fetchall()]
    
    # Obtener datos
    c.execute(f"SELECT * FROM {tabla}")
    resultados = c.fetchall()
    
    print(f"📋 BROWSE {tabla.upper()} - SISTEMA CAMPING")
    print("=" * 100)
    
    if resultados:
        # Mostrar con tabulate (formato profesional)
        print(tabulate(resultados, headers=columnas, tablefmt='grid'))
        print(f"\n📊 Total: {len(resultados)} registros")
    else:
        print("🚫 No hay registros en la tabla")
    
    conn.close()

def browse_ocupacion():
    """BROWSE específico para tabla ocupación"""
    browse_reservas('ocupacion')

if __name__ == "__main__":
    print("🎪 SISTEMA CAMPING - HERRAMIENTAS DEBUG")
    print("1. BROWSE reservas")
    print("2. BROWSE ocupación")
    print("3. Ambas tablas")
    
    opcion = input("\nSelecciona opción (1-3): ").strip()
    
    if opcion == '1':
        browse_reservas()
    elif opcion == '2':
        browse_ocupacion()
    elif opcion == '3':
        browse_reservas()
        print("\n")
        browse_ocupacion()
    else:
        browse_reservas()
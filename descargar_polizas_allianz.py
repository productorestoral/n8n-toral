#!/usr/bin/env python3
"""
Script para descargar pólizas de Allianz - Versión Simple
"""

from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime

URL_ALLIANZ = "https://net.allianz.com.ar/#/home"

print("\n" + "=" * 80)
print("DESCARGADOR DE PÓLIZAS ALLIANZ")
print("=" * 80 + "\n")

# Verificar dependencias
print("✓ Verificando dependencias...\n")
try:
    import pandas
    print("  ✓ pandas instalado")
except:
    print("  ✗ pandas NO instalado")

try:
    from playwright.sync_api import sync_playwright
    print("  ✓ playwright instalado\n")
except:
    print("  ✗ playwright NO instalado\n")
    exit()

# Iniciar
print("=" * 80)
print("PASO 1: Abriendo Allianz")
print("=" * 80 + "\n")

with sync_playwright() as p:
    print("Abriendo navegador...\n")
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.set_viewport_size({"width": 1400, "height": 900})

    print("Navegando a Allianz...\n")
    page.goto(URL_ALLIANZ)

    print("=" * 80)
    print("PASO 2: Completa manualmente")
    print("=" * 80 + "\n")

    print("En el navegador que se abrió, completa:")
    print("  1. Login (eduardo3 / eduardo10)")
    print("  2. Producción → AGENTE")
    print("  3. Organizador: TORAL EDUARDO")
    print("  4. Tipo: Hogar o Combinado Familiar")
    print("  5. PROCESAR DATOS")
    print("  6. Espera la tabla\n")

    print("Cuando veas la tabla, presiona ENTER:\n")
    input()

    print("\n" + "=" * 80)
    print("PASO 3: Extrayendo datos")
    print("=" * 80 + "\n")

    # Buscar tabla
    tables = page.query_selector_all('table')

    if not tables:
        print("ERROR: No encontré tabla\n")
        print("Presiona ENTER para cerrar:")
        input()
        browser.close()
        exit()

    print(f"Encontré tabla con datos\n")

    tabla = tables[0]
    filas = tabla.query_selector_all('tbody tr')

    print(f"Filas encontradas: {len(filas)}\n")

    if not filas:
        print("ERROR: Tabla sin datos\n")
        print("Presiona ENTER para cerrar:")
        input()
        browser.close()
        exit()

    # Extraer
    polizas = []

    for i, fila in enumerate(filas):
        celdas = fila.query_selector_all('td')

        if len(celdas) >= 6:
            poliza = {
                'Número de Póliza': celdas[0].text_content().strip(),
                'Nombre Asegurado': celdas[1].text_content().strip(),
                'Ubicación del Riesgo': celdas[2].text_content().strip(),
                'Suma Incendio Edificio': celdas[3].text_content().strip(),
                'Vigencia Desde': celdas[4].text_content().strip(),
                'Vigencia Hasta': celdas[5].text_content().strip(),
            }
            polizas.append(poliza)

        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{len(filas)}")

    print(f"\n✓ Extracción completada: {len(polizas)} pólizas\n")

    # Generar Excel
    print("=" * 80)
    print("PASO 4: Generando Excel")
    print("=" * 80 + "\n")

    df = pd.DataFrame(polizas)
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre = f"Allianz_Polizas_{fecha}.xlsx"

    df.to_excel(nombre, index=False, sheet_name='Pólizas')

    print(f"✓ Archivo: {nombre}\n")
    print("Primeras pólizas:\n")
    print(df.head().to_string() + "\n")

    # Cerrar
    print("=" * 80)
    print("✓ LISTO")
    print("=" * 80 + "\n")

    print("Presiona ENTER para cerrar el navegador:")
    input()

    browser.close()

print("\n✓ Hecho\n")

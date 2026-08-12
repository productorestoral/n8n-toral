#!/usr/bin/env python3
"""
Script para descargar pólizas de Allianz - Auto-detección
"""

from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import time

URL_ALLIANZ = "https://net.allianz.com.ar/#/home"

print("\n" + "=" * 80)
print("DESCARGADOR DE PÓLIZAS ALLIANZ")
print("=" * 80 + "\n")

with sync_playwright() as p:
    print("Abriendo navegador Chromium...\n")
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.set_viewport_size({"width": 1400, "height": 900})

    print("Navegando a Allianz...\n")
    page.goto(URL_ALLIANZ)

    print("=" * 80)
    print("ESPERANDO - Completa estos pasos en el navegador:")
    print("=" * 80 + "\n")
    print("  1. Login (eduardo3 / eduardo10)")
    print("  2. Producción → AGENTE")
    print("  3. Organizador: TORAL EDUARDO")
    print("  4. Tipo: Hogar o Combinado Familiar")
    print("  5. PROCESAR DATOS")
    print("  6. Espera la tabla\n")
    print("El script detectará automáticamente cuando aparezca la tabla...\n")

    # Esperar a que aparezca la tabla (máximo 5 minutos)
    print("Detectando tabla...")
    encontrada = False
    intentos = 0
    max_intentos = 300  # 5 minutos

    while not encontrada and intentos < max_intentos:
        try:
            tables = page.query_selector_all('table')
            if tables and len(tables) > 0:
                tabla = tables[0]
                filas = tabla.query_selector_all('tbody tr')
                if filas and len(filas) > 0:
                    encontrada = True
                    print(f"\n✓ ¡Tabla detectada! ({len(filas)} filas)\n")
                    break
        except:
            pass

        time.sleep(1)
        intentos += 1

        if intentos % 10 == 0:
            print(f"  Esperando... ({intentos}s)")

    if not encontrada:
        print("\n✗ Timeout: No se detectó tabla después de 5 minutos\n")
        print("Presiona Ctrl+C para salir")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            browser.close()
            exit()

    # Extraer datos
    print("=" * 80)
    print("EXTRAYENDO DATOS")
    print("=" * 80 + "\n")

    tabla = tables[0]
    filas = tabla.query_selector_all('tbody tr')
    total = len(filas)

    print(f"Total de filas: {total}\n")

    polizas = []
    errores = 0

    for i, fila in enumerate(filas):
        try:
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
                print(f"  {i + 1}/{total}")

        except Exception as e:
            errores += 1

    print(f"\n✓ Extracción completada")
    print(f"  Pólizas: {len(polizas)}")
    print(f"  Errores: {errores}\n")

    # Generar Excel
    print("=" * 80)
    print("GENERANDO EXCEL")
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
    print("✓ COMPLETADO")
    print("=" * 80 + "\n")
    print("Presiona Ctrl+C para cerrar el navegador\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nCerrando...")
        browser.close()
        print("✓ Hecho\n")

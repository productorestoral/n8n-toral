#!/usr/bin/env python3
"""
Script para descargar pólizas de Allianz
"""

from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import time

print("\n" + "=" * 80)
print("DESCARGADOR DE PÓLIZAS ALLIANZ")
print("=" * 80 + "\n")

try:
    print("1. Iniciando Playwright...")
    p = sync_playwright().start()
    print("   ✓ Listo\n")

    print("2. Abriendo navegador...")
    browser = p.chromium.launch(headless=False)
    print("   ✓ Listo\n")

    print("3. Creando página...")
    page = browser.new_page()
    page.set_viewport_size({"width": 1400, "height": 900})
    print("   ✓ Listo\n")

    print("4. Navegando a Allianz...")
    page.goto("https://net.allianz.com.ar/#/home")
    print("   ✓ Listo\n")

    print("=" * 80)
    print("COMPLETÁ EN EL NAVEGADOR:")
    print("=" * 80 + "\n")
    print("  • Login")
    print("  • Producción → AGENTE")
    print("  • Organizador: TORAL EDUARDO")
    print("  • Tipo: Hogar o Combinado Familiar")
    print("  • PROCESAR DATOS")
    print("  • Espera la tabla\n")

    print("El script esperará la tabla (máximo 5 minutos)...\n")
    print("Esperando 5 segundos a que la página cargue completamente...")
    time.sleep(5)

    print("Searching...", end="", flush=True)

    # Loop esperando tabla
    encontrada = False
    filas = None

    for segundo in range(300):
        try:
            # Buscar el iframe HTML embebido
            iframe_locator = page.locator('iframe[src*="pkg_aznet_container"]')
            if iframe_locator.count() > 0:
                # Acceder al contenido del iframe
                frame_content = iframe_locator.frame_locator(":scope")

                # Intentar 1: Buscar table HTML normal
                tables = frame_content.locator('table')
                if tables.count() > 0:
                    tabla = tables.first
                    filas_locator = tabla.locator('tbody tr')
                    if filas_locator.count() > 0:
                        filas = filas_locator
                        encontrada = True
                        break

                # Intentar 2: Buscar role="row"
                if not encontrada:
                    rows = frame_content.locator('[role="row"]')
                    if rows.count() > 1:
                        filas = rows
                        encontrada = True
                        break

                # Intentar 3: Buscar divs con clases de fila
                if not encontrada:
                    row_divs = frame_content.locator('div[class*="row"]')
                    if row_divs.count() > 1:
                        filas = row_divs
                        encontrada = True
                        break

        except:
            pass

        if segundo % 10 == 0 and segundo > 0:
            print(f"\n  {segundo}s", end="", flush=True)
        else:
            print(".", end="", flush=True)

        time.sleep(1)

    print("\n")

    if not encontrada:
        print("✗ Timeout: no se detectó tabla\n")
        print("Presiona Ctrl+C para salir\n")
        while True:
            time.sleep(1)

    print("✓ ¡Tabla detectada!\n")

    print("=" * 80)
    print("EXTRAYENDO:")
    print("=" * 80 + "\n")

    total = filas.count()
    print(f"Filas: {total}\n")

    polizas = []
    for i in range(total):
        try:
            fila = filas.nth(i)
            texto_fila = fila.text_content().strip()

            # Buscar celdas (td o divs que actúen como celdas)
            celdas_td = fila.locator('td')
            if celdas_td.count() > 0:
                # Es una tabla HTML normal
                if celdas_td.count() >= 6:
                    polizas.append({
                        'Número de Póliza': celdas_td.nth(0).text_content().strip(),
                        'Nombre Asegurado': celdas_td.nth(1).text_content().strip(),
                        'Ubicación del Riesgo': celdas_td.nth(2).text_content().strip(),
                        'Suma Incendio Edificio': celdas_td.nth(3).text_content().strip(),
                        'Vigencia Desde': celdas_td.nth(4).text_content().strip(),
                        'Vigencia Hasta': celdas_td.nth(5).text_content().strip(),
                    })
            else:
                # Intentar extraer de role="cell"
                celdas = fila.locator('[role="cell"], [role="gridcell"]')
                if celdas.count() >= 6:
                    polizas.append({
                        'Número de Póliza': celdas.nth(0).text_content().strip(),
                        'Nombre Asegurado': celdas.nth(1).text_content().strip(),
                        'Ubicación del Riesgo': celdas.nth(2).text_content().strip(),
                        'Suma Incendio Edificio': celdas.nth(3).text_content().strip(),
                        'Vigencia Desde': celdas.nth(4).text_content().strip(),
                        'Vigencia Hasta': celdas.nth(5).text_content().strip(),
                    })

            if (i + 1) % 10 == 0:
                print(f"  {i + 1}/{total}")

        except Exception as e:
            pass

    print(f"\n✓ Extracción: {len(polizas)} pólizas\n")

    print("=" * 80)
    print("GENERANDO EXCEL:")
    print("=" * 80 + "\n")

    df = pd.DataFrame(polizas)
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo = f"Allianz_Polizas_{fecha}.xlsx"

    df.to_excel(archivo, index=False, sheet_name='Pólizas')

    print(f"✓ Archivo: {archivo}\n")
    print("Primeras pólizas:\n")
    print(df.head().to_string() + "\n")

    print("=" * 80)
    print("✓ COMPLETADO")
    print("=" * 80 + "\n")
    print("Presiona Ctrl+C para cerrar\n")

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n\nCerrando...")
    if 'browser' in locals():
        browser.close()
    if 'p' in locals():
        p.stop()
    print("✓ Hecho\n")

except Exception as e:
    print(f"\n\n✗ ERROR: {e}\n")
    print(f"Tipo: {type(e).__name__}\n")
    import traceback
    traceback.print_exc()
    print()

    if 'browser' in locals():
        try:
            browser.close()
        except:
            pass
    if 'p' in locals():
        try:
            p.stop()
        except:
            pass

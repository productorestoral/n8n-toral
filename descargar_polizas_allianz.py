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

    # Loop esperando tabla (buscar de múltiples formas)
    encontrada = False
    tabla = None
    filas = None
    frame_usado = None

    for segundo in range(300):
        try:
            # Intentar 1: table HTML normal en página principal
            tables = page.query_selector_all('table')
            if tables:
                tabla = tables[0]
                filas = tabla.query_selector_all('tbody tr')
                if filas:
                    encontrada = True
                    break

            # Intentar 2: grid role en página principal
            if not encontrada:
                grids = page.query_selector_all('[role="grid"]')
                if grids:
                    tabla = grids[0]
                    filas = tabla.query_selector_all('[role="row"]')
                    if len(filas) > 1:
                        encontrada = True
                        break

            # Intentar 3: cualquier tbody en página principal
            if not encontrada:
                tbodies = page.query_selector_all('tbody')
                if tbodies:
                    filas = tbodies[0].query_selector_all('tr')
                    if filas:
                        tabla = tbodies[0].evaluate('el => el.closest("table")')
                        encontrada = True
                        break

            # Intentar 4: Buscar en iframes
            if not encontrada:
                frames = page.frames
                for frame_idx, frame in enumerate(frames):
                    try:
                        # Buscar table en iframe
                        tables_frame = frame.query_selector_all('table')
                        if tables_frame:
                            tabla = tables_frame[0]
                            filas = tabla.query_selector_all('tbody tr')
                            if filas:
                                encontrada = True
                                frame_usado = frame
                                break

                        # Buscar role="grid" en iframe
                        if not encontrada:
                            grids_frame = frame.query_selector_all('[role="grid"]')
                            if grids_frame:
                                tabla = grids_frame[0]
                                filas = tabla.query_selector_all('[role="row"]')
                                if len(filas) > 1:
                                    encontrada = True
                                    frame_usado = frame
                                    break

                        # Buscar role="row" en iframe
                        if not encontrada:
                            rows_frame = frame.query_selector_all('[role="row"]')
                            if len(rows_frame) > 1:
                                filas = rows_frame[1:]  # Saltar header
                                encontrada = True
                                frame_usado = frame
                                break

                    except:
                        pass

                if encontrada:
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

    total = len(filas)

    print(f"Filas: {total}\n")

    polizas = []
    for i, fila in enumerate(filas):
        try:
            # Intentar extraer como tabla HTML (td)
            celdas = fila.query_selector_all('td')

            # Si no hay td, intentar extraer como rol="cell" o rol="gridcell"
            if not celdas:
                celdas = fila.query_selector_all('[role="cell"], [role="gridcell"]')

            # Si aún no hay celdas, intentar usar divs dentro de la fila
            if not celdas:
                celdas = fila.query_selector_all('div')

            if len(celdas) >= 6:
                polizas.append({
                    'Número de Póliza': celdas[0].text_content().strip(),
                    'Nombre Asegurado': celdas[1].text_content().strip(),
                    'Ubicación del Riesgo': celdas[2].text_content().strip(),
                    'Suma Incendio Edificio': celdas[3].text_content().strip(),
                    'Vigencia Desde': celdas[4].text_content().strip(),
                    'Vigencia Hasta': celdas[5].text_content().strip(),
                })

            if (i + 1) % 10 == 0:
                print(f"  {i + 1}/{total}")

        except Exception as e:
            print(f"  Error en fila {i + 1}: {e}")

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

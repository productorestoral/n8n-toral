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
    frame_datos = None

    for segundo in range(300):
        try:
            # Buscar en todos los frames
            frames = page.frames

            # Buscar en Frame 3 (select) y Frame 4 (DATOS)
            for frame_idx in [3, 4]:
                if frame_idx < len(frames):
                    frame = frames[frame_idx]
                    try:
                        # Buscar tabla HTML normal
                        tables = frame.query_selector_all('table')
                        if tables:
                            for tabla in tables:
                                # Intentar con tbody
                                filas_elem = tabla.query_selector_all('tbody tr')
                                if len(filas_elem) > 0:
                                    # Validar que sea la tabla correcta (debe tener datos, no JS)
                                    primer_texto = filas_elem[0].text_content().strip()
                                    if len(primer_texto) > 10 and 'function' not in primer_texto.lower():
                                        filas = filas_elem
                                        frame_datos = frame
                                        encontrada = True
                                        break

                                # Intentar sin tbody (tr directamente)
                                if not encontrada:
                                    filas_elem = tabla.query_selector_all('tr')
                                    if len(filas_elem) > 1:
                                        primer_texto = filas_elem[1].text_content().strip() if len(filas_elem) > 1 else ""
                                        if len(primer_texto) > 10 and 'function' not in primer_texto.lower():
                                            filas = filas_elem[1:]  # Saltar header
                                            frame_datos = frame
                                            encontrada = True
                                            break

                        if encontrada:
                            break

                        # Intentar role="row"
                        if not encontrada:
                            rows = frame.query_selector_all('[role="row"]')
                            if len(rows) > 1:
                                filas = rows[1:]
                                frame_datos = frame
                                encontrada = True
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
            # Buscar celdas (td)
            celdas = fila.query_selector_all('td')

            # Si no hay td, intentar th (en caso de header mal etiquetado)
            if not celdas:
                celdas = fila.query_selector_all('th')

            # Si aún no hay celdas, intentar divs
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
            pass

    print(f"\n✓ Extracción: {len(polizas)} pólizas\n")

    print("=" * 80)
    print("GENERANDO EXCEL:")
    print("=" * 80 + "\n")

    if len(polizas) > 0:
        df = pd.DataFrame(polizas)
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo = f"Allianz_Polizas_{fecha}.xlsx"

        df.to_excel(archivo, index=False, sheet_name='Pólizas')

        print(f"✓ Archivo: {archivo}\n")
        print("Primeras pólizas:\n")
        print(df.head().to_string() + "\n")
    else:
        print("✗ No se extrajeron pólizas\n")

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

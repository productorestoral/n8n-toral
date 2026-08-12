#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time

print("\n" + "=" * 80)
print("ANALIZADOR DE ESTRUCTURA DE TABLAS EN FRAMES 3 Y 4")
print("=" * 80 + "\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.set_viewport_size({"width": 1400, "height": 900})

    print("Abriendo Allianz...\n")
    page.goto("https://net.allianz.com.ar/#/home")

    print("=" * 80)
    print("INSTRUCCIONES:")
    print("=" * 80)
    print("\n1. Login")
    print("2. Producción → AGENTE")
    print("3. Configurar filtros")
    print("4. PROCESAR DATOS")
    print("5. Presiona ENTER cuando veas la tabla\n")

    input()

    print("\nAnalizando tablas en frames...\n")
    time.sleep(3)

    frames = page.frames

    # Analizar frames 3 y 4
    for frame_idx in [3, 4]:
        if frame_idx >= len(frames):
            print(f"Frame {frame_idx}: No existe\n")
            continue

        frame = frames[frame_idx]
        try:
            nombre = frame.name
            url = frame.url
        except:
            nombre = "?"
            url = "?"

        print("=" * 80)
        print(f"FRAME {frame_idx}: {nombre} ({url})")
        print("=" * 80 + "\n")

        try:
            # Contar tablas
            tables = frame.query_selector_all('table')
            print(f"Tablas encontradas: {len(tables)}\n")

            if tables:
                for t_idx, tabla in enumerate(tables):
                    print(f"Tabla {t_idx}:")
                    print(f"  Atributos: id='{tabla.get_attribute('id')}' class='{tabla.get_attribute('class')}'")

                    # Contar filas por diferentes métodos
                    tbody_trs = tabla.query_selector_all('tbody tr')
                    tr_directos = tabla.query_selector_all('tr')
                    trs_sin_thead = tabla.query_selector_all('tbody tr, tr:not(thead tr)')

                    print(f"  Filas (tbody tr): {len(tbody_trs)}")
                    print(f"  Filas (tr directo): {len(tr_directos)}")
                    print(f"  Filas (tbody tr o tr sin thead): {len(trs_sin_thead)}")

                    # Mostrar primeras celdas de la primera fila
                    if tbody_trs:
                        primera_fila = tbody_trs[0]
                        celdas = primera_fila.query_selector_all('td')
                        print(f"\n  Primera fila (tbody tr) tiene {len(celdas)} celdas:")
                        for c_idx, celda in enumerate(celdas[:8]):
                            texto = celda.text_content().strip()[:60]
                            print(f"    [{c_idx}]: {texto}")
                    elif tr_directos:
                        primera_fila = tr_directos[0]
                        celdas = primera_fila.query_selector_all('td')
                        if not celdas:
                            celdas = primera_fila.query_selector_all('th')
                        print(f"\n  Primera fila (tr directo) tiene {len(celdas)} celdas:")
                        for c_idx, celda in enumerate(celdas[:8]):
                            texto = celda.text_content().strip()[:60]
                            print(f"    [{c_idx}]: {texto}")

                    print()

        except Exception as e:
            print(f"Error analizando frame: {e}\n")

    print("=" * 80)
    print("Presiona ENTER para cerrar")
    print("=" * 80 + "\n")

    input()
    browser.close()

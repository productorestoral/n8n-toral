#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time

print("\n" + "=" * 80)
print("ANALIZADOR DE ESTRUCTURA DE TABLA ALLIANZ")
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

    print("\nAnalizando estructura...\n")
    time.sleep(2)

    # Buscar en todos los frames
    frames = page.frames
    print(f"Total de frames: {len(frames)}\n")

    encontrado = False

    for frame_idx, frame in enumerate(frames):
        try:
            # Buscar cualquier texto que contenga "260" o "250" (números de póliza típicos)
            all_text = frame.content()

            # Buscar divs que podrían contener datos
            divs_con_data = frame.query_selector_all('[data-testid]')
            if divs_con_data:
                print(f"Frame {frame_idx}: {len(divs_con_data)} elementos con data-testid")
                for i, div in enumerate(divs_con_data[:3]):
                    print(f"  {i}: {div.text_content().strip()[:80]}")

            # Buscar elementos con role
            roles = frame.query_selector_all('[role]')
            role_types = {}
            for role_elem in roles:
                role_type = role_elem.get_attribute('role')
                role_types[role_type] = role_types.get(role_type, 0) + 1

            if role_types:
                print(f"Frame {frame_idx}: Roles encontrados: {role_types}")

            # Buscar tablas
            tables = frame.query_selector_all('table')
            if tables:
                print(f"Frame {frame_idx}: {len(tables)} tablas HTML")
                for t_idx, table in enumerate(tables):
                    filas = table.query_selector_all('tr')
                    celdas = table.query_selector_all('td')
                    print(f"  Tabla {t_idx}: {len(filas)} filas, {len(celdas)} celdas TD")
                    if filas and len(filas) > 0:
                        primera_fila = filas[0].text_content().strip()[:100]
                        print(f"    Primera fila: {primera_fila}")

            # Buscar divs en estructura grid (Material-UI, Ant Design, etc)
            grid_rows = frame.query_selector_all('[role="row"]')
            if grid_rows:
                print(f"Frame {frame_idx}: {len(grid_rows)} elementos role='row'")
                for i, row in enumerate(grid_rows[:2]):
                    cells = row.query_selector_all('[role="cell"], [role="gridcell"]')
                    text = row.text_content().strip()[:100]
                    print(f"  Fila {i}: {len(cells)} celdas - {text}")
                encontrado = True

            # Buscar divs con clases típicas de tablas
            tbody_like = frame.query_selector_all('div[class*="row"], div[class*="table-row"], div[class*="tbody"]')
            if tbody_like:
                print(f"Frame {frame_idx}: {len(tbody_like)} divs con clases de fila")
                for i, row_div in enumerate(tbody_like[:3]):
                    clase = row_div.get_attribute('class')
                    texto = row_div.text_content().strip()[:150]
                    print(f"  Fila {i}: clase='{clase}'")
                    print(f"           texto='{texto}'")

                    # Buscar divs dentro que actúen como celdas
                    celdas = row_div.query_selector_all('div')
                    print(f"           {len(celdas)} divs internos")

            # Buscar todos los divs y sus clases
            todos_divs = frame.query_selector_all('div')
            clases_unicas = set()
            for div in todos_divs:
                clase = div.get_attribute('class')
                if clase and ('row' in clase.lower() or 'cell' in clase.lower() or 'table' in clase.lower()):
                    clases_unicas.add(clase)

            if clases_unicas:
                print(f"Frame {frame_idx}: Clases CSS con 'row', 'cell' o 'table':")
                for clase in sorted(list(clases_unicas))[:5]:
                    print(f"  - {clase}")

            print()

        except Exception as e:
            print(f"Frame {frame_idx}: Error - {e}\n")

    print("\n" + "=" * 80)
    if encontrado:
        print("✓ Estructura de tabla encontrada")
    else:
        print("✗ No se detectó estructura de tabla clara")
    print("=" * 80)
    print("\nPresiona ENTER para cerrar")
    print("=" * 80 + "\n")

    input()
    browser.close()

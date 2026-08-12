#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time

print("\n" + "=" * 80)
print("VERIFICADOR DE ACCESO AL IFRAME")
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

    print("\nVerificando acceso al iframe...\n")
    time.sleep(2)

    # Método 1: Usando page.locator
    print("Método 1: page.locator")
    try:
        iframe_locator = page.locator('iframe[src*="pkg_aznet_container"]')
        count = iframe_locator.count()
        print(f"  Iframes encontrados: {count}")

        if count > 0:
            # Intentar acceder con frame_locator
            frame_locator = page.frame_locator('iframe[src*="pkg_aznet_container"]')
            print(f"  Frame locator creado: {frame_locator}")

            # Intentar buscar tabla en el frame
            tables = frame_locator.locator('table')
            print(f"  Tablas en iframe: {tables.count()}")

            if tables.count() > 0:
                print("  ✓ Tabla HTML encontrada en iframe")
                first_table = tables.first
                rows = first_table.locator('tbody tr')
                print(f"  Filas en tabla: {rows.count()}")
            else:
                print("  ✗ No hay tablas HTML")

            # Buscar role="row"
            rows = frame_locator.locator('[role="row"]')
            print(f"  Elementos con role='row': {rows.count()}")

            # Buscar divs
            divs = frame_locator.locator('div')
            print(f"  Total divs: {divs.count()}")

            # Obtener contenido de texto
            texto = frame_locator.locator('body').text_content()
            print(f"\n  Contenido de texto en iframe (primeros 200 chars):")
            print(f"  {texto[:200]}\n")

    except Exception as e:
        print(f"  ✗ Error: {e}\n")

    # Método 2: Usando page.frames
    print("Método 2: page.frames (Playwright frames)")
    try:
        frames = page.frames
        print(f"  Frames totales en página: {len(frames)}")

        for i, frame in enumerate(frames):
            try:
                nombre = frame.name
                url = frame.url
                print(f"  Frame {i}: nombre='{nombre}' url='{url}'")
            except:
                pass

    except Exception as e:
        print(f"  ✗ Error: {e}\n")

    # Método 3: Verificar estructura del iframe
    print("\nMétodo 3: Estructura del iframe")
    try:
        frame_locator = page.frame_locator('iframe[src*="pkg_aznet_container"]')

        # Intentar acceder a diferentes elementos
        elementos = {
            'table': frame_locator.locator('table').count(),
            '[role="grid"]': frame_locator.locator('[role="grid"]').count(),
            '[role="row"]': frame_locator.locator('[role="row"]').count(),
            '[role="table"]': frame_locator.locator('[role="table"]').count(),
            'tbody': frame_locator.locator('tbody').count(),
            'tr': frame_locator.locator('tr').count(),
            'td': frame_locator.locator('td').count(),
            'div': frame_locator.locator('div').count(),
        }

        print("\n  Elementos encontrados en iframe:")
        for selector, count in elementos.items():
            print(f"    {selector}: {count}")

    except Exception as e:
        print(f"  ✗ Error: {e}\n")

    print("\n" + "=" * 80)
    print("Análisis completado")
    print("=" * 80)
    print("\nPresiona ENTER para cerrar")
    print("=" * 80 + "\n")

    input()
    browser.close()

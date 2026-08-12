#!/usr/bin/env python3
"""
Inspector: Detecta la estructura de la tabla en Allianz
"""

from playwright.sync_api import sync_playwright
import time

print("\n" + "=" * 80)
print("INSPECTOR DE ALLIANZ")
print("=" * 80 + "\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.set_viewport_size({"width": 1400, "height": 900})

    print("Abriendo Allianz...\n")
    page.goto("https://net.allianz.com.ar/#/home")

    print("=" * 80)
    print("COMPLETÁ TODO EN EL NAVEGADOR:")
    print("=" * 80 + "\n")
    print("  • Login")
    print("  • Producción → AGENTE")
    print("  • Filtros")
    print("  • PROCESAR DATOS\n")

    print("Presiona Ctrl+C cuando veas la tabla\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("ANALIZANDO TABLA...")
        print("=" * 80 + "\n")

        # Buscar todo lo que podría ser tabla
        print("Buscando elementos...\n")

        # 1. Tablas HTML
        tables = page.query_selector_all('table')
        print(f"<table> encontradas: {len(tables)}")
        if tables:
            for i, t in enumerate(tables):
                rows = t.query_selector_all('tr')
                print(f"  Tabla {i}: {len(rows)} filas")

        # 2. Grids
        grids = page.query_selector_all('[role="grid"]')
        print(f"\n[role='grid']: {len(grids)}")
        if grids:
            for i, g in enumerate(grids):
                rows = g.query_selector_all('[role="row"]')
                print(f"  Grid {i}: {len(rows)} filas")

        # 3. Tabindex tables
        divs_role_table = page.query_selector_all('div[role="table"]')
        print(f"\ndiv[role='table']: {len(divs_role_table)}")
        if divs_role_table:
            for i, d in enumerate(divs_role_table):
                rows = d.query_selector_all('[role="row"]')
                print(f"  Tabla {i}: {len(rows)} filas")

        # 4. Datos
        print("\n" + "=" * 80)
        print("BUSCANDO DATOS...")
        print("=" * 80 + "\n")

        # Intentar obtener los primeros datos
        todas_las_celdas = page.query_selector_all('td, [role="cell"]')
        print(f"Celdas encontradas: {len(todas_las_celdas)}\n")

        if todas_las_celdas:
            print("Primeras 10 celdas:\n")
            for i, celda in enumerate(todas_las_celdas[:10]):
                texto = celda.text_content().strip()[:50]
                print(f"  {i}: {texto}")

        # 5. Ver si hay datos en divs
        print("\n" + "=" * 80)
        print("ESTRUCTURA HTML (primeros 2000 caracteres):")
        print("=" * 80 + "\n")
        html = page.content()
        # Buscar sección con datos
        if 'tbody' in html:
            idx = html.find('tbody')
            print(html[max(0, idx-100):idx+500])
        elif 'grid' in html.lower():
            idx = html.lower().find('grid')
            print(html[max(0, idx-100):idx+500])
        else:
            print(html[:1000])

        print("\n\n" + "=" * 80)
        print("LISTO")
        print("=" * 80 + "\n")
        print("Copia esta información y pégala.\n")

        browser.close()

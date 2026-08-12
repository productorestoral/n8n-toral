#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time

print("\n" + "=" * 80)
print("INSPECTOR")
print("=" * 80 + "\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.set_viewport_size({"width": 1400, "height": 900})

    print("Abriendo Allianz...\n")
    page.goto("https://net.allianz.com.ar/#/home")

    print("=" * 80)
    print("COMPLETÁ TODO EN NAVEGADOR:")
    print("=" * 80)
    print("\n• Login")
    print("• Producción → AGENTE")
    print("• Filtros")
    print("• PROCESAR DATOS\n")
    print("Presiona ENTER cuando veas la tabla\n")

    input()

    print("\nAnalizando...\n")

    # Buscar tabla
    tables = page.query_selector_all('table')
    print(f"Tables encontradas: {len(tables)}")

    grids = page.query_selector_all('[role="grid"]')
    print(f"Grids encontradas: {len(grids)}")

    tbodies = page.query_selector_all('tbody')
    print(f"Tbodies encontradas: {len(tbodies)}")

    cells = page.query_selector_all('td')
    print(f"Celdas TD encontradas: {len(cells)}\n")

    # Si hay tabla
    if tables:
        print("Filas en primera tabla:")
        rows = tables[0].query_selector_all('tr')
        print(f"  Total: {len(rows)}")
        print(f"  Filas con tbody: {len(tables[0].query_selector_all('tbody tr'))}\n")

    if cells:
        print("Primeras 5 celdas:")
        for i, cell in enumerate(cells[:5]):
            texto = cell.text_content().strip()[:40]
            print(f"  {i}: {texto}")

    print("\n" + "=" * 80)
    print("Listo. Presiona ENTER para cerrar")
    print("=" * 80 + "\n")

    input()
    browser.close()

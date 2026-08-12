#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time
import re

print("\n" + "=" * 80)
print("BÚSQUEDA EXACTA DE ESTRUCTURA DE PÓLIZAS")
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

    print("\nBuscando estructura exacta...\n")
    time.sleep(2)

    frame = page.frames[0]

    # Buscar todos los divs
    todos_divs = frame.query_selector_all('div')
    print(f"Total de divs: {len(todos_divs)}\n")

    # Buscar divs que contengan números de póliza
    poliza_pattern = re.compile(r'\b\d{8}\b')  # Números de 8 dígitos (típicos de pólizas)

    divs_con_polizas = []

    for div in todos_divs:
        try:
            texto = div.text_content().strip()
            # Buscar números de póliza
            if poliza_pattern.search(texto):
                # Contar cuántas líneas/elementos contiene
                filas = div.query_selector_all('div[class*="row"], div[class*="item"], *')
                clase = div.get_attribute('class')

                divs_con_polizas.append({
                    'class': clase,
                    'texto_preview': texto[:150],
                    'contiene_divs': len(filas)
                })
        except:
            pass

    if divs_con_polizas:
        print(f"Encontrados {len(divs_con_polizas)} divs que contienen números de póliza:\n")

        # Mostrar los 5 más relevantes (probablemente los más grandes contengan la tabla)
        divs_por_tamaño = sorted(divs_con_polizas, key=lambda x: x['contiene_divs'], reverse=True)

        for i, div_info in enumerate(divs_por_tamaño[:5]):
            print(f"{i}: Clase: {div_info['class']}")
            print(f"   Contiene {div_info['contiene_divs']} elementos internos")
            print(f"   Texto: {div_info['texto_preview']}\n")
    else:
        print("No se encontraron divs con números de póliza")

    # Alternativa: buscar por filas
    print("\n" + "=" * 80)
    print("Buscando filas/registros...")
    print("=" * 80 + "\n")

    # Buscar elements con roles de tabla
    filas = frame.query_selector_all('[role="row"]')
    print(f"Filas con role='row': {len(filas)}")

    # Buscar elementos que parecen contenedores de filas
    contenedores = frame.query_selector_all('div[class*="ng-repeat"], div[class*="*ngFor"], tbody, table')
    print(f"Contenedores de tabla (tbody, table, *ngFor): {len(contenedores)}")

    # Buscar por atributos data
    data_rows = frame.query_selector_all('[data-row-index], [data-index], [data-id]')
    print(f"Elementos con data-row-index/data-index/data-id: {len(data_rows)}")

    if data_rows:
        print("\nPrimera fila encontrada:")
        texto = data_rows[0].text_content().strip()
        clase = data_rows[0].get_attribute('class')
        print(f"  Clase: {clase}")
        print(f"  Texto: {texto[:100]}")

    print("\n" + "=" * 80)
    print("Presiona ENTER para cerrar")
    print("=" * 80 + "\n")

    input()
    browser.close()

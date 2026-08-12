#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time

print("\n" + "=" * 80)
print("BUSCADOR DE TABLA DE PÓLIZAS REAL")
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

    print("\nBuscando tabla de pólizas...\n")
    time.sleep(2)

    # Buscar en todos los frames
    frames = page.frames
    print(f"Total de frames: {len(frames)}\n")

    for frame_idx, frame in enumerate(frames):
        try:
            # Obtener todo el HTML del frame
            html = frame.content()

            # Buscar palabras clave de pólizas
            palabras_clave = ['Productor', 'Organizador', 'Póliza', 'Endoso', 'Vigencia', 'Suma']
            encontradas = []
            for palabra in palabras_clave:
                if palabra in html:
                    encontradas.append(palabra)

            if encontradas:
                print(f"Frame {frame_idx}: Encontradas palabras clave: {', '.join(encontradas)}")

            # Buscar números que parecen pólizas (6+ dígitos)
            import re
            numeros = re.findall(r'\b\d{6,}\b', html)
            if numeros:
                print(f"Frame {frame_idx}: {len(set(numeros))} números encontrados (6+ dígitos)")
                print(f"  Ejemplos: {', '.join(sorted(set(numeros))[:5])}")

            # Buscar elementos que contengan texto de pólizas
            all_elements = frame.query_selector_all('*')
            elementos_polizas = []

            for elem in all_elements[:500]:  # Limitar búsqueda
                try:
                    texto = elem.text_content().strip()
                    # Si contiene palabras de pólizas Y números
                    if any(palabra in texto for palabra in ['Productor', 'Organizador', 'Póliza']):
                        if re.search(r'\d{4,}', texto):
                            tag = elem.evaluate('el => el.tagName')
                            clase = elem.get_attribute('class')
                            elementos_polizas.append({
                                'tag': tag,
                                'class': clase,
                                'texto': texto[:100]
                            })
                except:
                    pass

            if elementos_polizas:
                print(f"Frame {frame_idx}: {len(elementos_polizas)} elementos con datos de pólizas")
                for i, elem in enumerate(elementos_polizas[:3]):
                    print(f"  {i}: <{elem['tag']}> class='{elem['class']}'")
                    print(f"      {elem['texto']}")

            print()

        except Exception as e:
            print(f"Frame {frame_idx}: Error - {e}\n")

    print("\n" + "=" * 80)
    print("Análisis completado")
    print("=" * 80)
    print("\nPresiona ENTER para cerrar")
    print("=" * 80 + "\n")

    input()
    browser.close()

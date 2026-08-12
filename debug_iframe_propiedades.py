#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time

print("\n" + "=" * 80)
print("VERIFICADOR DE PROPIEDADES DEL IFRAME")
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

    print("\nAnalizando propiedades del iframe...\n")
    time.sleep(3)

    # Buscar el iframe
    iframe_elem = page.locator('iframe[src*="pkg_aznet_container"]')

    if iframe_elem.count() == 0:
        print("✗ No se encontró el iframe")
    else:
        print("✓ Iframe encontrado\n")

        # Obtener atributos
        src = iframe_elem.first.get_attribute('src')
        sandbox = iframe_elem.first.get_attribute('sandbox')
        id_attr = iframe_elem.first.get_attribute('id')
        name = iframe_elem.first.get_attribute('name')
        clase = iframe_elem.first.get_attribute('class')

        print("Atributos del iframe:")
        print(f"  src: {src}")
        print(f"  sandbox: {sandbox}")
        print(f"  id: {id_attr}")
        print(f"  name: {name}")
        print(f"  class: {clase}\n")

        # Verificar si el iframe tiene sandbox
        if sandbox:
            print("⚠️  El iframe tiene restricciones sandbox")
            print(f"  Permisos: {sandbox}\n")

        # Intentar acceder con page.frames
        print("Métodos de acceso a frames:\n")

        print("1. Usando page.frames (Playwright API):")
        frames = page.frames
        print(f"   Total frames: {len(frames)}")

        for i, frame in enumerate(frames):
            try:
                frame_name = frame.name
                frame_url = frame.url
                print(f"   Frame {i}: name='{frame_name}' url='{frame_url}'")

                # Intentar buscar tabla en cada frame
                try:
                    tables = frame.query_selector_all('table')
                    print(f"     - Tablas: {len(tables)}")

                    divs = frame.query_selector_all('div')
                    print(f"     - Divs: {len(divs)}")

                    # Si hay contenido, mostrar un poco
                    if divs or tables:
                        body_text = frame.content()[:200]
                        print(f"     - Contenido: {body_text}")
                except Exception as e:
                    print(f"     - Error accediendo: {e}")

            except Exception as e:
                print(f"   Frame {i}: Error - {e}")

        print("\n2. Usando frame_locator:")
        try:
            frame_loc = page.frame_locator('iframe[src*="pkg_aznet_container"]')

            # Intentar obtener el body
            body = frame_loc.locator('body')
            body_count = body.count()
            print(f"   Body encontrado: {body_count}")

            if body_count > 0:
                texto = body.text_content()
                print(f"   Texto en body (primeros 200 chars): {texto[:200]}")
        except Exception as e:
            print(f"   Error: {e}")

        print("\n3. Intentando esperar contenido:")
        try:
            # Esperar a que haya una tabla
            page.locator('iframe[src*="pkg_aznet_container"] table').wait_for(timeout=5000)
            print("   ✓ Tabla encontrada en iframe")
        except:
            print("   ✗ No hay tabla en el iframe después de 5 segundos")

        print("\n4. Verificando si el iframe tiene contenido cargado:")
        try:
            # Usar JavaScript para verificar
            result = page.evaluate('''() => {
                const iframe = document.querySelector('iframe[src*="pkg_aznet_container"]');
                if (!iframe) return "No iframe found";

                try {
                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                    if (!doc) return "Cannot access iframe document (CORS?)";

                    const body = doc.body;
                    return {
                        body_exists: !!body,
                        body_children: body ? body.children.length : 0,
                        body_text_length: body ? body.innerText.length : 0,
                        first_100_chars: body ? body.innerText.substring(0, 100) : ""
                    };
                } catch (e) {
                    return "Error: " + e.message;
                }
            }''')

            print(f"   Resultado: {result}")
        except Exception as e:
            print(f"   Error ejecutando JavaScript: {e}")

    print("\n" + "=" * 80)
    print("Presiona ENTER para cerrar")
    print("=" * 80 + "\n")

    input()
    browser.close()

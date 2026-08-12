#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time
import json

print("\n" + "=" * 80)
print("BÚSQUEDA DIRECTA EN JAVASCRIPT")
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

    print("\nBuscando en DOM renderizado...\n")
    time.sleep(2)

    frame = page.frames[0]

    # Buscar en el DOM renderizado con JavaScript
    resultado = frame.evaluate('''() => {
        const resultado = {
            total_elementos: document.querySelectorAll('*').length,
            texto_pagina_completa: document.body.innerText.substring(0, 500),
            elementos_visibles: [],
            shadow_doms: 0
        };

        // Contar shadow DOMs
        document.querySelectorAll('*').forEach(el => {
            if (el.shadowRoot) {
                resultado.shadow_doms++;
            }
        });

        // Buscar todos los elementos que contengan texto con números
        document.querySelectorAll('*').forEach(el => {
            const texto = el.innerText || el.textContent || '';
            // Si contiene un número de 8 dígitos
            if (/\\d{8}/.test(texto)) {
                resultado.elementos_visibles.push({
                    tag: el.tagName,
                    class: el.className,
                    id: el.id,
                    texto: texto.substring(0, 100)
                });
            }
        });

        return resultado;
    }''')

    print(f"Total elementos en DOM: {resultado['total_elementos']}")
    print(f"Shadow DOMs encontrados: {resultado['shadow_doms']}\n")

    if resultado['elementos_visibles']:
        print(f"Elementos que contienen números de póliza (8 dígitos):")
        print(f"Total: {len(resultado['elementos_visibles'])}\n")

        for i, elem in enumerate(resultado['elementos_visibles'][:10]):
            print(f"{i}: <{elem['tag']}> class='{elem['class']}' id='{elem['id']}'")
            print(f"   Texto: {elem['texto']}\n")
    else:
        print("No se encontraron elementos con números de 8 dígitos")
        print("\nBuscando en el HTML plano:")
        print(resultado['texto_pagina_completa'])

    # Buscar en shadow DOM si existe
    print("\n" + "=" * 80)
    print("Verificando Shadow DOM...")
    print("=" * 80 + "\n")

    shadow_dom_info = frame.evaluate('''() => {
        const elementos_con_shadow = [];
        document.querySelectorAll('*').forEach(el => {
            if (el.shadowRoot) {
                const texto = el.shadowRoot.innerText || el.shadowRoot.textContent || '';
                if (texto.length > 0) {
                    elementos_con_shadow.push({
                        tag: el.tagName,
                        class: el.className,
                        shadow_texto: texto.substring(0, 100)
                    });
                }
            }
        });
        return elementos_con_shadow;
    }''')

    if shadow_dom_info:
        print(f"Encontrados {len(shadow_dom_info)} elementos con Shadow DOM")
        for i, elem in enumerate(shadow_dom_info[:3]):
            print(f"{i}: <{elem['tag']}> class='{elem['class']}'")
            print(f"   Shadow texto: {elem['shadow_texto']}\n")
    else:
        print("No se encontraron Shadow DOMs")

    # Buscar iframes internos
    print("\n" + "=" * 80)
    print("Buscando iframes internos...")
    print("=" * 80 + "\n")

    iframes = frame.query_selector_all('iframe')
    print(f"Iframes encontrados en el frame: {len(iframes)}\n")

    for i, iframe in enumerate(iframes[:3]):
        src = iframe.get_attribute('src')
        clase = iframe.get_attribute('class')
        print(f"Iframe {i}: src='{src}' class='{clase}'")

    print("\n" + "=" * 80)
    print("Presiona ENTER para cerrar")
    print("=" * 80 + "\n")

    input()
    browser.close()

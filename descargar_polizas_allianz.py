#!/usr/bin/env python3
"""
Script para descargar pólizas de Allianz y guardarlas en Excel
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import pandas as pd
from datetime import datetime
import time
import sys
import traceback

URL_ALLIANZ = "https://net.allianz.com.ar/#/home"

def main():
    print("🚀 Iniciando descarga de pólizas Allianz...\n")

    playwright = None
    browser = None

    try:
        # Iniciar Playwright
        print("📍 Iniciando Playwright...")
        playwright = sync_playwright().start()
        print("✅ Playwright iniciado\n")

        # Abrir navegador
        print("📍 Abriendo navegador Chromium...")
        browser = playwright.chromium.launch(headless=False)
        print("✅ Navegador abierto\n")

        # Crear página
        print("📍 Creando página...")
        page = browser.new_page()
        page.set_viewport_size({"width": 1400, "height": 900})
        print("✅ Página creada\n")

        # Abrir Allianz
        print("=" * 80)
        print("PASO 1: ABRIENDO ALLIANZ")
        print("=" * 80)
        print("\n🌐 Abriendo https://net.allianz.com.ar...\n")

        try:
            page.goto(URL_ALLIANZ, wait_until="networkidle", timeout=30000)
            print("✅ Página cargada\n")
        except PlaywrightTimeoutError:
            print("⚠️ Timeout, pero continuamos...\n")
        except Exception as e:
            print(f"❌ Error abriendo página: {e}\n")
            raise

        time.sleep(3)

        print("=" * 80)
        print("PASO 2: COMPLETA TODO MANUALMENTE EN EL NAVEGADOR")
        print("=" * 80)
        print("\n👉 Cosas que hacer en el navegador:")
        print("   ✓ Acepta cookies (si aparecen)")
        print("   ✓ Cierra banners (si aparecen)")
        print("   ✓ Usuario: eduardo3")
        print("   ✓ Contraseña: eduardo10")
        print("   ✓ Click en INICIAR SESIÓN")
        print("   ✓ Ve a Producción → AGENTE")
        print("   ✓ Organizador: TORAL EDUARDO")
        print("   ✓ Tipo: Hogar o Combinado Familiar")
        print("   ✓ Click en PROCESAR DATOS")
        print("   ✓ Espera a ver la tabla de pólizas\n")

        print("=" * 80)
        print("⏳ Cuando veas la tabla, presiona ENTER aquí...")
        print("=" * 80 + "\n")

        input()

        print("\n✅ Continuando con extracción...\n")
        time.sleep(2)

        # Buscar tabla
        print("🔍 Buscando tabla de pólizas...")
        try:
            tables = page.query_selector_all('table')
            print(f"   Encontradas: {len(tables)} tablas\n")
        except Exception as e:
            print(f"❌ Error buscando tablas: {e}\n")
            return None

        if len(tables) == 0:
            print("❌ No se encontró tabla")
            print("\n💡 Verifica que:")
            print("   - Completaste el login")
            print("   - Estás en Producción > AGENTE")
            print("   - Completaste los filtros")
            print("   - Hiciste click en PROCESAR DATOS")
            print("   - Ves la tabla en el navegador\n")
            return None

        tabla = tables[0]

        print("🔍 Buscando filas en la tabla...")
        try:
            filas = tabla.query_selector_all('tbody tr')
            total = len(filas)
            print(f"   Encontradas: {total} filas\n")
        except Exception as e:
            print(f"❌ Error buscando filas: {e}\n")
            return None

        if total == 0:
            print("❌ La tabla no tiene datos\n")
            return None

        print(f"📋 Extrayendo {total} pólizas...\n")

        polizas = []
        errores = 0

        for i, fila in enumerate(filas):
            try:
                celdas = fila.query_selector_all('td')

                if len(celdas) >= 6:
                    poliza = {
                        'Número de Póliza': celdas[0].text_content().strip(),
                        'Nombre Asegurado': celdas[1].text_content().strip(),
                        'Ubicación del Riesgo': celdas[2].text_content().strip(),
                        'Suma Incendio Edificio': celdas[3].text_content().strip(),
                        'Vigencia Desde': celdas[4].text_content().strip(),
                        'Vigencia Hasta': celdas[5].text_content().strip(),
                    }
                    polizas.append(poliza)

                    if (i + 1) % 10 == 0:
                        print(f"   ✅ {i + 1}/{total}")

            except Exception as e:
                errores += 1
                if errores <= 3:
                    print(f"   ⚠️ Fila {i}: {e}")

        print(f"\n✅ Extracción completada")
        print(f"   Pólizas: {len(polizas)}")
        print(f"   Errores: {errores}\n")

        # Generar Excel
        if polizas:
            print("=" * 80)
            print("GENERANDO EXCEL")
            print("=" * 80 + "\n")

            try:
                df = pd.DataFrame(polizas)
                fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"Allianz_Polizas_{fecha}.xlsx"

                df.to_excel(nombre_archivo, index=False, sheet_name='Pólizas')

                print(f"✅ Excel guardado: {nombre_archivo}")
                print(f"📊 Total: {len(polizas)} pólizas\n")
                print("Primeras 5 pólizas:")
                print(df.head().to_string() + "\n")

                return nombre_archivo

            except Exception as e:
                print(f"❌ Error generando Excel: {e}\n")
                return None
        else:
            print("❌ No se extrajeron pólizas\n")
            return None

    except KeyboardInterrupt:
        print("\n⚠️ Cancelado por el usuario\n")
        return None

    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        print("Tipo:", type(e).__name__)
        print("\nDetalles:")
        traceback.print_exc()
        print()
        return None

    finally:
        print("=" * 80)
        print("CERRANDO")
        print("=" * 80 + "\n")

        if browser:
            print("El navegador seguirá abierto.")
            print("Presiona ENTER para cerrar...\n")

            try:
                input()
            except:
                pass

            print("Cerrando navegador...")
            try:
                browser.close()
                print("✅ Navegador cerrado\n")
            except Exception as e:
                print(f"⚠️ Error cerrando: {e}\n")

        if playwright:
            try:
                playwright.stop()
                print("✅ Playwright cerrado\n")
            except Exception as e:
                print(f"⚠️ Error: {e}\n")

if __name__ == "__main__":
    print("\n")
    archivo = main()

    if archivo:
        print(f"🎉 ¡Éxito! Archivo: {archivo}\n")
    else:
        print("⚠️ No se creó el archivo\n")

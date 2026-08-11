#!/usr/bin/env python3
"""
Script para descargar pólizas de Allianz y guardarlas en Excel
"""

from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import time

URL_ALLIANZ = "https://net.allianz.com.ar/#/home"

def descargar_polizas():
    print("🚀 Iniciando descarga de pólizas Allianz...\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1400, "height": 900})

        try:
            print("=" * 80)
            print("ABRIENDO ALLIANZ")
            print("=" * 80)
            print("\n🌐 Abriendo https://net.allianz.com.ar...\n")

            page.goto(URL_ALLIANZ, wait_until="networkidle", timeout=30000)
            time.sleep(3)

            print("=" * 80)
            print("COMPLETA MANUALMENTE EN EL NAVEGADOR")
            print("=" * 80)
            print("\n👉 En el navegador que se abrió:")
            print("   1. Acepta cookies (si aparecen)")
            print("   2. Cierra banners (si aparecen)")
            print("   3. Usuario: eduardo3")
            print("   4. Contraseña: eduardo10")
            print("   5. Click en INICIAR SESIÓN")
            print("   6. Ve a Producción → AGENTE")
            print("   7. Completa filtros (si quieres)")
            print("   8. Click en PROCESAR DATOS")
            print("   9. Espera a que cargue la tabla\n")

            print("⏳ Cuando veas la tabla de pólizas en el navegador,")
            print("   presiona ENTER aquí para que extraiga los datos...\n")
            print("=" * 80)
            input()

            print("\n✅ Extrayendo datos de la tabla...\n")

            # Buscar tabla
            tables = page.query_selector_all('table')

            if len(tables) == 0:
                print("❌ No se encontró tabla")
                print("\n💡 Verifica que:")
                print("   - Completaste el login")
                print("   - Navegaste a Producción > AGENTE")
                print("   - Hiciste click en PROCESAR DATOS")
                print("   - La tabla está visible\n")
                return None

            tabla = tables[0]
            filas = tabla.query_selector_all('tbody tr')
            total = len(filas)

            print(f"✅ Encontradas {total} pólizas\n")

            polizas = []

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
                            print(f"   {i + 1}/{total} pólizas...", end="\r")

                except Exception as e:
                    print(f"   ⚠️ Error en fila {i}: {e}")
                    continue

            print(f"\n✅ Extracción completada\n")

            # Generar Excel
            if polizas:
                print("=" * 80)
                print("GENERANDO EXCEL")
                print("=" * 80 + "\n")

                df = pd.DataFrame(polizas)
                fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"Allianz_Polizas_{fecha}.xlsx"

                df.to_excel(nombre_archivo, index=False, sheet_name='Pólizas')

                print(f"✅ Excel guardado: {nombre_archivo}")
                print(f"📊 Total de pólizas: {len(polizas)}\n")

                print("Primeras pólizas:")
                print(df.head().to_string() + "\n")

                return nombre_archivo
            else:
                print("❌ No se extrajeron pólizas")
                return None

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None

        finally:
            print("\n" + "=" * 80)
            print("✅ TERMINADO")
            print("=" * 80)
            print("El navegador seguirá abierto.")
            print("Presiona ENTER para cerrar...\n")

            try:
                input()
            except:
                pass

            browser.close()
            print("✅ Cerrado\n")

if __name__ == "__main__":
    try:
        archivo = descargar_polizas()
        if archivo:
            print(f"🎉 ¡Listo! Archivo: {archivo}\n")
    except KeyboardInterrupt:
        print("\n⚠️ Cancelado")
    except Exception as e:
        print(f"\n❌ Error: {e}")

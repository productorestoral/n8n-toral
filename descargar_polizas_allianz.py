#!/usr/bin/env python3
"""
Script para descargar pólizas de Allianz y guardarlas en Excel

Instalación:
    pip install playwright pandas openpyxl

Uso:
    python descargar_polizas_allianz.py
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import pandas as pd
from datetime import datetime
import time

URL_ALLIANZ = "https://net.allianz.com.ar/#/home"

def descargar_polizas():
    """Descarga pólizas de Allianz y las guarda en Excel"""

    print("🚀 Iniciando descarga de pólizas Allianz...\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1400, "height": 900})

        try:
            # ABRIR ALLIANZ
            print("=" * 70)
            print("PASO 1: ABRIENDO ALLIANZ")
            print("=" * 70)
            print("🌐 Accediendo a https://net.allianz.com.ar...\n")

            page.goto(URL_ALLIANZ, wait_until="networkidle", timeout=30000)
            time.sleep(3)

            # LOGIN MANUAL
            print("=" * 70)
            print("PASO 2: LOGIN")
            print("=" * 70)
            print("📍 Se abrió la página de Allianz")
            print()
            print("👉 AHORA TÚ (en el navegador):")
            print("   1. Acepta las cookies si aparecen")
            print("   2. Cierra cualquier banner que aparezca")
            print("   3. Completa usuario y contraseña")
            print("   4. Haz click en 'INICIAR SESIÓN'")
            print("   5. Espera a que cargue")
            print()
            print("⏳ Cuando hayas ingresado, presiona ENTER aquí...")
            print("=" * 70)
            input()

            time.sleep(5)

            # NAVEGAR A PRODUCCIÓN → AGENTE
            print("\n" + "=" * 70)
            print("PASO 3: NAVEGAR A PRODUCCIÓN → AGENTE")
            print("=" * 70)
            print("👉 AHORA TÚ (en el navegador):")
            print("   1. Haz click en 'PRODUCCIÓN' (menú izquierdo)")
            print("   2. Haz click en 'AGENTE' (submenú)")
            print("   3. Espera a que cargue")
            print()
            print("⏳ Cuando estés en la pantalla AGENTE, presiona ENTER aquí...")
            print("=" * 70)
            input()

            time.sleep(3)

            # CONFIGURAR FILTROS (AUTOMÁTICO)
            print("\n" + "=" * 70)
            print("PASO 4: CONFIGURAR FILTROS")
            print("=" * 70)
            print("🔧 Configurando automáticamente...")

            # Organizador
            try:
                all_inputs = page.query_selector_all('input')
                for inp in all_inputs:
                    try:
                        label = inp.evaluate('el => el.parentElement?.textContent || el.placeholder || ""').lower()
                        if 'organizador' in label or 'agente' in label:
                            inp.fill('TORAL EDUARDO')
                            print("   ✅ Organizador: TORAL EDUARDO")
                            break
                    except:
                        pass
            except Exception as e:
                print(f"   ⚠️ Error configurando organizador: {e}")

            time.sleep(1)

            # Tipo de póliza
            try:
                selects = page.query_selector_all('select')
                for select in selects:
                    try:
                        options_text = select.evaluate('''sel =>
                            Array.from(sel.querySelectorAll('option')).map(o => o.textContent.toLowerCase())
                        ''')

                        if any('hogar' in o or 'combinado' in o for o in options_text):
                            option_elements = select.query_selector_all('option')
                            for opt in option_elements:
                                opt_text = opt.text_content().lower()
                                if 'hogar' in opt_text or 'combinado' in opt_text:
                                    opt.evaluate('o => o.selected = true')
                                    select.evaluate('sel => sel.dispatchEvent(new Event("change", {bubbles: true}))')
                                    print("   ✅ Tipo de póliza: Hogar/Combinado")
                                    break
                            break
                    except:
                        pass
            except Exception as e:
                print(f"   ⚠️ Error configurando tipo: {e}")

            time.sleep(2)

            # PROCESAR DATOS (MANUAL)
            print("\n" + "=" * 70)
            print("PASO 5: PROCESAR DATOS")
            print("=" * 70)
            print("👉 AHORA TÚ (en el navegador):")
            print("   1. Haz click en el botón 'PROCESAR DATOS'")
            print("   2. Espera a que cargue la tabla de pólizas")
            print()
            print("⏳ Cuando veas la tabla con las pólizas, presiona ENTER aquí...")
            print("=" * 70)
            input()

            time.sleep(5)

            # EXTRAER TABLA
            print("\n" + "=" * 70)
            print("PASO 6: EXTRAYENDO DATOS")
            print("=" * 70)

            polizas = []

            # Buscar tabla
            tables = page.query_selector_all('table')

            if len(tables) == 0:
                print("❌ No se encontró tabla de pólizas")
                print()
                print("Posibles causas:")
                print("  - No hiciste click en PROCESAR DATOS")
                print("  - Los filtros no se configuraron correctamente")
                print("  - La tabla todavía está cargando")
                print()
                print("El navegador seguirá abierto. Revisa qué pasó.")
            else:
                tabla = tables[0]
                filas = tabla.query_selector_all('tbody tr')
                total_filas = len(filas)

                print(f"✅ Encontradas {total_filas} pólizas")
                print("🔄 Extrayendo datos...\n")

                for i, fila in enumerate(filas):
                    try:
                        celdas = fila.query_selector_all('td')

                        if len(celdas) >= 6:
                            numero_poliza = celdas[0].text_content().strip()
                            nombre_asegurado = celdas[1].text_content().strip()
                            ubicacion = celdas[2].text_content().strip()
                            suma_incendio = celdas[3].text_content().strip()
                            vigencia_desde = celdas[4].text_content().strip()
                            vigencia_hasta = celdas[5].text_content().strip()

                            # Buscar ícono de mapa
                            map_icon = fila.query_selector('[alt*="Argentina"], [title*="Argentina"], img[src*="argentina"]')
                            detalles_suma = suma_incendio

                            if map_icon:
                                try:
                                    print(f"   🔍 Póliza {numero_poliza}: accediendo detalles...")
                                    map_icon.click()
                                    time.sleep(3)

                                    try:
                                        page.wait_for_load_state("networkidle", timeout=8000)
                                    except:
                                        pass

                                    # Buscar suma asegurada en detalles
                                    cells = page.query_selector_all('td, div[role="cell"], span')
                                    for j, cell in enumerate(cells):
                                        cell_text = cell.text_content().lower()
                                        if 'suma' in cell_text and 'asegurada' in cell_text:
                                            if j + 1 < len(cells):
                                                detalles_suma = cells[j + 1].text_content().strip()
                                            break

                                    # Volver
                                    page.go_back()
                                    time.sleep(2)

                                    tabla = page.query_selector('table')
                                    if tabla:
                                        filas = tabla.query_selector_all('tbody tr')

                                except Exception as e:
                                    print(f"      ⚠️ Error: {str(e)}")
                                    try:
                                        page.go_back()
                                        time.sleep(2)
                                    except:
                                        pass

                            poliza = {
                                'Número de Póliza': numero_poliza,
                                'Nombre Asegurado': nombre_asegurado,
                                'Ubicación del Riesgo': ubicacion,
                                'Suma Incendio Edificio': detalles_suma,
                                'Vigencia Desde': vigencia_desde,
                                'Vigencia Hasta': vigencia_hasta,
                            }
                            polizas.append(poliza)

                            if (i + 1) % 5 == 0:
                                print(f"   ✅ {i + 1}/{total_filas} pólizas...", end="\r")

                    except Exception as e:
                        print(f"   ⚠️ Error en fila {i}: {str(e)}")
                        continue

                print(f"\n\n✅ Extracción completada: {len(polizas)} pólizas\n")

            # CREAR EXCEL
            if polizas:
                print("=" * 70)
                print("PASO 7: GENERANDO EXCEL")
                print("=" * 70)

                df = pd.DataFrame(polizas)

                fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"Allianz_Polizas_{fecha}.xlsx"

                df.to_excel(nombre_archivo, index=False, sheet_name='Pólizas')

                print(f"\n✅ Excel guardado: {nombre_archivo}")
                print(f"📊 Total de pólizas: {len(polizas)}\n")
                print("Primeras pólizas:")
                print(df.head().to_string())

                return nombre_archivo
            else:
                print("❌ No se extrajeron pólizas")
                return None

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

        finally:
            # NO cerrar automáticamente
            print("\n" + "=" * 70)
            print("✅ TERMINADO")
            print("=" * 70)
            print("El navegador seguirá abierto.")
            print("Presiona ENTER aquí para cerrar...")
            print("=" * 70)
            try:
                input()
            except:
                pass

            browser.close()
            print("\n✅ Navegador cerrado")

if __name__ == "__main__":
    try:
        archivo = descargar_polizas()
        if archivo:
            print(f"\n🎉 ¡Listo! Archivo guardado: {archivo}")
        else:
            print("\n⚠️ No se pudo crear el archivo")
    except KeyboardInterrupt:
        print("\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}")

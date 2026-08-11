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
import sys

# Configuración
USUARIO = "eduardo3"
PASSWORD = "eduardo10"
ORGANIZADOR = "TORAL EDUARDO"
URL_ALLIANZ = "https://net.allianz.com.ar/#/home"

def descargar_polizas():
    """Descarga pólizas de Allianz y las guarda en Excel"""

    print("🚀 Iniciando descarga de pólizas Allianz...\n")

    with sync_playwright() as p:
        # Abrir navegador
        print("📍 Abriendo navegador...")
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1400, "height": 900})

        try:
            # 1. ABRIR ALLIANZ
            print("🌐 Accediendo a Allianz...")
            print("   ⏳ Esperando que cargue la página (esto tarda un poco)...\n")
            try:
                page.goto(URL_ALLIANZ, wait_until="networkidle", timeout=30000)
            except:
                print("   ⚠️ Timeout, pero continuamos...")

            time.sleep(5)

            # 2. LOGIN
            print("🔐 Completando datos de login...\n")

            # Llenar usuario
            user_inputs = page.query_selector_all('input[type="text"]')
            if len(user_inputs) > 0:
                user_inputs[0].fill(USUARIO)
                print(f"   ✅ Usuario ingresado: {USUARIO}")
            else:
                print("   ⚠️ No se encontró campo de usuario")

            time.sleep(1)

            # Llenar contraseña
            pass_inputs = page.query_selector_all('input[type="password"]')
            if len(pass_inputs) > 0:
                pass_inputs[0].fill(PASSWORD)
                print(f"   ✅ Contraseña ingresada\n")
            else:
                print("   ⚠️ No se encontró campo de contraseña\n")

            time.sleep(2)

            # Login manual - el usuario hace click en el botón
            print("=" * 60)
            print("🔐 PASO 1: LOGIN")
            print("=" * 60)
            print("   ✅ Los campos de usuario y contraseña ya están completados")
            print("   ")
            print("   👉 AHORA TÚ:")
            print("      1. Mira el navegador que se abrió")
            print("      2. Haz click en el botón 'INICIAR SESIÓN'")
            print("      3. Espera a que cargue la siguiente página")
            print("   ")
            print("   ⏳ Cuando veas que pasó la página de login,")
            print("      presiona ENTER aquí...")
            print("=" * 60)
            input()

            # Esperar a que cargue después del login
            print("\n⏳ Esperando que cargue la página después del login...")
            time.sleep(8)
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except PlaywrightTimeoutError:
                print("   ⚠️ Timeout esperando carga, continuando...")

            # 3. BUSCAR MENU PRODUCCIÓN Y SUBMENÚ AGENTE
            print("\n" + "=" * 60)
            print("📊 PASO 2: NAVEGAR A PRODUCCIÓN → AGENTE")
            print("=" * 60)
            print("   👉 AHORA TÚ:")
            print("      1. Haz click en 'PRODUCCIÓN' (en el menú izquierdo)")
            print("      2. Espera a que cargue")
            print("      3. Haz click en 'AGENTE' (submenú)")
            print("      4. Espera a que cargue la página de AGENTE")
            print("   ")
            print("   ⏳ Presiona ENTER cuando estés viendo la pantalla de AGENTE...")
            print("=" * 60)
            input()

            time.sleep(3)

            # 4. CONFIGURAR FILTROS
            print("\n⚙️ Configurando filtros...")

            # Organizador
            all_inputs = page.query_selector_all('input')
            organizador_ingresado = False
            for inp in all_inputs:
                try:
                    label = inp.evaluate('el => el.parentElement?.textContent || el.placeholder || ""').lower()
                    if 'organizador' in label or 'agente' in label:
                        inp.fill(ORGANIZADOR)
                        print(f"   ✅ Organizador: {ORGANIZADOR}")
                        organizador_ingresado = True
                        break
                except:
                    pass

            if not organizador_ingresado:
                print("   ⚠️ No se encontró campo Organizador")

            time.sleep(1)

            # Tipo de póliza (si existe select)
            selects = page.query_selector_all('select')
            for select in selects:
                try:
                    options_text = select.evaluate('''sel =>
                        Array.from(sel.querySelectorAll('option')).map(o => o.textContent.toLowerCase())
                    ''')

                    if any('hogar' in o or 'combinado' in o for o in options_text):
                        # Buscar opción que tenga tanto hogar como combinado o similar
                        option_elements = select.query_selector_all('option')
                        for opt in option_elements:
                            opt_text = opt.text_content().lower()
                            if 'hogar' in opt_text or 'combinado' in opt_text:
                                opt.evaluate('o => o.selected = true')
                                select.evaluate('sel => sel.dispatchEvent(new Event("change", {bubbles: true}))')
                                print("   ✅ Tipo de póliza configurado")
                                break
                        break
                except:
                    pass

            time.sleep(1)

            # 5. PROCESAR DATOS
            print("\n" + "=" * 60)
            print("🔄 PASO 4: PROCESAR DATOS")
            print("=" * 60)
            print("   ✅ Los filtros ya están configurados:")
            print(f"      - Organizador: {ORGANIZADOR}")
            print("      - Tipo de póliza: Hogar o Combinado Familiar")
            print("   ")
            print("   👉 AHORA TÚ:")
            print("      1. Haz click en el botón 'PROCESAR DATOS'")
            print("      2. Espera a que se cargue la tabla con las pólizas")
            print("      3. Verás un listado de pólizas")
            print("   ")
            print("   ⏳ Presiona ENTER cuando veas la tabla de pólizas...")
            print("=" * 60)
            input()

            # Esperar a que carguen los datos
            time.sleep(5)
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except PlaywrightTimeoutError:
                print("   ⚠️ Timeout esperando carga")

            # 6. EXTRAER TABLA DE PÓLIZAS Y NAVEGAR DETALLES
            print("\n📋 Extrayendo pólizas y datos detallados...")

            polizas = []

            # Buscar tabla
            tables = page.query_selector_all('table')
            if len(tables) == 0:
                print("   ❌ No se encontró tabla de pólizas")
                print("   💡 Verifica que completaste correctamente los filtros y hiciste click en Procesar Datos")
            else:
                tabla = tables[0]
                filas = tabla.query_selector_all('tbody tr')
                total_filas = len(filas)

                print(f"   ℹ️ Encontradas {total_filas} pólizas")

                for i, fila in enumerate(filas):
                    try:
                        celdas = fila.query_selector_all('td')

                        if len(celdas) >= 6:
                            # Extraer datos básicos de la tabla
                            numero_poliza = celdas[0].text_content().strip()
                            nombre_asegurado = celdas[1].text_content().strip()
                            ubicacion = celdas[2].text_content().strip()
                            suma_incendio = celdas[3].text_content().strip()
                            vigencia_desde = celdas[4].text_content().strip()
                            vigencia_hasta = celdas[5].text_content().strip()

                            # Buscar ícono de mapa (Argentina) en la fila para obtener detalles
                            map_icon = fila.query_selector('[alt*="Argentina"], [title*="Argentina"], img[src*="argentina"]')
                            detalles_suma = suma_incendio  # Por defecto, usar la de la tabla

                            if map_icon:
                                try:
                                    # Click en el mapa para ir a página de detalles
                                    print(f"   🔍 Accediendo detalles de póliza {numero_poliza}...")
                                    map_icon.click()
                                    time.sleep(3)

                                    # En la página de detalles, buscar la suma asegurada
                                    try:
                                        page.wait_for_load_state("networkidle", timeout=8000)
                                    except:
                                        pass

                                    # Buscar fila con suma asegurada (scrollear si es necesario)
                                    try:
                                        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                                        time.sleep(1)
                                    except:
                                        pass

                                    # Intentar encontrar "Suma Asegurada" en la página
                                    cells = page.query_selector_all('td, div[role="cell"], span')
                                    for j, cell in enumerate(cells):
                                        cell_text = cell.text_content().lower()
                                        if 'suma' in cell_text and 'asegurada' in cell_text and j + 1 < len(cells):
                                            detalles_suma = cells[j + 1].text_content().strip()
                                            print(f"      ✅ Suma asegurada encontrada: {detalles_suma}")
                                            break

                                    # Volver a la tabla
                                    page.go_back()
                                    time.sleep(2)

                                    # Recargar tabla para siguiente iteración
                                    tabla = page.query_selector('table')
                                    if tabla:
                                        filas = tabla.query_selector_all('tbody tr')

                                except Exception as e:
                                    print(f"      ⚠️ Error accediendo detalles: {str(e)}")
                                    # Volver a la tabla
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

                            if (i + 1) % 10 == 0:
                                print(f"   ✅ {i + 1}/{total_filas} pólizas procesadas...")

                    except Exception as e:
                        print(f"   ⚠️ Error en fila {i}: {str(e)}")
                        continue

            # 7. CREAR EXCEL
            print(f"\n💾 Creando Excel con {len(polizas)} pólizas...")

            if polizas:
                df = pd.DataFrame(polizas)

                # Nombre del archivo
                fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"Allianz_Polizas_{fecha}.xlsx"

                # Guardar con formato
                df.to_excel(nombre_archivo, index=False, sheet_name='Pólizas')

                print(f"   ✅ Excel guardado: {nombre_archivo}")
                print(f"   📊 Total de pólizas: {len(polizas)}")

                # Mostrar preview
                print("\n📄 Vista previa:")
                print(df.head().to_string())

                return nombre_archivo
            else:
                print("   ❌ No se extrajeron pólizas")
                return None

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

        finally:
            # Cerrar navegador
            time.sleep(2)
            browser.close()
            print("\n✅ Navegador cerrado")

if __name__ == "__main__":
    try:
        archivo = descargar_polizas()
        if archivo:
            print(f"\n🎉 ¡Listo! Archivo guardado: {archivo}")
        else:
            print("\n❌ No se pudo crear el archivo")
    except KeyboardInterrupt:
        print("\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}")

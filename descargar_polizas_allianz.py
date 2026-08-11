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
            page.goto(URL_ALLIANZ, wait_until="networkidle", timeout=30000)
            time.sleep(3)

            # 2. LOGIN
            print("🔐 Realizando login...")

            # Llenar usuario
            user_inputs = page.query_selector_all('input[type="text"]')
            if len(user_inputs) > 0:
                user_inputs[0].fill(USUARIO)
                print(f"   ✅ Usuario ingresado: {USUARIO}")

            time.sleep(1)

            # Llenar contraseña
            pass_inputs = page.query_selector_all('input[type="password"]')
            if len(pass_inputs) > 0:
                pass_inputs[0].fill(PASSWORD)
                print(f"   ✅ Contraseña ingresada")

            time.sleep(1)

            # Clickear botón login - Intentar múltiples formas
            print("   Buscando botón INICIAR SESIÓN...")

            login_hecho = False
            try:
                # Intenta por :has-text
                page.click("button:has-text('INICIAR SESIÓN')")
                print("   ✅ Login iniciado (por has-text)")
                login_hecho = True
            except:
                pass

            if not login_hecho:
                try:
                    # Intenta por texto exacto
                    page.click("button:has-text('Iniciar Sesión')")
                    print("   ✅ Login iniciado (por Iniciar Sesión)")
                    login_hecho = True
                except:
                    pass

            if not login_hecho:
                try:
                    # Buscar botón por búsqueda de todos los botones
                    buttons = page.query_selector_all('button')
                    for btn in buttons:
                        text = btn.text_content().strip().upper()
                        if 'INICIAR' in text or 'SESION' in text:
                            btn.click()
                            print("   ✅ Login iniciado (por búsqueda de botones)")
                            login_hecho = True
                            break
                except Exception as e:
                    print(f"   ⚠️ Error en búsqueda de botones: {str(e)}")

            if not login_hecho:
                print("   ⚠️ No se encontró botón de login - verifica manualmente en el navegador")
                print("   💡 Cuando hayas ingresado manualmente, presiona ENTER aquí...")
                input()

            # Esperar a que cargue después del login
            time.sleep(5)
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except PlaywrightTimeoutError:
                print("   ⚠️ Timeout esperando carga, continuando...")

            # 3. BUSCAR MENU PRODUCCIÓN Y SUBMENÚ AGENTE
            print("\n📊 Navegando a Producción → AGENTE...")

            # Primero buscar Producción
            links = page.query_selector_all('a, button, [role="button"], span, div')
            produccion_encontrada = False
            for link in links:
                text = link.text_content().lower().strip()
                if text == 'producción' or text == 'produccion':
                    try:
                        link.click()
                        print("   ✅ Producción seleccionada")
                        produccion_encontrada = True
                        break
                    except:
                        pass

            if not produccion_encontrada:
                print("   ⚠️ No se encontró Producción, intenta manualmente")

            time.sleep(3)

            # Buscar submenú AGENTE
            links = page.query_selector_all('a, button, [role="button"], span, div, li')
            agente_encontrado = False
            for link in links:
                text = link.text_content().lower().strip()
                if text == 'agente':
                    try:
                        link.click()
                        print("   ✅ Submenú AGENTE seleccionado")
                        agente_encontrado = True
                        break
                    except:
                        pass

            if not agente_encontrado:
                print("   ⚠️ No se encontró AGENTE, intenta manualmente")

            time.sleep(2)

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
            print("\n🔄 Ejecutando Procesar Datos...")
            buttons = page.query_selector_all('button, a, [role="button"]')
            procesar_hecho = False
            for btn in buttons:
                text = btn.text_content().lower()
                if 'procesar' in text and 'dato' in text:
                    try:
                        btn.click()
                        print("   ✅ Procesar datos ejecutado")
                        procesar_hecho = True
                        break
                    except:
                        pass

            if not procesar_hecho:
                print("   ⚠️ No se encontró botón Procesar Datos, intenta manualmente")
                print("   💡 Cuando hayas hecho click, presiona ENTER aquí...")
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

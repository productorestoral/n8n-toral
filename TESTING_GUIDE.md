# Guía de Prueba - Extractor de Pólizas Allianz

## Estado Actual

✅ **Script puede:**
- Abrir navegador y conectarse a Allianz
- Esperar hasta 5 minutos a que usuario complete login manual
- Detectar tabla en iframes (ahora busca dentro de iframes, no solo en página principal)
- Extraer datos en múltiples formatos (HTML table, role="grid", role="row")

❌ **Problema pendiente:**
- Estructura exacta de la tabla en Allianz no está clara
- Necesitamos saber cómo están organizados los datos (td vs divs vs roles)

## Paso 1: Analizar Estructura (Primero ejecuta esto)

```bash
python3 debug_estructura.py
```

**Qué hace:**
1. Abre navegador
2. Te pide completar: login → Producción → AGENTE → filtros → PROCESAR DATOS
3. Una vez veas la tabla, presiona ENTER
4. El script analiza todos los frames y muestra:
   - Cantidad de elementos con diferentes estructuras
   - Qué roles HTML se usan (role="row", role="cell", etc.)
   - Cantidad de tablas HTML si las hay
   - Ejemplos de datos encontrados

**Qué buscar en la salida:**
- ¿Dice "Roles encontrados"? → Tabla usa role="row" (grid)
- ¿Dice "tablas HTML"? → Tabla usa `<table>` estándar
- Si ves datos de pólizas en la salida → Encontramos la estructura correcta

**Copia la salida completa y comparte conmigo** para saber exactamente cómo está estructurada la tabla.

---

## Paso 2: Probar Extracción (Después de entender la estructura)

Una vez sabemos cómo está estructurada la tabla, ejecuta el script principal:

```bash
python3 descargar_polizas_allianz.py
```

**Qué debería pasar:**
1. Navegador se abre
2. Manual: login → Producción → AGENTE → filtros → PROCESAR DATOS
3. Script automáticamente:
   - Detecta tabla (debería decir "✓ ¡Tabla detectada!")
   - Extrae todas las pólizas
   - Muestra: "✓ Extracción: X pólizas"
   - Genera archivo Excel: `Allianz_Polizas_YYYYMMDD_HHMMSS.xlsx`
   - Muestra primeras pólizas en pantalla

**Si falla:**
- ¿Dice "✗ Timeout: no se detectó tabla"? → Tabla no está en estructura esperada
  - Solución: Primero ejecuta `debug_estructura.py` para analizar
- ¿Dice "✗ Extracción: 0 pólizas"? → Estructura encontrada pero extracción falla
  - Solución: Necesitamos revisar qué datos hay realmente en las celdas

---

## Flujo Completo Recomendado

### Primera Vez:
1. `python3 debug_estructura.py` → Analizar estructura
2. Compartir salida conmigo
3. Actualizar script según estructura
4. `python3 descargar_polizas_allianz.py` → Probar extracción

### Próximas Veces (después de confirmar que funciona):
1. Solo ejecuta: `python3 descargar_polizas_allianz.py`
2. Completa pasos manualmente en navegador
3. Script automáticamente genera Excel

---

## Instalación de Dependencias

Si aún no las tienes:

```bash
pip3 install playwright pandas openpyxl
```

---

## Solución de Problemas

### "ModuleNotFoundError: No module named 'playwright'"
```bash
pip3 install playwright
```

### "No se encuentra Chromium"
```bash
python3 -m playwright install
```

### Script se cierra rápido
- Asegúrate de completar todos los pasos: login, navegación, filtros, PROCESAR DATOS
- El script espera hasta 5 minutos (300 segundos) a que termines

### Tabla visible pero no se extrae
1. Ejecuta `debug_estructura.py`
2. Busca en la salida qué estructura tiene (roles, tablas, etc.)
3. Compartir salida para ajustar script

---

## Archivos de Depuración

- **`debug_estructura.py`**: Analiza estructura de tabla → EJECUTA PRIMERO
- **`descargar_polizas_allianz.py`**: Script principal de extracción
- **`inspector.py`**: Inspector simple (legacy)

---

## Esperado en Salida

```
================================================================================
DESCARGADOR DE PÓLIZAS ALLIANZ
================================================================================

1. Iniciando Playwright...
   ✓ Listo

2. Abriendo navegador...
   ✓ Listo

[navegador se abre y espera...]

================================================================================
EXTRAYENDO:
================================================================================

Filas: 17

  10/17
✓ Extracción: 17 pólizas

================================================================================
GENERANDO EXCEL:
================================================================================

✓ Archivo: Allianz_Polizas_20240115_143022.xlsx

Primeras pólizas:

   Número de Póliza  Nombre Asegurado  ... Vigencia Hasta
0        12345678      Juan Pérez           31/12/2024
...

================================================================================
✓ COMPLETADO
================================================================================

Presiona Ctrl+C para cerrar
```

---

**Próximo paso:** Ejecuta `python3 debug_estructura.py` y comparte los resultados conmigo.

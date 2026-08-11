# Descarga Automática de Pólizas Allianz

Script Python que automatiza la extracción de datos de pólizas desde el portal de Allianz Argentina.

## ¿Qué hace?

El script realiza los siguientes pasos automáticamente:

1. ✅ Abre el portal de Allianz (https://net.allianz.com.ar)
2. ✅ Realiza login con credenciales (usuario: eduardo3, contraseña: eduardo10)
3. ✅ Navega a **Producción → AGENTE**
4. ✅ Configura filtros:
   - Organizador: TORAL EDUARDO
   - Tipo de póliza: Hogar o Combinado Familiar
5. ✅ Ejecuta "Procesar Datos" para generar la lista de pólizas
6. ✅ **Extrae datos en dos niveles:**
   - **Nivel 1 (Tabla):** Número de póliza, nombre asegurado, ubicación, vigencia
   - **Nivel 2 (Detalle):** Clickea en el ícono de mapa Argentina en cada fila para obtener detalles adicionales
7. ✅ Exporta todo a un archivo Excel con timestamp

## Instalación

### Requisitos
- Python 3.8+
- pip (gestor de paquetes)

### Paso 1: Instalar Python

Si no tienes Python:
1. Descarga desde https://www.python.org/downloads/
2. Instala normalmente
3. Verifica: `python --version`

### Paso 2: Instalar dependencias

```bash
pip install playwright pandas openpyxl
```

Esto instala:
- **playwright**: Automatización de navegador
- **pandas**: Manejo de datos
- **openpyxl**: Generación de Excel

## Uso

### Opción 1: Ejecución Manual (Recomendado para primeras pruebas)

```bash
python descargar_polizas_allianz.py
```

El navegador se abrirá automáticamente mostrando cada paso. Si algo falla en el login o configuración de filtros, el script pedirá que completes manualmente ese paso.

### Opción 2: Ejecución Desatendida

Igual que arriba, pero el navegador estará en modo headless (sin interfaz visual):

Edita el archivo y cambia:
```python
browser = p.chromium.launch(headless=True)  # En lugar de headless=False
```

## ¿Qué datos extrae?

El Excel generado contiene 6 columnas:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| Número de Póliza | Identificador único | 12345678 |
| Nombre Asegurado | Persona o empresa asegurada | Juan Pérez García |
| Ubicación del Riesgo | Dirección del bien asegurado | Calle 1234, Apt 5, CABA |
| Suma Incendio Edificio | Monto asegurado (incendio) | $500.000 |
| Vigencia Desde | Fecha de inicio | 01/01/2024 |
| Vigencia Hasta | Fecha de vencimiento | 31/12/2024 |

## Personalización

### Cambiar credenciales

Edita `descargar_polizas_allianz.py` y modifica:

```python
USUARIO = "tu_usuario"
PASSWORD = "tu_contraseña"
ORGANIZADOR = "Tu Organizador"
```

### Cambiar tipo de póliza

Busca en el script la sección de filtros:
```python
# Tipo de póliza (si existe select)
```

Y ajusta según los valores disponibles en Allianz.

## Solución de Problemas

### ❌ "python no se reconoce"
- Python no está instalado o no en PATH
- Reinicia la computadora después de instalar
- Intenta con `python3` en lugar de `python`

### ❌ "ModuleNotFoundError: No module named 'playwright'"
- Ejecuta: `pip install playwright pandas openpyxl`
- Espera a que termine completamente

### ❌ "Login no funciona automáticamente"
- El navegador se abrirá igual
- Ingresa manualmente las credenciales en el navegador que se abre
- Presiona ENTER en la terminal cuando hayas ingresado
- El script continuará automáticamente

### ❌ "No se encuentran los filtros"
- Algunos elementos de la página pueden tener nombres diferentes
- El script te indicará cuál paso falló
- Completa ese paso manualmente en el navegador
- Presiona ENTER en la terminal para continuar

### ❌ "No se encuentra tabla de pólizas"
- Verifica que:
  1. Hiciste login correctamente
  2. Estás en Producción → AGENTE
  3. Completaste los filtros
  4. Hiciste click en "Procesar Datos"
  5. Esperaste a que cargue la tabla

### ❌ "Error accediendo detalles"
- El script continúa incluso si falla al acceder a detalles
- Usa los datos de la tabla principal (que siempre se extraen)
- Si necesitas datos completos, ejecuta de nuevo

## Salida

El script crea un archivo Excel con nombre como:
```
Allianz_Polizas_20240115_143022.xlsx
```

Donde la fecha/hora se genera automáticamente. El archivo se guardaría en el mismo directorio donde ejecutaste el script.

## Automatización Diaria

### Windows (Tareas Programadas)

1. Abre "Tareas Programadas" (busca en Inicio)
2. Haz click en "Crear tarea básica"
3. Nombre: "Descargar Pólizas Allianz"
4. Trigger: "Diaria" a las 8:00 AM
5. Acción:
   - Programa: `python`
   - Argumentos: `C:\ruta\completa\descargar_polizas_allianz.py`

### Mac/Linux (Cron)

1. Abre Terminal
2. Ejecuta: `crontab -e`
3. Añade una línea como:
```
0 8 * * * /usr/bin/python3 /ruta/completa/descargar_polizas_allianz.py
```
4. Guarda (Ctrl+X, Y, Enter)

Esto ejecutará el script todos los días a las 8 AM.

## Pasos del Flujo Detallado

```
┌─────────────────────────────┐
│  Abrir Allianz Portal       │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│  Login (usuario/contraseña) │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│  Producción → AGENTE        │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│  Configurar Filtros         │
│  (Organizador, Tipo)        │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│  Click "Procesar Datos"     │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│  Extraer Tabla de Pólizas   │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────────┐
│  Para cada póliza:              │
│  1. Click en mapa Argentina     │
│  2. Extraer detalles            │
│  3. Volver a tabla              │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────┐
│  Generar Excel              │
│  (con timestamp)            │
└──────────────┬──────────────┘
               ↓
          ✅ LISTO
```

## Notas Técnicas

- **Playwright**: Usa Chromium (incluido automáticamente)
- **Timeouts**: El script espera 30s para login, 10s para cada página
- **Reintentos**: Si un elemento no se encuentra, intenta alternativas
- **Fallback manual**: Si la automatización falla, el script puede pausar para entrada manual
- **Navegación**: Usa `page.go_back()` para volver a la tabla entre detalles

## Preguntas Frecuentes

**P: ¿Es seguro guardar las credenciales en el script?**
R: El script incluye credenciales de ejemplo. Para producción, considera usar variables de entorno o un archivo de configuración separado (no versionado).

**P: ¿Puedo cambiar el organizador?**
R: Sí, edita la variable `ORGANIZADOR` en el script con el valor correcto.

**P: ¿Qué pasa si Allianz cambia su interfaz?**
R: El script está diseñado con múltiples estrategias de búsqueda. Si falla, avísanos para actualizar los selectores.

**P: ¿Puedo automatizar varias ejecuciones?**
R: Sí, configura una tarea programada (Windows) o cron job (Mac/Linux).

## Contacto / Soporte

Si encuentras problemas:
1. Verifica que Playwright esté instalado: `pip show playwright`
2. Comprueba tu conexión a internet
3. Revisa que las credenciales sean correctas
4. Ejecuta en modo interactivo (headless=false) para ver qué pasa

---

**Última actualización:** 2024-01-15
**Versión:** 1.1 (con extracción de detalles)

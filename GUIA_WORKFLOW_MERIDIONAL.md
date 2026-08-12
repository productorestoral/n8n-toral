# Guía de Workflow: Scraper Meridional - Pólizas a Google Drive

## Descripción General

Este workflow automatiza la descarga de pólizas de seguros desde Meridional (https://ws8.meridionalnet.com.ar/Gestion/PolizaEmitida/Endosos), aplica filtros de exclusión y genera un archivo Excel que se sube a Google Drive.

## Correcciones Realizadas

### 1. **GET Login Page** - Formato de respuesta
**Problema:** El nodo no devolvía el HTML en un formato accesible.

**Solución:**
- `Response Format: text` - Recibe la respuesta como texto plano (HTML)
- `Put Output in Field: data` - Almacena el HTML en el campo `data` del output

**Impacto:** Permite que el siguiente nodo (Extraer Token CSRF) acceda correctamente al HTML.

### 2. **Extraer Token CSRF** - Mejora en robustez
**Cambios:**
- Múltiples patrones de búsqueda para el token `__RequestVerificationToken`
- Mejor manejo de errores con información de diagnóstico
- Valida que el HTML recibido sea una cadena válida

**Impacto:** El nodo puede extraer el token incluso si el HTML tiene variaciones de formato.

### 3. **POST Login** - Configuración de credenciales
**Asegurado:**
- `Send Body: true` - Habilita el envío del cuerpo
- `Body Content Type: form-urlencoded` - Formato correcto para formularios
- Parámetros: Usuario, password, token CSRF

**Impacto:** Las credenciales se envían correctamente al servidor Meridional.

### 4. **GET Pólizas Page** - Acceso a datos
**Cambios:**
- `Response Format: text` - Recibe HTML como texto
- `Put Output in Field: data` - Almacena en campo `data`

**Impacto:** Mantiene consistencia con GET Login Page para acceso uniforme a datos.

### 5. **Procesar y Filtrar Datos** - Parsing robusto
**Mejoras:**
- Acceso flexible a datos: `response.data || response.body || response`
- Mejor manejo de errores con información de depuración
- Información adicional en caso de fallo (tipo de dato recibido, etc.)

**Filtros aplicados:**
- **Excluir pólizas** donde MOTIVO DE ENDOSO contiene: "Cambio forma de pago"
- **Excluir productores**: FASANELLA, LIJO, CALARCO, MAGNAGHI

**Output:** JSON con estructura:
```json
{
  "success": true,
  "total": 273,
  "incluidas": 200,
  "excluidas": 73,
  "polizas": [
    {
      "ramo": "HOGAR",
      "poliza": "12345678",
      "endoso": "001",
      "productor": "NOMBRE",
      "motivo": "Cambio de datos"
    }
  ]
}
```

## Pasos de Configuración en n8n Cloud

### 1. Importar el Workflow
1. Abre n8n cloud en tu navegador
2. Ve a "Workflows" → "Create new workflow"
3. Haz clic en el icono de importación (esquina superior)
4. Copia el contenido de `flujo-meridional-final.json` y pégalo
5. Haz clic en "Import"

### 2. Configurar Credenciales de Google Drive
1. Localiza el nodo **"Google Drive Upload"** en el canvas
2. Haz clic sobre él para seleccionar
3. En el panel lateral derecho, busca la sección "Credentials"
4. Haz clic en "Create new" o selecciona credenciales existentes
5. Sigue el flujo de autenticación OAuth de Google
6. Autoriza el acceso a Google Drive
7. Guarda los cambios

### 3. Verificar Configuración
- ✓ Trigger Manual está listo
- ✓ GET Login Page: Response Format = "text", Output Field = "data"
- ✓ Extraer Token CSRF: Extrae el token correctamente
- ✓ POST Login: Envía credenciales con CSRF token
- ✓ GET Pólizas Page: Response Format = "text", Output Field = "data"
- ✓ Procesar y Filtrar Datos: Parsea HTML y aplica filtros
- ✓ Google Drive Upload: Credenciales configuradas

## Ejecución del Workflow

### Ejecución Manual
1. Haz clic en el botón "Execute Workflow" (triángulo de reproducción azul)
2. O selecciona el nodo "Trigger Manual" y haz clic en "Test Trigger"

### Monitoreo
Durante la ejecución verás:
1. **GET Login Page**: Obtiene la página de login (devuelve HTML)
2. **Extraer Token CSRF**: Extrae el token de seguridad (devuelve `csrfToken`)
3. **POST Login**: Inicia sesión con credenciales (devuelve respuesta de login)
4. **GET Pólizas Page**: Obtiene página de pólizas (devuelve HTML con tabla)
5. **Procesar y Filtrar Datos**: Parsea tabla y aplica filtros (devuelve JSON con pólizas filtradas)
6. **Google Drive Upload**: Crea y sube archivo Excel a Google Drive

### Output Esperado
Recibirás un archivo llamado `polizas_meridional_YYYY-MM-DD.xlsx` en tu Google Drive raíz con:
- Columnas: Ramo, Póliza, Endoso, Productor, Motivo
- Filas: Todas las pólizas que pasaron los filtros de exclusión
- Registro: Pólizas incluidas y excluidas (en el JSON de salida)

## Troubleshooting

### Error: "Token CSRF no encontrado"
- **Causa:** El patrón de búsqueda no coincide con el HTML actual
- **Solución:** Ejecuta solo hasta el nodo "GET Login Page", ve a su output, copia el HTML y busca manualmente `__RequestVerificationToken`

### Error: "Tabla no encontrada en el HTML"
- **Causa:** La página de pólizas devuelve un HTML diferente (posible error de login)
- **Solución:** Verifica que las credenciales sean correctas; ejecuta el workflow y revisa el output del nodo "GET Pólizas Page"

### Error: "No se recibió HTML válido"
- **Causa:** El formato de respuesta es incorrecto
- **Solución:** Verifica que "GET Pólizas Page" tenga `Response Format: text` y `Output Field: data`

### El archivo Excel está vacío
- **Causa:** Todas las pólizas fueron excluidas por los filtros
- **Solución:** Revisa el output del nodo "Procesar y Filtrar Datos" para ver `incluidas` vs `excluidas`

## Estructura del Workflow

```
Trigger Manual
    ↓
GET Login Page (obtiene formulario de login)
    ↓
Extraer Token CSRF (extrae __RequestVerificationToken)
    ↓
POST Login (inicia sesión con usuario/password/token)
    ↓
GET Pólizas Page (obtiene página con tabla de pólizas)
    ↓
Procesar y Filtrar Datos (parsea HTML, aplica filtros)
    ↓
Google Drive Upload (crea Excel y lo sube)
```

## Notas Importantes

1. **Credenciales:** Las credenciales de Meridional (usuario ESTORAL, password) están hardcodeadas. Si es necesario cambiarlas, edita los nodos "POST Login".

2. **Filtros:** Los filtros de exclusión están en el nodo "Procesar y Filtrar Datos". Para modificarlos, edita la sección:
   ```javascript
   const motivos_excluir = ['Cambio forma de pago'];
   const productores_excluir = ['FASANELLA', 'LIJO', 'CALARCO', 'MAGNAGHI'];
   ```

3. **Respuesta de Datos:** El workflow espera que Meridional devuelva HTML con una tabla `<table>` estándar. Si la estructura HTML cambia, habrá que ajustar el regex en "Procesar y Filtrar Datos".

4. **Google Drive:** El archivo se sube a la carpeta raíz de Google Drive. Para cambiar la ubicación, modifica el campo `parentId` en el nodo "Google Drive Upload".

5. **Nombre de Archivo:** El archivo se nombra automáticamente como `polizas_meridional_YYYY-MM-DD.xlsx` con la fecha actual.

## Próximos Pasos Opcionales

- Agregar validaciones adicionales en el parsing
- Implementar reintentos automáticos en caso de fallo
- Agregar notificaciones por email al completar
- Programar ejecución automática con triggers de horario
- Expandir los filtros de exclusión según sea necesario

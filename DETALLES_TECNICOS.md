# Detalles Técnicos - Workflow Meridional

## Análisis de Flujo de Datos

### 1. GET Login Page
**URL:** `https://ws8.meridionalnet.com.ar/Account/Login`  
**Método:** GET  
**Configuración Crítica:**
- `responseFormat: text` - Recibe respuesta como texto
- `outputPropertyName: data` - Almacena en campo `data`

**Response esperado:**
```html
<html>
  <form>
    <input type="hidden" name="__RequestVerificationToken" value="ABC123XYZ...">
    ...
  </form>
</html>
```

**Output del nodo:**
```json
{
  "body": "...", 
  "data": "<html>...</html>",
  "headers": {...},
  "statusCode": 200
}
```

---

### 2. Extraer Token CSRF
**Entrada:** `$input.first().data` (HTML del nodo anterior)

**Patrones de búsqueda (en orden de intento):**
```javascript
// Patrón 1: name primero, value después
/name=["']__RequestVerificationToken["'][^>]*value=["']([^"']+)["']/i

// Patrón 2: value primero, name después  
/value=["']([^"']+)["'][^>]*name=["']__RequestVerificationToken["']/i

// Patrón 3: Sintaxis alternativa con coma
/__RequestVerificationToken['"]\s*,?\s*value['"]\s*=\s*["']([^'"]+)["']/

// Patrón 4: Pattern más flexible
/__RequestVerificationToken.*?value="([^"]+)"/
```

**Output esperado:**
```json
{
  "csrfToken": "ABC123XYZ789..."
}
```

---

### 3. POST Login
**URL:** `https://ws8.meridionalnet.com.ar/Account/Login`  
**Método:** POST  
**Content-Type:** `application/x-www-form-urlencoded`  

**Body enviado:**
```
Usuario=ESTORAL&password=Etoral59s&__RequestVerificationToken=ABC123XYZ789...
```

**Configuración:**
```json
{
  "sendBody": true,
  "bodyContentType": "form-urlencoded",
  "bodyParameters": {
    "parameters": [
      {"name": "Usuario", "value": "ESTORAL"},
      {"name": "password", "value": "Etoral59s"},
      {"name": "__RequestVerificationToken", "value": "={{$json.csrfToken}}"}
    ]
  }
}
```

**Resultado esperado:**
- Status 200 (OK) o redirect (302)
- Session cookie establecida para usar en siguientes requests
- n8n maneja cookies automáticamente con `followRedirects: true`

---

### 4. GET Pólizas Page
**URL:** `https://ws8.meridionalnet.com.ar/Gestion/PolizaEmitida/Endosos`  
**Método:** GET  
**Configuración:**
- `followRedirects: true` - Sigue redirects (importante post-login)
- `responseFormat: text` - Recibe HTML
- `outputPropertyName: data` - Almacena en campo `data`

**Response esperado:**
```html
<table>
  <thead>...</thead>
  <tbody>
    <tr>
      <td>Nº</td>
      <td>HOGAR</td>
      <td>12345678</td>
      <td>001</td>
      <td>Vigencia</td>
      <td>Cambio de datos</td>
      <td>NOMBRE PRODUCTOR</td>
      ...
    </tr>
    <!-- Más filas -->
  </tbody>
</table>
```

**Output del nodo:**
```json
{
  "data": "<html>...<table>...</table>...</html>",
  "statusCode": 200
}
```

---

### 5. Procesar y Filtrar Datos

#### Entrada
```javascript
$input.first() = {
  "data": "<html>...",
  "statusCode": 200,
  "headers": {...}
}
```

#### Proceso de Parsing

**Paso 1: Extraer tabla**
```javascript
const tableMatch = html.match(/<table[^>]*>([\s\S]*?)<\/table>/);
// Obtiene todo entre <table> y </table>
```

**Paso 2: Extraer filas**
```javascript
const rowRegex = /<tr[^>]*>([\s\S]*?)<\/tr>/g;
// Extrae cada <tr>...</tr>
```

**Paso 3: Extraer celdas**
```javascript
const cellRegex = /<td[^>]*>([\s\S]*?)<\/td>/g;
// De cada fila, extrae cada <td>...</td>
// Remueve tags HTML interiores y hace trim()
```

**Paso 4: Mapear campos**
```javascript
const ramo = cells[1];      // "HOGAR"
const poliza = cells[2];    // "12345678"
const endoso = cells[3];    // "001"
const motivo = cells[5];    // "Cambio de datos"
const productor = cells[6]; // "NOMBRE PRODUCTOR"
```

#### Aplicar Filtros

**Exclusión 1: Motivo de Endoso**
```javascript
const motivos_excluir = ['Cambio forma de pago'];
if (motivos_excluir.some(m => 
    motivo.toUpperCase().includes(m.toUpperCase()))) {
  excluir = true;
}
```

**Exclusión 2: Productores**
```javascript
const productores_excluir = ['FASANELLA', 'LIJO', 'CALARCO', 'MAGNAGHI'];
if (productores_excluir.some(p => 
    productor.toUpperCase().includes(p.toUpperCase()))) {
  excluir = true;
}
```

#### Salida
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
      "productor": "CARLOS",
      "motivo": "Cambio de datos"
    },
    {
      "ramo": "HOGAR",
      "poliza": "87654321",
      "endoso": "002",
      "productor": "JUAN",
      "motivo": "Actualización"
    }
  ],
  "polizasExcluidas": [
    {
      "poliza": "11111111",
      "productor": "FASANELLA",
      "razon": "Cambio de datos"
    },
    {
      "poliza": "22222222",
      "productor": "JUAN",
      "razon": "Cambio forma de pago"
    }
  ]
}
```

---

### 6. Google Drive Upload

**Entrada:** Usa el output del nodo anterior en formato de tabla

**Configuración:**
```json
{
  "authentication": "oAuth2",
  "operation": "upload",
  "parentId": {"mode": "id", "value": "root"},
  "fileName": "=polizas_meridional_{{$now.toFormat('yyyy-MM-dd')}}.xlsx"
}
```

**Archivo generado:**
- Nombre: `polizas_meridional_2026-08-12.xlsx` (ejemplo)
- Ubicación: Carpeta raíz de Google Drive (root)
- Formato: Excel (.xlsx)
- Contenido: Tabla con pólizas filtradas

---

## Manejo de Errores

### Error: "Cannot read properties of undefined"
**Ubicación típica:** Procesar y Filtrar Datos (línea 5)

**Causas posibles:**
1. `response.data` es `undefined` - El nodo anterior no retornó datos
2. `html.match()` - Si `html` no es string
3. GET Pólizas Page no tiene `responseFormat: text`

**Diagnóstico:**
```javascript
// Agregar al inicio del nodo:
console.log('Response type:', typeof $input.first());
console.log('Response keys:', Object.keys($input.first()));
console.log('Response.data type:', typeof $input.first().data);
```

### Error: "Token CSRF no encontrado"
**Cause:** El patrón regex no coincide con el HTML real

**Diagnóstico:**
1. Ejecuta solo hasta GET Login Page
2. Ve al output y busca manualmente `__RequestVerificationToken`
3. Copia el HTML exacto que la rodea
4. Crea un nuevo patrón regex

Ejemplo de variaciones:
```html
<!-- Versión 1 -->
<input type="hidden" name="__RequestVerificationToken" value="ABC123">

<!-- Versión 2 -->
<input type="hidden" value="ABC123" name="__RequestVerificationToken">

<!-- Versión 3 (con espacios) -->
<input type="hidden" 
  name = "__RequestVerificationToken" 
  value = "ABC123" >
```

### Error: "Tabla no encontrada"
**Causa:** GET Pólizas Page no devuelve HTML con `<table>`

**Posibles razones:**
1. Login falló (credenciales incorrectas)
2. Sesión expiró
3. URL cambió
4. HTML tiene estructura diferente

**Verificar:**
1. Output de POST Login - ¿tiene status 200?
2. Output de GET Pólizas Page - ¿contiene `<table>`?
3. Credenciales en POST Login - ¿son correctas?

---

## Flujo de Cookies y Sesión

n8n HTTP Request maneja cookies automáticamente:

```
1. GET Login Page
   ↓ Servidor devuelve Set-Cookie: sessionid=XXX
   
2. Extraer Token CSRF
   ↓ No hay request, solo procesamiento local
   
3. POST Login
   ↓ n8n envía Cookie: sessionid=XXX
   ↓ Servidor valida credenciales y CSRF token
   ↓ Sesión se mantiene válida
   
4. GET Pólizas Page
   ↓ n8n envía Cookie: sessionid=XXX (la misma)
   ↓ Servidor devuelve página con pólizas
   
5. Procesar datos
   ↓ No hay request HTTP
   
6. Google Drive Upload
   ↓ Usa credenciales de Google (OAuth2), no Meridional
```

---

## Tamaño de Datos Esperado

- **GET Login Page:** ~50-100 KB (HTML del formulario)
- **GET Pólizas Page:** ~200-500 KB (tabla con 273 filas)
- **Procesar y Filtrar:** En memoria, JSON ~50-100 KB
- **Archivo Excel:** ~50-200 KB (200 pólizas)

Total de transferencia: ~300-800 KB por ejecución

---

## Timeouts y Límites

n8n Cloud tiene límites:
- **Tiempo de ejecución:** Por defecto 30-60 segundos
- **Reintentos:** Se pueden configurar en cada nodo
- **Rate limiting:** Meridional podría limitar requests

Si el scraping tarda más de 30 segundos, considera:
1. Aumentar timeouts en HTTP nodes
2. Agregar delays con `Wait` nodes si es necesario
3. Reducir rango de fechas

---

## Seguridad

**Credenciales hardcodeadas:**
El workflow actual tiene credenciales de Meridional en texto plano:
```json
{"name": "Usuario", "value": "ESTORAL"},
{"name": "password", "value": "Etoral59s"}
```

**Mejora recomendada:**
Usar n8n Credentials Manager:
1. Crear credenciales en n8n para Meridional
2. Referenciar con `{{$credentials.meridionalApi.username}}`
3. Las credenciales se encriptan en la DB de n8n

---

## Testing y Validación

**Nodo por nodo:**
1. GET Login Page → Verifica HTML recibido
2. Extraer Token CSRF → Verifica csrfToken existe
3. POST Login → Verifica status 200 o redirect
4. GET Pólizas Page → Verifica HTML con tabla
5. Procesar y Filtrar → Verifica JSON válido
6. Google Drive → Verifica archivo creado

**Validaciones automáticas en el código:**
```javascript
// En cada nodo se verifica el tipo y estructura
if (!html || typeof html !== 'string') {
  return { error: 'No HTML data received' };
}

// Se cuenta filas: validar que al menos hay algunas
if (cells.length < 6) continue;

// Se validan políticas
if (!poliza) continue; // Skip filas sin póliza
```

# 📧 Guía - Flujo Completo Gmail RAG

## Qué hace este flujo

```
📨 Email llega       → 🔍 Busca en documentos    → 🤖 Genera respuesta   → ✉️ Responde automáticamente
   (Cliente)           (Drive + Embeddings)       (Gemini)                (al cliente)
```

**Ejemplo real:**
```
Cliente: "¿Qué documentos necesito para contratar hogar?"
         ↓
Sistema busca en "Requisitos_Contratacion.md"
         ↓
Gemini genera: "Para contratar hogar necesitas: DNI/CUIT, comprobante de propiedad, fotos..."
         ↓
Envía respuesta automática al cliente
```

---

## 📋 Pasos para Importar el Flujo

### 1. Abre n8n
- Ve a tu instancia de n8n
- Click en **"New Workflow"** o **"Import Workflow"**

### 2. Importa el archivo JSON
- Opción A: Copia el contenido de `FLUJO_COMPLETO.json`
- Opción B: Click en **"Import"** y sube el archivo

### 3. Configura Credenciales
Antes de activar, asegúrate de tener:

**Credencial: Google API**
```
name: google_api_credentials
type: OAuth2 / Service Account
access: 
  - Gmail API (lectura/escritura)
  - Google Drive API (lectura)
  - Google Generative AI API (embeddings + Gemini)
```

---

## 🔧 Pasos de Configuración

### Nodo 1: Gmail Trigger ✉️
```json
{
  "triggerOn": "newEmail",
  "credentials": "google_api_credentials"
}
```
**¿Qué hace?** Escucha nuevos emails en tu inbox

---

### Nodo 2: Gmail RAG Search 🔍
```json
{
  "resource": "gmailRag",
  "operation": "searchAndRespond",
  "searchFolderName": "Documentos_Seguros",
  "topK": 3,
  "customPromptContext": "Eres un asesor profesional de seguros..."
}
```

**Parámetros importantes:**
- `searchFolderName`: Carpeta en Drive donde están tus documentos
  - Ej: "Documentos_Seguros", "Seguros", o vacío para todos
- `topK`: Cantidad de documentos relevantes a usar
  - 3 = balance entre velocidad y precisión
  - 5+ = más contexto pero más tokens
- `customPromptContext`: Instrucciones para Gemini
  - Define tono, rol, restricciones
  - Mejora mucho la calidad de respuestas

**¿Qué hace?** Busca documentos relevantes y genera respuesta

---

### Nodo 3: Gmail Reply ✉️
```json
{
  "resource": "message",
  "operation": "reply",
  "messageId": "email_id",
  "body": "respuesta generada"
}
```

**¿Qué hace?** Envía la respuesta al cliente

---

### Nodo 4 (Opcional): Registrar Respuesta 📊
```json
{
  "operation": "create",
  "data": [["timestamp", "cliente", "asunto", "respuesta", "confianza"]]
}
```

**¿Qué hace?** Guarda un registro de todas las respuestas para auditoría

---

## 🚀 Cómo Usar

### Primera Vez - Testing
1. No actives aún el flujo
2. Haz click en **"Test Workflow"**
3. Envía un email de prueba a tu cuenta
4. Verifica que:
   - ✓ Gmail Trigger recibe el email
   - ✓ Gmail RAG busca documentos
   - ✓ Genera respuesta correcta
   - ✓ Envía reply

### En Producción
1. Una vez validado, activa el flujo (botón toggle)
2. **El flujo escuchará automáticamente nuevos emails**
3. Responderá en tiempo real

---

## 📝 Variables Clave

```javascript
// Email ID
{{ $node['Gmail Trigger'].json.id }}

// Asunto del email
{{ $node['Gmail Trigger'].json.payload.headers
  .find(h => h.name === 'Subject')?.value }}

// De quién es el email
{{ $node['Gmail Trigger'].json.payload.headers
  .find(h => h.name === 'From')?.value }}

// Respuesta generada por RAG
{{ $node['gmail_rag_search'].json.answer }}

// Confianza de la respuesta (0-1)
{{ $node['gmail_rag_search'].json.confidence }}

// Documentos usados
{{ $node['gmail_rag_search'].json.sourcedDocuments }}
```

---

## ⚙️ Personalización

### Cambiar Carpeta de Documentos
En nodo "Buscar en Documentos RAG":
```
searchFolderName: "Tu_Carpeta_Name"
```

### Cambiar Tono de Respuesta
En nodo "Buscar en Documentos RAG", edita:
```
customPromptContext: "Tu nuevo contexto aquí..."
```

**Ejemplos:**
- Profesional: "Eres un asesor experto en seguros"
- Amigable: "Eres un amigo que ayuda con seguros"
- Legal: "Proporciona asesoramiento basado únicamente..."

### Agregar Más Documentos
1. Sube nuevos archivos a tu carpeta en Drive
2. El flujo automáticamente los encontrará
3. Sin cambiar configuración

### Cambiar Número de Documentos
En nodo "Buscar en Documentos RAG":
```
topK: 5  // Usa 5 documentos en lugar de 3
```

---

## 🎯 Casos de Uso

### 1. Preguntas Sobre Requisitos
```
Cliente: "¿Necesito comprobante de ingresos?"
RAG busca: Requisitos_Contratacion.md
Responde: "Según tu ramo, necesitas..."
```

### 2. Consultas de Cobertura
```
Cliente: "¿Cubre robo?"
RAG busca: Coberturas_por_Ramo.md
Responde: "Sí, la cobertura de robo incluye..."
```

### 3. Cómo Reclamar
```
Cliente: "¿Cómo reclamo?"
RAG busca: Proceso_Reclamos.md
Responde: "Para reclamar necesitas: 1) Notificar en 48hs..."
```

---

## 🐛 Solución de Problemas

### "No encuentra documentos"
- [ ] Verifica que los archivos están en Drive
- [ ] Comprueba que `searchFolderName` es correcto
- [ ] Los archivos deben ser TXT o Markdown

### "Respuesta genérica"
- [ ] Mejora tus documentos (más detalle, estructura)
- [ ] Aumenta `topK` a 5 o 6
- [ ] Edita `customPromptContext` con instrucciones específicas

### "No envía respuestas"
- [ ] Verifica credenciales de Gmail
- [ ] Comprueba que el email llegó al Trigger
- [ ] Revisa logs del flujo para errores

### "Responde de más"
- [ ] Reduce `topK` a 2
- [ ] Edita contexto para ser más conciso
- [ ] Agrega al contexto: "Responde en máximo 3 párrafos"

---

## 📊 Monitoreo

### Ver Ejecuciones
- Panel "Executions" en n8n
- Cada respuesta generada aparece registrada
- Puedes ver qué documentos se usaron

### Métricas Útiles
- **Execution Time**: Cuánto tarda generar respuesta
- **Confidence**: Cuán relevante es la respuesta
- **Documents Used**: Cuáles documentos se consultaron

### Mejoras Basadas en Ejecuciones
1. Mira las respuestas generadas
2. Si son malas: mejora documentos o contexto
3. Si son buenas: mantén configuración

---

## 🔐 Seguridad

### Cuidado
- ⚠️ No compartas credenciales de Google
- ⚠️ Los emails se procesan pero no se almacenan
- ⚠️ Mantén API keys privadas

### Buenas Prácticas
- ✅ Usa service account si es posible
- ✅ Limita permisos a lo necesario
- ✅ Revisa logs regularmente
- ✅ Archiva respuestas para auditoría

---

## 📈 Optimización Futura

Una vez funcionando, considera:

1. **Base de Datos de Embeddings**
   - Guarda embeddings calculados
   - Búsquedas más rápidas
   - Menos costo en API

2. **Filtros Inteligentes**
   - Clasificar emails por asunto
   - Ruteos a diferentes equipos
   - Escalada manual si es necesario

3. **Análisis de Feedback**
   - ¿Cliente quedó satisfecho?
   - Mejorar respuestas basado en feedback
   - Identificar documentos faltantes

4. **Multi-idioma**
   - Procesar emails en varios idiomas
   - Responder en idioma del cliente

---

## 📞 Support

Si necesitas ayuda:
1. Revisa los documentos en Drive
2. Edita el `customPromptContext`
3. Ajusta parámetros del RAG
4. Contacta al equipo de Productores Toral

**Happy Automating! 🚀**

# Gmail RAG Node

Búsqueda inteligente en documentos y generación de respuestas automáticas para emails usando RAG (Retrieval-Augmented Generation).

## Funcionalidad

Este nodo permite crear flujos de trabajo que:

1. **Escuchan emails en Gmail**
2. **Buscan información relevante en documentos de Google Drive**
3. **Generan respuestas automáticas usando Gemini basadas en tu documentación específica**
4. **Envían respuestas por Gmail automáticamente**

## Ventajas

- ✅ Respuestas personalizadas basadas en tus documentos (pólizas, requisitos, etc.)
- ✅ Uso eficiente de tokens (busca solo documentos relevantes)
- ✅ No requiere indexación previa (genera embeddings en tiempo real)
- ✅ Integrado con Google APIs

## Operaciones

### 1. Search and Respond

Procesa un email, busca en documentos relevantes y genera una respuesta automática.

**Parámetros:**
- `emailId`: ID del email a procesar (desde Gmail Trigger)
- `queryText`: Texto a buscar (opcional - si está vacío, usa el asunto del email)
- `searchFolderName`: Patrón de nombre de carpeta en Drive (ej: "Documentos_Seguros")
- `topK`: Cantidad de documentos relevantes a usar (default: 3)
- `customPromptContext`: Instrucciones personalizadas para Gemini
- `includeSources`: Si incluir documentos fuente en la respuesta

**Salida:**
```json
{
  "success": true,
  "answer": "Respuesta generada por Gemini...",
  "sourcedDocuments": [
    {
      "documentId": "...",
      "fileName": "Requisitos_Contratacion.md",
      "relevanceScore": 0.95,
      "snippet": "..."
    }
  ],
  "confidence": 0.95
}
```

### 2. Index Documents

Indexa documentos de Google Drive generando embeddings para búsqueda rápida.

**Parámetros:**
- `folderNamePattern`: Patrón para filtrar documentos
- `rebuildIndex`: Regenerar todos los embeddings

**Salida:**
```json
{
  "success": true,
  "indexed": 4,
  "total": 4,
  "message": "Successfully indexed 4 documents"
}
```

## Ejemplo de Flujo

```
Gmail Trigger (Nuevos emails)
    ↓
Gmail RAG (Search and Respond)
    │
    ├─ Lee email de cliente
    ├─ Busca en Requisitos_Contratacion.md
    ├─ Busca en Coberturas_por_Ramo.md
    ├─ Busca en Proceso_Reclamos.md
    ├─ Genera respuesta con Gemini
    │
    ↓
Gmail (Send Reply)
    └─ Envía respuesta automática
```

## Configuración Requerida

### Credenciales

Requiere credenciales de Google API con acceso a:
- **Gmail API**: Para leer/enviar emails
- **Google Drive API**: Para leer documentos
- **Google Generative AI API**: Para embeddings y Gemini

### Documentos en Drive

Prepara documentos en Google Drive que contengan:
- Pólizas de seguros
- Términos y condiciones
- Requisitos de contratación
- Procesos de reclamos
- Información de coberturas

## Casos de Uso

### 1. Atención al Cliente Automática
- Cliente pregunta sobre requisitos de contratación
- El nodo busca en tu documento "Requisitos_Contratacion.md"
- Genera respuesta personalizada automáticamente

### 2. Respuestas a Consultas de Pólizas
- Cliente consulta cobertura específica
- Busca en "Coberturas_por_Ramo.md"
- Responde con información exacta de tu servicio

### 3. Orientación en Procesos de Reclamo
- Cliente pregunta cómo reclamar
- Busca en "Proceso_Reclamos.md"
- Proporciona pasos específicos según su ramo

## Limitaciones y Consideraciones

- Requiere documentos en formato texto (TXT, Markdown) en Google Drive
- Las respuestas son tan buenas como los documentos indexados
- Requiere credenciales válidas de Google APIs
- El costo depende de:
  - Cantidad de caracteres procesados por Gemini
  - Cantidad de embeddings generados

## Solución de Problemas

### "No documents found"
- Verifica que tienes documentos en Google Drive
- Comprueba que los documentos son formato texto
- Valida el patrón de búsqueda de carpeta

### "Failed to query Gemini"
- Verifica que la API Key de Google está configurada
- Comprueba límites de uso de Gemini API
- Asegúrate de tener el plan correcto en Google Cloud

### Respuestas imprecisas
- Mejora la calidad y claridad de tus documentos
- Usa instrucciones más específicas en `customPromptContext`
- Aumenta `topK` para usar más documentos como contexto

## Próximas Mejoras

- [ ] Almacenamiento persistente de embeddings
- [ ] Búsqueda multi-idioma
- [ ] Integración con bases de datos vectoriales (Pinecone, Weaviate)
- [ ] Feedback loop para mejorar respuestas
- [ ] Soporte para documentos PDF

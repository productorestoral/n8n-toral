# 📊 Diagrama del Flujo Gmail RAG

## Flujo Completo - Vista General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  SISTEMA AUTOMÁTICO DE ASESORAMIENTO                        │
└─────────────────────────────────────────────────────────────────────────────┘

                              📧 CLIENTE
                                 │
                    ┌────────────┴────────────┐
                    │  "¿Qué documentos      │
                    │   necesito?"           │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Gmail Trigger        │
                    │   Escucha emails       │
                    │   en inbox             │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────────────────────────┐
                    │                                              │
                    │        Gmail RAG - Procesa Consulta          │
                    │   ┌──────────────────────────────────────┐  │
                    │   │ 1. Lee email del cliente             │  │
                    │   │ 2. Extrae pregunta                   │  │
                    │   │ 3. Genera embedding de pregunta      │  │
                    │   │ 4. Busca en Google Drive             │  │
                    │   │ 5. Carga documentos:                 │  │
                    │   │    - Requisitos_Contratacion.md      │  │
                    │   │    - Coberturas_por_Ramo.md          │  │
                    │   │    - Deducibles_Limites.md           │  │
                    │   │    - Proceso_Reclamos.md             │  │
                    │   │ 6. Genera embeddings de docs         │  │
                    │   │ 7. Busca docs relevantes (top-k)     │  │
                    │   │ 8. Envía a Gemini con contexto       │  │
                    │   │ 9. Genera respuesta personalizada    │  │
                    │   └──────────────────────────────────────┘  │
                    └────────────┬────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  Gmail Reply            │
                    │  Envía respuesta        │
                    │  al cliente             │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │ Registrar en Drive/BD   │
                    │ (Auditoría opcional)    │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │      ✅ RESPUESTA      │
                    │    AUTOMÁTICA ENVIADA   │
                    └────────────────────────┘
```

---

## Detalles Técnicos

### Búsqueda Semántica (RAG)

```
                    PREGUNTA DEL CLIENTE
                           │
                           ▼
            ┌──────────────────────────────┐
            │ Google Generative AI API     │
            │ Genera embedding             │
            │ (vector de 768 dimensiones)  │
            └──────────────┬───────────────┘
                           │
                    ┌──────▼──────┐
                    │  EMBEDDING   │
                    │ [0.23,0.45,] │
                    │  [0.12,...  ]│
                    └──────┬──────┘
                           │
      ┌────────────────────┼────────────────────┐
      │                    │                    │
      ▼                    ▼                    ▼
   DOC 1              DOC 2                 DOC 3
 Requisitos        Coberturas            Deducibles
      │                  │                    │
      │ Embedding        │ Embedding         │ Embedding
      ▼                  ▼                    ▼
   [0.21..]          [0.89..]             [0.15..]
      │                  │                    │
      └────────────────────┬────────────────────┘
                           │
              ┌────────────▼─────────────┐
              │  Cosine Similarity       │
              │  Calcula relevancia      │
              │  de cada documento       │
              └────────────┬─────────────┘
                           │
              ┌────────────▼──────────────┐
              │  Ranking Top-K            │
              │  Toma los 3 mejores       │
              │  1. Requisitos (0.89)     │
              │  2. Coberturas (0.76)     │
              │  3. Deducibles (0.65)     │
              └────────────┬──────────────┘
                           │
              ┌────────────▼──────────────┐
              │  Construye Contexto       │
              │  para Gemini              │
              └────────────┬──────────────┘
                           │
              ┌────────────▼──────────────┐
              │  Gemini LLM               │
              │  Con instrucciones:       │
              │  "Eres asesor de         │
              │   seguros..."             │
              │  + Contexto de docs       │
              │  + Pregunta del cliente   │
              └────────────┬──────────────┘
                           │
              ┌────────────▼──────────────┐
              │  Genera Respuesta         │
              │  Personalizada y         │
              │  Precisa                  │
              └──────────────────────────┘
```

---

## Flujo de Datos

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INPUT: EMAIL LLEGA                              │
│  To: productores.toral@gmail.com                                        │
│  From: cliente@example.com                                              │
│  Subject: ¿Qué documentos necesito para hogar?                         │
│  Body: Quiero asegurar mi departamento...                              │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                    PASO 1: TRIGGER
                           │
┌──────────────────────────▼──────────────────────────────────────────────┐
│  Gmail Trigger                                                           │
│  ├─ ID: msg_123456                                                      │
│  ├─ ThreadID: thread_789                                                │
│  ├─ From: cliente@example.com                                           │
│  ├─ Subject: ¿Qué documentos necesito para hogar?                      │
│  └─ Body: Quiero asegurar mi departamento...                           │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                    PASO 2: BUSCAR
                           │
┌──────────────────────────▼──────────────────────────────────────────────┐
│  Gmail RAG - Search and Respond                                          │
│                                                                          │
│  📄 Documentos Encontrados:                                             │
│  ├─ Requisitos_Contratacion.md (0.89 relevancia)                       │
│  │  └─ "Para Hogar necesitas: DNI/CUIT, escritura..."                 │
│  ├─ Coberturas_por_Ramo.md (0.76 relevancia)                           │
│  │  └─ "Hogar incluye: incendio, robo, daños por agua..."             │
│  └─ Deducibles_Limites.md (0.65 relevancia)                            │
│     └─ "Hogar Meridional: deducible 3%, límite $500k..."              │
│                                                                          │
│  🤖 Respuesta Generada:                                                 │
│  "Estimado cliente,                                                      │
│   Para contratar un seguro de hogar en Productores Toral necesitas:    │
│                                                                          │
│   DOCUMENTACIÓN REQUERIDA:                                              │
│   • DNI o CUIT                                                           │
│   • Comprobante de propiedad (escritura o contrato)                     │
│   • Fotos interiores y exteriores                                        │
│   • Comprobante de domicilio                                             │
│                                                                          │
│   INFORMACIÓN NECESARIA:                                                │
│   • Tipo de construcción                                                │
│   • Valor del inmueble                                                  │
│   • Año de construcción                                                 │
│   • Coberturas deseadas (incendio, robo, etc.)                         │
│                                                                          │
│   TIEMPO ESTIMADO: 2-5 días hábiles                                     │
│                                                                          │
│   Para más detalles, nos contactamos directamente.                      │
│   Atentamente,                                                           │
│   Productores Toral"                                                     │
│                                                                          │
│  📊 Confianza: 0.89 (89%)                                               │
│  📚 Documentos usados: 3                                                │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                    PASO 3: RESPONDER
                           │
┌──────────────────────────▼──────────────────────────────────────────────┐
│  Gmail Reply                                                             │
│  Envía respuesta al cliente vía email                                   │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                    PASO 4: REGISTRAR
                           │
┌──────────────────────────▼──────────────────────────────────────────────┐
│  Log/Auditoría (Opcional)                                               │
│  ├─ Timestamp: 2026-08-18 14:30:00                                      │
│  ├─ Cliente: cliente@example.com                                        │
│  ├─ Asunto: ¿Qué documentos necesito para hogar?                      │
│  ├─ Respuesta: [respuesta completa]                                     │
│  ├─ Confianza: 0.89                                                     │
│  └─ Docs usados: Requisitos, Coberturas, Deducibles                    │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                    OUTPUT: EMAIL ENVIADO
                           │
                           ▼
                    ✅ EXITOSO
```

---

## Alternativas de Flujo

### Opción A: Con Validación Manual
```
Trigger → RAG → Validación Manual → Reply
                (humano revisa)
```
Uso: Para consultas complejas o sensibles

### Opción B: Con Clasificación
```
Trigger → Clasificar Email → 
  ├─ Tipo A: Auto-reply con RAG
  ├─ Tipo B: Escalar a equipo
  └─ Tipo C: Request de callback
```
Uso: Diferentes tipos de consultas

### Opción C: Con Feedback Loop
```
Trigger → RAG → Reply → 
  ↓
  Cliente valida respuesta
  ↓
  Feedback → Mejora documentos
```
Uso: Mejora continua del sistema

---

## Performance Expected

| Métrica | Valor |
|---------|-------|
| Tiempo total | 30-60 seg |
| Lectura email | 2 seg |
| Búsqueda RAG | 15-20 seg |
| Generación Gemini | 10-30 seg |
| Envío reply | 2 seg |
| **Total** | **~60 seg** |

---

## Costo API Estimado

Por email procesado:
- **Google Drive API**: ~$0.0001 (negligible)
- **Google Embeddings**: ~$0.002 (por documento)
- **Gemini API**: ~$0.01-0.03 (por respuesta)
- **Gmail API**: Free

**Por 100 emails/día: ~$2-5/día (~$60-150/mes)**

---

## Próximos Pasos

1. ✅ Flujo creado
2. ⏳ Importar en n8n
3. ⏳ Configurar credenciales
4. ⏳ Testing con email real
5. ⏳ Activar en producción

# Razonador de Tierra

Tierra puede usar cualquier servicio con API de chat compatible con OpenAI (OpenAI, y muchos otros proveedores o servidores locales).
Sin configuración, Tierra usa el razonador nulo y solo reutiliza fichas verificadas del Libro.

## Variables de entorno
- `MUNDO_MENTAL_API_KEY`: la clave. Nunca se escribe en archivos del repositorio.
- `MUNDO_MENTAL_MODELO`: nombre del modelo.
- `MUNDO_MENTAL_API_URL`: opcional. Por defecto `https://api.openai.com/v1`. Debe ser https (o localhost).

Si falta la clave o el modelo, `crear_razonador()` devuelve el razonador nulo.

## Garantías
- El código que propone el modelo sigue pasando por el Verificador y requiere aprobación humana.
- Cada instancia tiene un tope de llamadas (50 por defecto).
- Los errores se resumen en un código (`http_401`, `red`, `respuesta_invalida`, `presupuesto_agotado`); la clave nunca aparece en ellos.
- Los tests no hacen llamadas de red: usan un envío simulado.

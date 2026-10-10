# Ciudad Mental visual

Abre una ciudad gráfica local con:

```bash
python mundo.py
```

No necesita dependencias externas: usa Tkinter, incluido habitualmente con Python. La ventana muestra la Ciudad estable, sus rutas declaradas, los Aspectos como habitantes, actividad reciente e inspección por clic.

## Diseño

- La Ciudad estable contiene Biblioteca, Corazón, Observación y Calles.
- El Portal no es un laboratorio: conduce a Universos de Experimentación separados que se implementarán como espacios autorizados por Curiosidad.
- El botón **Simular pulso** genera actividad demostrativa visible sin alterar la memoria persistente del proyecto.
- El modelo `CiudadMental` mantiene los eventos en memoria y es comprobable sin abrir interfaz gráfica.

Esta primera versión visualiza una ciudad viva y sus fronteras. Las siguientes iteraciones conectarán los eventos reales de los Aspectos y los Universos de Experimentación al mismo flujo de actividad.

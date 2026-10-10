# Biblioteca 0.2

La Biblioteca ya no es solo una carpeta que acumula datos. Tiene tres clases de memoria:

- **Episódica:** conserva experiencias concretas: qué entró, qué se respondió y qué ocurrió.
- **Semántica:** consolida varias experiencias bajo conceptos generales.
- **Procedimental:** guarda habilidades y versiones anteriores de cada Casa.

## Ciclo de un recuerdo

1. Una experiencia entra en la Hemeroteca episódica.
2. Se calculan su novedad, sorpresa e importancia.
3. Cuando se busca un recuerdo, la Biblioteca combina parecido, importancia y éxito.
4. La recuperación incluye una explicación legible.
5. Al consolidar, varios episodios forman un concepto sin destruir los originales.
6. Al depurar, los duplicados se fusionan y los recuerdos protegidos sobreviven.

## Salas físicas

Dentro de `.mente/` se crean:

```text
experiencias.jsonl              Hemeroteca episódica
conceptos.json                  Sala semántica
obras.jsonl                     Archivo urbanístico
habilidades/*.json              Habilidades actuales
habilidades/versiones/*.json    Versiones antiguas restaurables
planos/                          Mapoteca futura
```

## Operaciones principales

```python
biblioteca.recordar(...)
biblioteca.buscar_similares(...)
biblioteca.consolidar()
biblioteca.depurar(max_recuerdos=1000)
biblioteca.guardar_habilidad(...)
biblioteca.consultar_obras(...)
biblioteca.estado()
```

## Seguridad

La depuración nunca elimina un recuerdo marcado como protegido para cumplir un límite. Si existen más recuerdos protegidos que el límite solicitado, se conservan todos. Las habilidades anteriores se archivan antes de sobrescribir la versión activa.

## Diseño de escala: libros y estanterías

Una Biblioteca con millones de recuerdos no debe revisar todos sus episodios para responder una consulta. Los recuerdos se agruparán físicamente en **Libros** de tamaño limitado y se localizarán mediante un catálogo jerárquico cargado bajo demanda.

```text
Catálogo maestro
├── Estantería temporal: 2026-10
│   ├── Libro 2026-10-10/0001
│   └── Libro 2026-10-10/0002
├── Estantería temática: patrones
│   ├── referencias al libro 0001
│   └── referencias al libro 0142
└── Estantería de origen: curiosidad
    └── referencias a sus experimentos
```

Un episodio tendrá un único cuerpo canónico. Podrá aparecer en muchas estanterías mediante referencias ligeras, evitando duplicar el recuerdo completo. El tiempo será una partición física estable; tema, origen, importancia, rareza y relaciones serán rutas lógicas adicionales.

### Catalogador mecánico

El **Catalogador** será un auxiliar algorítmico sin identidad, deseos, autobiografía ni autoridad interpretativa. No será un Aspecto Mental ni competirá con la personalidad de la Biblioteca.

Sus responsabilidades serán:

- Cerrar un Libro cuando alcance su límite de tamaño o tiempo.
- Crear y nombrar estanterías conforme a reglas deterministas.
- Mantener índices por tiempo, tema, origen, tipo, importancia y huellas estructurales.
- Escribir al final de cada Libro un manifiesto que describa su contenido.
- Actualizar el catálogo de la estantería sin cargar todos los recuerdos.
- Verificar que cada referencia apunta a un recuerdo existente.
- Reconstruir cualquier índice a partir de los Libros canónicos.
- Avisar a la Biblioteca cuando una clasificación sea ambigua; nunca inventar significado.

La Biblioteca conserva la decisión semántica: interpreta, relaciona, consolida y explica. El Catalogador solamente coloca señales fiables para que ella llegue rápidamente a la zona adecuada.

### Índices en capas

La búsqueda seguirá una ruta de embudo:

```text
consulta
   ↓
catálogo maestro: selecciona estanterías
   ↓
catálogos de estantería: seleccionan Libros
   ↓
manifiestos de Libro: seleccionan páginas o bloques
   ↓
Biblioteca: lee y comprende los recuerdos candidatos
   ↓
respuesta explicada
```

Cada capa contendrá información más concreta que la anterior, pero ninguna necesitará permanecer completa en memoria. El sistema operativo y SQLite podrán mantener calientes únicamente las páginas consultadas con frecuencia.

### Manifiesto de Libro

Cuando se cierre un Libro se generará un manifiesto inmutable con:

- Identificador, versión y rango temporal.
- Cantidad de recuerdos y tamaño físico.
- Temas principales y secundarios.
- Aspectos de origen y destinos relacionados.
- Rangos de importancia, novedad y confianza.
- Tipos de experiencia y conceptos mencionados.
- Huellas compactas para preselección por similitud.
- Posición de cada recuerdo o bloque.
- Hashes para detectar corrupción.
- Enlace al Libro anterior y al siguiente de la serie.

El manifiesto es el “libro sobre el Libro”: permite decidir si vale la pena abrirlo y dónde mirar, sin recordar permanentemente su contenido.

### Rutas múltiples

Una clasificación única sería demasiado rígida. El mismo recuerdo puede recuperarse por:

- **Cuándo:** día, periodo o secuencia autobiográfica.
- **De qué trata:** temas y conceptos.
- **Quién lo produjo:** Aspecto, Casa o experimento.
- **Para qué sirve:** habilidad, problema o decisión.
- **Qué carácter tiene:** éxito, error, contradicción, sorpresa o anomalía.
- **Con qué se relaciona:** enlaces explícitos y huellas de similitud.

Estas rutas almacenarán identificadores y puntuaciones, no copias del episodio. Si una clasificación cambia, se modifica el índice, no el recuerdo histórico.

### Búsqueda estratégica

La recuperación tendrá dos fases:

1. **Localización mecánica:** el Catalogador y sus índices reducen millones de recuerdos a un conjunto pequeño de candidatos.
2. **Comprensión mental:** la Biblioteca evalúa esos candidatos usando contexto, importancia, identidad, relaciones y propósito actual.

La primera fase debe ser rápida y reconstruible. La segunda puede ser más rica y costosa porque trabaja sobre decenas de recuerdos, no sobre millones.

### Estanterías terminadas

Una estantería cerrada tendrá un catálogo propio, inmutable y verificable. El catálogo maestro solo necesitará conservar un resumen pequeño de cada estantería:

```text
estantería: patrones/alternancia
periodo: 2026-10-01..2026-10-31
libros: 38
recuerdos: 24 182
temas: alternancia, periodicidad, simetría
orígenes: biblioteca, curiosidad, casa_patrones
rareza_máxima: 0.97
ruta_catalogo: catalogos/patrones-alternancia-2026-10.idx
hash: ...
```

Al seleccionar esa estantería, se carga su catálogo; al terminar la búsqueda, puede salir de memoria. Ningún agente necesita memorizar la ubicación de cada recuerdo.

### Vestíbulo y archivo

Los recuerdos nuevos vivirán primero en un **Vestíbulo** pequeño y mutable. Allí todavía pueden corregirse metadatos, recibir nuevas relaciones o fusionarse con duplicados. Al alcanzar suficiente estabilidad se escriben en un Libro cerrado y pasan a las Salas o al Archivo profundo.

```text
experiencia → Vestíbulo → Libro abierto → Libro sellado
                                  ├── Salas activas
                                  └── Archivo profundo
```

Los Libros sellados no se reescriben por cambios ordinarios. Las correcciones se representan mediante nuevos registros y referencias, facilitando auditoría, copias incrementales y recuperación.

### Fallos y reconstrucción

Los recuerdos son la fuente de verdad; los índices son mapas reemplazables. Si un catálogo se corrompe:

1. Se aísla el índice dañado.
2. Los Libros permanecen intactos.
3. El Catalogador relee manifiestos o Libros afectados.
4. Reconstruye solamente las rutas perdidas.
5. Compara hashes y recuentos.
6. Publica el catálogo nuevo de forma atómica.

Esta separación impide que una optimización de búsqueda se convierta en propietaria de la memoria.

### Riesgos a medir

El diseño no se promoverá sin medir:

- Coste de catalogar un recuerdo nuevo.
- Tiempo para cerrar y manifestar un Libro.
- Tamaño total de índices y referencias.
- Calidad de recuperación frente a búsqueda exhaustiva.
- Recuerdos relevantes omitidos por una mala clasificación.
- Tiempo de reconstrucción tras corrupción.
- Coste de recuerdos pertenecientes a muchos temas.
- Degradación cuando una estantería domina el catálogo.
- Latencia con catálogos fríos y calientes.

La regla de identidad se mantiene: el Catalogador puede ordenar, pero solo la Biblioteca puede interpretar el significado de lo guardado.

# Biblioteca 0.5 experimental

La Biblioteca mantiene tres memorias —episódica, semántica y procedimental— y añade una arquitectura interna preparada para crecer sin perder su identidad. Ella conserva la autoridad de interpretar; el Catalogador solo localiza.

## Pacto interno

```text
experiencia
   ↓
Biblioteca decide recordarla
   ↓
memoria canónica conserva el cuerpo
   ↓
Catalogador crea rutas y manifiestos
   ↓
consulta futura
   ↓
Catalogador señala candidatos
   ↓
Biblioteca comprende, ordena y explica
```

El contrato `PuertoCatalogo` desacopla ambas funciones. Un catálogo futuro podrá usar nuevas estructuras, índices vectoriales o archivos distribuidos sin obligar a reescribir la personalidad, la consolidación ni las explicaciones de la Biblioteca.

## Catalogador 0.2

El Catalogador sigue siendo un órgano mecánico, no un Aspecto independiente. No posee deseos, identidad, autobiografía ni autoridad semántica. Su trabajo es hacer posible que la Biblioteca piense a escala.

Ahora puede:

- Agrupar recuerdos canónicos en Libros limitados.
- Mantener rutas por estructura, categoría, origen y tema.
- Actualizar manifiestos incrementalmente sin releer el Libro completo tras cada llegada.
- Sellar Libros completos.
- Localizar un presupuesto pequeño de candidatos.
- Verificar referencias, recuentos y hashes de manifiestos.
- Reconstruirse completamente desde los recuerdos canónicos.
- Ser sustituido mediante un contrato estable.

## Recuperación segura

La recuperación ocurre en dos fases:

1. El Catalogador reduce el espacio de búsqueda.
2. La Biblioteca interpreta y puntúa los candidatos.

Si el catálogo no devuelve candidatos o sufre una corrupción recuperable, la Biblioteca degrada temporalmente a búsqueda exhaustiva. Será más lenta, pero no fingirá haber olvidado. Cada búsqueda deja un diagnóstico con estrategia, universo total, presupuesto, candidatos localizados, recuerdos comprendidos y motivo de degradación.

```python
recuerdos = biblioteca.buscar_similares(entrada)
diagnostico = biblioteca.diagnostico_ultima_busqueda()
```

## Fuente de verdad

Los episodios son la memoria canónica. Libros, ubicaciones, términos y manifiestos son mapas reconstruibles. Una optimización nunca se convierte silenciosamente en propietaria del recuerdo.

Cada episodio tiene un único cuerpo, aunque múltiples rutas puedan apuntar a él. Esto permite encontrarlo por tiempo, patrón, concepto, origen o tema sin duplicar su contenido.

## Salas actuales

```text
biblioteca.sqlite3              Memoria canónica, catálogo y conceptos
habilidades/*.json              Habilidades actuales
habilidades/versiones/*.json    Versiones restaurables
planos/                          Mapoteca futura
autobiografias/                 Continuidad de los Aspectos
```

## Límites conocidos

- La consolidación todavía relee todos los episodios.
- La depuración todavía reconstruye la memoria episódica completa.
- El índice estructural actual está pensado para secuencias discretas, no para lenguaje o imágenes.
- SQLite mantiene un único escritor simultáneo.
- Una preselección rápida puede omitir recuerdos relevantes; la calidad debe compararse siempre con búsqueda exhaustiva.
- El fallback exhaustivo protege la memoria, pero no será barato a gran escala.

## Próximas pruebas

Viabilidad 0.3 medirá por separado:

- Coste de guardar el recuerdo canónico y coste de catalogarlo.
- Latencia de búsqueda catalogada y exhaustiva.
- Fracción de episodios que la Biblioteca necesita comprender.
- Coincidencia entre los mejores resultados de ambas estrategias.
- Coste de construir, verificar y reconstruir el catálogo.
- Comportamiento con índices vacíos, dañados, fríos y calientes.
- Tamaño de memoria canónica, rutas y manifiestos.

El éxito no será solo responder más rápido. También deberá conservar recuerdos raros, explicar la recuperación y permitir que la Biblioteca siga siendo una identidad coherente en lugar de convertirse en una envoltura decorativa de una base de datos.

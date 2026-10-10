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

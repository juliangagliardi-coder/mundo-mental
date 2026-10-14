# Autoridad

Regla acordada: **no existen acciones irreversibles**.

1. Toda acción se ejecuta con una forma de deshacerla.
2. Si falla, se revierte y Observación recibe una alarma. Sin reversa, la alarma es grave y se congela la zona.
3. Las zonas protegidas (`constitucion`, `guardian`, `centinela`, `copias_protegidas`) se bloquean y se congelan.
4. Un desacuerdo entre Aspectos no detiene el trabajo: se anota como deuda y se salda con una nota.
5. Todo queda en `autoridad/registro.jsonl`, solo de añadir.

Implementación: `mundo_mental/autoridad.py`. Pruebas: `tests/test_autoridad.py`.

## Reformas del Corazón

`mundo_mental/reforma.py` hace latir al Corazón a través de la Autoridad. Antes de latir guarda la habilidad vigente; si algo falla, la restaura con `guardar_habilidad`, que archiva la versión reemplazada, de modo que revertir tampoco pierde nada. Una reforma sobre una zona protegida ni siquiera llega a ejecutarse. Pruebas: `tests/test_reforma.py`.

## Ciclo integrado

En `iniciar.py`, la validación de evidencia pasa por la Autoridad. Antes de validar se guarda `experiencias.jsonl`; si el paso falla, la reversa lo restaura. El resultado del ciclo incluye la clave `decision`. Prueba: `tests/test_ciclo_autoridad.py`.

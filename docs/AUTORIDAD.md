# Autoridad

Regla acordada: **no existen acciones irreversibles**.

1. Toda acción se ejecuta con una forma de deshacerla.
2. Si falla, se revierte y Observación recibe una alarma. Sin reversa, la alarma es grave y se congela la zona.
3. Las zonas protegidas (`constitucion`, `guardian`, `centinela`, `copias_protegidas`) se bloquean y se congelan.
4. Un desacuerdo entre Aspectos no detiene el trabajo: se anota como deuda y se salda con una nota.
5. Todo queda en `autoridad/registro.jsonl`, solo de añadir.

Implementación: `mundo_mental/autoridad.py`. Pruebas: `tests/test_autoridad.py`.

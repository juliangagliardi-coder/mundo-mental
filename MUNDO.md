# Monitor gráfico del trabajo real

Esto no es un juego ni una animación con tareas inventadas. Es una interfaz Tkinter que ejecuta el ciclo integrado de `iniciar.py` y transforma su telemetría en actividad visual.

## Abrirlo

Primero entra en la rama que contiene el monitor:

```bash
git fetch origin
git switch evolucion/ciudad-visual-01
```

Comprueba que estás en la carpeta correcta:

```bash
# Windows
 dir mundo.py

# macOS o Linux
ls mundo.py
```

Si el comando muestra `mundo.py`, ábrelo así:

```bash
# Windows
py mundo.py

# macOS o Linux
python3 mundo.py
```

## Qué ocurre realmente

Al pulsar **Ejecutar un ciclo**, la aplicación llama al ciclo integrado real en un directorio temporal:

1. Curiosidad examina conceptos, formula una pregunta y ejecuta un experimento aislado.
2. El validador comprueba reproducibilidad y corroboración; si acepta la evidencia, Biblioteca escribe el recuerdo temporal.
3. Guardián recibe una alarma, aísla el laboratorio, verifica la recuperación y lo reanuda.
4. La ventana recibe esos eventos mediante un observador y destaca al personaje correspondiente.

Catalogador y Corazón permanecen visualmente presentes pero en espera porque el ciclo integrado actual no los llama. La interfaz lo muestra así en lugar de fingir trabajo.

## Controles

- **Ejecutar un ciclo:** ejecuta una vez el ciclo real.
- **Trabajar continuamente:** repite ciclos reales en espacios temporales independientes.
- **Detener:** solicita detenerse después de la operación en curso.
- **Clic en un personaje:** muestra su estado y última actividad.
- **Botón derecho y arrastrar:** mueve la cámara.
- **Rueda del ratón:** cambia el zoom.

## Diagnóstico

Si aparece `No module named tkinter`, falta el componente gráfico de Python. En Debian o Ubuntu:

```bash
sudo apt install python3-tk
```

Si aparece `can't open file 'mundo.py'`, la terminal no está dentro de la carpeta correcta o sigues en la rama `main`. Ejecuta `git branch --show-current` y confirma que responde `evolucion/ciudad-visual-01`.

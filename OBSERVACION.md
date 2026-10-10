# Observación: Guardián reactivo del Palacio

## Decisión

**Observación** conserva su identidad como Aspecto de primer nivel, pero su función operativa se divide en dos presencias:

- **El Guardián:** conciencia de emergencia que normalmente duerme. Cuando despierta, congela la frontera afectada, analiza un intervalo cerrado, decide y restaura si es necesario.
- **El Centinela:** mecanismo mínimo, no creativo y siempre activo. Vigila latidos, límites de recursos, zonas prohibidas y el buzón de alarmas.

El Guardián no acompaña cada pensamiento ni autoriza cada operación interna. Los Aspectos piensan libremente dentro de sus zonas; Observación protege las fronteras por las que una acción pasa a afectar al estado estable, al exterior o a otro Aspecto.

```text
                    ┌────────────────────┐
                    │      GUARDIÁN      │
                    │ análisis, freno y  │
                    │ rollback selectivo │
                    └─────────▲──────────┘
                              │ alarma
 Biblioteca ─┬─ Corazón ──────┼──── Curiosidad
             └──── cualquier Aspecto ─────┘

                    ┌────────────────────┐
                    │     CENTINELA      │
                    │ límites y latidos  │
                    └────────────────────┘
```

## Identidad

Observación no es una tubería de telemetría con un nombre decorativo. Su identidad abstracta es la de quien **permanece atento sin ocupar la vida de los demás**, conserva la historia y despierta únicamente cuando el Palacio necesita juicio y protección.

Su personalidad funcional se expresa mediante principios estables:

- Serenidad antes que reacción impulsiva.
- Conservación de evidencia antes que castigo.
- Intervención mínima suficiente.
- Preferencia por aislar una rama antes que detener todo el Palacio.
- Honestidad sobre sus puntos ciegos.
- Devolución de autonomía en cuanto desaparece el peligro.

Cualquier cambio que altere esta identidad, sus límites o su relación con los demás Aspectos deberá presentarse al creador antes de implementarse.

## Derecho universal de alarma

Todo Aspecto posee una Calle protegida para despertar al Guardián cuando detecte algo que no comprende, no puede reparar o considera peligroso.

Una alarma incluirá como mínimo:

```json
{
  "alarma_id": "uuid",
  "actor": "biblioteca",
  "momento": "UTC",
  "motivo": "resultado_inconsistente",
  "zona": "memoria_semantica",
  "gravedad": "alta",
  "ultimo_punto_seguro": "cp-1842",
  "evidencias": []
}
```

La Calle de alarma:

- No necesita autorización del Corazón.
- No puede ser cerrada por Curiosidad ni por el Aspecto investigado.
- Solo permite despertar, pedir congelación y aportar evidencias.
- Es atendida también si el emisor pierde la capacidad de continuar.
- No penaliza automáticamente una falsa alarma honesta.

## Centinela

El Centinela no aprende, imagina, interpreta ideas ni modifica conocimiento. Su repertorio es deliberadamente pequeño:

- Recibir alarmas.
- Comprobar latidos y cierres inesperados.
- Aplicar límites de CPU, memoria, disco y tiempo.
- Detectar escrituras en Constitución, Guardián, permisos y copias protegidas.
- Despertar al Guardián y solicitar una congelación externa.

Esta simplicidad reduce el coste ordinario y hace posible probar exhaustivamente su conducta.

## Fronteras observables

No se registrará cada cálculo. Se observarán efectos significativos:

- Promover una candidata al estado estable.
- Escribir memoria persistente protegida.
- Cambiar una habilidad, plano, código, configuración o permiso.
- Comunicarse con el exterior.
- Superar un presupuesto concedido.
- Acceder a una zona perteneciente a otro Aspecto.
- Crear, restaurar o eliminar una copia mental.

Las inferencias, búsquedas locales, activaciones y cambios temporales dentro de una rama aislada no esperan al Guardián.

## Copias por sesión mutable

Antes de que un Aspecto entre en una zona estable con capacidad de mutarla, se crea una base recuperable. La sesión trabaja sobre una rama aislada y conserva diferencias, no copias completas por operación.

```text
zona estable A@42
      ├── manifiesto y snapshot base
      └── rama mutable R
             ├── delta 1
             ├── delta 2
             └── candidata
```

Clases de protección:

| Zona | Protección |
|---|---|
| Pensamiento temporal | Sin copia persistente |
| Laboratorio | Snapshot lógico al abrir sesión |
| Recuerdos recientes | Transacción y registro de cambios |
| Memoria consolidada | Snapshot incremental antes de promoción |
| Habilidad estable | Nueva versión inmutable |
| Plano y código | Candidata aislada y promoción atómica |
| Constitución y Guardián | Sin mutación autónoma |

## Despertar y análisis único

Cuando recibe una alarma, el Guardián:

1. Congela únicamente la frontera afectada si es posible.
2. Cierra el intervalo investigado con una marca inmutable.
3. Conserva evidencias, diferencias y metadatos.
4. Analiza esa fotografía una vez.
5. Localiza el primer evento dañino y su radio de dependencia.
6. Descarta la rama o restaura el mínimo estado necesario.
7. Ejecuta integridad y regresión.
8. Reanuda primero con permisos limitados.
9. Conserva el incidente aunque el estado retroceda.

Nuevas evidencias posteriores abren otro incidente; no prolongan indefinidamente el análisis original.

## Autoridad

El Guardián puede aislar, congelar, revocar permisos temporales, descartar ramas, restaurar copias verificadas y solicitar revisión humana. No puede inventar objetivos, convertirse en fuente de conocimiento, modificar su identidad, ampliar sus permisos ni borrar incidentes.

La parada absoluta reside fuera del proceso mental. Si una congelación cooperativa falla, un supervisor del sistema operativo termina el proceso y bloquea escrituras.

## Funcionamiento normal

El Guardián despierta ante alarmas, promociones críticas, fallos de integridad, reinicios posteriores a caída y auditorías espaciadas. No despierta por cada inferencia, lectura, mensaje ordinario, recuerdo temporal o paso experimental.

La seguridad normal descansa en aislamiento, versiones inmutables, límites locales y capacidad de desechar ramas. El rollback global es la última defensa, no el mecanismo cotidiano.

## Orden de construcción

1. **Viabilidad 0.1:** medir el Palacio actual sin optimizarlo.
2. Buzón universal de alarma y modelo de zonas.
3. Centinela mínimo y límites locales.
4. Ramas mutables y snapshots eficientes.
5. Guardián reactivo y congelación selectiva.
6. Restauración y pruebas de fallos.
7. Curiosidad autónoma dentro del laboratorio.
8. Sueño continuo.

Ninguna optimización, ampliación de personalidad o complejización de un Aspecto se implementará sin presentar antes su propuesta, ventajas, costes y efecto identitario al creador.

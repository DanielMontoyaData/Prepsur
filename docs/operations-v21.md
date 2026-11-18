# Operación — Laboratorio de escenarios PRO 2.1

## Modelo
El usuario registra nodos (servicios/activos), municipio, sector, criticidad, capacidad de referencia, unidad, fuente y dependencias proveedoras. Se recomienda crear primero los nodos proveedores y después los nodos dependientes para poder referenciar sus IDs.

## Escenarios
Las afectaciones se escriben como `ID=porcentaje`, una por línea. `0` representa indisponibilidad total hipotética y `40` representa 40 % de disponibilidad directa. Los nodos no afectados parten de 100 %.

## Regla de propagación
Para cada nodo, disponibilidad efectiva = disponibilidad directa × mínimo de disponibilidad efectiva de sus dependencias / 100. Todas las dependencias listadas se consideran obligatorias (regla AND/cuello de botella). No modela redundancia, rutas alternativas, inventarios, tiempos de recuperación ni relaciones físicas no ingresadas. Los ciclos y dependencias inexistentes se rechazan.

## Capacidad
Si se registra una capacidad de referencia y unidad, la capacidad efectiva se calcula multiplicando la capacidad por la disponibilidad efectiva. No se infiere demanda, población servida ni déficit de consumo.

## Fuentes y uso responsable
No hay infraestructura real precargada. Cada nodo debe incluir una referencia verificable aportada por el operador. Los escenarios son hipótesis de análisis de sensibilidad, no pronósticos, alertas, instrucciones de despacho ni evaluaciones de seguridad. No usar el resultado como sustituto de información de operadores, autoridades o validación en campo.

## CLI reproducible
```bash
python backend/scripts/simulate_service_scenario.py --input examples/scenario-nodes.example.json --override POWER=0 --name "Corte hipotético de energía" --out reports/scenario.json
```

# PREPPER MAP PRO 1.7 — Autonomía y abastecimiento

## Uso en la aplicación
En Autonomía y abastecimiento selecciona el tipo de escenario, personas atendidas y horizonte en días. Registra las reservas reales de agua (L), alimentos (kg) y energía (kWh). Ajusta consumos por persona/día y consumos adicionales colectivos. Pulsa Calcular autonomía.

La aplicación presenta consumo diario, días de autonomía estimados, cobertura del horizonte y déficit/excedente. Permite guardar hasta 50 escenarios localmente y exportar JSON o CSV.

## Cálculo por recurso
- Consumo diario = personas × consumo por persona/día + consumo adicional diario.
- Requerimiento = consumo diario × días objetivo.
- Autonomía = reserva disponible / consumo diario.
- Déficit = máximo entre cero y requerimiento menos reserva.
- Cobertura = reserva / requerimiento, limitada al 100%.

Si el consumo diario es cero, la autonomía se presenta como no calculable y no como infinita.

## Ejemplo CLI
Crea `stocks.json`:
```json
{"water":56,"food":8.4,"energy":7}
```
Crea `rates.json`:
```json
{"water":4,"food":0.6,"energy":0.5}
```
Ejecuta:
```bash
python backend/scripts/calculate_autonomy.py --people 2 --days 7 --stocks stocks.json --rates rates.json --out reports/autonomy.json
```

## Advertencias
Las tasas predeterminadas de la interfaz son parámetros editables para iniciar el cálculo, no recomendaciones universales ni estándares sanitarios. Agua requerida depende de clima, salud, higiene, preparación de alimentos y directrices locales. Los kilogramos de alimentos no representan suficiencia nutricional: se requiere revisar calorías, proteínas, micronutrientes, restricciones alimentarias y conservación. La energía se estima en kWh agregados y no comprueba potencia instantánea, voltaje, compatibilidad de equipos ni combustible. No se certifica potabilidad, inocuidad, estado de baterías o acceso físico. Registrar una reserva no implica que esté disponible o utilizable.

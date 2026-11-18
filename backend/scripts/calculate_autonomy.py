#!/usr/bin/env python3
"""Calculadora PREPPER MAP de autonomía y déficit de abastecimiento."""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

def calculate(people, days, stocks, per_person_daily, extra_daily=None):
    if isinstance(people,bool) or not isinstance(people,int) or not 1<=people<=100000:
        raise ValueError("people debe ser entero entre 1 y 100000")
    if not isinstance(days,(int,float)) or isinstance(days,bool) or not 1<=days<=365:
        raise ValueError("days debe estar entre 1 y 365")
    extra_daily=extra_daily or {}
    resources={}
    for key in ("water","food","energy"):
        stock=float(stocks.get(key,0));rate=float(per_person_daily.get(key,0));extra=float(extra_daily.get(key,0))
        if min(stock,rate,extra)<0: raise ValueError(f"Valores negativos no permitidos: {key}")
        daily=people*rate+extra
        required=daily*days
        resources[key]={"stock":stock,"daily_consumption":daily,"required_for_target":required,
          "autonomy_days":stock/daily if daily>0 else None,
          "deficit":max(0,required-stock),"surplus":max(0,stock-required),
          "coverage_percent":min(100,100*stock/required) if required>0 else 100}
    return {"application":"PREPPER MAP PRO","version":"1.7.0","created_at":datetime.now(timezone.utc).isoformat(),
      "people":people,"target_days":days,"resources":resources,
      "limitations":["Cálculo basado exclusivamente en consumos y reservas introducidos.",
        "No verifica potabilidad, inocuidad, disponibilidad física ni estado de equipos.",
        "No contempla pérdidas, desperdicio, cambios de demanda ni reabastecimiento futuro."]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--people",type=int,required=True);p.add_argument("--days",type=float,required=True)
    p.add_argument("--stocks",type=Path,required=True,help="JSON: water L, food kg, energy kWh")
    p.add_argument("--rates",type=Path,required=True,help="JSON: consumo por persona/día")
    p.add_argument("--extra",type=Path,help="JSON: consumo adicional total/día")
    p.add_argument("--out",type=Path,default=Path("reports/autonomy-v17.json"))
    a=p.parse_args()
    result=calculate(a.people,a.days,json.loads(a.stocks.read_text()),json.loads(a.rates.read_text()),
      json.loads(a.extra.read_text()) if a.extra else {})
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    for key,val in result["resources"].items():
        print(f"{key}: {val['autonomy_days'] if val['autonomy_days'] is not None else 'N/A'} días · déficit {val['deficit']}")
    print(f"Informe: {a.out}")
if __name__=="__main__": main()

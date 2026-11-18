#!/usr/bin/env python3
"""Métricas topológicas descriptivas de una red lineal OSM (no mide transitabilidad)."""
import argparse,json
from pathlib import Path
import networkx as nx
from shapely.geometry import shape,LineString,MultiLineString

def parts(g):
    if g.geom_type=="LineString":return [g]
    if g.geom_type=="MultiLineString":return list(g.geoms)
    return []
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",default="gis/routes/osm_trails.geojson");p.add_argument("--output",default="gis/routes/network_metrics.json");p.add_argument("--precision",type=int,default=5);a=p.parse_args()
    data=json.loads(Path(a.input).read_text(encoding="utf-8"));G=nx.Graph();segments=0;length=0.0
    for feat in data.get("features",[]):
        if not feat.get("geometry"):continue
        for line in parts(shape(feat["geometry"])):
            coords=list(line.coords)
            if len(coords)<2:continue
            segments+=1;length+=line.length
            for u,v in zip(coords,coords[1:]):
                key=lambda p:(round(p[0],a.precision),round(p[1],a.precision))
                x,y=key(u),key(v)
                if x!=y:G.add_edge(x,y,weight=G.get_edge_data(x,y,{}).get("weight",0)+1)
    comps=sorted((len(c) for c in nx.connected_components(G)),reverse=True)
    degree=dict(G.degree());dead=sum(1 for _,d in degree.items() if d==1);junctions=sum(1 for _,d in degree.items() if d>=3)
    report={"source":a.input,"source_attribution":"© OpenStreetMap contributors","source_license":"ODbL",
      "verification":"topology_only_not_field_verified","precision_decimal_places":a.precision,
      "metrics":{"input_line_parts":segments,"graph_nodes":G.number_of_nodes(),"graph_edges":G.number_of_edges(),
      "connected_components":len(comps),"largest_component_nodes":comps[0] if comps else 0,
      "dead_end_nodes_degree_1":dead,"junction_nodes_degree_3_or_more":junctions,
      "sum_segment_length_degrees_approx":round(length,6)},
      "warning":"Conectividad geométrica aproximada. No demuestra que los caminos conecten físicamente, estén abiertos, sean transitables o seguros; las intersecciones sin nodo compartido pueden dividir la red."}
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Métricas guardadas: {out}")
if __name__=="__main__":main()

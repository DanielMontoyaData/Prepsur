import importlib.util, unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"backend/scripts/simulate_service_scenario.py"
spec=importlib.util.spec_from_file_location("scenario_engine",P); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
class ScenarioEngineTests(unittest.TestCase):
 def setUp(self):
  self.nodes=[
   {"id":"POWER","name":"Red eléctrica","municipality":"Envigado","sector":"energia","criticality":"critica","capacity":100,"unit":"kW","dependencies":[],"source":"Fuente de prueba"},
   {"id":"PUMP","name":"Bombeo","municipality":"Envigado","sector":"agua","criticality":"critica","capacity":50,"unit":"L/s","dependencies":["POWER"],"source":"Fuente de prueba"},
   {"id":"RADIO","name":"Radio","municipality":"Itagüí","sector":"comunicaciones","criticality":"alta","capacity":20,"unit":"Mbps","dependencies":["POWER","PUMP"],"source":"Fuente de prueba"}]
 def test_cascading_dependency_and_capacity(self):
  r=mod.calculate(self.nodes,{"POWER":0})
  by={x["id"]:x for x in r["results"]}
  self.assertEqual(by["POWER"]["effective_availability_pct"],0)
  self.assertEqual(by["PUMP"]["effective_availability_pct"],0)
  self.assertEqual(by["RADIO"]["effective_availability_pct"],0)
  self.assertEqual(r["summary"]["critical_nodes_affected"],2)
 def test_derating_and_scope(self):
  r=mod.calculate(self.nodes,{"POWER":50},"Envigado")
  by={x["id"]:x for x in r["results"]}
  self.assertEqual(set(by),{"POWER","PUMP"})
  self.assertEqual(by["PUMP"]["effective_capacity"],25)
 def test_cycle_and_unknown_dependency_rejected(self):
  bad=[dict(self.nodes[0],dependencies=["PUMP"]),self.nodes[1]]
  with self.assertRaisesRegex(ValueError,"circular"): mod.calculate(bad)
  bad=[dict(self.nodes[0]),dict(self.nodes[1],dependencies=["MISSING"])]
  with self.assertRaisesRegex(ValueError,"inexistente"): mod.calculate(bad)
 def test_invalid_override_rejected(self):
  with self.assertRaises(ValueError): mod.calculate(self.nodes,{"POWER":120})
if __name__=="__main__": unittest.main()

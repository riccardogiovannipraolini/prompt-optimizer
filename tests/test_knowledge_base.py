import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("ai_optimizer", ROOT / "ai_optimizer.py")
ai_optimizer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ai_optimizer)


class KnowledgeBaseTest(unittest.TestCase):
    def setUp(self):
        self.kb = ai_optimizer.load_knowledge_base(str(ROOT))
        path = ROOT / "prompt_optimizer_knowledge_base.json"
        self.techniques = json.loads(path.read_text(encoding="utf-8"))["techniques"]

    def test_every_technique_reaches_the_model_with_its_rules(self):
        self.assertEqual(len(self.techniques), 7)
        for tech in self.techniques:
            self.assertIn(tech["name"], self.kb)
            for rule in (tech.get("transformation_rules") or {}).values():
                self.assertIn(str(rule), self.kb)

    def test_summary_table_is_included(self):
        self.assertIn("TABELLA DELLE BEST PRACTICE", self.kb)


if __name__ == "__main__":
    unittest.main()

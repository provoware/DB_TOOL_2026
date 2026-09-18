from __future__ import annotations

import unittest
from types import SimpleNamespace

from provoware_db.web.read_adapter import WebCatalogReadAdapter
from provoware_db.web.render import render_page


class FakeCatalog:
    def list_categories(self):
        return [SimpleNamespace(id="cat-1", name="Werkzeug", revision=1)]

    def list_entries(self, category_id):
        return [
            SimpleNamespace(
                id="ent-1",
                title="Akkuschrauber",
                revision=1,
                is_favorite=False,
            )
        ]

    def list_fields(self, entry_id):
        return [
            SimpleNamespace(id="f1", name="Hersteller", field_type="text", is_required=True),
            SimpleNamespace(id="f2", name="Zustand", field_type="single_choice", is_required=False),
            SimpleNamespace(id="f3", name="Kaufdatum", field_type="date", is_required=False),
        ]


class ReadOnlyUxTests(unittest.TestCase):
    def setUp(self):
        self.adapter = WebCatalogReadAdapter(FakeCatalog())

    def test_field_types_are_beginner_friendly(self):
        labels = [item.field_type for item in self.adapter.fields("ent-1")]
        self.assertEqual(labels, ["Text", "Einfachauswahl", "Datum"])

    def test_page_marks_read_only_mode_and_disables_mutating_actions(self):
        page = render_page(
            self.adapter,
            category_id="cat-1",
            entry_id="ent-1",
        )

        self.assertIn("🔒 NUR LESEN", page)
        self.assertIn("Text · Pflichtfeld", page)
        self.assertIn("Einfachauswahl", page)
        self.assertIn("Datum", page)

        for label in ("+ Neu", "Bearbeiten", "Undo", "Papierkorb"):
            marker = f'>{label}</button>'
            self.assertIn(marker, page)

        self.assertGreaterEqual(page.count('disabled aria-disabled="true"'), 4)
        self.assertIn(">Hilfe</button>", page)


if __name__ == "__main__":
    unittest.main()

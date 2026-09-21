from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Sequence

from textual.widgets import Input, ListView

from provoware_db.domain.models import FieldDefinition, FieldScope, FieldType
from provoware_db.tui.runtime import ProvowareDbTui
from provoware_db.tui.view_models import EventItem, FieldRow, HealthItem, NavItem


SCALES = (
    ("100", (160, 40)),
    ("150", (107, 27)),
    ("200", (80, 20)),
)


class EvidencePort:
    def __init__(self) -> None:
        self.fields_data: list[FieldRow] = []

    def categories(self) -> Sequence[NavItem]:
        return (NavItem("cat-a", "Kategorie A"),)

    def entries(self, category_id: str) -> Sequence[NavItem]:
        return (NavItem("entry-a", "Eintrag A"),)

    def fields(self, entry_id: str) -> Sequence[FieldRow]:
        return tuple(self.fields_data)

    def health(self) -> Sequence[HealthItem]:
        return ()

    def recent_events(self, limit: int = 10) -> Sequence[EventItem]:
        return ()


class EvidenceWriter:
    def __init__(self, port: EvidencePort) -> None:
        self.port = port
        self.calls: list[tuple[str, str, FieldType]] = []

    def create_entry_field(
        self,
        entry_id: str,
        name: str,
        field_type: FieldType,
    ) -> FieldDefinition:
        self.calls.append((entry_id, name, field_type))
        field = FieldDefinition.new(
            id=f"field-{len(self.calls)}",
            scope=FieldScope.ENTRY,
            entry_id=entry_id,
            name=name,
            field_type=field_type,
        )
        self.port.fields_data.append(
            FieldRow(field.id, field.name, "Nicht gesetzt", field.field_type.value)
        )
        return field


async def _exercise_scale(scale: str, size: tuple[int, int]) -> dict[str, object]:
    port = EvidencePort()
    writer = EvidenceWriter(port)
    app = ProvowareDbTui(port, field_writer=writer)  # type: ignore[arg-type]

    async with app.run_test(size=size) as pilot:
        await pilot.press("enter")
        await pilot.pause()

        entry_list = app.query_one("#entry-list", ListView)
        assert entry_list.has_focus

        await pilot.press("f")
        await pilot.pause()

        type_list = app.query_one("#field-type-list", ListView)
        assert type_list.display is True
        assert type_list.has_focus
        assert len(type_list.children) == 7
        assert type_list.region.height >= 3

        # Keyboard-only path: first type -> name input -> successful create.
        await pilot.press("enter")
        await pilot.pause()
        field_input = app.query_one("#field-create-input", Input)
        assert field_input.display is True
        assert field_input.has_focus

        await pilot.press(*"Notiz")
        await pilot.press("enter")
        await pilot.pause()

        field_list = app.query_one("#field-list", ListView)
        assert writer.calls == [("entry-a", "Notiz", FieldType.TEXT)]
        assert field_list.has_focus
        assert len(field_list.children) == 1
        assert app.read_status == "Feld „Notiz“ angelegt."

        out = Path("runtime/iteration-61")
        out.mkdir(parents=True, exist_ok=True)
        (out / f"field-create-{scale}.svg").write_text(
            app.export_screenshot(),
            encoding="utf-8",
        )

        return {
            "scale_percent": int(scale),
            "viewport": f"{size[0]}x{size[1]}",
            "layout_mode": app.layout_mode.value,
            "type_selector_height": type_list.region.height,
            "keyboard_path": "entry-list -> f -> field-type-list -> enter -> field-create-input -> enter -> field-list",
            "field_type_count": len(type_list.children),
            "write_calls": len(writer.calls),
            "final_focus": "field-list" if field_list.has_focus else "unexpected",
            "status": "GREEN",
        }


async def _capture_accessibility_evidence() -> None:
    results = []
    for scale, size in SCALES:
        results.append(await _exercise_scale(scale, size))

    out = Path("runtime/iteration-61")
    (out / "accessibility-evidence.json").write_text(
        json.dumps(
            {
                "iteration": 61,
                "method": (
                    "Automated layout-stress proxy for 100/150/200 percent: "
                    "constant information load with progressively smaller terminal cell grids."
                ),
                "human_review_required": True,
                "results": results,
                "status": "GREEN",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_field_create_keyboard_accessibility_at_100_150_200_percent_proxy() -> None:
    asyncio.run(_capture_accessibility_evidence())


if __name__ == "__main__":
    test_field_create_keyboard_accessibility_at_100_150_200_percent_proxy()

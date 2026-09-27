from __future__ import annotations

from provoware_db.mask_builder.browser_shell import render_editor_shell


def main() -> None:
    html = render_editor_shell()

    required = (
        'defaultSelection: null,',
        'function defaultSelectionIds(item)',
        'function defaultSelectionForDataType(item, nextDataType)',
        'function updateSingleDefaultSelection(id, select)',
        'function updateMultiDefaultSelection(id, optionId, checked)',
        'function choiceDefaultSelectionPreview(item)',
        'defaultOption.value = option.id;',
        'checkbox.dataset.optionId = option.id;',
        'item.defaultSelection = item.options',
        '"Standardauswahl: keine"',
        '"Standardauswahl: " + labels.join(" | ")',
        'defaultSelectionIds(item).includes(optionId)',
        '" ist als Standardauswahl aktiv. Zuerst Standardauswahl lösen."',
        '"Mehrere Standardoptionen müssen vor dem Wechsel zur Einfachauswahl gelöst werden."',
        'focusDefaultSelectionControl(id, optionId);',
        '.default-selection-control',
    )
    missing = [token for token in required if token not in html]
    if missing:
        raise SystemExit("I132 DEFAULT SELECTION: ROT · missing " + ", ".join(missing))

    change_start = html.index('function changeDataType(id, select)')
    change_end = html.index('function isChoiceDataType(dataType)', change_start)
    change_block = html[change_start:change_end]
    if change_block.index('const prepared = defaultSelectionForDataType(item, nextDataType);') > change_block.index('item.dataType = nextDataType;'):
        raise SystemExit("I132 DEFAULT SELECTION: ROT · type mutation precedes guard")

    remove_start = html.index('function removeDraftOption(draftId, optionId)')
    remove_end = html.index('function moveDraftOption(draftId, optionId, direction)', remove_start)
    remove_block = html[remove_start:remove_end]
    if remove_block.index('defaultSelectionIds(item).includes(optionId)') > remove_block.index('item.options.splice(index, 1);'):
        raise SystemExit("I132 DEFAULT SELECTION: ROT · remove mutation precedes selected-option guard")

    forbidden = ("localStorage", "sessionStorage", "indexedDB", "MaskTemplateStore", "sqlite")
    present = [token for token in forbidden if token in html]
    if present:
        raise SystemExit("I132 DEFAULT SELECTION: ROT · persistence token " + ", ".join(present))

    print("I132 DEFAULT SELECTION STEP 1: GRÜN · browser-local contract implemented")


if __name__ == "__main__":
    main()

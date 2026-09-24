from provoware_db.mask_builder.browser_shell import render_editor_shell


def main() -> None:
    html = render_editor_shell()

    assert 'function focusDataTypeControl(id)' in html
    assert 'placedLayer.querySelectorAll(".datatype-select")' in html
    assert 'focusDataTypeControl(id);' in html

    assert 'dataTypeLabel.className = "datatype-label";' in html
    assert 'dataTypeLabel.id = "draft-datatype-label-" + item.id;' in html
    assert 'dataTypeLabel.textContent = "Datentyp";' in html
    assert 'dataTypeLabel.htmlFor = "draft-datatype-" + item.id;' in html
    assert 'dataTypeSelect.id = "draft-datatype-" + item.id;' in html
    assert 'dataTypeSelect.setAttribute("aria-labelledby", dataTypeLabel.id);' in html

    field_start = html.index('if (item.kind === "field")')
    field_end = html.index('const moveButton', field_start)
    field_block = html[field_start:field_end]
    assert 'datatype-select' in field_block
    assert 'draft-datatype-label-' in field_block

    assert 'button:focus-visible, select:focus-visible' in html
    assert '.datatype-select, .move-draft, .remove-draft { align-self:stretch; width:100%; }' in html

    change_start = html.index('function changeDataType(id, select)')
    change_end = html.index('function removeDraft(id)')
    change_block = html[change_start:change_end]
    assert 'item.dataType = select.value;' in change_block
    assert 'item.id =' not in change_block
    assert 'item.kind =' not in change_block
    assert 'item.label =' not in change_block
    assert 'item.helpText =' not in change_block
    assert 'item.isRequired =' not in change_block
    assert 'item.column =' not in change_block
    assert 'item.width =' not in change_block

    forbidden = ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "indexedDB", 'method="post"', "WebSocket")
    assert all(token not in html for token in forbidden)

    print("MASK BUILDER TEMPORARY DATATYPE I109 STEP 2: GRÜN")


if __name__ == "__main__":
    main()

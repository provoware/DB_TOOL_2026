from __future__ import annotations

from provoware_db.mask_builder.browser_shell import render_editor_shell


def main() -> None:
    html = render_editor_shell()

    required = (
        'function nextDraftElementId()',
        'return "draft-" + String(nextDraftId++);',
        'function duplicateDraft(id)',
        'id: nextDraftElementId(),',
        'const optionIdMap = new Map();',
        'const nextId = "draft-option-" + String(nextDraftOptionId++);',
        'optionIdMap.set(option.id, nextId);',
        'defaultSelection = source.defaultSelection',
        '.map((optionId) => optionIdMap.get(optionId))',
        'defaultSelection = optionIdMap.get(source.defaultSelection) ?? null;',
        'draftElements.push(duplicate);',
        'focusDuplicateControl(duplicate.id);',
        'duplicateButton.className = "duplicate-draft";',
        'duplicateButton.addEventListener("click", () => duplicateDraft(item.id));',
    )
    missing = [token for token in required if token not in html]
    if missing:
        raise SystemExit("I133 DUPLICATE: ROT · missing " + ", ".join(missing))

    block_start = html.index('function duplicateDraft(id)')
    block_end = html.index('function removeDraft(id)', block_start)
    block = html[block_start:block_end]

    if block.index('const options = source.options === null') > block.index('const duplicate = {'):
        raise SystemExit("I133 DUPLICATE: ROT · option clone prepared too late")
    if block.index('id: nextDraftElementId(),') > block.index('draftElements.push(duplicate);'):
        raise SystemExit("I133 DUPLICATE: ROT · duplicate pushed before new ID")
    if 'source.id' in block:
        raise SystemExit("I133 DUPLICATE: ROT · source identity reused")
    if 'options: source.options' in block:
        raise SystemExit("I133 DUPLICATE: ROT · option array reused")
    if html.count('return "draft-" + String(nextDraftId++);') != 1:
        raise SystemExit("I133 DUPLICATE: ROT · draft ID allocator is not singular")

    forbidden = ("localStorage", "sessionStorage", "indexedDB", "MaskTemplateStore", "sqlite")
    present = [token for token in forbidden if token in html]
    if present:
        raise SystemExit("I133 DUPLICATE: ROT · persistence token " + ", ".join(present))

    print("I133 DUPLICATE STEP 1: GRÜN · new draft and option identities are monotone")


if __name__ == "__main__":
    main()

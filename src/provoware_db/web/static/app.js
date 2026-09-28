(() => {
  "use strict";

  const boxes = Array.from(document.querySelectorAll(".entry-multiselect"));
  const count = document.getElementById("multiselect-count");
  const clear = document.getElementById("multiselect-clear");
  const previewSummary = document.getElementById("mass-preview-summary");
  const previewList = document.getElementById("mass-preview-list");

  if (!count || !clear || !previewSummary || !previewList || boxes.length === 0) {
    return;
  }

  const refresh = () => {
    const selected = boxes.filter((box) => box.checked);
    count.textContent = `${selected.length} ausgewählt`;
    clear.disabled = selected.length === 0;

    previewList.replaceChildren();
    selected.forEach((box) => {
      const row = box.closest("[data-entry-select-row]");
      const label = row?.querySelector(".data-row strong")?.textContent?.trim() || box.dataset.entryId || "Unbekannter Eintrag";
      const item = document.createElement("li");
      item.textContent = label;
      previewList.append(item);
    });
    previewSummary.textContent = selected.length === 0
      ? "Keine Einträge ausgewählt."
      : `Diese Vorschau würde ${selected.length} Einträge betreffen.`;

    boxes.forEach((box) => {
      const row = box.closest("[data-entry-select-row]");
      if (row) {
        row.toggleAttribute("data-multi-selected", box.checked);
      }
    });
  };

  boxes.forEach((box) => box.addEventListener("change", refresh));
  clear.addEventListener("click", () => {
    boxes.forEach((box) => {
      box.checked = false;
    });
    refresh();
    boxes[0].focus();
  });

  refresh();
})();

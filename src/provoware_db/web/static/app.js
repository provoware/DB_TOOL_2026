(() => {
  "use strict";

  const boxes = Array.from(document.querySelectorAll(".entry-multiselect"));
  const count = document.getElementById("multiselect-count");
  const clear = document.getElementById("multiselect-clear");

  if (!count || !clear || boxes.length === 0) {
    return;
  }

  const refresh = () => {
    const selected = boxes.filter((box) => box.checked);
    count.textContent = `${selected.length} ausgewählt`;
    clear.disabled = selected.length === 0;

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

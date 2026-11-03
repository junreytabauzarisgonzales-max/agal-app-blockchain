// Super Admin UI behaviour. Loaded as an external script (the admin CSP forbids inline JS).
(function () {
  "use strict";

  // --- Responsive sidebar -------------------------------------------------
  var sidebar = document.getElementById("sidebar");
  var backdrop = document.querySelector(".sidebar-backdrop");
  var toggle = document.querySelector("[data-sidebar-toggle]");

  function setSidebar(open) {
    if (!sidebar || !toggle) return;
    sidebar.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    if (backdrop) backdrop.hidden = !open;
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      setSidebar(!sidebar.classList.contains("is-open"));
    });
  }
  if (backdrop) backdrop.addEventListener("click", function () { setSidebar(false); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setSidebar(false);
  });

  // --- Notifications ------------------------------------------------------
  function dismiss(toast) { if (toast && toast.parentNode) toast.parentNode.removeChild(toast); }

  document.addEventListener("click", function (e) {
    var close = e.target.closest("[data-toast-close]");
    if (close) dismiss(close.closest(".toast"));
  });
  // Errors stay until dismissed; everything else fades out on its own.
  document.querySelectorAll(".toast:not([data-level='error'])").forEach(function (toast) {
    setTimeout(function () { dismiss(toast); }, 6000);
  });

  // --- Confirmation dialog + loading state --------------------------------
  // <form data-confirm="Delete this record?" data-confirm-detail="This cannot be undone."
  //       data-confirm-label="Delete"> asks before submitting.
  var dialog = document.getElementById("confirm-dialog");
  var pending = null;

  function lock(form) {
    form.setAttribute("aria-busy", "true");
    form.querySelectorAll("button[type=submit]").forEach(function (b) { b.disabled = true; });
  }

  if (dialog && typeof dialog.showModal === "function") {
    dialog.addEventListener("close", function () {
      var form = pending;
      pending = null;
      if (form && dialog.returnValue === "confirm") {
        lock(form);
        form.submit(); // programmatic submit skips our submit handler, so no re-prompt
      }
    });
  }

  document.addEventListener("submit", function (e) {
    var form = e.target;
    if (!(form instanceof HTMLFormElement) || form.method.toLowerCase() !== "post") return;

    var message = form.getAttribute("data-confirm");
    if (message) {
      // No <dialog> support: fall back to the browser's built-in prompt.
      if (!dialog || typeof dialog.showModal !== "function") {
        if (!window.confirm(message)) e.preventDefault();
        else lock(form);
        return;
      }
      e.preventDefault();
      pending = form;
      document.getElementById("confirm-title").textContent = message;
      document.getElementById("confirm-message").textContent = form.getAttribute("data-confirm-detail") || "";
      document.getElementById("confirm-accept").textContent = form.getAttribute("data-confirm-label") || "Confirm";
      dialog.returnValue = "cancel";
      dialog.showModal();
      return;
    }
    // Defer so other submit handlers can still cancel before we disable buttons.
    setTimeout(function () { if (!e.defaultPrevented) lock(form); }, 0);
  });

  // Re-enable buttons when returning via the back/forward cache.
  window.addEventListener("pageshow", function (e) {
    if (!e.persisted) return;
    document.querySelectorAll("form[aria-busy]").forEach(function (form) {
      form.removeAttribute("aria-busy");
      form.querySelectorAll("button[type=submit]").forEach(function (b) { b.disabled = false; });
    });
  });
  // --- Printing -------------------------------------------------------------
  document.addEventListener("click", function (e) {
    if (e.target.closest("[data-print]")) window.print();
  });

  // --- Row selection on list pages ("Print selected") -----------------------
  var selectForm = document.getElementById("select-form");
  if (selectForm) {
    var boxes = Array.prototype.slice.call(document.querySelectorAll("input[name=id][form=select-form]"));
    var selectAll = document.getElementById("select-all");
    var printSelected = document.getElementById("print-selected");

    var refreshSelection = function () {
      var n = boxes.filter(function (b) { return b.checked; }).length;
      printSelected.disabled = n === 0;
      printSelected.textContent = "Print selected (" + n + ")";
      if (selectAll) {
        selectAll.checked = n > 0 && n === boxes.length;
        selectAll.indeterminate = n > 0 && n < boxes.length;
      }
    };

    boxes.forEach(function (b) { b.addEventListener("change", refreshSelection); });
    if (selectAll) {
      selectAll.addEventListener("change", function () {
        boxes.forEach(function (b) { b.checked = selectAll.checked; });
        refreshSelection();
      });
    }
    // Browsers may restore ticked boxes on back/forward; keep the button in sync.
    window.addEventListener("pageshow", refreshSelection);
    refreshSelection();
  }
})();

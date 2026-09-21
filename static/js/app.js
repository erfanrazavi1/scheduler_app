(function () {
  "use strict";

  var root = document.documentElement;

  function showDialog(dialog) {
    if (!dialog) return;
    if (typeof dialog.showModal === "function") {
      if (!dialog.open) dialog.showModal();
    } else {
      dialog.setAttribute("open", "");
    }
  }

  function bindDialog(dialog) {
    if (!dialog) return;
    dialog.querySelectorAll("[data-dialog-close]").forEach(function (button) {
      button.addEventListener("click", function () { dialog.close(); });
    });
    // Close when the backdrop (the dialog element itself) is clicked.
    dialog.addEventListener("click", function (event) {
      if (event.target === dialog) dialog.close();
    });
  }

  /* ----------------------------- Dark mode ----------------------------- */
  function syncThemeIcons() {
    var isDark = root.classList.contains("dark");
    document.querySelectorAll('[data-icon="sun"]').forEach(function (el) {
      el.classList.toggle("hidden", !isDark);
    });
    document.querySelectorAll('[data-icon="moon"]').forEach(function (el) {
      el.classList.toggle("hidden", isDark);
    });
  }

  function toggleTheme() {
    var isDark = root.classList.toggle("dark");
    try {
      localStorage.setItem("theme", isDark ? "dark" : "light");
    } catch (e) {}
    syncThemeIcons();
  }

  document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
    button.addEventListener("click", toggleTheme);
  });

  /* ------------------------------ Messages ----------------------------- */
  document.querySelectorAll("[data-message-close]").forEach(function (button) {
    button.addEventListener("click", function () {
      var box = button.closest("[data-message]");
      if (box) box.remove();
    });
  });

  /* -------------------------- Mobile day tabs -------------------------- */
  var ACTIVE_TAB = ["border-blue-600", "bg-blue-600", "text-white", "shadow-sm"];
  var INACTIVE_TAB = [
    "border-slate-200", "bg-white", "text-slate-600", "hover:bg-slate-100",
    "dark:border-slate-800", "dark:bg-slate-900", "dark:text-slate-300",
    "dark:hover:bg-slate-800",
  ];

  var tabs = document.querySelectorAll("[data-day-tab]");
  var panels = document.querySelectorAll("[data-day-panel]");

  function selectDay(value) {
    tabs.forEach(function (tab) {
      var isActive = tab.getAttribute("data-day-tab") === value;
      tab.setAttribute("aria-selected", isActive ? "true" : "false");
      ACTIVE_TAB.forEach(function (c) { tab.classList.toggle(c, isActive); });
      INACTIVE_TAB.forEach(function (c) { tab.classList.toggle(c, !isActive); });
    });
    panels.forEach(function (panel) {
      panel.hidden = panel.getAttribute("data-day-panel") !== value;
    });
  }

  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      selectDay(tab.getAttribute("data-day-tab"));
    });
  });

  tabs.forEach(function (tab, index) {
    tab.addEventListener("keydown", function (event) {
      var next = null;
      if (event.key === "ArrowLeft") next = tabs[(index + 1) % tabs.length];
      if (event.key === "ArrowRight") next = tabs[(index - 1 + tabs.length) % tabs.length];
      if (next) {
        event.preventDefault();
        next.focus();
        selectDay(next.getAttribute("data-day-tab"));
      }
    });
  });

  /* ----------------------------- Details dialog ------------------------ */
  var detailsDialog = document.getElementById("class-dialog");

  function itemData(item) {
    var get = function (name) { return item.getAttribute("data-" + name) || ""; };
    return {
      title: get("title"),
      dayName: get("day-name"),
      time: get("time"),
      instructor: get("instructor"),
      location: get("location"),
      description: get("description"),
    };
  }

  function setText(scope, selector, value) {
    var el = scope.querySelector(selector);
    if (el) el.textContent = value || "";
  }

  function toggleRow(scope, selector, hasValue) {
    var el = scope.querySelector(selector);
    if (el) el.hidden = !hasValue;
  }

  function openDetails(item) {
    if (!detailsDialog) return;
    var data = itemData(item);
    setText(detailsDialog, "[data-dialog-title]", data.title);
    setText(detailsDialog, "[data-dialog-day]", data.dayName);
    setText(detailsDialog, "[data-dialog-time]", data.time);
    setText(detailsDialog, "[data-dialog-instructor]", data.instructor);
    setText(detailsDialog, "[data-dialog-location]", data.location);
    setText(detailsDialog, "[data-dialog-description]", data.description);
    toggleRow(detailsDialog, "[data-dialog-instructor-row]", !!data.instructor);
    toggleRow(detailsDialog, "[data-dialog-location-row]", !!data.location);
    toggleRow(detailsDialog, "[data-dialog-description-row]", !!data.description);
    showDialog(detailsDialog);
  }

  /* --------------------------- Form dialog ----------------------------- */
  var formDialog = document.getElementById("class-form-dialog");
  var classForm = document.getElementById("class-form");

  function field(id) { return classForm ? classForm.querySelector("#" + id) : null; }

  function setField(id, value) {
    var el = field(id);
    if (el) el.value = value == null ? "" : value;
  }

  function openCreateForm(dayValue) {
    if (!formDialog || !classForm) return;
    classForm.reset();
    setField("id_day", dayValue);
    classForm.setAttribute("action", formDialog.getAttribute("data-create-url"));
    setText(formDialog, "[data-form-title]", formDialog.getAttribute("data-create-title"));
    showDialog(formDialog);
  }

  function openEditForm(item) {
    if (!formDialog || !classForm) return;
    setField("id_title", item.getAttribute("data-title"));
    setField("id_instructor", item.getAttribute("data-instructor"));
    setField("id_day", item.getAttribute("data-day-value"));
    setField("id_start_time", item.getAttribute("data-start-time"));
    setField("id_end_time", item.getAttribute("data-end-time"));
    setField("id_location", item.getAttribute("data-location"));
    setField("id_description", item.getAttribute("data-description"));
    setField("id_color", item.getAttribute("data-color"));
    classForm.setAttribute("action", item.getAttribute("data-edit-url"));
    setText(formDialog, "[data-form-title]", formDialog.getAttribute("data-edit-title"));
    showDialog(formDialog);
  }

  /* --------------------------- Delete dialog --------------------------- */
  var deleteDialog = document.getElementById("delete-dialog");
  var deleteForm = document.getElementById("delete-form");

  function openDelete(item) {
    if (!deleteDialog || !deleteForm) return;
    deleteForm.setAttribute("action", item.getAttribute("data-delete-url"));
    setText(deleteDialog, "[data-delete-title]", item.getAttribute("data-title"));
    showDialog(deleteDialog);
  }

  /* ------------------------- Event delegation -------------------------- */
  document.addEventListener("click", function (event) {
    var item = event.target.closest("[data-class-item]");

    if (event.target.closest("[data-add-class]")) {
      var add = event.target.closest("[data-add-class]");
      openCreateForm(add.getAttribute("data-day"));
      return;
    }
    if (event.target.closest("[data-edit-class]") && item) {
      openEditForm(item);
      return;
    }
    if (event.target.closest("[data-delete-class]") && item) {
      openDelete(item);
      return;
    }
    if (event.target.closest("[data-class-card]") && item) {
      openDetails(item);
    }
  });

  bindDialog(detailsDialog);
  bindDialog(formDialog);
  bindDialog(deleteDialog);

  // Re-open the form after a failed server-side validation.
  if (formDialog && formDialog.getAttribute("data-auto-open") === "form") {
    showDialog(formDialog);
  }

  syncThemeIcons();
})();

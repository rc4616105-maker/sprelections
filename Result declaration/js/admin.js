/**
 * Admin Panel & Settings Modal
 * Clean theme candidate and settings editor with localStorage persistence.
 */

class AdminManager {
  constructor(app) {
    this.app = app;
    this.modal = document.getElementById("adminModal");
    this.houseSelect = document.getElementById("adminHouseSelect");
    this.formContainer = document.getElementById("adminFormContainer");
    this.selectedHouseId = "bheeshma";

    this.init();
  }

  init() {
    if (!this.modal) return;

    // Populate House Select
    this.houseSelect.innerHTML = "";
    this.app.houses.forEach(h => {
      const opt = document.createElement("option");
      opt.value = h.id;
      opt.textContent = `${h.fullName || h.name + ' House'}`;
      this.houseSelect.appendChild(opt);
    });

    this.houseSelect.addEventListener("change", (e) => {
      this.selectedHouseId = e.target.value;
      this.renderForm();
    });

    // Close buttons
    const closeBtns = this.modal.querySelectorAll(".btn-close-modal");
    closeBtns.forEach(b => b.addEventListener("click", () => this.close()));

    // Save Button
    const saveBtn = document.getElementById("btnSaveAdmin");
    if (saveBtn) {
      saveBtn.addEventListener("click", () => this.saveChanges());
    }

    // Reset Progress Button
    const resetProgressBtn = document.getElementById("btnResetProgress");
    if (resetProgressBtn) {
      resetProgressBtn.addEventListener("click", () => {
        if (confirm("Reset the election progress? The wheel will be restored with all 6 houses.")) {
          this.app.resetProgress();
          this.close();
        }
      });
    }

    // Reset All Defaults Button
    const resetAllBtn = document.getElementById("btnResetAllDefaults");
    if (resetAllBtn) {
      resetAllBtn.addEventListener("click", () => {
        if (confirm("Reset all candidate details back to defaults?")) {
          this.app.resetAllDataToDefaults();
          this.renderForm();
          alert("Data restored to defaults!");
        }
      });
    }
  }

  open() {
    this.selectedHouseId = this.houseSelect.value || "bheeshma";
    this.renderForm();
    this.modal.classList.add("active");
  }

  close() {
    this.modal.classList.remove("active");
  }

  renderForm() {
    const house = this.app.houses.find(h => h.id === this.selectedHouseId);
    if (!house) return;

    this.formContainer.innerHTML = "";

    const houseBanner = document.createElement("div");
    houseBanner.className = "admin-house-badge";
    houseBanner.style.borderLeft = `6px solid ${house.color}`;
    houseBanner.style.background = "#FFFFFF";
    houseBanner.style.padding = "0.75rem 1rem";
    houseBanner.style.border = "1px solid var(--border-subtle)";
    houseBanner.style.borderLeft = `6px solid ${house.color}`;
    houseBanner.style.borderRadius = "8px";
    houseBanner.style.marginBottom = "1.25rem";
    houseBanner.innerHTML = `<strong>${house.fullName || house.name + ' House'}</strong> • <span style="color: #6B7280;">${house.motto}</span>`;
    this.formContainer.appendChild(houseBanner);

    POST_KEYS.forEach(postKey => {
      const candidate = house.candidates[postKey];
      const meta = POST_METADATA[postKey];

      const postBox = document.createElement("div");
      postBox.className = "admin-post-group";
      postBox.innerHTML = `
        <div class="admin-post-header">
          <span>${meta.title}</span>
        </div>
        <div class="admin-fields-row">
          <div class="admin-field">
            <label>Full Name</label>
            <input type="text" class="input-candidate-name" data-post="${postKey}" value="${candidate.name || ''}" placeholder="Candidate Name">
          </div>
          <div class="admin-field">
            <label>Grade / Section</label>
            <input type="text" class="input-candidate-grade" data-post="${postKey}" value="${candidate.grade || ''}" placeholder="e.g. Grade 12-A">
          </div>
        </div>
        <div class="admin-fields-row">
          <div class="admin-field">
            <label>Photo URL / File</label>
            <input type="text" class="input-candidate-photo" data-post="${postKey}" value="${candidate.photo || ''}" placeholder="URL or file path">
          </div>
          <div class="admin-field">
            <label>Quote / Motto</label>
            <input type="text" class="input-candidate-quote" data-post="${postKey}" value="${candidate.quote || ''}" placeholder="e.g. Leading with honor">
          </div>
        </div>
      `;
      this.formContainer.appendChild(postBox);
    });
  }

  saveChanges() {
    const house = this.app.houses.find(h => h.id === this.selectedHouseId);
    if (!house) return;

    POST_KEYS.forEach(postKey => {
      const nameInput = this.formContainer.querySelector(`.input-candidate-name[data-post="${postKey}"]`);
      const gradeInput = this.formContainer.querySelector(`.input-candidate-grade[data-post="${postKey}"]`);
      const photoInput = this.formContainer.querySelector(`.input-candidate-photo[data-post="${postKey}"]`);
      const quoteInput = this.formContainer.querySelector(`.input-candidate-quote[data-post="${postKey}"]`);

      if (house.candidates[postKey]) {
        if (nameInput) house.candidates[postKey].name = nameInput.value.trim();
        if (gradeInput) house.candidates[postKey].grade = gradeInput.value.trim();
        if (photoInput) house.candidates[postKey].photo = photoInput.value.trim();
        if (quoteInput) house.candidates[postKey].quote = quoteInput.value.trim();
      }
    });

    this.app.saveCustomData();
    alert(`Changes saved for ${house.fullName || house.name + ' House'}!`);
    this.close();
  }
}

window.AdminManager = AdminManager;

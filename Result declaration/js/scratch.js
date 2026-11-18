/**
 * Big Screen Scratch Card & Spotlight Focus Engine
 * Designed for large touchscreen/smartboard presentation without a mouse.
 * 
 * Flow:
 * 1. For Houses: 4 Cards shown in the arena grid. Tapping opens Large Spotlight.
 * 2. For Cabinet: Single centerpiece card shown. Tapping opens Large Spotlight.
 * 3. Broad-coverage touch scratching (140px stroke width).
 * 4. At 70% cleared: Triggers celebratory pop-up animation, fanfare & confetti.
 * 5. Spacebar/Escape or tapping backdrop returns to the arena (never kicks back to the wheel).
 */

class ScratchArenaManager {
  constructor(containerId, spotlightModalId, houseOrPostData, options = {}) {
    this.container = document.getElementById(containerId);
    this.modal = document.getElementById(spotlightModalId);
    this.backdrop = document.getElementById("spotlightBackdrop");
    this.spotlightTarget = document.getElementById("spotlightCardTarget");
    this.isCabinet = Boolean(options.isCabinet);
    this.options = options;

    if (this.isCabinet) {
      this.cabinetPost = houseOrPostData;
      this.house = {
        id: houseOrPostData.id,
        name: houseOrPostData.name,
        fullName: "School Cabinet (Central Council)",
        color: houseOrPostData.color || "#059669",
        textColor: houseOrPostData.textColor || "#FFFFFF"
      };
    } else {
      this.cabinetPost = null;
      this.house = houseOrPostData;
    }

    this.onAllRevealed = options.onAllRevealed || null;
    this.onPostRevealed = options.onPostRevealed || null;

    this.revealedPosts = new Set();
    this.activePostKey = null;
    this.currentSpotlightInstance = null;

    this.init();
  }

  init() {
    this.renderGrid();
    this.attachGlobalEvents();
  }

  attachGlobalEvents() {
    // Tapping outside the spotlight card on the backdrop closes spotlight and stays in scratch arena
    if (this.backdrop) {
      this.backdrop.addEventListener("click", () => this.closeSpotlight());
    }

    // Spacebar or Escape returns to the cards
    this.keyHandler = (e) => {
      if (this.modal && this.modal.classList.contains("active")) {
        if (e.code === "Space" || e.key === "Escape") {
          e.preventDefault();
          this.closeSpotlight();
        }
      }
    };
    window.addEventListener("keydown", this.keyHandler);
  }

  destroy() {
    if (this.keyHandler) {
      window.removeEventListener("keydown", this.keyHandler);
    }
    if (this.currentSpotlightInstance) {
      this.currentSpotlightInstance.destroy();
      this.currentSpotlightInstance = null;
    }
  }

  renderGrid() {
    if (!this.container) return;
    this.container.innerHTML = "";

    if (this.isCabinet) {
      this.renderCabinetGrid();
      return;
    }

    this.container.classList.remove("cabinet-single-mode");

    POST_KEYS.forEach(postKey => {
      const candidate = this.house.candidates[postKey];
      const meta = POST_METADATA[postKey] || { title: candidate.postTitle, badge: "Leader" };
      const isRevealed = this.revealedPosts.has(postKey);

      const gridCard = document.createElement("div");
      gridCard.className = `scratch-grid-card ${isRevealed ? 'is-revealed' : 'is-unrevealed'}`;
      gridCard.style.borderTop = `6px solid ${this.house.color}`;
      gridCard.setAttribute("data-post", postKey);

      if (isRevealed) {
        // Revealed State Card
        gridCard.innerHTML = `
          <div class="card-header">
            <span class="post-title">${meta.title}</span>
          </div>
          <div class="card-body">
            <div class="candidate-photo-frame" style="border-color: ${this.house.color};">
              ${this.getPhotoMarkup(candidate, postKey)}
              <div class="winner-badge" style="background: ${this.house.color}; color: ${this.house.textColor};">ELECTED</div>
            </div>
            <h3 class="candidate-name">${candidate.name}</h3>
            <p class="candidate-grade">${candidate.grade}</p>
            <div class="candidate-badge" style="background: rgba(0,0,0,0.05); color: #4B5563;">
              ${this.house.fullName || this.house.name}
            </div>
          </div>
        `;
      } else {
        // Unrevealed State: Tap to Expand & Scratch
        gridCard.innerHTML = `
          <div class="card-header">
            <span class="post-title">${meta.title}</span>
          </div>
          <div class="card-foil-preview">
            <div class="foil-preview-pattern"></div>
            <div class="foil-preview-content">
              <span class="foil-tap-icon">👆</span>
              <span class="foil-tap-label">TAP TO SCRATCH</span>
              <span class="foil-post-sub">${meta.title}</span>
            </div>
          </div>
        `;
      }

      gridCard.addEventListener("click", () => {
        this.openSpotlight(postKey);
      });

      this.container.appendChild(gridCard);
    });
  }

  renderCabinetGrid() {
    this.container.classList.add("cabinet-single-mode");

    const post = this.cabinetPost;
    const postTitle = post.fullName || post.postTitle || post.name;
    const candidate = (post.candidate) ? post.candidate : {
      name: post.winnerName || "Awaiting Result",
      grade: post.grade || "Class 10",
      photo: "",
      quote: "Apex Leadership"
    };
    candidate.postTitle = postTitle;

    const isRevealed = this.revealedPosts.has(post.id);

    const gridCard = document.createElement("div");
    gridCard.className = `scratch-grid-card ${isRevealed ? 'is-revealed' : 'is-unrevealed'}`;
    gridCard.style.borderTop = `7px solid ${post.color || '#059669'}`;
    gridCard.setAttribute("data-post", post.id);

    if (isRevealed) {
      gridCard.innerHTML = `
        <div class="card-header" style="background: #F0FDF4; border-bottom: 1px solid #BBF7D0;">
          <span class="post-title" style="color: ${post.color || '#059669'}; font-weight: 800;">${postTitle}</span>
        </div>
        <div class="card-body">
          <div class="candidate-photo-frame" style="border-color: ${post.color || '#059669'};">
            ${this.getPhotoMarkup(candidate, post.id)}
            <div class="winner-badge" style="background: ${post.color || '#059669'}; color: #FFFFFF;">ELECTED</div>
          </div>
          <h3 class="candidate-name">${candidate.name}</h3>
          <p class="candidate-grade">${candidate.grade}</p>
          <div class="candidate-badge" style="background: rgba(5, 150, 105, 0.08); color: #065F46; font-weight: 700;">
            🏛️ School Cabinet (Central Council)
          </div>
        </div>
      `;
    } else {
      gridCard.innerHTML = `
        <div class="card-header" style="background: #F0FDF4; border-bottom: 1px solid #BBF7D0;">
          <span class="post-title" style="color: ${post.color || '#059669'}; font-weight: 800;">${postTitle}</span>
        </div>
        <div class="card-foil-preview">
          <div class="foil-preview-pattern"></div>
          <div class="foil-preview-content">
            <span class="foil-tap-icon">👆</span>
            <span class="foil-tap-label">TAP TO SCRATCH & REVEAL</span>
            <span class="foil-post-sub">${postTitle}</span>
          </div>
        </div>
      `;
    }

    gridCard.addEventListener("click", () => {
      this.openSpotlight(post.id);
    });

    this.container.appendChild(gridCard);

    // Auto-open spotlight scratch card so user can scratch immediately
    if (!isRevealed && this.options.autoOpen !== false) {
      setTimeout(() => {
        this.openSpotlight(post.id);
      }, 200);
    }
  }

  getPhotoMarkup(candidate, postKey) {
    if (candidate.photo && candidate.photo.trim() !== "") {
      return `<img src="${candidate.photo}" alt="${candidate.name}" class="candidate-img" onerror="this.src=this.dataset.fallback" data-fallback="data:image/svg+xml;utf8,${encodeURIComponent(this.getAvatarSvg(postKey))}">`;
    }
    return `<div class="candidate-avatar-svg">${this.getAvatarSvg(postKey)}</div>`;
  }

  getAvatarSvg(postKey) {
    const isGirl = String(postKey).toLowerCase().includes("girl");
    const color = (this.isCabinet && this.cabinetPost) ? (this.cabinetPost.color || "#059669") : (this.house.color || "#2563EB");
    return `
      <svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
        <circle cx="60" cy="60" r="58" fill="#F3F4F6" stroke="#E5E7EB" stroke-width="3"/>
        ${isGirl ? `
          <path d="M40 45 C40 28, 80 28, 80 45 C80 60, 40 60, 40 45 Z" fill="#D1D5DB"/>
          <path d="M60 58 C68 58, 73 50, 73 44 C73 35, 67 30, 60 30 C53 30, 47 35, 47 44 C47 50, 52 58, 60 58 Z" fill="#E5E7EB"/>
          <path d="M35 105 C35 88, 48 76, 60 76 C72 76, 85 88, 85 105 Z" fill="${color}"/>
        ` : `
          <circle cx="60" cy="44" r="16" fill="#D1D5DB"/>
          <path d="M32 105 C32 84, 46 72, 60 72 C74 72, 88 84, 88 105 Z" fill="${color}"/>
        `}
      </svg>
    `;
  }

  openSpotlight(postKey) {
    this.activePostKey = postKey;
    const isAlreadyRevealed = this.revealedPosts.has(postKey);

    let candidate;
    let houseContext;

    if (this.isCabinet) {
      const p = this.cabinetPost;
      candidate = (p.candidate) ? p.candidate : {
        name: p.winnerName || "Awaiting Result",
        grade: p.grade || "Class 10",
        photo: "",
        quote: "Apex Leadership"
      };
      candidate.postTitle = p.fullName || p.postTitle || p.name;
      houseContext = {
        name: p.name,
        fullName: "School Cabinet (Central Council)",
        color: p.color || "#059669",
        textColor: p.textColor || "#FFFFFF"
      };
    } else {
      candidate = this.house.candidates[postKey];
      houseContext = this.house;
    }

    this.spotlightTarget.innerHTML = "";

    this.currentSpotlightInstance = new SpotlightScratchCard(
      this.spotlightTarget,
      candidate,
      houseContext,
      postKey,
      isAlreadyRevealed,
      {
        isCabinet: this.isCabinet,
        onRevealed: () => {
          this.revealedPosts.add(postKey);
          this.renderGrid();
          if (typeof this.onPostRevealed === "function") {
            this.onPostRevealed(postKey);
          }
          const totalExpected = this.isCabinet ? 1 : POST_KEYS.length;
          if (this.revealedPosts.size >= totalExpected) {
            if (typeof this.onAllRevealed === "function") {
              this.onAllRevealed();
            }
          }
        },
        onRequestClose: () => {
          this.closeSpotlight();
        }
      }
    );

    this.modal.classList.add("active");
  }

  closeSpotlight() {
    if (!this.modal || !this.modal.classList.contains("active")) return;
    this.modal.classList.remove("active");
    if (this.currentSpotlightInstance) {
      this.currentSpotlightInstance.destroy();
      this.currentSpotlightInstance = null;
    }
    this.activePostKey = null;
  }
}

/**
 * Large Spotlight Scratch Card with Broad Touch Brush & 70% Pop-up Reveal
 */
class SpotlightScratchCard {
  constructor(container, candidate, house, postKey, isAlreadyRevealed, callbacks = {}) {
    this.container = container;
    this.candidate = candidate;
    this.house = house;
    this.postKey = postKey;
    this.isRevealed = isAlreadyRevealed;
    this.callbacks = callbacks;
    this.isCabinet = Boolean(callbacks.isCabinet);

    this.isDrawing = false;
    this.lastX = null;
    this.lastY = null;
    this.lastScratchAudio = 0;
    this.checkTimer = null;

    this.build();
  }

  build() {
    this.container.innerHTML = "";
    this.wrapper = document.createElement("div");
    this.wrapper.className = "spotlight-card-wrapper";
    this.wrapper.style.borderTop = `8px solid ${this.house.color}`;

    const meta = (typeof POST_METADATA !== "undefined" && POST_METADATA[this.postKey]) || {
      title: this.candidate.postTitle || this.house.name || "Leader",
      badge: this.isCabinet ? "Apex Leader" : "Leader"
    };

    // 1. Underlying Revealed Candidate Card (Large Scale)
    const cardInner = document.createElement("div");
    cardInner.className = "spotlight-candidate-card";

    let photoMarkup = "";
    if (this.candidate.photo && this.candidate.photo.trim() !== "") {
      photoMarkup = `<img src="${this.candidate.photo}" alt="${this.candidate.name}" class="spotlight-candidate-img" onerror="this.src=this.dataset.fallback" data-fallback="data:image/svg+xml;utf8,${encodeURIComponent(this.getAvatarSvg())}">`;
    } else {
      photoMarkup = `<div class="spotlight-avatar-svg">${this.getAvatarSvg()}</div>`;
    }

    cardInner.innerHTML = `
      <div class="spotlight-card-header">
        <span class="spotlight-post-title">${meta.title}</span>
      </div>
      <div class="spotlight-card-body">
        <div class="spotlight-photo-frame" style="border-color: ${this.house.color};">
          ${photoMarkup}
          <div class="spotlight-winner-badge" style="background: ${this.house.color}; color: ${this.house.textColor};">ELECTED</div>
        </div>
        <h2 class="spotlight-candidate-name">${this.candidate.name}</h2>
        <p class="spotlight-candidate-grade">${this.candidate.grade}</p>
        <div class="spotlight-candidate-badge" style="background: rgba(0,0,0,0.05); color: #4B5563;">
          ${this.house.fullName || this.house.name}
        </div>
      </div>
    `;

    this.wrapper.appendChild(cardInner);

    // 2. Scratch Canvas Layer (if not already revealed)
    if (!this.isRevealed) {
      const canvas = document.createElement("canvas");
      canvas.className = "spotlight-scratch-canvas";
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d", { willReadFrequently: true });
      this.wrapper.appendChild(canvas);

      // Instant Reveal quick action
      const instantBar = document.createElement("div");
      instantBar.className = "spotlight-instant-bar";
      const instantBtn = document.createElement("button");
      instantBtn.className = "btn-instant-reveal";
      instantBtn.innerHTML = `<span>Instant Reveal</span>`;
      instantBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        this.reveal();
      });
      instantBar.appendChild(instantBtn);
      this.wrapper.appendChild(instantBar);
    }

    this.container.appendChild(this.wrapper);

    if (!this.isRevealed) {
      requestAnimationFrame(() => {
        this.initCanvas();
        this.attachEvents();
      });
    }
  }

  getAvatarSvg() {
    const isGirl = String(this.postKey).toLowerCase().includes("girl");
    return `
      <svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
        <circle cx="60" cy="60" r="58" fill="#F3F4F6" stroke="#E5E7EB" stroke-width="3"/>
        ${isGirl ? `
          <path d="M40 45 C40 28, 80 28, 80 45 C80 60, 40 60, 40 45 Z" fill="#D1D5DB"/>
          <path d="M60 58 C68 58, 73 50, 73 44 C73 35, 67 30, 60 30 C53 30, 47 35, 47 44 C47 50, 52 58, 60 58 Z" fill="#E5E7EB"/>
          <path d="M35 105 C35 88, 48 76, 60 76 C72 76, 85 88, 85 105 Z" fill="${this.house.color}"/>
        ` : `
          <circle cx="60" cy="44" r="16" fill="#D1D5DB"/>
          <path d="M32 105 C32 84, 46 72, 60 72 C74 72, 88 84, 88 105 Z" fill="${this.house.color}"/>
        `}
      </svg>
    `;
  }

  initCanvas() {
    if (!this.canvas) return;
    const rect = this.wrapper.getBoundingClientRect();
    const width = Math.floor(rect.width || 520);
    const height = Math.floor(rect.height || 620);

    this.width = width;
    this.height = height;
    this.canvas.width = width;
    this.canvas.height = height;

    this.renderFoil();
  }

  renderFoil() {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;

    // Metallic silver foil gradient
    const foilGrad = ctx.createLinearGradient(0, 0, w, h);
    foilGrad.addColorStop(0, "#D1D5DB");
    foilGrad.addColorStop(0.25, "#E5E7EB");
    foilGrad.addColorStop(0.5, "#F3F4F6");
    foilGrad.addColorStop(0.75, "#E5E7EB");
    foilGrad.addColorStop(1, "#9CA3AF");

    ctx.fillStyle = foilGrad;
    ctx.fillRect(0, 0, w, h);

    // Subtle diagonal scratch line texture
    ctx.strokeStyle = "rgba(0, 0, 0, 0.04)";
    ctx.lineWidth = 2;
    for (let i = -h; i < w + h; i += 28) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i + h, h);
      ctx.stroke();
    }

    // Top color accent line
    ctx.fillStyle = this.house.color;
    ctx.fillRect(0, 0, w, 8);

    // Scratch instructions
    ctx.save();
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    ctx.fillStyle = "#6B7280";
    ctx.font = "800 14px 'Plus Jakarta Sans', sans-serif";
    ctx.letterSpacing = "2.5px";
    ctx.fillText("SWIPE TO SCRATCH & REVEAL", w / 2, h / 2 - 24);

    ctx.font = "900 28px 'Plus Jakarta Sans', sans-serif";
    ctx.fillStyle = "#111827";
    const postTitle = this.candidate.postTitle || (POST_METADATA[this.postKey] && POST_METADATA[this.postKey].title) || "Leader";
    ctx.fillText(postTitle.toUpperCase(), w / 2, h / 2 + 18);

    ctx.restore();
  }

  attachEvents() {
    if (!this.canvas) return;

    const startDraw = (e) => {
      if (this.isRevealed) return;
      this.isDrawing = true;
      const pos = this.getPointerPos(e);
      this.lastX = pos.x;
      this.lastY = pos.y;
      this.scratchAt(pos.x, pos.y);
      window.soundEngine.playScratch();
      this.scheduleCheck();
    };

    const draw = (e) => {
      if (!this.isDrawing || this.isRevealed) return;
      e.preventDefault();
      const pos = this.getPointerPos(e);
      this.scratchLine(this.lastX, this.lastY, pos.x, pos.y);
      this.scratchAt(pos.x, pos.y);
      this.lastX = pos.x;
      this.lastY = pos.y;

      const now = performance.now();
      if (now - this.lastScratchAudio > 65) {
        window.soundEngine.playScratch();
        this.lastScratchAudio = now;
      }

      this.scheduleCheck();
    };

    const stopDraw = () => {
      this.isDrawing = false;
      this.lastX = null;
      this.lastY = null;
    };

    this.canvas.addEventListener("mousedown", startDraw);
    window.addEventListener("mousemove", draw);
    window.addEventListener("mouseup", stopDraw);

    this.canvas.addEventListener("touchstart", startDraw, { passive: false });
    window.addEventListener("touchmove", draw, { passive: false });
    window.addEventListener("touchend", stopDraw);

    this.cleanups = [
      () => window.removeEventListener("mousemove", draw),
      () => window.removeEventListener("mouseup", stopDraw),
      () => window.removeEventListener("touchmove", draw),
      () => window.removeEventListener("touchend", stopDraw)
    ];
  }

  getPointerPos(e) {
    const rect = this.canvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return {
      x: clientX - rect.left,
      y: clientY - rect.top
    };
  }

  // Broad brush radius (140px coverage) optimized for big screen fingertip & pointer scratching
  scratchAt(x, y) {
    const ctx = this.ctx;
    ctx.save();
    ctx.globalCompositeOperation = "destination-out";
    ctx.beginPath();
    ctx.arc(x, y, 70, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  scratchLine(x1, y1, x2, y2) {
    const ctx = this.ctx;
    ctx.save();
    ctx.globalCompositeOperation = "destination-out";
    ctx.lineWidth = 140;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
    ctx.restore();
  }

  scheduleCheck() {
    if (this.checkTimer) return;
    this.checkTimer = setTimeout(() => {
      this.checkTimer = null;
      this.calculateClearedArea();
    }, 100);
  }

  calculateClearedArea() {
    if (this.isRevealed) return;
    try {
      const imgData = this.ctx.getImageData(0, 0, this.width, this.height);
      const data = imgData.data;
      let clearedPixels = 0;

      const step = 28;
      let samples = 0;

      for (let i = 3; i < data.length; i += 4 * step) {
        samples++;
        if (data[i] === 0) {
          clearedPixels++;
        }
      }

      const ratio = clearedPixels / samples;
      // When 70% (0.70) has been scratched, auto-reveal with pop-up animation
      if (ratio >= 0.70) {
        this.reveal();
      }
    } catch (e) {
      // ignore
    }
  }

  reveal() {
    if (this.isRevealed) return;
    this.isRevealed = true;

    // Dissolve canvas foil
    if (this.canvas) {
      this.canvas.style.transition = "opacity 0.45s ease, transform 0.45s ease";
      this.canvas.style.opacity = "0";
      this.canvas.style.transform = "scale(1.06)";
      this.canvas.style.pointerEvents = "none";
    }

    // Hide instant button
    const instantBar = this.wrapper.querySelector(".spotlight-instant-bar");
    if (instantBar) {
      instantBar.style.display = "none";
    }

    // Pop-up Celebration Animation on the card
    this.wrapper.classList.add("card-pop-celebration");

    // Sound FX: Single clean reveal fanfare
    window.soundEngine.playFanfare();

    // Confetti burst centered right on the card
    const rect = this.wrapper.getBoundingClientRect();
    const originX = rect.left + rect.width / 2;
    const originY = rect.top + rect.height / 2;
    window.confettiEngine.burst(originX, originY, 65, [this.house.color, "#EAB308", "#111827", "#FFFFFF"]);

    if (typeof this.callbacks.onRevealed === "function") {
      this.callbacks.onRevealed();
    }
  }

  destroy() {
    if (this.cleanups) {
      this.cleanups.forEach(fn => fn());
    }
  }
}

window.ScratchArenaManager = ScratchArenaManager;

/**
 * Spin Wheel Engine
 * Large prominent canvas wheel with clickable center hub button.
 * Clear bold house names and smooth physics.
 */

class SpinWheel {
  constructor(canvasId, options = {}) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext("2d");
    this.centerBtn = document.getElementById("btnCenterSpin");
    this.houses = [];
    this.currentRotation = 0; // in radians
    this.isSpinning = false;
    this.onSelectCallback = options.onSelect || null;
    this.lastTickSlice = -1;

    this.init();
  }

  init() {
    this.resize();
    window.addEventListener("resize", () => {
      this.resize();
      this.draw();
    });

    // Clicking the center hub button spins the wheel
    if (this.centerBtn) {
      this.centerBtn.addEventListener("click", () => {
        if (!this.isSpinning) {
          this.spin();
        }
      });
    }

    // Also support clicking directly anywhere in the center region of canvas
    this.canvas.addEventListener("click", (e) => {
      if (this.isSpinning) return;
      const rect = this.canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const dist = Math.hypot(x - this.center, y - this.center);
      if (dist <= 60) {
        this.spin();
      }
    });
  }

  resize() {
    if (!this.canvas) return;
    // Maximizes wheel size to fit the full available viewport height with zero scrolling
    const availableHeight = window.innerHeight - 120;
    const availableWidth = window.innerWidth - 32;
    const maxSize = Math.min(availableWidth, availableHeight, 660);
    const size = Math.max(300, maxSize);

    this.canvas.width = size * window.devicePixelRatio;
    this.canvas.height = size * window.devicePixelRatio;
    this.canvas.style.width = `${size}px`;
    this.canvas.style.height = `${size}px`;
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    this.size = size;
    this.center = size / 2;
    this.radius = (size / 2) - 18;

    // Proportion the center button nicely
    if (this.centerBtn) {
      const btnSize = Math.max(84, Math.min(size * 0.19, 106));
      this.centerBtn.style.width = `${btnSize}px`;
      this.centerBtn.style.height = `${btnSize}px`;
      const textSpan = this.centerBtn.querySelector('.spin-text');
      if (textSpan) textSpan.style.fontSize = `${btnSize * 0.22}px`;
    }
  }

  setHouses(activeHouses) {
    this.houses = activeHouses;
    this.draw();
  }

  draw() {
    if (!this.canvas || this.houses.length === 0) return;
    const ctx = this.ctx;
    const c = this.center;
    const r = this.radius;
    const count = this.houses.length;
    const sliceAngle = (Math.PI * 2) / count;

    ctx.clearRect(0, 0, this.size, this.size);

    ctx.save();
    ctx.translate(c, c);
    ctx.rotate(this.currentRotation);

    // Outer wheel soft drop shadow
    ctx.save();
    ctx.beginPath();
    ctx.arc(0, 0, r + 12, 0, Math.PI * 2);
    ctx.fillStyle = "#FFFFFF";
    ctx.shadowColor = "rgba(0, 0, 0, 0.12)";
    ctx.shadowBlur = 24;
    ctx.shadowOffsetY = 8;
    ctx.fill();

    // Outer white rim
    ctx.beginPath();
    ctx.arc(0, 0, r + 7, 0, Math.PI * 2);
    ctx.strokeStyle = "#FFFFFF";
    ctx.lineWidth = 14;
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(0, 0, r + 13, 0, Math.PI * 2);
    ctx.strokeStyle = "#E5E7EB";
    ctx.lineWidth = 2.5;
    ctx.stroke();
    ctx.restore();

    // Draw Slices
    for (let i = 0; i < count; i++) {
      const house = this.houses[i];
      const startAngle = i * sliceAngle;
      const endAngle = startAngle + sliceAngle;

      // Slice background
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.arc(0, 0, r, startAngle, endAngle);
      ctx.closePath();
      ctx.fillStyle = house.color;
      ctx.fill();

      // Clean white borders between slices
      ctx.strokeStyle = "#FFFFFF";
      ctx.lineWidth = 5;
      ctx.stroke();

      // Subtle gradient sheen
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.arc(0, 0, r, startAngle, endAngle);
      ctx.closePath();
      ctx.clip();

      const sheen = ctx.createRadialGradient(0, 0, r * 0.1, 0, 0, r);
      sheen.addColorStop(0, "rgba(255, 255, 255, 0.22)");
      sheen.addColorStop(0.65, "rgba(255, 255, 255, 0.0)");
      sheen.addColorStop(1, "rgba(0, 0, 0, 0.14)");
      ctx.fillStyle = sheen;
      ctx.fill();
      ctx.restore();

      // House Name: Large, bold, centered in the slice
      ctx.save();
      const midAngle = startAngle + sliceAngle / 2;
      ctx.rotate(midAngle);

      const isLightBg = house.color.toUpperCase() === "#EAB308" || house.color.toUpperCase() === "#FACC15";
      ctx.fillStyle = isLightBg ? "#111827" : "#FFFFFF";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      // Larger, prominent font size for the bigger wheel
      const fontSize = count <= 2 ? 26 : count <= 4 ? 21 : 18;
      ctx.font = `800 ${fontSize}px 'Plus Jakarta Sans', sans-serif`;

      if (isLightBg) {
        ctx.shadowColor = "rgba(255, 255, 255, 0.9)";
        ctx.shadowBlur = 4;
      } else {
        ctx.shadowColor = "rgba(0, 0, 0, 0.4)";
        ctx.shadowBlur = 5;
      }

      // Centered along slice radius
      const textRadius = r * 0.62;
      ctx.fillText(house.name.toUpperCase(), textRadius, 0);

      ctx.restore();
    }

    // Outer perimeter metallic studs
    const pinCount = Math.max(12, count * 3);
    for (let p = 0; p < pinCount; p++) {
      const pinAngle = (p / pinCount) * Math.PI * 2;
      const px = Math.cos(pinAngle) * (r + 5);
      const py = Math.sin(pinAngle) * (r + 5);

      ctx.beginPath();
      ctx.arc(px, py, 3.5, 0, Math.PI * 2);
      ctx.fillStyle = "#F3F4F6";
      ctx.strokeStyle = "#9CA3AF";
      ctx.lineWidth = 1.2;
      ctx.fill();
      ctx.stroke();
    }

    ctx.restore(); // restore wheel rotation

    // Center Hub Base Rim (The interactive HTML button sits exactly on top)
    ctx.save();
    ctx.beginPath();
    ctx.arc(c, c, 56, 0, Math.PI * 2);
    ctx.fillStyle = "#FFFFFF";
    ctx.shadowColor = "rgba(0, 0, 0, 0.15)";
    ctx.shadowBlur = 14;
    ctx.fill();

    ctx.beginPath();
    ctx.arc(c, c, 52, 0, Math.PI * 2);
    ctx.strokeStyle = "#EAB308";
    ctx.lineWidth = 5;
    ctx.stroke();
    ctx.restore();
  }

  spin() {
    if (this.isSpinning || this.houses.length === 0) return;
    this.isSpinning = true;

    if (this.centerBtn) {
      this.centerBtn.disabled = true;
    }

    // Completely random, cryptographically secure house selection
    let selectedIndex;
    if (window.crypto && window.crypto.getRandomValues) {
      const randomBuf = new Uint32Array(1);
      window.crypto.getRandomValues(randomBuf);
      selectedIndex = randomBuf[0] % this.houses.length;
    } else {
      selectedIndex = Math.floor(Math.random() * this.houses.length);
    }
    const selectedHouse = this.houses[selectedIndex];

    const count = this.houses.length;
    const sliceAngle = (Math.PI * 2) / count;

    const pointerAngle = (3 * Math.PI) / 2;
    
    // Natural landing position with random offset inside the winning slice
    const sliceMargin = 0.2 + (Math.random() * 0.6); // landing between 20% and 80% into the slice
    const sliceCenterRel = (selectedIndex + sliceMargin) * sliceAngle;
    
    // Completely random full spins between 6 and 9 turns
    const fullSpins = 6 + Math.floor(Math.random() * 4);
    const currentNormalized = (this.currentRotation % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2);
    
    let targetDelta = (pointerAngle - sliceCenterRel - currentNormalized);
    while (targetDelta < 0) {
      targetDelta += Math.PI * 2;
    }
    const totalRotationNeeded = (fullSpins * Math.PI * 2) + targetDelta;

    const startRotation = this.currentRotation;
    const targetRotation = startRotation + totalRotationNeeded;
    // Varied duration between 4.8s and 5.5s
    const duration = 4800 + Math.floor(Math.random() * 700);
    const startTime = performance.now();

    window.soundEngine.init();

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1.0);

      const ease = 1 - Math.pow(1 - progress, 3.4);
      this.currentRotation = startRotation + totalRotationNeeded * ease;

      const normalizedCurrent = (this.currentRotation % (Math.PI * 2) + (Math.PI * 2)) % (Math.PI * 2);
      const currentSlice = Math.floor((pointerAngle - normalizedCurrent + (Math.PI * 2)) % (Math.PI * 2) / sliceAngle);

      if (currentSlice !== this.lastTickSlice) {
        this.lastTickSlice = currentSlice;
        const freqMod = 1.0 - (progress * 0.3);
        window.soundEngine.playTick(freqMod);
      }

      this.draw();

      if (progress < 1.0) {
        requestAnimationFrame(animate);
      } else {
        this.isSpinning = false;
        this.currentRotation = targetRotation;
        this.draw();

        if (this.centerBtn) {
          this.centerBtn.disabled = false;
        }

        window.soundEngine.playFanfare();
        window.confettiEngine.burst(window.innerWidth / 2, window.innerHeight * 0.45, 65, [selectedHouse.color, "#FFFFFF", "#EAB308"]);

        if (typeof this.onSelectCallback === "function") {
          setTimeout(() => {
            this.onSelectCallback(selectedHouse);
          }, 600);
        }
      }
    };

    requestAnimationFrame(animate);
  }
}

window.SpinWheel = SpinWheel;

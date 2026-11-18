/**
 * Confetti & Celebration Particle Engine
 * Lightweight, zero-dependency canvas particle system
 */

class ConfettiEngine {
  constructor() {
    this.canvas = null;
    this.ctx = null;
    this.particles = [];
    this.animationId = null;
    this.defaultColors = [
      "#FACC15", "#3B82F6", "#EC4899", "#A855F7", "#F97316", "#EF4444", "#10B981", "#FFFFFF"
    ];
    this.init();
  }

  init() {
    this.canvas = document.createElement("canvas");
    this.canvas.id = "confettiCanvas";
    this.canvas.style.position = "fixed";
    this.canvas.style.top = "0";
    this.canvas.style.left = "0";
    this.canvas.style.width = "100vw";
    this.canvas.style.height = "100vh";
    this.canvas.style.pointerEvents = "none";
    this.canvas.style.zIndex = "9999";
    document.body.appendChild(this.canvas);

    this.ctx = this.canvas.getContext("2d");
    this.resize();
    window.addEventListener("resize", () => this.resize());
  }

  resize() {
    if (!this.canvas) return;
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }

  burst(x, y, count = 70, customColors = null) {
    const colors = customColors || this.defaultColors;
    const originX = x !== undefined ? x : window.innerWidth / 2;
    const originY = y !== undefined ? y : window.innerHeight / 2;

    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 4 + Math.random() * 12;
      this.particles.push({
        x: originX,
        y: originY,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 3,
        size: 6 + Math.random() * 8,
        color: colors[Math.floor(Math.random() * colors.length)],
        rotation: Math.random() * 360,
        rotationSpeed: (Math.random() - 0.5) * 14,
        opacity: 1,
        gravity: 0.28,
        friction: 0.96,
        life: 1.0,
        decay: 0.008 + Math.random() * 0.012,
        shape: Math.random() > 0.3 ? "rect" : "circle"
      });
    }

    if (!this.animationId) {
      this.loop();
    }
  }

  stageCannons(customColors = null) {
    const w = window.innerWidth;
    const h = window.innerHeight;
    const colors = customColors || this.defaultColors;

    // Left cannon
    for (let i = 0; i < 60; i++) {
      const angle = -Math.PI / 4 + (Math.random() - 0.5) * 0.5;
      const speed = 12 + Math.random() * 14;
      this.particles.push({
        x: 0,
        y: h * 0.85,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size: 7 + Math.random() * 8,
        color: colors[Math.floor(Math.random() * colors.length)],
        rotation: Math.random() * 360,
        rotationSpeed: (Math.random() - 0.5) * 15,
        opacity: 1,
        gravity: 0.32,
        friction: 0.97,
        life: 1.0,
        decay: 0.006 + Math.random() * 0.008,
        shape: "rect"
      });
    }

    // Right cannon
    for (let i = 0; i < 60; i++) {
      const angle = -Math.PI * 0.75 + (Math.random() - 0.5) * 0.5;
      const speed = 12 + Math.random() * 14;
      this.particles.push({
        x: w,
        y: h * 0.85,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size: 7 + Math.random() * 8,
        color: colors[Math.floor(Math.random() * colors.length)],
        rotation: Math.random() * 360,
        rotationSpeed: (Math.random() - 0.5) * 15,
        opacity: 1,
        gravity: 0.32,
        friction: 0.97,
        life: 1.0,
        decay: 0.006 + Math.random() * 0.008,
        shape: "rect"
      });
    }

    if (!this.animationId) {
      this.loop();
    }
  }

  loop() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];

      p.vx *= p.friction;
      p.vy *= p.friction;
      p.vy += p.gravity;

      p.x += p.vx;
      p.y += p.vy;

      p.rotation += p.rotationSpeed;
      p.life -= p.decay;
      p.opacity = Math.max(0, p.life);

      if (p.life <= 0 || p.y > this.canvas.height + 50) {
        this.particles.splice(i, 1);
        continue;
      }

      this.ctx.save();
      this.ctx.translate(p.x, p.y);
      this.ctx.rotate((p.rotation * Math.PI) / 180);
      this.ctx.globalAlpha = p.opacity;
      this.ctx.fillStyle = p.color;

      if (p.shape === "rect") {
        this.ctx.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2);
      } else {
        this.ctx.beginPath();
        this.ctx.arc(0, 0, p.size / 2, 0, Math.PI * 2);
        this.ctx.fill();
      }

      this.ctx.restore();
    }

    if (this.particles.length > 0) {
      this.animationId = requestAnimationFrame(() => this.loop());
    } else {
      this.animationId = null;
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
  }
}

window.confettiEngine = new ConfettiEngine();

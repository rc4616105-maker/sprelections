/**
 * Audio Engine powered by Web Audio API
 * Generates realistic procedural sound effects without relying on external audio files.
 */

class SoundEngine {
  constructor() {
    this.ctx = null;
    this.isMuted = false;
    this.scratchGainNode = null;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    return this.isMuted;
  }

  // Realistic mechanical click / wheel ticker sound
  playTick(frequencyModifier = 1.0) {
    if (this.isMuted) return;
    this.init();
    if (!this.ctx) return;

    try {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      const filter = this.ctx.createBiquadFilter();

      filter.type = "bandpass";
      filter.frequency.setValueAtTime(1400 * frequencyModifier, now);
      filter.Q.setValueAtTime(6.0, now);

      osc.type = "triangle";
      osc.frequency.setValueAtTime(800 * frequencyModifier, now);
      osc.frequency.exponentialRampToValueAtTime(120, now + 0.035);

      gain.gain.setValueAtTime(0.35, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.035);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 0.04);
    } catch (e) {
      console.warn("Audio tick error:", e);
    }
  }

  // Realistic scratch friction sound
  playScratch() {
    if (this.isMuted) return;
    this.init();
    if (!this.ctx) return;

    try {
      const now = this.ctx.currentTime;
      const bufferSize = this.ctx.sampleRate * 0.05; // 50ms buffer
      const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
      const data = buffer.getChannelData(0);

      for (let i = 0; i < bufferSize; i++) {
        data[i] = (Math.random() * 2 - 1) * 0.25;
      }

      const noise = this.ctx.createBufferSource();
      noise.buffer = buffer;

      const filter = this.ctx.createBiquadFilter();
      filter.type = "highpass";
      filter.frequency.value = 2200;

      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(0.2, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.05);

      noise.connect(filter);
      filter.connect(gain);
      gain.connect(this.ctx.destination);

      noise.start(now);
    } catch (e) {
      // ignore scratch audio interruption
    }
  }

  // Dramatic drumroll leading to reveal
  playDrumroll(duration = 1.2) {
    if (this.isMuted) return;
    this.init();
    if (!this.ctx) return;

    try {
      const now = this.ctx.currentTime;
      const interval = 0.055;
      const hits = Math.floor(duration / interval);

      for (let i = 0; i < hits; i++) {
        const hitTime = now + i * interval;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = "triangle";
        osc.frequency.setValueAtTime(140 + (i * 2), hitTime);
        osc.frequency.exponentialRampToValueAtTime(40, hitTime + 0.04);

        const volume = 0.08 + (i / hits) * 0.22;
        gain.gain.setValueAtTime(volume, hitTime);
        gain.gain.exponentialRampToValueAtTime(0.001, hitTime + 0.04);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(hitTime);
        osc.stop(hitTime + 0.05);
      }
    } catch (e) {
      console.warn("Drumroll audio error:", e);
    }
  }

  // Triumphant victory fanfare (Chord arpeggio + chime)
  playFanfare() {
    if (this.isMuted) return;
    this.init();
    if (!this.ctx) return;

    try {
      const now = this.ctx.currentTime;
      // C Major triumphant chord sequence (C4, G4, C5, E5, G5, C6)
      const notes = [
        { freq: 261.63, delay: 0.0,  duration: 0.2 }, // C4
        { freq: 392.00, delay: 0.12, duration: 0.2 }, // G4
        { freq: 523.25, delay: 0.24, duration: 0.25 }, // C5
        { freq: 659.25, delay: 0.38, duration: 0.3 }, // E5
        { freq: 783.99, delay: 0.52, duration: 0.35 }, // G5
        { freq: 1046.50, delay: 0.70, duration: 1.1 }  // High C6
      ];

      notes.forEach(note => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = "sine";
        osc.frequency.setValueAtTime(note.freq, now + note.delay);

        gain.gain.setValueAtTime(0.28, now + note.delay);
        gain.gain.exponentialRampToValueAtTime(0.001, now + note.delay + note.duration);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now + note.delay);
        osc.stop(now + note.delay + note.duration);
      });
    } catch (e) {
      console.warn("Fanfare audio error:", e);
    }
  }

  // Grand Finale Anthem
  playFinaleChime() {
    this.playFanfare();
    setTimeout(() => {
      this.playFanfare();
    }, 600);
  }
}

window.soundEngine = new SoundEngine();

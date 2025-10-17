"use strict";

// Dragon Quest - Web (HTML5 Canvas)
// Fixed version that waits for DOM

document.addEventListener('DOMContentLoaded', function() {
  const canvas = document.getElementById("game");
  if (!canvas) {
    console.error("Canvas not found!");
    return;
  }
  
  const ctx = canvas.getContext("2d");
  const W = canvas.width;
  const H = canvas.height;

  // World
  const WORLD_W = 3200;
  const WORLD_H = 3200;

  // Dragon
  const DRAGON_BASE_SPEED = 220;
  const DRAGON_DASH_SPEED = 420;
  const DRAGON_DASH_STAMINA_COST = 28;
  const DRAGON_MAX_STAMINA = 100;
  const DRAGON_STAMINA_RECOVERY = 22;
  const DRAGON_MAX_HEALTH = 100;

  // Fire
  const FIRE_COOLDOWN = 0.45;
  const FIRE_LIFETIME = 0.55;
  const FIRE_SPEED = 650;
  const FIRE_SPREAD_DEG = 10;
  const FIRE_CONE_PROJECTILES = 7;
  const FIRE_DAMAGE = 34;

  // Enemies
  const ENEMY_BASE_COUNT = 14;
  const ENEMY_SPEED = 120;
  const ENEMY_DAMAGE = 12;
  const ENEMY_MAX_HEALTH = 50;
  const ENEMY_SENSE_RADIUS = 360;

  // Pickups
  const LOOT_DROP_CHANCE = 0.35;

  // Boss
  const BOSS_RADIUS = 30;
  const BOSS_MAX_HEALTH = 900;
  const BOSS_SPEED = 150;
  const BOSS_TOUCH_DPS = 30;
  const BOSS_FIRE_COOLDOWN = 1.4;
  const BOSS_BURST_COUNT = 12;

  const keys = Object.create(null);
  const rng = mulberry32(1337);

  const state = {
    time: 0,
    paused: false,
    showHelp: true,
    camera: { x: 0, y: 0, w: W, h: H },
    dragon: {
      x: WORLD_W / 2,
      y: WORLD_H / 2,
      vx: 0,
      vy: 0,
      angle: 0,
      health: DRAGON_MAX_HEALTH,
      stamina: DRAGON_MAX_STAMINA,
      lastFireTime: -999,
      score: 0,
      level: 1,
      xp: 0,
      nextXp: 100,
      ability1ReadyAt: 0,
      ability2ReadyAt: 0,
    },
    enemies: [],
    bolts: [],
    hostileBolts: [],
    pickups: [],
    decor: createDecor(),
    level: 1,
    wave: 0,
    boss: null,
    bossLastFire: -999,
  };

  function mulberry32(a) {
    return function() {
      let t = (a += 0x6d2b79f5);
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function rand(min, max) {
    return min + (max - min) * rng();
  }

  function irand(min, max) {
    return Math.floor(rand(min, max + 1));
  }

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  function vec(deg) {
    const r = (deg * Math.PI) / 180;
    return { x: Math.cos(r), y: Math.sin(r) };
  }

  function createDecor() {
    const rects = [];
    for (let i = 0; i < 180; i++) {
      const w = irand(120, 420);
      const h = irand(80, 320);
      rects.push({ x: irand(0, WORLD_W - w), y: irand(0, WORLD_H - h), w, h, c: pick([[45,85,45],[35,75,35],[25,65,25]]) });
    }
    for (let i = 0; i < 80; i++) {
      const w = irand(140, 480);
      const h = irand(100, 420);
      rects.push({ x: irand(0, WORLD_W - w), y: irand(0, WORLD_H - h), w, h, c: pick([[30,90,130],[25,80,120]]) });
    }
    return rects;
  }

  function pick(arr) { return arr[Math.floor(rng() * arr.length)]; }

  function enemyScale() { return 1 + (state.level-1) * 0.25; }
  function bossScale() { return 1 + (state.level-1) * 0.35; }
  function rewardScale() { return 1 + (state.level-1) * 0.2; }

  function spawnEnemies(count) {
    for (let i = 0; i < count; i++) {
      state.enemies.push({
        x: rand(0, WORLD_W),
        y: rand(0, WORLD_H),
        vx: 0,
        vy: 0,
        health: Math.floor(ENEMY_MAX_HEALTH * enemyScale()),
        patrolDir: vec(rand(0, 360)),
        nextTurn: state.time + rand(1.0, 3.5),
        stunnedUntil: 0,
      });
    }
  }

  function spawnBoss() {
    state.boss = {
      x: rand(WORLD_W*0.2, WORLD_W*0.8),
      y: rand(WORLD_H*0.2, WORLD_H*0.8),
      vx: 0, vy: 0,
      health: Math.floor(BOSS_MAX_HEALTH * bossScale()),
    };
    state.bossLastFire = state.time - rand(0, BOSS_FIRE_COOLDOWN);
  }

  function canFire() {
    return (state.time - state.dragon.lastFireTime) >= FIRE_COOLDOWN;
  }

  function fireCone() {
    state.dragon.lastFireTime = state.time;
    for (let i = 0; i < FIRE_CONE_PROJECTILES; i++) {
      const t = (FIRE_CONE_PROJECTILES > 1) ? (i / (FIRE_CONE_PROJECTILES - 1)) : 0.5;
      const spread = (t - 0.5) * 2 * FIRE_SPREAD_DEG;
      const dir = vec(state.dragon.angle + spread);
      state.bolts.push({
        x: state.dragon.x,
        y: state.dragon.y,
        vx: dir.x * FIRE_SPEED,
        vy: dir.y * FIRE_SPEED,
        die: state.time + FIRE_LIFETIME,
        dmg: FIRE_DAMAGE,
      });
    }
  }

  function update(dt) {
    if (state.paused) return;

    // Movement
    const d = state.dragon;
    let mx = 0, my = 0;
    if (keys["w"] || keys["ArrowUp"]) my -= 1;
    if (keys["s"] || keys["ArrowDown"]) my += 1;
    if (keys["a"] || keys["ArrowLeft"]) mx -= 1;
    if (keys["d"] || keys["ArrowRight"]) mx += 1;
    let len = Math.hypot(mx, my);
    if (len > 0) { mx /= len; my /= len; d.angle = Math.atan2(my, mx) * 180/Math.PI; }

    let speed = DRAGON_BASE_SPEED;
    if ((keys["Shift"]) && d.stamina > 0) {
      speed = DRAGON_DASH_SPEED;
      d.stamina -= DRAGON_DASH_STAMINA_COST * dt;
    } else {
      d.stamina += DRAGON_STAMINA_RECOVERY * dt;
    }
    d.stamina = clamp(d.stamina, 0, DRAGON_MAX_STAMINA);

    d.vx = mx * speed; d.vy = my * speed;
    d.x = clamp(d.x + d.vx * dt, 0, WORLD_W);
    d.y = clamp(d.y + d.vy * dt, 0, WORLD_H);

    // Enemies
    for (const e of state.enemies) {
      const dx = d.x - e.x, dy = d.y - e.y;
      const dist = Math.hypot(dx, dy);
      if (state.time < e.stunnedUntil) {
        e.vx = 0; e.vy = 0;
      } else if (dist < ENEMY_SENSE_RADIUS) {
        const ndx = dx / (dist || 1), ndy = dy / (dist || 1);
        e.vx = ndx * ENEMY_SPEED; e.vy = ndy * ENEMY_SPEED;
      } else {
        if (state.time > e.nextTurn) {
          const dir = vec(rand(0, 360));
          e.patrolDir = dir; e.nextTurn = state.time + rand(1.0, 3.5);
        }
        e.vx = e.patrolDir.x * ENEMY_SPEED * 0.5; e.vy = e.patrolDir.y * ENEMY_SPEED * 0.5;
      }
      e.x = clamp(e.x + e.vx * dt, 0, WORLD_W);
      e.y = clamp(e.y + e.vy * dt, 0, WORLD_H);
    }

    // Projectiles
    const alive = [];
    for (const b of state.bolts) {
      if (state.time > b.die) continue;
      b.x += b.vx * dt; b.y += b.vy * dt;
      if (b.x >= 0 && b.x <= WORLD_W && b.y >= 0 && b.y <= WORLD_H) alive.push(b);
    }
    state.bolts = alive;

    // Hostile projectiles (boss)
    const aliveH = [];
    for (const b of state.hostileBolts) {
      if (state.time > b.die) continue;
      b.x += b.vx * dt; b.y += b.vy * dt;
      if (b.x >= 0 && b.x <= WORLD_W && b.y >= 0 && b.y <= WORLD_H) aliveH.push(b);
    }
    state.hostileBolts = aliveH;

    // Boss AI
    if (state.boss) {
      const bx = state.boss.x, by = state.boss.y;
      const dx = d.x - bx, dy = d.y - by; const dist = Math.hypot(dx, dy);
      const ndx = dx / (dist || 1), ndy = dy / (dist || 1);
      const keep = 260;
      let sp = BOSS_SPEED * 0.6;
      if (dist > keep) sp = BOSS_SPEED; else sp = -BOSS_SPEED * 0.4;
      state.boss.vx = ndx * sp; state.boss.vy = ndy * sp;
      state.boss.x = clamp(state.boss.x + state.boss.vx * dt, 0, WORLD_W);
      state.boss.y = clamp(state.boss.y + state.boss.vy * dt, 0, WORLD_H);

      if (state.time - state.bossLastFire >= BOSS_FIRE_COOLDOWN) {
        state.bossLastFire = state.time;
        const baseAngle = Math.atan2(ndy, ndx) * 180/Math.PI;
        for (let i=0;i<BOSS_BURST_COUNT;i++) {
          const a = baseAngle - 40 + (i*(80/(BOSS_BURST_COUNT-1)));
          const v = vec(a); const speed = 420 + 120*rng();
          state.hostileBolts.push({ x: bx, y: by, vx: v.x*speed, vy: v.y*speed, die: state.time + 2.5, dmg: 18 });
        }
      }
    }

    // Collisions: dragon vs enemies (touch damage)
    for (const e of state.enemies) {
      if (Math.hypot(e.x - d.x, e.y - d.y) < 28) {
        d.health = Math.max(0, d.health - ENEMY_DAMAGE * enemyScale() * dt * 8);
      }
    }
    if (state.boss && Math.hypot(state.boss.x - d.x, state.boss.y - d.y) < (BOSS_RADIUS+6)) {
      d.health = Math.max(0, d.health - BOSS_TOUCH_DPS * dt);
    }

    // Hostile bolts vs dragon
    const keepHB = [];
    for (const b of state.hostileBolts) {
      if (Math.hypot(b.x - d.x, b.y - d.y) < 16) {
        d.health = Math.max(0, d.health - (b.dmg||12));
        continue;
      }
      keepHB.push(b);
    }
    state.hostileBolts = keepHB;

    // Collisions: projectiles vs enemies
    for (const b of state.bolts) {
      for (const e of state.enemies) {
        if (Math.hypot(e.x - b.x, e.y - b.y) < 24 && e.health > 0) {
          e.health -= b.dmg; b.die = 0;
          const dx = e.x - b.x, dy = e.y - b.y; const dl = Math.hypot(dx, dy) || 1;
          e.x += (dx/dl) * 12; e.y += (dy/dl) * 12;
          if (e.health <= 0) {
            maybeDropLoot(e.x, e.y);
            const xp = Math.floor(20 * rewardScale());
            d.score += 25; addXp(xp);
          }
        }
      }
      if (state.boss && Math.hypot(state.boss.x - b.x, state.boss.y - b.y) < (BOSS_RADIUS+6)) {
        state.boss.health -= b.dmg; b.die = 0;
        if (state.boss.health <= 0) {
          const xp = Math.floor(200 * rewardScale());
          d.score += 500; addXp(xp);
          state.boss = null;
          state.wave = 0;
          state.level += 1;
          startNextLevel();
        }
      }
    }

    // Dragon vs pickups
    const remain = [];
    for (const p of state.pickups) {
      if (Math.hypot(p.x - d.x, p.y - d.y) < 28) {
        if (p.kind === "gold") d.score += p.value; else d.health = Math.min(DRAGON_MAX_HEALTH, d.health + p.value);
      } else {
        remain.push(p);
      }
    }
    state.pickups = remain;

    // Camera
    state.camera.x = clamp(Math.floor(d.x - W/2), 0, WORLD_W - W);
    state.camera.y = clamp(Math.floor(d.y - H/2), 0, WORLD_H - H);
  }

  function maybeDropLoot(x, y) {
    if (rng() < LOOT_DROP_CHANCE) {
      if (rng() < 0.7) state.pickups.push({ kind: "gold", x, y, value: irand(5, 20) });
      else state.pickups.push({ kind: "heart", x, y, value: irand(10, 25) });
    }
  }

  function draw() {
    const cam = state.camera;
    // base
    ctx.fillStyle = "#3c7a3c";
    ctx.fillRect(0, 0, W, H);

    // decor
    for (const r of state.decor) {
      if (rectIntersects(r, cam, 200)) {
        ctx.fillStyle = `rgb(${r.c[0]},${r.c[1]},${r.c[2]})`;
        ctx.fillRect(Math.floor(r.x - cam.x), Math.floor(r.y - cam.y), r.w, r.h);
      }
    }

    // pickups
    for (const p of state.pickups) {
      const x = Math.floor(p.x - cam.x), y = Math.floor(p.y - cam.y);
      if (p.kind === "gold") {
        circle(x, y, 6, "#e6be14");
        ring(x, y, 6, "#ffd23c");
      } else {
        heart(x, y, 10, "#c82846");
      }
    }

    // enemies
    for (const e of state.enemies) {
      const x = Math.floor(e.x - cam.x), y = Math.floor(e.y - cam.y);
      circle(x, y, 18, "#282828");
      circle(x, y, 16, "#b23232");
      const pct = clamp(e.health / (ENEMY_MAX_HEALTH * enemyScale()), 0, 1);
      ring(x, y, 20, `rgb(${Math.floor(255*(1-pct))},${Math.floor(255*pct)},40)`);
    }

    // bolts
    for (const b of state.bolts) {
      const x = Math.floor(b.x - cam.x), y = Math.floor(b.y - cam.y);
      circle(x, y, 5, "#ff9628");
      circle(x, y, 3, "#ffe69c");
    }

    // hostile bolts
    for (const b of state.hostileBolts) {
      const x = Math.floor(b.x - cam.x), y = Math.floor(b.y - cam.y);
      circle(x, y, 4, "#9933ff");
      ring(x, y, 6, "#cc99ff");
    }

    // dragon triangle
    const d = state.dragon;
    const dir = vec(d.angle); const perp = { x: -dir.y, y: dir.x };
    const tip = { x: d.x + dir.x*22, y: d.y + dir.y*22 };
    const left = { x: d.x - dir.x*12 + perp.x*14, y: d.y - dir.y*12 + perp.y*14 };
    const right = { x: d.x - dir.x*12 - perp.x*14, y: d.y - dir.y*12 - perp.y*14 };
    polygon([
      { x: tip.x - cam.x, y: tip.y - cam.y },
      { x: left.x - cam.x, y: left.y - cam.y },
      { x: right.x - cam.x, y: right.y - cam.y },
    ], "#3c3c3c", "#32b4dc", 2);

    // Boss
    if (state.boss) {
      const bx = Math.floor(state.boss.x - cam.x), by = Math.floor(state.boss.y - cam.y);
      circle(bx, by, BOSS_RADIUS+4, "#101010");
      circle(bx, by, BOSS_RADIUS, "#663399");
      const pct = clamp(state.boss.health / (BOSS_MAX_HEALTH * bossScale()), 0, 1);
      ring(bx, by, BOSS_RADIUS+8, `rgb(${Math.floor(255*(1-pct))},${Math.floor(255*pct)},200)`);
    }

    // HUD
    hud();

    if (state.paused) centerText("Paused - Press P to resume");
    if (state.showHelp) helpOverlay();

    minimap();
  }

  function hud() {
    // left panel
    fillRect(10, 10, 350, 86, "#000");
    fillRect(W-220, 10, 210, 86, "#000");

    // health
    const d = state.dragon;
    const hpPct = clamp(d.health / DRAGON_MAX_HEALTH, 0, 1);
    fillRect(18, 18, 330, 18, "#782828");
    fillRect(18, 18, Math.floor(330*hpPct), 18, "#dc3c3c");
    text("Health", 22, 32, 14, "#fff");

    // stamina
    const stPct = clamp(d.stamina / DRAGON_MAX_STAMINA, 0, 1);
    fillRect(18, 42, 330, 18, "#222850");
    fillRect(18, 42, Math.floor(330*stPct), 18, "#3c64d4");
    text("Stamina", 22, 56, 14, "#fff");

    // fire cooldown
    const since = state.time - d.lastFireTime;
    const cdPct = clamp(since / FIRE_COOLDOWN, 0, 1);
    fillRect(18, 66, 330, 18, "#5a2c00");
    fillRect(18, 66, Math.floor(330*cdPct), 18, "#ffa028");
    text("Fire", 22, 80, 14, "#fff");

    text(`Score: ${Math.floor(d.score)}`, W-208, 28, 16, "#fff");
    text("P: Pause  H/?: Help", W-208, 52, 14, "#ddd");
    text("Esc: Quit tab", W-208, 74, 14, "#ddd");

    // XP/Level panel
    fillRect(10, 104, 420, 54, "#000");
    const xpPct = clamp(state.dragon.xp / state.dragon.nextXp, 0, 1);
    fillRect(18, 112, 404, 18, "#1b2540");
    fillRect(18, 112, Math.floor(404*xpPct), 18, "#3aa3ff");
    text(`Level ${state.dragon.level}  XP ${Math.floor(state.dragon.xp)}/${state.dragon.nextXp}`, 22, 126, 14, "#fff");
    const a1Ready = state.time >= state.dragon.ability1ReadyAt;
    const a2Ready = state.time >= state.dragon.ability2ReadyAt;
    text(`1: Roar ${a1Ready?"READY":"..."}   2: Nova ${a2Ready?"READY":"..."}`, 22, 146, 14, "#ddd");
  }

  function helpOverlay() {
    const lines = [
      "Dragon Quest - Web",
      "WASD/Arrows to move, Shift dash",
      "Space to breathe fire",
      "1: Roar (stun), 2: Nova (radial fire)",
      "Pick up gold and hearts",
      "Roaming enemies chase if close",
      "P to pause, H/? for help",
    ];
    const x = 12; const y = H - 18 * (lines.length + 1);
    fillRect(x - 4, y - 6, 460, 24 + 18 * lines.length, "#000");
    for (let i = 0; i < lines.length; i++) text(lines[i], x, y + i*18 + 12, 14, "#eee");
  }

  function centerText(t) {
    ctx.font = "bold 28px Verdana, sans-serif";
    const m = ctx.measureText(t);
    fillRect(W/2 - m.width/2 - 10, H/2 - 24, m.width + 20, 42, "#000");
    ctx.fillStyle = "#fff";
    ctx.fillText(t, W/2 - m.width/2, H/2 + 8);
  }

  // Drawing helpers
  function fillRect(x, y, w, h, c) { ctx.fillStyle = c; ctx.fillRect(Math.floor(x), Math.floor(y), Math.floor(w), Math.floor(h)); }
  function text(t, x, y, size, c) { ctx.fillStyle = c; ctx.font = `${size}px Verdana, sans-serif`; ctx.fillText(t, x, y); }
  function circle(x, y, r, c) { ctx.fillStyle = c; ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI*2); ctx.fill(); }
  function ring(x, y, r, c) { ctx.strokeStyle = c; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI*2); ctx.stroke(); }
  function polygon(pts, fill, stroke, lw=1) { ctx.beginPath(); ctx.moveTo(pts[0].x, pts[0].y); for (let i=1;i<pts.length;i++) ctx.lineTo(pts[i].x, pts[i].y); ctx.closePath(); ctx.fillStyle = fill; ctx.fill(); ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); }
  function heart(x, y, size, c) {
    ctx.fillStyle = c;
    circle(x - size*0.3, y, size*0.35, c);
    circle(x + size*0.3, y, size*0.35, c);
    ctx.beginPath();
    ctx.moveTo(x - size*0.6, y);
    ctx.lineTo(x + size*0.6, y);
    ctx.lineTo(x, y + size*0.8);
    ctx.closePath();
    ctx.fill();
  }

  function rectIntersects(r, cam, pad=0) {
    return !(r.x + r.w < cam.x - pad || r.x > cam.x + cam.w + pad || r.y + r.h < cam.y - pad || r.y > cam.y + cam.h + pad);
  }

  // Input
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") { window.close?.(); return; }
    keys[e.key] = true;
    if (e.key === " ") { // space
      if (!state.paused && canFire()) fireCone();
      e.preventDefault();
    }
    if (e.key.toLowerCase() === "p") state.paused = !state.paused;
    if (e.key.toLowerCase() === "h" || e.key === "?") state.showHelp = !state.showHelp;
    if (e.key === "1") tryAbility1();
    if (e.key === "2") tryAbility2();
  });
  window.addEventListener("keyup", (e) => { keys[e.key] = false; });

  // Level/Wave System
  function startNextLevel() {
    state.enemies = [];
    state.hostileBolts = [];
    state.boss = null;
    state.wave = 1;
    const count = Math.floor(ENEMY_BASE_COUNT * enemyScale());
    spawnEnemies(count);
  }

  function checkWaves() {
    if (!state.boss) {
      const alive = state.enemies.filter(e => e.health > 0);
      if (alive.length === 0) {
        if (state.wave === 1) {
          state.wave = 2;
          spawnEnemies(Math.floor(ENEMY_BASE_COUNT * 0.8 * enemyScale()));
        } else if (state.wave === 2) {
          state.wave = 3;
          spawnBoss();
        }
      }
    }
  }

  // XP/Level/Abilities
  function addXp(amount) {
    state.dragon.xp += amount;
    while (state.dragon.xp >= state.dragon.nextXp) {
      state.dragon.xp -= state.dragon.nextXp;
      state.dragon.level += 1;
      state.dragon.nextXp = Math.floor(state.dragon.nextXp * 1.6);
      state.dragon.health = Math.min(DRAGON_MAX_HEALTH, state.dragon.health + 25);
    }
  }

  function tryAbility1() {
    if (state.time < state.dragon.ability1ReadyAt) return;
    state.dragon.ability1ReadyAt = state.time + 8;
    const radius = 220;
    for (const e of state.enemies) {
      if (Math.hypot(e.x - state.dragon.x, e.y - state.dragon.y) <= radius) {
        e.stunnedUntil = state.time + 2.5;
      }
    }
    pulse(state.dragon.x, state.dragon.y, radius, "rgba(50,180,255,0.25)");
  }

  function tryAbility2() {
    if (state.time < state.dragon.ability2ReadyAt) return;
    if (state.dragon.level < 3) return;
    state.dragon.ability2ReadyAt = state.time + 12;
    const bolts = 28;
    for (let i=0;i<bolts;i++) {
      const a = (i/bolts)*360;
      const dir = vec(a);
      state.bolts.push({ x: state.dragon.x, y: state.dragon.y, vx: dir.x*FIRE_SPEED*0.75, vy: dir.y*FIRE_SPEED*0.75, die: state.time + 0.6, dmg: FIRE_DAMAGE });
    }
    pulse(state.dragon.x, state.dragon.y, 180, "rgba(255,160,40,0.25)");
  }

  const pulses = [];
  function pulse(x, y, r, color) { pulses.push({x,y,r,color,t: state.time, life: 0.35}); }
  const _draw = draw;
  draw = function() {
    _draw();
    const cam = state.camera; const keep = [];
    for (const p of pulses) {
      const age = state.time - p.t; if (age < p.life) {
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(Math.floor(p.x - cam.x), Math.floor(p.y - cam.y), p.r * (1 + age*0.4), 0, Math.PI*2);
        ctx.fill();
        keep.push(p);
      }
    }
    pulses.length = 0; for (const k of keep) pulses.push(k);
  }

  // Minimap
  function minimap() {
    const size = 160;
    const x = W - size - 12; const y = H - size - 12;
    fillRect(x-2, y-2, size+4, size+4, "#000");
    fillRect(x, y, size, size, "#1f2f1f");
    const sx = size / WORLD_W; const sy = size / WORLD_H;
    ctx.fillStyle = "#2b512b";
    for (let i=0;i<state.decor.length;i+=8) {
      const r = state.decor[i];
      ctx.fillRect(x + Math.floor(r.x * sx), y + Math.floor(r.y * sy), Math.max(1, Math.floor(r.w * sx)), Math.max(1, Math.floor(r.h * sy)));
    }
    for (const p of state.pickups) {
      ctx.fillStyle = p.kind === "gold" ? "#ffd23c" : "#c82846";
      ctx.fillRect(x + Math.floor(p.x * sx)-1, y + Math.floor(p.y * sy)-1, 3, 3);
    }
    ctx.fillStyle = "#ff5555";
    for (const e of state.enemies) ctx.fillRect(x + Math.floor(e.x * sx), y + Math.floor(e.y * sy), 2, 2);
    if (state.boss) { ctx.fillStyle = "#cc99ff"; ctx.fillRect(x + Math.floor(state.boss.x * sx)-2, y + Math.floor(state.boss.y * sy)-2, 4, 4); }
    ctx.fillStyle = "#32b4dc";
    ctx.fillRect(x + Math.floor(state.dragon.x * sx)-2, y + Math.floor(state.dragon.y * sy)-2, 4, 4);
    text(`L${state.level} W${state.wave}${state.boss?" Boss":""}`, x+8, y+16, 14, "#fff");
  }

  // Bootstrap
  startNextLevel();

  let last = performance.now() / 1000;
  function loop() {
    const t = performance.now() / 1000; const dt = Math.min(0.05, t - last); last = t; state.time += dt;
    update(dt);
    checkWaves();
    draw();
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
});
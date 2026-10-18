// 背景点阵：每个点记着自己的网格位置，在附近 3–6px 内朝随机方向慢慢晃，整体网格不散。
(function () {
  var canvas = document.getElementById("dots");
  if (!canvas) return;

  var ctx = canvas.getContext("2d");
  var darkQuery = matchMedia("(prefers-color-scheme: dark)");
  var motion = matchMedia("(prefers-reduced-motion: reduce)");
  var dots = [];
  var w = 0;
  var h = 0;
  var color = "";
  var raf = 0;
  var last = 0;
  var mobile = matchMedia("(max-width: 30rem)");
  var GAP = 24;   // 和原来的点阵间距一致
  var RAD = 1;    // 点的半径
  var driftMin = 3;
  var driftSpan = 3;

  function isDark() {
    var t = document.documentElement.dataset.theme;
    return t ? t === "dark" : darkQuery.matches;
  }

  function draw() {
    if (!dots.length) return;
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = color;
    ctx.beginPath();
    for (var i = 0; i < dots.length; i++) {
      var d = dots[i];
      ctx.moveTo(d.x + RAD, d.y);
      ctx.arc(d.x, d.y, RAD, 0, Math.PI * 2);
    }
    ctx.fill();
  }

  function setColor() {
    var light = !isDark();
    var alpha = mobile.matches ? (light ? "0.13" : "0.10") : (light ? "0.15" : "0.11");
    color = light ? "rgba(23, 25, 28, " + alpha + ")" : "rgba(231, 231, 228, " + alpha + ")";
    draw();
  }

  function resize() {
    var dpr = Math.min(devicePixelRatio || 1, 2);
    w = innerWidth;
    h = innerHeight;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // 手机上点更小更密，漂移范围也按比例收，网格感更稳。
    GAP = mobile.matches ? 18 : 24;
    RAD = mobile.matches ? 0.75 : 1;
    driftMin = mobile.matches ? 2 : 3;
    driftSpan = mobile.matches ? 2 : 3;

    dots = [];
    for (var y = GAP / 2; y < h; y += GAP) {
      for (var x = GAP / 2; x < w; x += GAP) {
        dots.push({
          hx: x,
          hy: y,
          x: x,
          y: y,
          a: Math.random() * Math.PI * 2,        // 方向
          v: 0.8 + Math.random() * 1.4,          // px/s
          va: (Math.random() - 0.5) * 0.5,       // 方向缓慢拐弯
          r: driftMin + Math.random() * driftSpan  // 离家最远 3–6px（手机 2–4px）
        });
      }
    }
    setColor();   // 跨断点时透明度也要跟着换
    start();
  }

  function frame(now) {
    raf = requestAnimationFrame(frame);
    var dt = Math.min((now - last) / 1000, 0.05);
    last = now;

    for (var i = 0; i < dots.length; i++) {
      var d = dots[i];
      d.a += d.va * dt;
      d.x += Math.cos(d.a) * d.v * dt;
      d.y += Math.sin(d.a) * d.v * dt;

      var dx = d.x - d.hx;
      var dy = d.y - d.hy;
      var dist = Math.sqrt(dx * dx + dy * dy);
      if (dist > d.r) {
        // 到了自己的边界：转回家那边，顺带拐个随机弯，免得每颗点来回走直线。
        d.a = Math.atan2(-dy, -dx) + (Math.random() - 0.5) * 1.2;
        d.x = d.hx + (dx / dist) * d.r;
        d.y = d.hy + (dy / dist) * d.r;
      }
    }
    draw();
  }

  function start() {
    if (motion.matches) { draw(); return; }
    if (raf) return;
    last = performance.now();
    raf = requestAnimationFrame(frame);
  }

  darkQuery.addEventListener("change", setColor);
  motion.addEventListener("change", function () {
    if (motion.matches) { cancelAnimationFrame(raf); raf = 0; draw(); }
    else start();
  });
  var toggle = document.getElementById("theme-toggle");
  if (toggle) toggle.addEventListener("click", setColor);

  // 手机地址栏缩放也会触发 resize，等稳定再重排。
  var timer;
  addEventListener("resize", function () {
    clearTimeout(timer);
    timer = setTimeout(resize, 150);
  });

  setColor();
  resize();
})();

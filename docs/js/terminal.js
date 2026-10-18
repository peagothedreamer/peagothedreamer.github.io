// 彩蛋：从底部滑出一个能敲命令的假终端。
// 结构和 <template id="term-ls"> 都在 baseof.html 里。
(function () {
  var term = document.getElementById("term");
  if (!term) return;

  var out = document.getElementById("term-out");
  var form = document.getElementById("term-form");
  var input = document.getElementById("term-in");
  var banner = document.querySelector(".banner");
  var lsTemplate = document.getElementById("term-ls");
  var open = false;
  var motion = matchMedia("(prefers-reduced-motion: reduce)");

  function scroll() { out.scrollTop = out.scrollHeight; }

  // 纯文本输出，不拼 HTML。
  function print(text, cls) {
    var p = document.createElement("p");
    if (cls) p.className = cls;
    p.textContent = text;
    out.appendChild(p);
    scroll();
    return p;
  }

  // 左往右从乱码里解出目标句子。乱码每 90ms 换一茬，不是每帧都在闪。
  function decode(el, target, dur) {
    var glyphs = "!<>-_\\/[]{}=+*^?#abcdefghijklmnopqrstuvwxyz0123456789";
    var start = performance.now();
    var lastNoise = 0;
    var noise = "";

    function noiseAt(n) {
      var s = "";
      for (var i = 0; i < n; i++) {
        s += glyphs.charAt(Math.floor(Math.random() * glyphs.length));
      }
      return s;
    }

    function tick(now) {
      var p = Math.min((now - start) / dur, 1);
      var settled = Math.floor(p * target.length);
      if (now - lastNoise >= 90) {
        noise = noiseAt(target.length);
        lastNoise = now;
      }
      el.textContent = target.slice(0, settled) + noise.slice(settled);
      scroll();
      if (p < 1) requestAnimationFrame(tick);
      else el.textContent = target;
    }
    requestAnimationFrame(tick);
  }

  function dream() {
    var line = print("you are already dreaming.");
    setTimeout(function () {
      if (motion.matches) { line.textContent = "have a nice day."; scroll(); return; }
      decode(line, "have a nice day.", 1300);
    }, 1500);
  }

  var commands = {
    help: function () {
      ["help", "whoami", "ls", "dream", "theme", "exit"]
        .forEach(function (line) { print(line, "dim"); });
    },
    whoami: function () { print("peago — the dreamer."); },
    ls: function () {
      if (lsTemplate) { out.appendChild(lsTemplate.content.cloneNode(true)); scroll(); }
    },
    dream: dream,
    theme: function () {
      document.getElementById("theme-toggle").click();   // 复用现有切换逻辑
      print("switched to " + document.documentElement.dataset.theme + ".");
    },
    exit: function () { closeTerm(); },
    sudo: function () { print("nice try."); }
  };

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var raw = input.value.trim();
    input.value = "";
    if (!raw) return;
    print("> " + raw, "dim");
    var fn = commands[raw.toLowerCase()];
    if (fn) fn(); else print("command not found: " + raw);
  });

  function openTerm() {
    open = true;
    term.classList.add("on");
    if (!out.childNodes.length) {
      print("peago shell. type 'help'.", "dim");
    }
    input.focus();
  }

  function closeTerm() {
    open = false;
    term.classList.remove("on");
    input.blur();
  }

  // 打开时清掉选区，免得图片带着选中框。
  var taps = 0;
  var timer;
  if (banner) {
    banner.addEventListener("click", function () {
      if (open) return;
      taps++;
      clearTimeout(timer);
      if (taps >= 3) {
        taps = 0;
        var sel = getSelection();
        if (sel) sel.removeAllRanges();
        openTerm();
      } else {
        timer = setTimeout(function () { taps = 0; }, 600);
      }
    });
  }

  document.addEventListener("keydown", function (e) {
    if (open && e.key === "Escape") closeTerm();
  });

  document.addEventListener("click", function (e) {
    // isTrusted：theme 命令里程序化的 click 不该把面板关掉。
    if (!open || !e.isTrusted || term.contains(e.target) ||
        (banner && banner.contains(e.target))) return;
    closeTerm();
  });
})();

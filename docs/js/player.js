// 正文里的播放器（audio / album 短代码）。原生 <audio> 藏起来当引擎，控件在 HTML 里。
// 进度条是 <input type=range>，0–1000 按比例换算成秒，省得每次 loadedmetadata 改 max。
// 单曲和专辑共用这一份：专辑比单曲多一个 .tracks 列表，列表空的就是单曲。
// 只在用了短代码的页面加载（baseof.html 里的 .HasShortcode 判断）。
(function () {
  var clock = function (s) {
    if (!isFinite(s)) return "0:00";
    return Math.floor(s / 60) + ":" + String(Math.floor(s % 60)).padStart(2, "0");
  };

  var roots = [].slice.call(document.querySelectorAll(".player"));

  // 页面上不止一个播放器时先掐掉别的，免得两首歌叠在一起。
  var only = function (keep) {
    roots.forEach(function (root) {
      var a = root.querySelector("audio");
      if (a !== keep) a.pause();
    });
  };

  roots.forEach(function (root) {
    var audio = root.querySelector("audio");
    var btn = root.querySelector(".play");
    var seek = root.querySelector(".seek");
    var time = root.querySelector(".time");
    // 专辑播放器才有曲目列表；单曲那个列表是空的，标题靠 HTML 里写死的那行。
    var list = [].slice.call(root.querySelectorAll(".track"));
    var title = root.querySelector(".player-title");
    var at = 0;

    var paint = function () {
      seek.value = audio.duration ? (audio.currentTime / audio.duration) * 1000 : 0;
      time.textContent = clock(audio.currentTime) + " / " + clock(audio.duration);
      btn.textContent = audio.paused ? "▶" : "❚❚";
      btn.setAttribute("aria-label", audio.paused ? "播放" : "暂停");
    };

    // 换到第 i 首。autoplay=false 只装填不播放（初始化用）。
    // 卡片第一行跟着换成这一首的曲名（第二行是歌手 · 专辑名，不动）。
    var select = function (i, autoplay) {
      at = i;
      audio.src = list[i].dataset.src;
      if (title) title.textContent = list[i].dataset.title;
      seek.value = 0;
      time.textContent = "0:00 / 0:00";
      list.forEach(function (el, n) {
        el.classList.toggle("on", n === i);
        el.setAttribute("aria-current", n === i ? "true" : "false");
      });
      if (autoplay) { only(audio); audio.play(); }
    };

    list.forEach(function (el, i) {
      el.addEventListener("click", function () { select(i, true); });
    });

    btn.addEventListener("click", function () {
      if (!audio.paused) return audio.pause();
      only(audio);
      audio.play();
    });

    seek.addEventListener("input", function () {
      if (audio.duration) audio.currentTime = (seek.value / 1000) * audio.duration;
    });

    ["timeupdate", "loadedmetadata", "play", "pause"].forEach(function (e) {
      audio.addEventListener(e, paint);
    });

    // 一首放完接下一首，最后一首放完就停。
    audio.addEventListener("ended", function () {
      if (at + 1 < list.length) select(at + 1, true);
      else paint();
    });

    // 链接挂了（release 资产改名、本地文件被删）别装死，给个字。
    audio.addEventListener("error", function () {
      time.textContent = "加载失败";
    });

    if (list.length) select(0, false);
    paint();
  });
})();

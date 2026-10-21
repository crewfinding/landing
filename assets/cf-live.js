/* Live feature cards. Declarative: any element with data-at="seconds" gets class "on" at that time after the card scrolls into view.
   data-until="seconds" turns it off again, data-say="TEXT" sets the card's status line, data-num="1840" counts up (with data-pre, data-suf, data-dec).
   Reduced motion, or no IntersectionObserver, shows the finished state at once. Vanilla, no dependencies. */
(function(){
  var reduced = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  function fmt(el, v){
    var s = v.toFixed(+el.dataset.dec || 0).split(".");
    s[0] = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return (el.dataset.pre || "") + s.join(".") + (el.dataset.suf || "");
  }
  function count(el, instant){
    var to = +el.dataset.num;
    cancelAnimationFrame(el._raf);
    if(instant || reduced){ el.textContent = fmt(el, to); return; }
    var t0 = performance.now(), dur = 1100;
    (function step(now){
      var k = Math.min(1, (now - t0) / dur);
      el.textContent = fmt(el, to * (1 - Math.pow(1 - k, 3)));
      if(k < 1) el._raf = requestAnimationFrame(step);
    })(t0);
  }
  function observe(root, fn, threshold){
    if(reduced || !("IntersectionObserver" in window)) return false;
    var io = new IntersectionObserver(function(es){
      es.forEach(function(en){ if(en.isIntersecting){ io.disconnect(); fn(); } });
    }, {threshold: threshold || .3});
    io.observe(root);
    return true;
  }

  function initLive(root){
    var items = Array.prototype.slice.call(root.querySelectorAll("[data-at]")),
        status = root.querySelector("[data-lstatus]"), btn = root.querySelector("[data-lreplay]"), timers = [];
    function say(txt){
      if(!status || !txt) return;
      status.textContent = txt;
      status.classList.remove("tick"); void status.offsetWidth;
      if(!reduced) status.classList.add("tick");
    }
    function reset(){
      timers.forEach(clearTimeout); timers = [];
      root.classList.remove("lv-static");
      items.forEach(function(el){
        el.classList.remove("on");
        if(el.dataset.num){ cancelAnimationFrame(el._raf); el.textContent = fmt(el, 0); }
      });
      if(status) status.textContent = status.dataset.init || "";
    }
    function on(el){ el.classList.add("on"); if(el.dataset.say) say(el.dataset.say); if(el.dataset.num) count(el); }
    function play(){
      reset();
      items.forEach(function(el){
        timers.push(setTimeout(function(){ on(el); }, (+el.dataset.at) * 1000));
        if(el.dataset.until) timers.push(setTimeout(function(){ el.classList.remove("on"); }, (+el.dataset.until) * 1000));
      });
    }
    function final(){
      reset(); root.classList.add("lv-static");
      var last = "";
      items.slice().sort(function(a, b){ return (+a.dataset.at) - (+b.dataset.at); }).forEach(function(el){
        if(el.dataset.until) return;
        el.classList.add("on");
        if(el.dataset.say) last = el.dataset.say;
        if(el.dataset.num) count(el, true);
      });
      if(status && last) status.textContent = last;
    }
    reset();
    if(btn) btn.addEventListener("click", function(){ if(!reduced) play(); });
    if(!observe(root, play, .3)){ final(); if(btn) btn.hidden = true; }
  }
  document.querySelectorAll("[data-live]").forEach(initLive);

  /* languages: the owner reads English, the foreman reads the same job in his own language. The foreman's side cycles while it is on screen. */
  var LANG = [
    {n: "Português", w: "FOREMAN · PORTUGUÊS", t: ["Começar o trabalho", "Colher a assinatura", "Tirar a foto do depois", "Total do trabalho"]},
    {n: "Español",   w: "FOREMAN · ESPAÑOL",   t: ["Empezar el trabajo", "Conseguir la firma", "Tomar la foto del final", "Total del trabajo"]},
    {n: "Français",  w: "FOREMAN · FRANÇAIS",  t: ["Commencer le travail", "Obtenir la signature", "Prendre la photo finale", "Total du travail"]},
    {n: "Polski",    w: "FOREMAN · POLSKI",    t: ["Rozpocznij pracę", "Zbierz podpis", "Zrób zdjęcie po pracy", "Suma zlecenia"]}
  ];
  function initLang(root){
    var who = root.querySelector("[data-lgwho]"), lis = Array.prototype.slice.call(root.querySelectorAll("[data-lglist] li")),
        chips = Array.prototype.slice.call(root.querySelectorAll("[data-lg]")), cur = 0, timer = 0, vis = false;
    function show(i, fade){
      var L = LANG[i];
      function apply(){
        who.textContent = L.w;
        lis.forEach(function(li, k){ li.querySelector("span").textContent = L.t[k]; li.classList.remove("sw"); });
        chips.forEach(function(c, k){ c.classList.toggle("on", k === i); });
      }
      if(!fade){ apply(); return; }
      lis.forEach(function(li){ li.classList.add("sw"); });
      setTimeout(apply, 300);
    }
    function tick(){ cur = (cur + 1) % LANG.length; show(cur, true); }
    function start(){ if(timer) return; timer = setInterval(tick, 2600); }
    function stop(){ clearInterval(timer); timer = 0; }
    show(0, false);
    if(reduced || !("IntersectionObserver" in window)) return;
    new IntersectionObserver(function(es){
      es.forEach(function(en){ vis = en.isIntersecting; if(vis) start(); else stop(); });
    }, {threshold: .35}).observe(root);
  }
  document.querySelectorAll("[data-lang]").forEach(initLang);
})();

/* story: photo stage + six beats. Each beat's progress bar ends with animationend, which advances to the next beat. */
(function(){
  var reduced = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.querySelectorAll("[data-story]").forEach(function(root){
    var slides = Array.prototype.slice.call(root.querySelectorAll(".st-slide")), items = Array.prototype.slice.call(root.querySelectorAll(".st-list li"));
    function show(i){
      items.forEach(function(li, k){ li.classList.remove("on"); li.querySelector("button").setAttribute("aria-current", "false"); if(k === i) li.classList.add("on"); });
      slides.forEach(function(s, k){ s.classList.toggle("on", k === i); });
      items[i].querySelector("button").setAttribute("aria-current", "true");
    }
    items.forEach(function(li, i){
      li.querySelector("button").addEventListener("click", function(){ show(i); });
      li.querySelector(".st-bar").addEventListener("animationend", function(){ show((i + 1) % items.length); });
    });
    root.addEventListener("mouseenter", function(){ root.classList.add("paused"); });
    root.addEventListener("mouseleave", function(){ root.classList.remove("paused"); });
    root.addEventListener("focusin", function(){ root.classList.add("paused"); });
    root.addEventListener("focusout", function(){ root.classList.remove("paused"); });
    show(0);
    if(reduced || !("IntersectionObserver" in window)) return;
    new IntersectionObserver(function(es){ es.forEach(function(en){ root.classList.toggle("run", en.isIntersecting); }); }, {threshold: .35}).observe(root);
  });
})();

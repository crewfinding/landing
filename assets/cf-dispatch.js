/* Shipment journey: pickup BOL, live GPS, signed hand-off to a third-party carrier, signed offload. Vanilla, no dependencies. */
(function(){
  function emit(n){ document.dispatchEvent(new CustomEvent("cfflow",{detail:n})); }
  var reduced = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var X1 = 70, XA = 345, XB0 = 428, X3 = 650;
  var SAY = ["WAITING FOR PICKUP","PICKED UP · BOL SIGNED","IN TRANSIT · YOUR TRUCK 2 · GPS LIVE","HANDED OFF · CARRIER B SIGNED","IN TRANSIT · CARRIER B · GPS LIVE","DELIVERED · OFFLOAD SIGNED"];
  function ease(t){ return t<.5 ? 4*t*t*t : 1-Math.pow(-2*t+2,3)/2; }
  function lerp(a,b,t){ return a+(b-a)*t; }
  function clamp01(v){ return Math.max(0,Math.min(1,v)); }
  function hm(m){ m = Math.round(m); var h = Math.floor(m/60); return (h<10?"0":"") + h + ":" + (m%60<10?"0":"") + (m%60); }
  function init(root){
    var $ = function(s){ return root.querySelector(s); }, $$ = function(s){ return root.querySelectorAll(s); };
    var A = $("[data-a]"), B = $("[data-b]"), prog = $("[data-prog]"), status = $("[data-status]"), clock = $("[data-clock]"),
        rows = $$("[data-row]"), nodes = $$("[data-node]"), badges = $$("[data-badge]"), replay = $("[data-replay]");
    var stage = -1, raf = 0, t0 = 0;
    function say(i){
      var own = root.getAttribute("data-say"), arr = own ? JSON.parse(own) : SAY;
      status.textContent = arr[i]; status.classList.toggle("done", i === 5);
      status.classList.remove("tick"); void status.offsetWidth; if(!reduced) status.classList.add("tick");
    }
    function done(i){
      nodes[i].classList.add("on"); badges[i].classList.add("on"); badges[i].querySelector("text").textContent = "✓";
      if(!reduced){ nodes[i].classList.remove("ping"); void nodes[i].getBoundingClientRect(); nodes[i].classList.add("ping"); }
    }
    function reset(){
      stage = -1; B.classList.add("dim"); A.classList.remove("dim");
      nodes.forEach(function(n,i){ n.classList.remove("on","ping"); badges[i].classList.remove("on"); badges[i].querySelector("text").textContent = String(i+1); });
      rows.forEach(function(r){ r.classList.remove("on"); });
      A.setAttribute("transform","translate("+X1+",68)"); B.setAttribute("transform","translate("+XB0+",68)");
      prog.setAttribute("x2", X1); say(0); clock.textContent = "--:--";
    }
    function enter(s){
      stage = s; say(s);
      if(s === 1){ done(0); rows[0].classList.add("on");  emit(4); }
      if(s === 2){ rows[1].classList.add("on"); }
      if(s === 3){ done(1); rows[2].classList.add("on"); A.classList.add("dim"); B.classList.remove("dim"); }
      if(s === 5){ done(2); rows[3].classList.add("on");  emit(5); }
    }
    function frame(now){
      var t = (now - t0)/1000, s = t >= 8.4 ? 5 : t >= 5.6 ? 4 : t >= 4.4 ? 3 : t >= 1.6 ? 2 : t >= .6 ? 1 : 0;
      while(stage < s) enter(stage+1);
      var ax = lerp(X1, XA, ease(clamp01((t-1.6)/2.8))), bx = lerp(XB0, X3, ease(clamp01((t-5.6)/2.8)));
      A.setAttribute("transform","translate("+ax.toFixed(1)+",68)"); B.setAttribute("transform","translate("+bx.toFixed(1)+",68)");
      prog.setAttribute("x2", (s >= 4 ? bx : ax).toFixed(1));
      var m = t < .6 ? null : t < 1.6 ? 502 : t < 4.4 ? lerp(502,700,(t-1.6)/2.8) : t < 5.6 ? 700 : t < 8.4 ? lerp(700,905,(t-5.6)/2.8) : 905;
      clock.textContent = m === null ? "--:--" : hm(m);
      if(t < 9.2) raf = requestAnimationFrame(frame); else raf = 0;
    }
    function play(){ cancelAnimationFrame(raf); reset(); t0 = performance.now(); raf = requestAnimationFrame(frame); }
    function final(){
      reset(); for(var s = 1; s <= 5; s++) enter(s);
      A.setAttribute("transform","translate("+XA+",68)"); B.setAttribute("transform","translate("+X3+",68)");
      prog.setAttribute("x2", X3); clock.textContent = "15:05";
      nodes.forEach(function(n){ n.classList.remove("ping"); });
    }
    reset();
    if(replay) replay.addEventListener("click", function(){ if(!reduced) play(); });
    if(reduced || !("IntersectionObserver" in window)){ final(); if(replay) replay.hidden = true; return; }
    var io = new IntersectionObserver(function(es){
      es.forEach(function(en){ if(en.isIntersecting){ io.disconnect(); play(); } });
    },{threshold:.5});
    io.observe(root);
  }
  document.querySelectorAll("[data-shipment]").forEach(init);

  /* five-step strip: lights up as the board and then the shipment card play */
  document.querySelectorAll("[data-flow]").forEach(function(flow){
    var max = 0, lis = flow.querySelectorAll("li");
    function lit(n){ if(n <= max) return; max = n; lis.forEach(function(li){ li.classList.toggle("on", +li.dataset.s <= max); }); }
    document.addEventListener("cfflow", function(e){ lit(e.detail); });
    if(reduced) lit(5);
  });

  /* dispatch board: jobs are assigned to a fleet truck, a broker and a 3PL carrier, and each shows when it is received */
  function initBoard(root){
    var $$ = function(s){ return Array.prototype.slice.call(root.querySelectorAll(s)); };
    var jobs = $$("[data-job]"), lanes = $$("[data-lane]"), sum = root.querySelector("[data-sum]"), btn = root.querySelector("[data-board-replay]");
    var BASE = [0.5, 3.3, 6.1], RECV = [1.2, 1.7, 2.3], ACC = [1.15, 1.2, 1.25], timers = [], got = 0;
    function T(fn, s){ timers.push(setTimeout(fn, s*1000)); }
    function chip(l, k){ lanes[l].querySelector('[data-rc="'+k+'"]').classList.add("on"); }
    function settle(){ sum.textContent = got + " OF 3 RECEIVED" + (got === 3 ? " · ALL ACCEPTED" : ""); }
    function reset(){
      timers.forEach(clearTimeout); timers = []; got = 0;
      jobs.forEach(function(j){ j.style.transform = ""; j.style.width = ""; j.classList.remove("placed"); });
      $$("[data-rc]").forEach(function(i){ i.classList.remove("on"); });
      lanes.forEach(function(l){ l.querySelector(".db-route").classList.remove("on"); });
      sum.textContent = "0 OF 3 RECEIVED";
    }
    function move(i){
      var a = jobs[i].getBoundingClientRect(), b = lanes[i].querySelector("[data-slot]").getBoundingClientRect();
      jobs[i].style.transform = "translate(" + (b.left - a.left).toFixed(1) + "px," + (b.top - a.top).toFixed(1) + "px)";
      jobs[i].classList.add("placed");
      if(window.matchMedia("(max-width:900px)").matches) jobs[i].style.width = b.width.toFixed(1) + "px";
    }
    function play(){
      reset(); emit(1);
      lanes.forEach(function(l, i){
        var t = BASE[i];
        T(function(){ move(i); if(i === 0) emit(2); }, t);
        T(function(){ chip(i, "sent"); }, t + .9);
        T(function(){ chip(i, "recv"); got++; settle(); if(got === 1) emit(3); }, t + .9 + RECV[i]);
        T(function(){ chip(i, "acc"); l.querySelector(".db-route").classList.add("on"); settle(); }, t + .9 + RECV[i] + ACC[i]);
      });
    }
    function final(){
      reset(); got = 3; settle();
      jobs.forEach(function(j, i){ j.style.transition = "none"; move(i); });
      lanes.forEach(function(l, i){ ["sent","recv","acc"].forEach(function(k){ chip(i, k); }); l.querySelector(".db-route").classList.add("on"); });
      emit(3);
    }
    reset();
    if(btn) btn.addEventListener("click", function(){ if(!reduced) play(); });
    if(reduced || !("IntersectionObserver" in window)){ final(); if(btn) btn.hidden = true; return; }
    var io = new IntersectionObserver(function(es){ es.forEach(function(en){ if(en.isIntersecting){ io.disconnect(); play(); } }); }, {threshold:.12});
    io.observe(root);
  }
  document.querySelectorAll("[data-board]").forEach(initBoard);
})();

/* CrewFinding card clips: plays the short muted clip inside .clip[data-src] when it scrolls into view.
   data-mode="loop" loops (and pauses off-screen); anything else plays once and holds its last frame.
   Skipped entirely for reduced-motion and data-saver, where the poster still stays. */
(function(){
"use strict";
var reduce=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches;
var save=navigator.connection&&navigator.connection.saveData;
if(reduce||save||!("IntersectionObserver" in window))return;
function make(el){
  var v=document.createElement("video");
  v.muted=true;v.defaultMuted=true;v.playsInline=true;v.setAttribute("playsinline","");
  v.setAttribute("aria-hidden","true");v.tabIndex=-1;v.preload="auto";
  if(el.getAttribute("data-mode")==="loop")v.loop=true;
  v.addEventListener("playing",function(){el.classList.add("live");},{once:true});
  v.src=el.getAttribute("data-src");
  el.appendChild(v);
  return v;
}
function play(v){var p=v.play();if(p&&p.catch)p.catch(function(){});}
var io=new IntersectionObserver(function(es){
  es.forEach(function(en){
    var el=en.target,v=el.querySelector("video"),loop=el.getAttribute("data-mode")==="loop";
    if(en.isIntersecting){
      if(!v)v=make(el);
      if(loop||!el.getAttribute("data-done")){play(v);}
      if(!loop){el.setAttribute("data-done","1");io.unobserve(el);}
    }else if(v&&loop){v.pause();}
  });
},{threshold:.55});
document.querySelectorAll(".clip[data-src]").forEach(function(e){io.observe(e);});
})();

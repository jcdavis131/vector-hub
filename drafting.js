// Drafting Board theme toggle — paper default, night-board dark. Zero deps.
(function(){
  var KEY="dm-theme";
  function apply(t){
    document.documentElement.setAttribute("data-theme",t);
    try{localStorage.setItem(KEY,t);}catch(e){}
    var b=document.getElementById("themeToggle");
    if(b)b.textContent=(t==="night"?"paper":"night");
  }
  function init(){
    var t=null;
    try{t=localStorage.getItem(KEY);}catch(e){}
    if(!t)t=(window.matchMedia&&window.matchMedia("(prefers-color-scheme: dark)").matches)?"night":"paper";
    apply(t);
    var b=document.getElementById("themeToggle");
    if(b)b.addEventListener("click",function(){
      apply(document.documentElement.getAttribute("data-theme")==="night"?"paper":"night");
    });
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);
  else init();
})();

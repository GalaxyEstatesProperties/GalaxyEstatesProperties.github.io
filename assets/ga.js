(function(){var K="gep-analytics",ID="G-QXRN29DKLR",v=null,on=!1;try{v=localStorage.getItem(K)}catch(e){}
function load(){if(on)return;on=!0;window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};gtag("js",new Date);gtag("config",ID);var s=document.createElement("script");s.async=!0;s.src="https://www.googletagmanager.com/gtag/js?id="+ID;document.head.appendChild(s)}
function save(x){try{localStorage.setItem(K,x)}catch(e){}}
function clear(){document.cookie.split(";").forEach(function(c){var n=c.split("=")[0].trim();if(/^_ga/.test(n))["",location.hostname,"."+location.hostname.replace(/^www\./,"")].forEach(function(d){document.cookie=n+"=; Max-Age=0; path=/"+(d?"; domain="+d:"")})})}
function bar(){var b=document.querySelector(".consent-bar");if(b){b.hidden=!1;return}b=document.createElement("div");b.className="consent-bar";b.setAttribute("role","dialog");b.setAttribute("aria-label","Analytics choice");
b.innerHTML='<p>May we use Google Analytics cookies to count visits and improve this site? Nothing is used to identify you, and you can change this any time. <a href="privacy.html">Privacy notice</a></p><div><button type="button" data-a="yes">Allow</button><button type="button" data-a="no">Don’t allow</button></div>';
b.addEventListener("click",function(e){var a=e.target.getAttribute("data-a");if(!a)return;save(a);b.hidden=!0;if(a==="yes")load();else{clear();if(on)location.reload()}});document.body.appendChild(b)}
if(v==="yes")load();
function init(){if(v!=="yes"&&v!=="no")bar();document.addEventListener("click",function(e){if(e.target.closest&&e.target.closest("[data-analytics-choice]"))bar()})}
document.readyState==="loading"?document.addEventListener("DOMContentLoaded",init):init()})();

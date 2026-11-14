// Shared behaviour for every page. The site works without this file;
// it only adds the mobile menu, dark mode, reveal animations and event tracking.
(function () {
  window.tr = function (n, p) { try { if (window.gtag) gtag("event", n, p || {}); } catch (e) {} };
  var $ = function (id) { return document.getElementById(id); };
  var mm = $("mm"), hb = $("hbtn"), tb = $("tb"), nav = $("nav");
  function closeMenu() { if (!mm) return; mm.classList.remove("o"); hb && hb.classList.remove("o"); hb && hb.setAttribute("aria-expanded", "false"); document.body.style.overflow = ""; }
  if (hb && mm) {
    hb.setAttribute("aria-expanded", "false");
    hb.addEventListener("click", function () {
      var o = mm.classList.toggle("o"); hb.classList.toggle("o", o);
      hb.setAttribute("aria-expanded", String(o)); document.body.style.overflow = o ? "hidden" : "";
    });
    mm.addEventListener("click", function (e) { if (e.target.closest("a")) closeMenu(); });
  }
  var dark = false;
  try { dark = localStorage.getItem("dark") === "1"; } catch (e) {}
  function setDark(on) { document.body.toggleAttribute("data-dark", on); if (tb) tb.textContent = on ? "☀️" : "🌙"; try { localStorage.setItem("dark", on ? "1" : "0"); } catch (e) {} }
  if (dark) setDark(true);
  if (tb) tb.addEventListener("click", function () { setDark(!document.body.hasAttribute("data-dark")); });
  if (nav) window.addEventListener("scroll", function () { nav.classList.toggle("up", scrollY > 20); }, { passive: true });
  document.addEventListener("click", function (e) {
    var a = e.target.closest("[data-tr]"); if (!a) return;
    var p = a.getAttribute("data-tr").split(":"); window.tr(p[0], { l: p[1] });
  });
  var els = document.querySelectorAll(".fi");
  if ("IntersectionObserver" in window) {
    var obs = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("vis"); obs.unobserve(e.target); } }); }, { threshold: 0.05 });
    els.forEach(function (el) { obs.observe(el); });
  } else els.forEach(function (el) { el.classList.add("vis"); });
})();

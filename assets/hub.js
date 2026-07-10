/* dumbmodel.com hub — scroll-spy for the sticky nav.
 * The nav wraps on small screens the same way the games' .site-nav does,
 * so there's no toggle to wire up — just active-section highlighting. */
(function () {
  'use strict';

  var links = Array.prototype.slice.call(
    document.querySelectorAll('.site-nav__link[href^="#"]')
  );
  var sections = [];

  links.forEach(function (link) {
    var id = link.getAttribute('href').slice(1);
    var el = document.getElementById(id);
    if (el) sections.push({ id: id, el: el, link: link });
  });

  if (!sections.length || !('IntersectionObserver' in window)) return;

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      var id = entry.target.id;
      links.forEach(function (link) {
        var active = link.getAttribute('href') === '#' + id;
        link.classList.toggle('is-active', active);
        if (active) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
      });
    });
  }, { rootMargin: '-45% 0px -45% 0px', threshold: 0 });

  sections.forEach(function (s) { observer.observe(s.el); });
})();

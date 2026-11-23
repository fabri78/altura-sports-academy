/* =====================================================================
   ALTURA Sports Academy · main.js
   Interacciones mínimas. Sin JavaScript el sitio sigue siendo legible:
   todo el contenido es visible y los estilos no dependen de este archivo.
   ===================================================================== */
(function () {
  'use strict';

  var raiz = document.documentElement;
  raiz.classList.remove('no-js');
  raiz.classList.add('js');

  var reducido = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 1. Componentes de Material Design ---------- */
  var snackbar = null;
  function iniciarMDC() {
    if (!window.mdc) return;
    window.mdc.autoInit();
    var el = document.getElementById('snackbar');
    if (el) snackbar = new window.mdc.snackbar.MDCSnackbar(el);
  }

  function avisar(texto) {
    if (snackbar) {
      snackbar.labelText = texto;
      snackbar.open();
    }
  }

  /* ---------- 2. Aparición al hacer scroll ---------- */
  function iniciarReveal() {
    var elementos = document.querySelectorAll('[data-reveal]');
    if (!('IntersectionObserver' in window) || reducido) {
      elementos.forEach(function (el) { el.classList.add('is-visible'); });
      return;
    }
    var obs = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('is-visible');
          obs.unobserve(e.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    elementos.forEach(function (el) { obs.observe(el); });
  }

  /* ---------- 3. Contadores de cifras ---------- */
  function iniciarContadores() {
    var nums = document.querySelectorAll('[data-contar]');
    if (!nums.length || !('IntersectionObserver' in window)) return;
    var obs = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target;
        var fin = parseFloat(el.getAttribute('data-contar'));
        var sufijo = el.getAttribute('data-sufijo') || '';
        var inicio = performance.now();
        var duracion = reducido ? 0 : 1400;
        (function paso(ahora) {
          var t = duracion ? Math.min((ahora - inicio) / duracion, 1) : 1;
          var valor = Math.round(fin * (1 - Math.pow(1 - t, 3)));
          el.textContent = valor.toLocaleString('es-PE') + sufijo;
          if (t < 1) requestAnimationFrame(paso);
        })(inicio);
        obs.unobserve(el);
      });
    }, { threshold: 0.6 });
    nums.forEach(function (n) { obs.observe(n); });
  }

  /* ---------- 4. Galería horizontal con flechas y puntos ---------- */
  function iniciarGalerias() {
    document.querySelectorAll('[data-galeria]').forEach(function (galeria) {
      var pista = galeria.querySelector('.galeria-h__track');
      var items = Array.prototype.slice.call(pista.children);
      var dots = galeria.querySelector('.galeria-h__dots');
      var prev = galeria.querySelector('[data-dir="-1"]');
      var next = galeria.querySelector('[data-dir="1"]');
      var actual = 0;

      items.forEach(function (item, i) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'galeria-h__dot';
        b.setAttribute('aria-label', 'Ir al elemento ' + (i + 1));
        b.addEventListener('click', function () { ir(i); });
        dots.appendChild(b);
      });

      function ir(i) {
        var destino = items[Math.max(0, Math.min(items.length - 1, i))];
        pista.scrollTo({ left: destino.offsetLeft - items[0].offsetLeft, behavior: reducido ? 'auto' : 'smooth' });
      }

      function marcar(i) {
        actual = i;
        items.forEach(function (it, j) { it.classList.toggle('is-activo', j === i); });
        Array.prototype.forEach.call(dots.children, function (d, j) {
          d.setAttribute('aria-current', j === i ? 'true' : 'false');
        });
        if (prev) prev.disabled = i === 0;
        if (next) next.disabled = i === items.length - 1;
      }

      if (prev) prev.addEventListener('click', function () { ir(actual - 1); });
      if (next) next.addEventListener('click', function () { ir(actual + 1); });

      var obs = new IntersectionObserver(function (entradas) {
        entradas.forEach(function (e) {
          if (e.isIntersecting) marcar(items.indexOf(e.target));
        });
      }, { root: pista, threshold: 0.6 });
      items.forEach(function (it) { obs.observe(it); });
      marcar(0);
    });
  }

  /* ---------- 5. Sección fija con scroll (pasos) ---------- */
  function iniciarHistorias() {
    document.querySelectorAll('.sticky-story').forEach(function (historia) {
      var pasos = historia.querySelectorAll('.step');
      var medios = historia.querySelectorAll('.sticky-story__media > *');
      function activar(i) {
        pasos.forEach(function (p, j) { p.classList.toggle('is-activo', j === i); });
        medios.forEach(function (m, j) { m.classList.toggle('is-activo', j === i); });
      }
      var obs = new IntersectionObserver(function (entradas) {
        entradas.forEach(function (e) {
          if (e.isIntersecting) activar(Array.prototype.indexOf.call(pasos, e.target));
        });
      }, { rootMargin: '-45% 0px -45% 0px' });
      pasos.forEach(function (p) { obs.observe(p); });
      activar(0);
    });
  }

  /* ---------- 6. Pestañas de Material Design ---------- */
  function iniciarPestanas() {
    document.querySelectorAll('[data-pestanas]').forEach(function (grupo) {
      var barra = grupo.querySelector('.mdc-tab-bar');
      var paneles = grupo.querySelectorAll('.panel');
      if (!barra) return;
      barra.addEventListener('MDCTabBar:activated', function (e) {
        paneles.forEach(function (p, i) { p.hidden = i !== e.detail.index; });
      });
    });
  }

  /* ---------- 7. Filtros y orden del catálogo ---------- */
  function iniciarCatalogo() {
    var catalogo = document.querySelector('[data-catalogo]');
    if (!catalogo) return;
    var productos = Array.prototype.slice.call(catalogo.querySelectorAll('.producto'));
    var chips = document.querySelectorAll('[data-filtro]');
    var orden = document.querySelector('[data-orden]');
    var contador = document.querySelector('[data-resultados]');

    function aplicar() {
      var activos = Array.prototype.filter.call(chips, function (c) { return c.checked; })
        .map(function (c) { return c.value; });
      var visibles = 0;
      productos.forEach(function (p) {
        var ok = !activos.length || activos.indexOf(p.getAttribute('data-cat')) > -1;
        p.hidden = !ok;
        if (ok) visibles += 1;
      });
      if (contador) contador.textContent = visibles + (visibles === 1 ? ' producto' : ' productos');
    }

    function ordenar() {
      var criterio = orden.value;
      productos.sort(function (a, b) {
        var pa = parseFloat(a.getAttribute('data-precio'));
        var pb = parseFloat(b.getAttribute('data-precio'));
        if (criterio === 'menor') return pa - pb;
        if (criterio === 'mayor') return pb - pa;
        return parseInt(a.getAttribute('data-orden'), 10) - parseInt(b.getAttribute('data-orden'), 10);
      }).forEach(function (p) { catalogo.appendChild(p); });
    }

    chips.forEach(function (c) { c.addEventListener('change', aplicar); });
    if (orden) orden.addEventListener('change', ordenar);
    aplicar();
  }

  /* ---------- 8. Carrito (solo demostración visual) ---------- */
  function iniciarCarrito() {
    var contador = document.querySelector('.carrito-contador');
    var total = 0;
    document.querySelectorAll('[data-carrito]').forEach(function (b) {
      b.addEventListener('click', function () {
        total += 1;
        if (contador) {
          contador.textContent = total;
          contador.classList.remove('is-nuevo');
          void contador.offsetWidth;
          contador.classList.add('is-nuevo');
        }
        avisar(b.getAttribute('data-carrito') + ' se agregó al carrito.');
      });
    });
  }

  /* ---------- 9. Formularios (validación HTML5 + confirmación) ---------- */
  function iniciarFormularios() {
    document.querySelectorAll('form[data-form]').forEach(function (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (!form.checkValidity()) {
          form.reportValidity();
          return;
        }
        var tipo = form.getAttribute('data-form');
        var mensaje = form.getAttribute('data-ok') || 'Recibimos tus datos.';
        if (tipo === 'reclamo') {
          var n = String(Math.floor(Math.random() * 9000) + 1000);
          mensaje = 'Registramos tu hoja N.° 2026-' + n + '. Te responderemos en un plazo máximo de 15 días hábiles.';
        }
        var ok = form.querySelector('.form-ok');
        if (ok) {
          ok.textContent = mensaje;
          ok.hidden = false;
          ok.focus();
        }
        avisar(mensaje);
        form.reset();
      });
    });
  }

  /* ---------- 10. Menú móvil: cerrar al elegir una opción ---------- */
  function iniciarMenu() {
    var toggle = document.getElementById('menu-toggle');
    if (!toggle) return;
    document.querySelectorAll('.menu a').forEach(function (a) {
      a.addEventListener('click', function () { toggle.checked = false; });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') toggle.checked = false;
    });
  }

  function iniciar() {
    iniciarMDC();
    iniciarReveal();
    iniciarContadores();
    iniciarGalerias();
    iniciarHistorias();
    iniciarPestanas();
    iniciarCatalogo();
    iniciarCarrito();
    iniciarFormularios();
    iniciarMenu();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
})();

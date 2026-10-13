// Enlaces a las graficas interactivas (_static/interactivas/<gid>.html) desde cualquier nivel de la
// documentacion: Sphinx publica la raiz relativa de cada pagina en <html data-content_root>.
document.addEventListener("DOMContentLoaded", function () {
  var raiz = document.documentElement.dataset.content_root ||
    (window.DOCUMENTATION_OPTIONS && window.DOCUMENTATION_OPTIONS.URL_ROOT) || "";
  document.querySelectorAll("a[data-grafica]").forEach(function (a) {
    a.href = raiz + "_static/interactivas/" + a.dataset.grafica + ".html";
  });
});

// Gráfica de la portada: en pantallas angostas se desplaza dentro de su recuadro; se abre mostrando el final de la
// serie, donde está la ventana de transacciones.
document.addEventListener("DOMContentLoaded", function () {
  var c = document.querySelector(".ea-impacto");
  if (c && c.scrollWidth > c.clientWidth) {
    c.scrollLeft = c.scrollWidth;
  }
});

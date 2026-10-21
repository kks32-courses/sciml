// Fold the code of notebook cells tagged hide-input behind a Show code button.
function foldTaggedCode() {
  document.querySelectorAll('.celltag_hide-input').forEach(function (cell) {
    var input = cell.querySelector('.jp-Cell-inputWrapper');
    if (!input || cell.querySelector('.code-toggle')) return;
    input.classList.add('code-folded');
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'code-toggle';
    button.textContent = 'Show code';
    button.setAttribute('aria-expanded', 'false');
    button.addEventListener('click', function () {
      var folded = input.classList.toggle('code-folded');
      button.textContent = folded ? 'Show code' : 'Hide code';
      button.setAttribute('aria-expanded', String(!folded));
    });
    input.parentNode.insertBefore(button, input);
  });
}

document.addEventListener('DOMContentLoaded', foldTaggedCode);
if (typeof document$ !== 'undefined') {
  document$.subscribe(foldTaggedCode);
}

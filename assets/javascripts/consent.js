/*
  Cookie consent: make "Accept" mean "accept all".

  The consent options start unticked (mkdocs.yml, extra.consent.cookies),
  because pre-ticked boxes don't count as consent. Material's Accept button
  saves exactly the boxes that are ticked, so on its own it would now
  accept nothing.

  This runs before Material's submit handler. When "Manage settings" is
  closed, Accept ticks every option first, so it accepts everything. When
  it's open, the visitor is choosing individually, so Accept saves only
  what they ticked. Reject is unaffected: it unticks everything.
*/
document.addEventListener("click", function (event) {
  var accept = event.target.closest(".md-consent__controls button:not([type=reset])");
  if (!accept) return;

  var settings = document.getElementById("__settings");
  if (settings && settings.checked) return;  // choosing individually

  for (var input of document.forms.consent.elements) {
    if (input.name) input.checked = true;
  }
}, true);

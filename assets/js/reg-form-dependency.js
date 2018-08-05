'use strict';
/* Factory returning a function that shows or hides dependent based on the
 * value of the bound element.
 * If showDependents is provided, it is called to determine visible state,
 * rather than examining the bound element.
 */
function dependentVisibility(dependent, showDependents) {
  var showDependents = showDependents;
  return function() {
    if (!showDependents) {
      if (this.type == 'checkbox') {
        showDependents = function() { return this.checked };
      } else {
        showDependents = function() { return this.value };
      }
    }
    var target = dependent;
    if (target.get(0).tagName != 'FIELDSET') {
      target = target.parents('.form-group');
    }
    if (showDependents.call(this)) {
      target.show();
    } else {
      target.hide();
    }
  };
}
/* Add an event handler to controller, when it changes value, dependent is
 * shown/hidden as appropriate.
 * By default a boolean evaluation is done of controller's value. If
 * showDependents is specified, this function is called instead (with
 * controller bound), to evaluate the state.
 */
function hookDependentVisibility(controller, dependent, showDependents) {
  var updateVisibility = dependentVisibility(dependent, showDependents);
  controller.change(updateVisibility);
  controller.each(updateVisibility);
};

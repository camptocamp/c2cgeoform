var c2cgeoform = {};

/**
 * This module provides convenience methods to make it easier to use
 * c2cgeoform with jQuery Steps.
 */
c2cgeoform.steps = {};

/**
 * Returns true if all fields on the step page with the given index
 * are valid.
 */
c2cgeoform.steps.lastStepIsValid = function(stepFormId, stepIndex) {
  return jQuery(stepFormId)
    .children('.content')
    .children(stepFormId + '-p-' + stepIndex)
    .find('.has-error')
    .size() <= 0;
}

/**
 * Get the number of steps.
 */
c2cgeoform.steps.getLastStepIndex = function(stepFormId) {
  // FIXME see https://github.com/rstaib/jquery-steps/pull/87
  return jQuery(stepFormId).data('state').stepCount;
}

/**
 * Go to the given step.
 */
c2cgeoform.steps.goToStep = function(stepFormId, current, target) {
  // FIXME see https://github.com/rstaib/jquery-steps/pull/67
  var stepsToGo = target - current;
  for (var i = 0; i < stepsToGo; i++) {
    jQuery(stepFormId).steps('next');
  }
}

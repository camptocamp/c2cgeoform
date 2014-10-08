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

/**
 * Initialize JQuery Steps.
 */
c2cgeoform.steps.init = function(options) {
  var form = $(options.stepsContainerId);
  var silent = false;

  form.steps({
    headerTag: options.headerTag,
    bodyTag: options.bodyTag,
    enableAllSteps: false,
    onStepChanging: function (event, currentIndex, newIndex) {
      // store the current step in a hidden field, so that the next step
      // can be restored after the form is submitted
      jQuery(options.customDataFieldId).val(currentIndex);
      if (newIndex < currentIndex) {
        // going backwards
        return true;
      } else if (silent) {
        return true;
      } else {
        var only_validate = 1;
        if (newIndex == c2cgeoform.steps.getLastStepIndex(options.stepsContainerId)) {
          // when on the last step, store the form data when validation successful
          only_validate = 0;
        }
        jQuery().val(only_validate);
        jQuery(options.formId).submit();
        return false;
      }
    },
    onFinishing: function (event, currentIndex) {
      jQuery(options.onlyValidateFieldId).val(0);
      jQuery(options.formId).submit();
      return true;
    },
    onStepChanged: function (event, currentIndex, priorIndex) {
      // call reinitMaps after a timeout to work around render issues on Chrome
      window.setTimeout(c2cgeoform.reinitMaps, 1);
    },
    onInit: function (event, currentIndex) {
      var lastIndex = parseInt(jQuery(options.customDataFieldId).val());
      var stepToGoTo;
      if (c2cgeoform.steps.lastStepIsValid(options.stepsContainerId, lastIndex)) {
        stepToGoTo = lastIndex + 1;
        // remove error messages on the current step, when the step is
        // opened for the first time
        jQuery(options.errorContainerId).hide();
        form.find('.has-error').removeClass('has-error');
      } else {
        stepToGoTo = lastIndex;
      }
      silent = true;
      c2cgeoform.steps.goToStep(options.stepsContainerId, currentIndex, stepToGoTo);
      silent = false;
    },
    labels: options.labels
  });
};
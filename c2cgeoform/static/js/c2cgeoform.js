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
c2cgeoform.steps.stepIsValid = function(stepFormId, stepIndex) {
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
 * Initialize JQuery Steps.
 */
c2cgeoform.steps.init = function(options) {
  var form = $(options.formId);
  var stepsContainer = $(options.stepsContainerId);
  var silent = false;

  var previousStep = 0;  // Step before the last request
  var requestedStep = 0; // Step asked at last request
  var currentStep = 0;   // requestedStep or previousStep if not valid
  customData = jQuery(options.customDataFieldId).val();
  if (customData != '') {
    customValues = jQuery.parseJSON(customData);
    previousStep = customValues.previousStep;
    requestedStep = customValues.requestedStep;
  }

  var form_clean = form.serialize();

  stepsContainer.steps(jQuery.extend({

    onInit: function (event, currentIndex) {
      silent = true;
      for (i=0; i<requestedStep; i++) {
        if (stepsContainer.steps('next') == false) {
          break;
        }
      }
      silent = false;
    },

    onStepChanging: function (event, currentIndex, newIndex) {
      if (newIndex < currentIndex) {
        // going backwards
        return true;
      }
      valid = c2cgeoform.steps.stepIsValid(options.stepsContainerId, currentIndex);
      if (silent) {
        return valid;
      }
      var form_dirty = form.serialize();
      if (form_clean==form_dirty && newIndex<=currentStep) {
        return valid;
      }
      // store the current step in a hidden field, so that the next step
      // can be restored after the form is submitted
      jQuery(options.customDataFieldId).val('{"previousStep":'+currentIndex+', "requestedStep":'+newIndex+'}');
      jQuery(options.onlyValidateFieldId).val(1);
      jQuery(options.formId).submit();
      return false;
    },

    onStepChanged: function (event, currentIndex, priorIndex) {
      if (silent) {
        currentStep = currentIndex;
      }
      // remove error messages on the current step, when the step is
      // opened for the first time
      if (currentIndex > previousStep) {
        jQuery(options.errorContainerId).hide();
        stepsContainer.find('.has-error').removeClass('has-error');
      }
      // call reinitMaps after a timeout to work around render issues on Chrome
      window.setTimeout(c2cgeoform.reinitMaps, 1);
    },

    onFinishing: function (event, currentIndex) {
      jQuery(options.onlyValidateFieldId).val(0);
      return true;
    },

    onFinished: function (event, currentIndex) {
      jQuery(options.formId).submit();
    }
  }, options));
};

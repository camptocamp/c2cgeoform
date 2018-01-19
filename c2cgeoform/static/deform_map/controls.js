/* global c2cgeoform */
/* global ol */
/* global $ */

if (!window.c2cgeoform) {
  c2cgeoform = {};
}

/**
 * ToolBar control which acts as a container for further controls.
 */
c2cgeoform.ToolBarControl = function() {
  this.controls_ = [];

  this.container = document.createElement('div');
  this.container.className = 'ol-unselectable ol-control toolbar-control';

  ol.control.Control.call(this, {
    element: this.container
  });
};
ol.inherits(c2cgeoform.ToolBarControl, ol.control.Control);

c2cgeoform.ToolBarControl.prototype.addControl = function(control) {
  this.controls_.push(control);
  this.container.appendChild(control.getElement());
  control.setParent(this);
};

c2cgeoform.ToolBarControl.prototype.initialize = function(map) {
  for(var i = this.controls_.length - 1; i >= 0; i--) {
    this.controls_[i].initialize(map);
  }
};

/**
 * Informs all contained controls that the active status of the given control
 * has changed.
 */
c2cgeoform.ToolBarControl.prototype.setActive = function(control, active) {
  for(var i = this.controls_.length - 1; i >= 0; i--) {
    if (control !== this.controls_[i]) {
      this.controls_[i].setActive(false, true);
    }
  }
};


/**
 * Abstract control to be used in a `c2cgeoform.ToolBarControl`.
 */
c2cgeoform.EditingControl = function(className, tooltipLabel) {
  this.parentToolBar = null;

  var button = document.createElement('button');
  button.type = 'button';
  button.className = 'ol-has-tooltip edit-control ' + className;
  button.title = tooltipLabel;

  this.handleAction = function(e) {};
  var this_ = this;
  var handleAction_ = function(e) {
    this_.handleAction();
  };

  $(button).on('click', handleAction_);

  this.element_ = button;
  ol.control.Control.call(this, {
    element: this.element_
  });
};
ol.inherits(c2cgeoform.EditingControl, ol.control.Control);

c2cgeoform.EditingControl.prototype.getElement = function() {
  return this.element_;
};

c2cgeoform.EditingControl.prototype.initialize = function(map) {
  this.map = map;
};

c2cgeoform.EditingControl.prototype.setParent = function(parentToolBar) {
  this.parentToolBar = parentToolBar;
};

c2cgeoform.EditingControl.prototype.setActive = function(active, silent) {
  if (silent === undefined) {
    silent = false;
  }

  if (active) {
    this.element_.setAttribute('activecontrol', 'active');
  } else {
    this.element_.removeAttribute('activecontrol');
  }

  if (active && !silent) {
    this.parentToolBar.setActive(this, active);
  }
};


/**
 * Abstract control for controls that are bound to an interaction.
 */
c2cgeoform.InteractionControl = function(className, tooltipLabel, source, callback) {
  c2cgeoform.EditingControl.call(this, className, tooltipLabel);

  this.callback = callback;
  this.interactions = this.createInteractions(source);

  this.handleAction = function(e) {
    this.setActive(true);
  };
};
ol.inherits(c2cgeoform.InteractionControl, c2cgeoform.EditingControl);

c2cgeoform.InteractionControl.prototype.setActive = function(active, silent) {
  c2cgeoform.EditingControl.prototype.setActive.call(this, active, silent);
  
  // add or remove the interactions when the control is enabled or disabled
  if (active) {
    for (var i = this.interactions.length - 1; i >= 0; i--) {
      this.map.addInteraction(this.interactions[i]);
    }
  } else {
    for (var i = this.interactions.length - 1; i >= 0; i--) {
      this.map.removeInteraction(this.interactions[i]);
    }
  }
};


/**
 * Control for drawing points.
 */
c2cgeoform.DrawPointControl = function(source, onDrawCallback, tooltip) {
  c2cgeoform.InteractionControl.call(this, 'draw-point', tooltip, source, onDrawCallback);
};
ol.inherits(c2cgeoform.DrawPointControl, c2cgeoform.InteractionControl);

c2cgeoform.DrawPointControl.prototype.createInteractions = function(source) {
  var drawInteraction = new ol.interaction.Draw({
    source: source,
    type: 'Point'
  });
  drawInteraction.on('drawstart', this.callback);
  return [drawInteraction];
};


/**
 * Control for drawing lines.
 */
c2cgeoform.DrawLineControl = function(source, onDrawCallback, tooltip) {
  c2cgeoform.InteractionControl.call(this, 'draw-line', tooltip, source, onDrawCallback);
};
ol.inherits(c2cgeoform.DrawLineControl, c2cgeoform.InteractionControl);

c2cgeoform.DrawLineControl.prototype.createInteractions = function(source) {
  var drawInteraction = new ol.interaction.Draw({
    source: source,
    type: 'LineString'
  });
  drawInteraction.on('drawstart', this.callback);
  return [drawInteraction];
};


/**
 * Control for drawing polygons.
 */
c2cgeoform.DrawPolygonControl = function(source, onDrawCallback, tooltip) {
  c2cgeoform.InteractionControl.call(this, 'draw-polygon', tooltip, source, onDrawCallback);
};
ol.inherits(c2cgeoform.DrawPolygonControl, c2cgeoform.InteractionControl);

c2cgeoform.DrawPolygonControl.prototype.createInteractions = function(source) {
  var drawInteraction = new ol.interaction.Draw({
    source: source,
    type: 'Polygon'
  });
  drawInteraction.on('drawstart', this.callback);
  return [drawInteraction];
};


/**
 * Control for a modify interaction.
 */
c2cgeoform.ModifyControl = function(source, onChangeCallback, tooltip) {
  c2cgeoform.InteractionControl.call(this, 'modify', tooltip, source, onChangeCallback);
};
ol.inherits(c2cgeoform.ModifyControl, c2cgeoform.InteractionControl);

c2cgeoform.ModifyControl.prototype.createInteractions = function(source) {
  var selectInteraction = new ol.interaction.Select();
  var modifyInteraction = new ol.interaction.Modify({
    features: selectInteraction.getFeatures()
  });
  source.on('change', function() {
    // reset the select interaction when the source was emptied
    if (source.getFeatures().length === 0) {
      selectInteraction.getFeatures().clear();
    }
  });
  return [selectInteraction, modifyInteraction];
};


/**
 * Control to remove all features from the given source.
 */
c2cgeoform.ClearFeaturesControl = function(source, onChangeCallback, tooltip) {
  c2cgeoform.EditingControl.call(this, 'clear-features', tooltip);
  this.handleAction = function(e) {
    // TODO ask for confirmation
    source.clear();
  };
};
ol.inherits(c2cgeoform.ClearFeaturesControl, c2cgeoform.EditingControl);


c2cgeoform.zoomToGeometry_ = function(map, geometry, zoomForGeometry) {
  geometry = (geometry === undefined) ? map.get('geometry') : geometry;
  if (geometry === undefined) {
    return;
  }
  zoomForGeometry = (zoomForGeometry === undefined) ?
    map.get('zoomForGeometry') : zoomForGeometry;

  map.getView().fit(geometry, {
    size: map.getSize(),
    maxZoom: zoomForGeometry
  });

  map.set('geometry', geometry);
  map.set('zoomForGeometry', zoomForGeometry);
};


/**
 * Creates a single MultiPoint, MultiLineString, MultiPolygon or
 * GeometryCollection geometry for the given features.
 */
c2cgeoform.makeGeometryCollection_ = function(features, options) {
  var geometry = null;
  if (options.point && !options.line && !options.polygon) {
    geometry = new ol.geom.MultiPoint([]);
    $.each(features, function(_index, feature) {
      geometry.appendPoint(feature.getGeometry());
    });
  } else if (!options.point && options.line && !options.polygon) {
    geometry = new ol.geom.MultiLineString([]);
    $.each(features, function(_index, feature) {
      geometry.appendLineString(feature.getGeometry());
    });
  } else if (!options.point && !options.line && options.polygon) {
    geometry = new ol.geom.MultiPolygon(null);
    $.each(features, function(_index, feature) {
      geometry.appendPolygon(feature.getGeometry());
    });
  } else {
    var geometries = [];
    $.each(features, function(_index, feature) {
      geometries.push(feature.getGeometry());
    });
    geometry = new ol.geom.GeometryCollection(geometries);
  }

  return geometry;
};


/**
 * Unpacks the given MultiPoint, MultiLineString, MultiPolygon or
 * GeometryCollection geometry and creates a feature for each
 * sub-element in the geometry.
 */
c2cgeoform.unpackGeometryCollection_ = function(collection, options) {
  var features = [];
  if (options.point && !options.line && !options.polygon) {
    var points = collection.getPoints();
    $.each(points, function(_index, point) {
      features.push(new ol.Feature(point));
    });
  } else if (!options.point && options.line && !options.polygon) {
    var lines = collection.getLineStrings();
    $.each(lines, function(_index, line) {
      features.push(new ol.Feature(line));
    });
  } else if (!options.point && !options.line && options.polygon) {
    var polygons = collection.getPolygons();
    $.each(polygons, function(_index, polygon) {
      features.push(new ol.Feature(polygon));
    });
  } else {
    var geometries = collection.getGeometries();
    $.each(geometries, function(_index, geometry) {
      features.push(new ol.Feature(geometry));
    });
  }

  return features;
};


/**
 * Adds the given geometry from the GeoJSON string to the vector source and
 * zooms the map to the geometry, so that the geometry is visible.
 */
c2cgeoform.addFeature = function(map, source, geoJson, zoomForGeometry, options) {
  if (geoJson === '') {
    return;
  }

  var geoJsonFormat = new ol.format.GeoJSON();
  var geometry = geoJsonFormat.readGeometry(geoJson);
  var features = null;
  if (options.isMultiGeometry) {
    features = c2cgeoform.unpackGeometryCollection_(geometry, options);
  } else {
    features = [new ol.Feature(geometry)];
  }
  source.addFeatures(features);

  c2cgeoform.zoomToGeometry_(map, geometry, zoomForGeometry);
};


/**
 * Initializes the toolbar containing the controls to draw, modify
 * and remove geometries.
 */
c2cgeoform.initializeToolbar = function(map, source, options) {
  if (options.controlsDefinition.readonly) {
    return;
  }

  var toolbar = new c2cgeoform.ToolBarControl();

  var geoJsonFormat = new ol.format.GeoJSON();
  var onChangeCallback = function() {
    // if the vector source changes, write the geometry as GeoJSON to the
    // input field using the provided callback
    var geometry = null;
    if (source.getFeatures().length > 0) {
      if (!options.controlsDefinition.isMultiGeometry) {
        geometry = source.getFeatures()[0].getGeometry();
      } else {
        geometry = c2cgeoform.makeGeometryCollection_(source.getFeatures(), options.controlsDefinition);
      }
    }
    var geoJson = '';
    if (geometry !== null) {
      geoJson = geoJsonFormat.writeGeometry(geometry);
    }
    options.updateField(geoJson);
  };
  var onDrawCallback = function(event) {
    if (!options.controlsDefinition.isMultiGeometry) {
      // if the geometry type is not a collection type (like MultiPoint),
      // make sure that there is always only one geometry
      source.clear();
    }
  };

  if (options.controlsDefinition.point) {
    toolbar.addControl(new c2cgeoform.DrawPointControl(
      source, onDrawCallback, options.controlsDefinition.drawPointTooltip));
  }
  if (options.controlsDefinition.line) {
    toolbar.addControl(new c2cgeoform.DrawLineControl(
      source, onDrawCallback, options.controlsDefinition.drawLineTooltip));
  }
  if (options.controlsDefinition.polygon) {
    toolbar.addControl(new c2cgeoform.DrawPolygonControl(
      source, onDrawCallback, options.controlsDefinition.drawPolygonTooltip));
  }
  toolbar.addControl(new c2cgeoform.ModifyControl(
    source, onChangeCallback, options.controlsDefinition.modifyTooltip));
  toolbar.addControl(new c2cgeoform.ClearFeaturesControl(
    source, onChangeCallback, options.controlsDefinition.clearTooltip));

  map.addControl(toolbar);
  toolbar.initialize(map);

  source.on('change', onChangeCallback);
};


/**
 * Setup the map for a `RelationSelectMapWidget`.
 */
c2cgeoform.initializeSelectMap = function(map, options) {
  var selectClick = new ol.interaction.Select({
    condition: ol.events.condition.click,
    toggleCondition: ol.events.condition.never
  });
  map.addInteraction(selectClick);

  selectClick.getFeatures().on('add', function() {
    var feature = selectClick.getFeatures().getArray()[0];
    options.updateField(feature.getId());
    options.updateLabel(feature.get(options.labelField));
  });

  selectClick.getFeatures().on('remove', function() {
    options.updateField('');
    options.updateLabel(null);
  });

  var listenerKey = options.source.on('change', function() {
    if (options.source.getState() !== 'ready') {
      return;
    }
    ol.Observable.unByKey(listenerKey);

    // if the GeoJSON file is loaded, try to get the selected feature
    if (options.source.getFeatures().length === 0) {
      return;
    }

    var selectedFeature = null;
    // select feature if available
    if (options.featureId !== '') {
      var feature = options.source.getFeatureById(options.featureId);
      if (feature !== null) {
        selectClick.getFeatures().push(feature);
        selectedFeature = feature;
      }
    }

    if (selectedFeature !== null) {
      // zoom on the selected feature
      c2cgeoform.zoomToGeometry_(map, selectedFeature.getGeometry(), options.maxZoom);
      options.updateLabel(selectedFeature.get(options.labelField));
    } else {
      // zoom on all features
      var extent = ol.geom.Polygon.fromExtent(options.source.getExtent());
      c2cgeoform.zoomToGeometry_(map, extent, options.maxZoom);
      options.updateLabel(null);
    }
  });

  if (options.readonly) {
    selectClick.setActive(false);
  }
};


/**
 * All maps on a page {deform field oid: ol.Map}.
 */
c2cgeoform.maps = {};

/*
 * Calls 'updateSize' on all maps.
 * When the map div of an ol3 map is in a hidden container at the moment
 * it is initialized, it will not be displayed properly. So once the map
 * is shown (e.g. the parent container becomes visible), this method can
 * be called to fix the map.
 */
c2cgeoform.reinitMaps = function() {
  $.each(c2cgeoform.maps, function(_i, map) {
    var initialWidth = map.getSize()[0];
    map.updateSize();
    if (initialWidth === 0) {
      c2cgeoform.zoomToGeometry_(map);
    }
  });
};

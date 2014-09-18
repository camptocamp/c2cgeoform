<%inherit file="site.mako" />

<h3>${_("All entities")}</h3>
% for entity in entities:
  <p>
  % for field in schema.list_fields:
    ${getattr(entity, field)}
  % endfor
  	<a href="${request.route_url('view', schema=schema.name, id=entity.id)}">${_("View")}</a>
  	<a href="${request.route_url('edit', schema=schema.name, id=entity.id)}">${_("Edit")}</a>
  </p>
% endfor

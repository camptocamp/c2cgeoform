<%inherit file="site.mako" />

<h3>All entities</h3>
% for entity in entities:
  <p>${entity.id} ${entity.name} <a href="${request.route_url('edit', schema=schema.name, id=entity.id)}">Edit</a></p>
% endfor

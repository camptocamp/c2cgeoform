<%inherit file="site.mako" />

<h3>View</h3>
<p><a href="${request.route_url('list', schema=schema.name)}">Back to overview</a></p>
${form|n}

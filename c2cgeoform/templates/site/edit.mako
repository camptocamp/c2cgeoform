<%inherit file="site.mako" />

<h3>${_("Edit")}</h3>
<p><a href="${request.route_url('list', schema=schema.name)}">${_("Back to overview")}</a></p>
${form|n}

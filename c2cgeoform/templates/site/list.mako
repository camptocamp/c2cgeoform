<%inherit file="site.mako" />

<h3>${_("All entities")}</h3>

<div class="list-grid">
<table id="grid" data-toggle="bootgrid" class="table table-condensed table-hover table-striped">
    <thead>
        <tr>
        % for field in schema.list_fields:
            <th data-column-id="${field}">${schema.schema_admin[field].title}</th>
        % endfor
            <th data-column-id="_id_" data-searchable="false" data-sortable="false"
                data-converter="commands">${_('Commands')}</th>
        </tr>
    </thead>
    <tbody><tbody>
</table>

<script type="text/javascript">
    $('#grid').bootgrid({
        ajax: true,
        url: '${request.route_url('grid', schema=schema.name)}',
        labels: {
            all: '${_('All')}',
            infos: '${_('Showing ((ctx.start)) to ((ctx.end)) of ((ctx.total)) entries')}'.replace(/\(\(/g, '{{').replace(/\)\)/g, '}}'),
            loading: '${_('Loading...')}',
            noResults: '${_('No results found!')}',
            refresh: '${_('Refresh')}',
            search: '${_('Search')}'
        },
        converters: {
            commands: {
                from: function(value) {
                    return '_id_';
                },
                to: function(value) {
                    return '' +
                        '<a href="${request.route_url('view', schema=schema.name, id='_id_')}">${_("View")}</a> '.replace('_id_', value) +
                        '<a href="${request.route_url('edit', schema=schema.name, id='_id_')}">${_("Edit")}</a>'.replace('_id_', value);
                },
            }
        }
    });
</script>
</div>

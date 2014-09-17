<!DOCTYPE html>
<html lang="${request.locale_name}">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>c2cgeoform</title>
    <link rel="icon" href="data:;base64,=">
    <!-- Bootstrap core CSS -->
    <link href="//oss.maxcdn.com/libs/twitter-bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom styles for this scaffold -->
    <link href="${request.static_url('c2cgeoform:static/theme.css')}" rel="stylesheet">

    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="//oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
      <script src="//oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
    <![endif]-->

    <!-- Deform CSS -->
    % if deform_dependencies is not Undefined:
    <link rel="stylesheet" href="${request.static_url('deform:static/css/form.css')}" type="text/css" />
     % for css in deform_dependencies['css']:
    <link rel="stylesheet" href="${request.static_url(css)}" type="text/css"/>
    % endfor
    % endif


    <!-- Bootstrap core JavaScript -->
    <script type="text/javascript" src="${request.static_url('deform:static/scripts/jquery-2.0.3.min.js')}"></script>
    <script src="//oss.maxcdn.com/libs/twitter-bootstrap/3.0.3/js/bootstrap.min.js"></script>

    <!-- Deform JavaScript -->
    % if deform_dependencies is not Undefined:
    % for js in deform_dependencies['js']:
    <script type="text/javascript" src="${request.static_url(js)}"></script>
    % endfor
    % endif
  </head>

  <body>
    <div class="starter-template">
      <div class="container">
        <div class="row">
          <div class="col-md-11"></div>
          <div class="col-md-1">
            <a href="${request.route_url('locale', _query=(('language', 'en'),))}">en</a> 
            <a href="${request.route_url('locale', _query=(('language', 'fr'),))}">fr</a>
          </div>
        </div>
        <div class="row">
          <div class="col-md-2">
            <img class="logo img-responsive" src="${request.static_url('c2cgeoform:static/pyramid.png')}" alt="pyramid web framework">
          </div>
          <div class="col-md-10">
            <div class="content">
            ${self.body()}
            </div>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>

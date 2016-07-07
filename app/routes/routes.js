module.exports = RouteHandler;

function RouteHandler(app, config)
{
  app.get('/', function(req, res)
  {
    res.sendfile("views/index.html");
  });
}

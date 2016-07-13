const request = require('request');
module.exports = RouteHandler;

function RouteHandler(app, config)
{
  app.get('/', (req, res)=>
  {
    res.sendfile('views/index.html');
  });

  app.get('/test', (req, res)=>
  {
    res.sendfile('views/test.html');
    console.log(config.MYMLH_CLIENT_ID);
  });

  app.get('/dashboard/account', (req, res)=>
  {
    let AUTH_CODE = req.query.code;
    console.log(req.query.code);
    request({
      url: 'https://my.mlh.io/oauth/token',
      method: 'POST',
      qs: {
        client_id: config.MYMLH_CLIENT_ID,
        client_secret: config.MYMLH_SECRET,
        code: AUTH_CODE,
        redirect_uri: 'http://localhost:8080/mymlh/callback',
        grant_type: 'authorization_code'
      }
    }, (error, response, body)=>{
      if(error) {
        return console.log(error);
      }
      //console.log(response);
      console.log()
      console.log(response);
    });
  });

  app.get('/dashboard', (req, res)=>
  {
    res.sendfile('views/dashboard.html');
  });
}

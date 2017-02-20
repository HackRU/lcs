const request = require('request');

const init = function RouteHandler(app, config, passport) {
  app.get('/', (req, res)=>{
    res.sendfile('views/index.html');
  });

  app.get('/test', (req, res)=>{
    res.sendfile('views/test.html');
  });

  app.get('/register', isLoggedIn, (req, res)=>{
    res.render('register.ejs');
  });

  app.get('/callback/mymlh',
    passport.authenticate('mymlh', {
      successRedirect: '/register',
      failureRedirect: '/'
    })
  );

  app.get('/dashboard', isLoggedIn, (req, res)=>{
    res.render('dashboard.ejs');
  });
};

// Middleware
// Authentication Check
const isLoggedIn = function checkLoggedIn(req, res, next) {
  if (req.isAuthenticated()) {
    return next();
  }
  res.redirect('/');
}

module.exports = init;

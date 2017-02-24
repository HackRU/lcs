// Dependencies
const request = require('request');
const path    = require('path');
const multer  = require('multer');

// Middleware
// Authentication Check
const isLoggedIn = function checkLoggedIn(req, res, next) {
  if (req.isAuthenticated()) {
    return next();
  }
  res.redirect('/');
}

// Initialization function
const init = function RouteHandler(app, config, passport, upload) {

  app.get('/', (req, res)=>{
    res.render('index.ejs');
  });

  app.get('/register-mymlh', isLoggedIn, (req, res)=>{
    res.render('register-mymlh.ejs');
  });

  app.get('/callback/mymlh',
    passport.authenticate('mymlh', {
      successRedirect: '/register-mymlh',
      failureRedirect: '/'
    })
  );

  app.get('/dashboard', isLoggedIn, (req, res)=>{
    res.render('dashboard.ejs');
  });

  app.post('/register-mymlh', isLoggedIn, (req, res)=>{
    upload.single('resume')(req, res, (err)=>{
      if(err) {
        return err;
      }
      console.log(req.file);
      res.json(201);
    });
    console.log(req.user);
    console.log("BODY");
    console.log(req.body);
  });
};

module.exports = init;

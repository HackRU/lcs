// Dependencies
const request = require('request');
const path    = require('path');
const User    = require('../models/user.js');

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
    //console.log(User.findOne());
    res.render('register-mymlh.ejs', { user: req.user});
  });

  app.get('/logout', (req, res)=>{
    req.logout();
    res.redirect('/');
  });

  app.get('/callback/mymlh',
    passport.authenticate('mymlh', {
      successRedirect: '/register-mymlh',
      failureRedirect: '/'
    })
  );

  app.get('/dashboard', isLoggedIn, (req, res)=>{
    console.log('Dashboard: \n' + req.user);
    res.render('dashboard.ejs', { user: req.user });
  });

  app.post('/register-mymlh', isLoggedIn, (req, res)=>{
    upload.single('resume')(req, res, (err)=>{
      if(err) {
        console.log(err);
        return err;
      }
      let github = false;
      let resume = false;
      if ((req.user.github !== req.body.github) && (req.body.github !== "")) {
        github = true;
      }
      if((req.file) && (req.user.resume !== req.file.originalname)) {
        resume = true;
      }
      if(github || resume) {
        User.findOne({ '_id': req.user._id }, (err, user)=>{
          if (err) {
            throw err;
          }
          if(github) {
            user.github = req.body.github;
          }
          if(resume) {
            user.resume = req.file.originalname;
          }
          user.data_sharing = true;
          user.registration_status = 1;
          user.save((err)=>{
            if (err) {
              throw err;
            }
            res.redirect('/dashboard');
          });
        });
      }
    });
  });
};

module.exports = init;

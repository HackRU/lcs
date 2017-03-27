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
  req.flash('info', 'Something happened with authentication! Please log in again.');
  res.redirect('/');
}

// Initialization function
const init = function RouteHandler(app, config, passport, upload) {

  app.get('/', (req, res)=>{
    res.render('index.ejs', { user: req.user, message: req.flash('info') });
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

  app.get('/register-mymlh', isLoggedIn, (req, res)=>{
    //console.log(User.findOne());
    if(req.user.registration_status == 1) {
      res.redirect('/dashboard');
    }
    res.render('register-mymlh.ejs', { user: req.user, message: req.flash('register') });
  });

  app.get('/register-confirmation', isLoggedIn, (req, res)=>{
    res.render('registration-confirmation.ejs');
  });

  app.get('/dashboard', isLoggedIn, (req, res)=>{
    if(req.user.registration_status == 0) {
      res.redirect('/register-mymlh');
    }
    console.log('Dashboard: \n' + req.user);
    res.render('dashboard.ejs', { user: req.user });
  });

  app.get('/account', isLoggedIn, (req, res)=>{
    res.render('account.ejs', { user: req.user, message: req.flash('account') });
  });

  app.get('/resume/:file', isLoggedIn, (req, res)=>{
    // change later
    res.download('resumes/Spring2017/' + req.params.file);
  });

  app.post('/register-mymlh', isLoggedIn, (req, res)=>{
    upload.single('resume')(req, res, (err)=>{
      if(err) {
        if(err.code == 'LIMIT_FILE_SIZE') {
          req.flash('register', 'The file you\'re trying to upload is too large! Max Size is 2MB! :(');
          //res.redirect('/register-mymlh');
        } else if(err.code == 'WRONG_FILE_TYPE') {
          req.flash('register', 'Wrong file type. Please upload only PDF, DOC, DOCX, RTF, RTF, TXT files.');
        } else {
          req.flash('register', err.code);
        }
        res.render('register-mymlh.ejs', { user: req.user, message: req.flash('register') });
        return;
      }
      let github = false;
      let resume = false;
      if ((req.user.github !== req.body.github) && (req.body.github !== "")) {
        github = true;
      }
      if((req.file) && (req.user.resume !== req.file.originalname)) {
        resume = true;
      }
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
            console.log(err);
            throw err;
          }
          res.redirect('/register-confirmation');
        });
      });
    });
  });

  app.post('/account', isLoggedIn, (req, res)=>{
    upload.single('resume')(req, res, (err)=>{
      if(err) {
        if(err.code == 'LIMIT_FILE_SIZE') {
          req.flash('account', 'The file you\'re trying to upload is too large! Max Size is 2MB! :(');
          //res.redirect('/register-mymlh');
        } else if(err.code == 'WRONG_FILE_TYPE') {
          req.flash('account', 'Wrong file type. Please upload only PDF, DOC, DOCX, RTF, RTF, TXT files.');
        } else {
          req.flash('account', err.code);
        }
        res.render('account', { user: req.user, message: req.flash('account') });
        return;
      }
      let github = false;
      let resume = false;
      if ((req.user.github !== req.body.github) && (req.body.github !== "")) {
        github = true;
      }
      if((req.file) && (req.user.resume !== req.file.originalname)) {
        resume = true;
      }
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
        user.save((err)=>{
          if (err) {
            console.log(err);
            throw err;
          }
          req.flash('account', 'Success! Your information was saved.')
          res.redirect('/account');
        });
      });
    });
  });

  app.use(function (req, res, next) {
    res.render('404.ejs');
  });
  // app.get('*', (req, res)=>{
  //   res.render('404.ejs');
  // });
};

module.exports = init;

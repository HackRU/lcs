// Dependencies
const request     = require('request');
const path        = require('path');
const User        = require('../models/user.js');
const Waitlist    = require('../models/waitlist.js');
const EmailClient = require('./email.js');
const config      = require('../config/config.js');

// Middleware
// Authentication Check
const isLoggedIn = function checkLoggedIn(req, res, next) {
  if(req && req.session && req.session.user_tmp && config.devmode) {
    req.user == req.session.user_tmp;
    return next();
  }
  if (req.isAuthenticated()) {
    return next();
  }
  req.flash('info', 'Something happened with authentication! Please log in again.');
  res.redirect('/');
}

// Initialization function
const init = function RouteHandler(app, config, passport, upload) {

  app.get('/', (req, res)=>{
    //console.log(req.session);
    res.render('index.ejs', { user: req.user, message: req.flash('info') });
  });

  app.get('/authenticate', passport.authenticate('mymlh'), (req, res)=>{
    //
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
    if(req.user.registration_status > 1) {
      return res.redirect('/dashboard');
    }

    res.render('register-mymlh.ejs', { user: req.user, message: req.flash('register') });
  });

  app.get('/register-confirmation', isLoggedIn, (req, res)=>{
    res.render('registration-confirmation.ejs');
  });

  app.get('/dashboard', isLoggedIn, (req, res)=>{
    //console.log(req.session);
    if(req.user.registration_status == 0) {
      res.redirect('/register-mymlh');
    }
    res.render('dashboard.ejs', { user: req.user, message: req.flash('dashboard') });
  });

  app.get('/account', isLoggedIn, (req, res)=>{
    res.render('account.ejs', { user: req.user, message: req.flash('account') });
  });

  app.get('/resume/:file', isLoggedIn, (req, res)=>{
    // change later
    res.download('resumes/Spring2017/' + req.params.file);
  });

  app.get('/confirm-status', isLoggedIn, (req, res)=>{
    res.render('manage-confirmation.ejs', { user: req.user, message: req.flash('attendance') });
  });

  app.post('/register-mymlh', isLoggedIn, (req, res)=>{
    let dob = new Date(req.user.mlh_data.date_of_birth);
    let eventdate = new Date(config.event_date);
    let deltaTime = Math.abs(dob.getTime() - eventdate.getTime());
    let deltaDays = Math.ceil(deltaTime/(1000 * 3600 * 24));
    if(req.user.mlh_data.school.id != 2 && req.user.mlh_data.school.id != 2037) {
      if(deltaDays < (18 * 365)) {
        req.flash('info', 'Sorry, you have to be at least 18 to attend this event.');
        return res.redirect('/');
      }
    }
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
        } else if(err.code == 'WRONG_FILE_TYPE') {
          req.flash('account', 'Wrong file type. Please upload only PDF, DOC, DOCX, RTF, RTF, TXT files.');
        } else {
          req.flash('account', err.code);
        }
        res.render('account.ejs', { user: req.user, message: req.flash('account') });
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

  app.post('/confirm-status', isLoggedIn, (req, res)=>{

    var email = new EmailClient();
    // Finds the current user
    User.findOne({ '_id': req.user._id }, (err, user)=>{
      if (err) {
        throw err;
      }

      // Determine attendance from POST request
      // if Attending, see if there's space, else set Not Attending
      if (req.body.attendance === 'attending') {
        if (user.registration_status != 3) {
          User.count({'registration_status': 3}, (err, count)=>{
            if (count < config.capacity) {
              user.registration_status = 3;
              user.save((err)=>{
                if (err) {
                  throw err;
                }
                email.sendConfirmedEmail(user.local.email);
                return res.redirect('/dashboard');
              });
            } else {
              // Capacity has been filled, check space in waitlist
              Waitlist.count({}, (err, queueSize)=>{
                if (queueSize < config.waitlistCapacity) {
                  user.registration_status = 4;
                  var waitlisted = new Waitlist();

                  waitlisted.id = user.id;
                  waitlisted.mlhid = user.mlh_data.mlhid;

                  waitlisted.save((err)=>{
                    if (err) {
                      throw err;
                    }
                    email.sendWaitlistEmail(user.local.email);
                    user.save((err)=>{
                      if (err) {
                        throw err;
                      }
                      return res.redirect('/dashboard');
                    });
                  });

                } else {
                  req.flash('dashboard', 'Sorry, our waitlist is full. Currently, you may not attend HackRU, but check back later; spots on the waitlist may open up.');
                  res.redirect('/dashboard');
                }
              });
            }
          });
        } else {
          return res.redirect('/dashboard');
        }
      } else {
        // Set Not Attending
        user.registration_status = 2;
        user.save((err)=>{
          if (err) {
            throw err;
          }
          return res.redirect('/dashboard');
        });
      }
    });
  });

  app.get('/auth/fake/test', (req, res)=>{
    if(config.devmode) {
      req.session = req.session || {};
      req.session.passport = config.fakeuser.passport;
      isLoggedIn(req, res, res.redirect('/'));
    }
    return res.redirect('/');
  });
};

module.exports = init;

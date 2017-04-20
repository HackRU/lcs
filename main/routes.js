// Dependencies
const request   = require('request');
const path      = require('path');
const JSX       = require('node-jsx').install();
const React     = require('react');
const ReactDOMServer = require('react-dom/server');
const TweetsApp = React.createFactory(require('./components/TweetsApp.react'));
const EventsApp = React.createFactory(require('./components/EventsApp.react'));
const AnouncementsApp = React.createFactory(require('./components/AnouncementsApp.react'));
const Tweet     = require('../models/Tweet.js');
const User      = require('../models/user.js');
const GCEvent   = require('../models/GCEvent.js');
const SlackMsg  = require('../models/SlackMsg.js');
const config    = require('../config/config.js');

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

//Get Event data
const getEvents = function getEventsData(req, res, next){
  
  GCEvent.getEvents(0,0, function(events){ 

    req.body.eventsmarkup = ReactDOMServer.renderToString(
      EventsApp({
        events:events
      })
    );

    req.body.events = events;
    return next();
  });
}

const getTweets = function getTweetsData(req,res,next){
  Tweet.getTweets(0,0, function(tweets){
        
    req.body.tweetsmarkup = ReactDOMServer.renderToString(
      TweetsApp({
        tweets: tweets
      })
    );

    req.body.tweets = tweets;
    return next();
  });
}

const getAnouncements = function getAnouncementsData(req,res,next){
  SlackMsg.getSlackMsgs(0,0,function(anouncements){ 

    req.body.anouncementsmarkup = ReactDOMServer.renderToString(
      AnouncementsApp({
        anouncements:anouncements
      })
    );

    req.body.anouncements = anouncements;
    return next();
  });
}

const getQRImage = function getQRImageData(req,res,next){
  var url = 'http://qru.hackru.org:8080/images/'+req.user.mlh_data.email+'.png';
  var r = request.defaults({encoding:null});
  r.get(url,(err,response,body)=>{
    if(err){ 
      console.log(err);      
    }else if(response.statusCode === 404 && (req.body.qrRetries == null || req.body.qrRetries < 3)){
      console.log('404 ERROR');
      //NOT SURE IF THIS IS COOL-> generate a new QRImage by passing in email to QRU server
      var qrurl = 'http://qru.hackru.org:8080/viewqr?email='+req.user.mlh_data.email;
      request.get(qrurl,(error,resp,bod)=>{
          if(req.body.qrRetries == null){
            req.body.qrRetries = 1;
          }else{
            req.body.qrRetries += 1;
          }
          getQRImageData(req,res,next);
      });
    }
    else{     
      req.body.qrimage = new Buffer(body).toString('base64'); 
      return next();
    }
  });
}
const getGavel = function getGavelData(req,res,next){
  
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
    if(req.user.registration_status == 1) {
      return res.redirect('/dashboard');
    }

    res.render('register-mymlh.ejs', { user: req.user, message: req.flash('register') });
  });

  app.get('/register-confirmation', isLoggedIn, (req, res)=>{
    res.render('registration-confirmation.ejs');
  });

  app.get('/dashboard', isLoggedIn, (req, res)=>{
    console.log(req.session);
    if(req.user.registration_status == 0) {
      res.redirect('/register-mymlh');
    }
    res.render('dashboard.ejs', { user: req.user });
  });


  app.get('/dashboard-dayof',isLoggedIn,getEvents, getTweets, getAnouncements, getQRImage,(req,res) =>{
      res.render('dashboard-dayof.ejs',{
                user: req.user,
                qrimage:req.body.qrimage, 
                anouncementsMarkup: req.body.anouncementsmarkup,
                anouncementsState: JSON.stringify(req.body.anouncements),
           
                tweetsMarkup: req.body.tweetsmarkup,
                tweetsState: JSON.stringify(req.body.tweets),

                eventsMarkup: req.body.eventsmarkup,
                eventsState: JSON.stringify(req.body.events)//Pass current state to client side #MAGIC
      });
    
  });

  app.post('/slack',(req,res)=>{
    console.log(req);
    if(req.body.type === 'url_verification'){
      console.log(req.body);
      res.send(''+req.body.challenge);
    }else if(req.body.type === 'event_callback'){
      console.log(req.body.event);
      var slackEvent = req.body.event;
      if(slackEvent.type === 'message'){
        console.log(slackEvent.text);
        if(slackEvent.channel === config.slack.channel){ 
          var message ={
            ts:slackEvent.ts,
            text:slackEvent.text,
            user:slackEvent.user
          };
          if(message.text.search("has joinced the channel") == -1){
            SlackMsg.findOneAndUpdate({ts:message.ts},message,{upsert:true,new:true},(err,res)=>{
              if(err) console.log(err);
            });
          }
        }
      }
      res.send(200);
    }
  });

  app.get('/account', isLoggedIn, (req, res)=>{
    res.render('account.ejs', { user: req.user, message: req.flash('account') });
  });

  app.get('/resume/:file', isLoggedIn, (req, res)=>{
    // change later
    res.download('resumes/Spring2017/' + req.params.file);
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

// Dependencies
const express         = require('express');
const helmet          = require('helmet');
const path            = require('path');
const morgan          = require('morgan');
const bodyParser      = require('body-parser');
const ejs             = require('ejs');
const flash           = require('connect-flash');
const mongoose        = require('mongoose');
const session         = require('express-session');
const RedisStore      = require('connect-redis')(session);
const passport        = require('passport');
const multer          = require('multer');
const routes          = require('./main/routes.js');
const errors          = require('./main/errors.js');
const passConfig      = require('./main/passport.js');
const multerConfig    = require('./main/multer.js');
const config          = require('./config/config.js');
//Dashboard specific stuff
const twitter         = require('twitter');
const eventfeed       = require('./main/calendar.js');
const twitterfeed     = require('./main/loadtweets.js');
const slackfeed       = require('./main/loadmsgs.js');

// Set up Application
const app = express();
var port = process.env.PORT || 8080;


mongoose.connect(config.db.url);
passConfig(passport);

var upload = multerConfig(multer, config);

app.use(helmet());
app.use(morgan('dev'));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static(__dirname + "/views"));
app.set('view engine', 'ejs');
app.use(flash());

// Set up Sessions
app.use(session({
  store: new RedisStore(config.session.options),
  secret: config.session.secret,
  resave: false,
  saveUninitialized: false,
  cookie: {
    maxAge: config.session.maxAge
  }
}));
app.use(passport.initialize());
app.use(passport.session());

// Initialize Routes Handler
routes(app, config, passport, upload);
// Load Error Handling last
errors(app);

setTimeout(eventfeed.loadEvents,5000);
setTimeout(eventfeed.setUpPushNotifications,5000);
twitterfeed.loadTweets();
slackfeed.loadMsgs();


// Launch
app.listen(port);
console.log('Listening on port: %d', port);


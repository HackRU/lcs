// Dependencies
const express       = require('express');
const helmet        = require('helmet');
const path          = require('path');
const morgan        = require('morgan');
const bodyParser    = require('body-parser');
const ejs           = require('ejs');
const flash         = require('connect-flash');
const mongoose      = require('mongoose');
const session       = require('express-session');
const RedisStore    = require('connect-redis')(session);
const passport      = require('passport');
const multer        = require('multer');
const twitter       = require('twitter'); 
const routes        = require('./main/routes.js');
const errors        = require('./main/errors.js');
const config        = require('./config/config.js');
const passConfig    = require('./main/passport.js');
const multerConfig  = require('./main/multer.js');
const streamHandler = require('./utils/streamHandler.js'); //Handles twitter stream
const eventfeed     = require('./main/calendar.js');
const twitterfeed   = require('./main/loadtweets.js');
const slackfeed     = require('./main/loadmsgs.js');


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

// Load calendar, twitter, slack
setTimeout(eventfeed.loadEvents,5000);
twitterfeed.loadTweets();
slackfeed.loadMsgs();

// Launch
var server = app.listen(port);
console.log('Listening on port: %d', port);

//Initialize socket.io
var io = require('socket.io').listen(server);

var twit = new twitter(config.twitter);

//Set a stream listener for tweets matching tracking keywords 
//WILL BE CHANGED IN FUTURE TO HACKRU TWEETS ONLY
twit.stream('statuses/filter',{follow:'853467496493481984'},function(stream){
    streamHandler(stream,io);
});

/** IGNORE
var testTweet = {
    twid:"123",
    active:false,
    author:"test-author",
    avatar:"test-avatar",
    body: "test-body",
    date: null,
    screenname: "test-screenname"
};


var newTweet = new Tweet(testTweet);

newTweet.save(function(err){

    if(!err){
        console.log("ya did it!");
    }
});
*/

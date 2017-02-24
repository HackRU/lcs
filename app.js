// Dependencies
const express       = require('express');
const helmet        = require('helmet');
const path          = require('path');
const morgan        = require('morgan');
const bodyParser    = require('body-parser');
const ejs           = require('ejs');
const mongoose      = require('mongoose');
const session       = require('express-session');
const RedisStore    = require('connect-redis')(session);
const passport      = require('passport');
const multer        = require('multer');
const routes        = require('./main/routes.js');
const config        = require('./config/config.js');
const passConfig    = require('./main/passport.js');
const multerConfig  = require('./main/multer.js');

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

// Set up Sessions
app.use(session({
  store: new RedisStore(config.session.options),
  secret: config.session.secret,
  resave: false,
  saveUninitialized: false,
  cookie: {
    maxAge: 60000
  }
}));
app.use(passport.initialize());
app.use(passport.session());

// Initialize Routes Handler
routes(app, config, passport, upload);

// Launch
app.listen(port);
console.log('Listening on port: %d', port);

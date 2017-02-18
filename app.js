// Dependencies
const express       = require('express');
const helmet        = require('helmet');
const morgan        = require('morgan');
const bodyParser    = require('body-parser');
const session       = require('express-session');
const RedisStore    = require('connect-redis')(session);
const passport      = require('passport');
const passportMyMLH = require('passport-mymlh').Strategy;
const routes        = require('./main/routes.js');
const config        = require('./config/config.js');
const passconfig    = require('./main/passport.js');

// Set up Application
const app = express();
var port = process.env.PORT || 8080;

app.use(helmet());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(morgan('dev'));
app.use(express.static(__dirname + "/views"));

app.set('view engine', 'ejs');

// Set up Sessions

routes(app, config);

// Launch
app.listen(port);
console.log('Listening on port: ' + port);

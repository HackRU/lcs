// Dependencies
const express = require('express');
const morgan  = require('morgan');
const routes  = require('./app/routes/routes.js');
const config  = require('./config/config.js');

// Set up Application
const app = express();
var port = process.env.PORT || 8080;

app.use(morgan('dev'));
app.use(express.static(__dirname + "/views"));
routes(app);

// Launch
app.listen(port);

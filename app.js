// Dependencies
const express = require('express');
const routes  = require('./app/routes/routes.js');
const morgan  = require('morgan');

// Set up Application
const app = express();
var port = process.env.PORT || 8080;

app.use(morgan('dev'));
app.use(express.static(__dirname + "/views"));
routes(app);

// Launch
app.listen(port);

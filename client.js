var React = require('react');
var TweetsApp = require('./main/components/TweetsApp.react.js');
var EventsApp = require('./main/components/EventsApp.react.js');
var socket = require('socket.io');


// Render the components, picking up where react left off on the server
React.renderComponent(
  <TweetsApp tweets={initialState}/>,
  document.getElementById('tweets-app')
);

React.renderComponent(
  <EventsApp events={eventsInitialState}/>,
  document.getElementById('events-app')
);


var React = require('react');
var TweetsApp = require('./main/components/TweetsApp.react.js');
var EventsApp = require('./main/components/EventsApp.react.js');
var AnouncementsApp = require('./main/components/AnouncementsApp.react.js');
var socket = require('socket.io');

var tweetsInitialState = JSON.parse(document.getElementById('tweets-initial-state').innerHtml);
var eventsInitialState = JSON.parse(document.getElementById('events-initial-state').innerHtml);
var anouncementsInitialState = JSON.parse(document.getElementById('anouncements-initial-state').innerHtml);

// Render the components, picking up where react left off on the server
React.renderComponent(
  <TweetsApp tweets={tweetsInitialState}/>,
  document.getElementById('tweets-app')
);

React.renderComponent(
  <EventsApp events={eventsInitialState}/>,
  document.getElementById('events-app')
);

React.renderComponent(
  <AnouncementsApp events={anouncementsInitialState}/>,
  document.getElementById('anouncements-app')
);



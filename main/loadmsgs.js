var fs = require('fs');
var config = require('../config/config.js');
var SlackMsg = require('../models/SlackMsg.js');
var https = require('https');
/**
 *
 * Lists the next 10 events on the user's primary calendar.
 *
 * @param {google.auth.OAuth2} auth An authorized OAuth2 client.
 */
module.exports.loadMsgs= function loadMsgs() {
 
  var pathparam = '/api/channels.history?channel='+config.slack.channel+'&token='+config.slack.token;
  
  var url = 'https://slack.com'+pathparam;

  const options = {
    hostname:'slack.com',
    path:pathparam,
    method:'GET'
  };

  const req = https.request(options,(res) => {

  
    var body = '';
    
    res.on('data',function(d){
      body += d;
    });

    res.on('end',function(){
  
      var data = JSON.parse(body);
     

      
      for(var i = 0; i < data.messages.length;i++){
        var message = data.messages[i];
        var slackmessage={
          ts:message.ts,
          text:message.text,
          user:message.user
        };

        if(slackmessage.text.search("has joined the channel") == -1){
          SlackMsg.findOneAndUpdate({ts:message.ts},slackmessage,{upsert:true,new:true},(err,res)=>{
            if(err) console.log(err);
          });
        }
      }
    
      console.log("DONE LOADING MESSAGES");

   });

  });
  
  req.on('error',(e)=>{console.log(e)});

  req.end();
  /*
    for (var i = 0; i < events.length; i++) {
        var data = events[i];

        var message = {
          
        };



        console.log(gcevent);
        

        GCEvent.findOneAndUpdate({eventid:gcevent.eventid} ,gcevent,{upsert:true, new:true},(err,res)=>{ 
          if(err) console.log(err);
        });

      
      }

 }
  
  */    
 
}

var mongoose = require('mongoose');

var schema = new mongoose.Schema({
    ts    : String,
    text  : String,
    user  : String
});

//Static method to return tweet data from db
schema.statics.getSlackMsgs = function(page,skip,callback){
    
    var msgs = [];
    var start = (page*10)+(skip*1);

    Tweet.find({},'twid active author avatar body date screenname',{skip:start, limit: 10}).sort({ts:'desc'}).exec(function(err,docs){
        if(!err){
            msgs = docs;
        }else{
            console.log("YOU DONE GOOFD");
        }
        callback(msgs);
    }); 
};

module.exports = SlackMsg = mongoose.model('SlackMsg',schema);

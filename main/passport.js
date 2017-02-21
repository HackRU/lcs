const mongoose      = require('mongoose');
const MyMLHStrategy = require('passport-mymlh').Strategy;
const User          = require('../models/user.js');
const config        = require('../config/config.js');

const init = function PassportSetup(passport) {
  passport.serializeUser((user, callback)=>{
    callback(null, user.mlhid);
  });

  passport.deserializeUser((mlhid, callback)=>{
    User.findOne({ 'mlhid': mlhid }, (err, user)=>{
      callback(err, user);
    });
  });

  passport.use(new MyMLHStrategy({
    clientID: config.MYMLH_CLIENT_ID,
    clientSecret: config.MYMLH_SECRET,
    callbackURL: config.MYMLH_CALLBACK,
    scope: [
      'email',
      'phone_number',
      'demographics',
      'birthday',
      'education',
      'event'
    ]
  }, (accessToken, refreshToken, profile, callback)=>{
    process.nextTick(()=>{
      // Check if the user exists in the database
      User.findOne({'mlhid': profile.id}, (err, user)=>{
        if (err) {
          return callback(err);
        }
        // If a user was found, then return the user.
        if (user) {
          console.log("Found User");
          return callback(null, user);
        } else {
          console.log("Creating new User");
          // Create a New User
          var newUser = new User();

          // MyMLH Data
          newUser.mlhid = profile.id;
          newUser.email = profile.email;
          newUser.first_name = profile.first_name;
          newUser.last_name = profile.last_name;
          newUser.level_of_study = profile.level_of_study;
          newUser.major = profile.major;
          newUser.shirt_size = profile.shirt_size;
          newUser.dietary_restrictions = profile.dietary_restrictions;
          newUser.special_needs = profile.special_needs;
          newUser.date_of_birth = profile.date_of_birth;
          newUser.gender = profile.gender;
          newUser.phone_number = profile.phone_number;
          newUser.school = profile.school;

          // Our Data
          newUser.registration_status = 0;
          newUser.github = '';
          newUser.resume = '';
          newUser.data_sharing = 'false';

          // User ID is determined by how many have registered.
          var nextAvailableID = User.count({}, (err, count)=>{
            newUser.id = count;

            newUser.save((err)=>{
              if (err) {
                throw err;
              }
              return callback(null, newUser);
            });
          });
        }
      });
    });
  }));
};

module.exports = init;

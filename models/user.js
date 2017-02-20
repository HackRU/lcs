const mongoose = require('mongoose');
//const bcrypt   = require('bcrypt-nodejs');

var Schema     = mongoose.Schema;

var userSchema = new Schema({
  // MLH Data
  mlhid: Number,
  email: String,
  first_name: String,
  last_name: String,
  level_of_study: String,
  major: String,
  shirt_size: String,
  dietary_restrictions: String,
  special_needs: String,
  date_of_birth: String,
  gender: String,
  phone_number: String,
  school: {
    id: Number,
    name: String
  },

  // Our Data
  id: Number,
  registration_status: Number,
  github: String,
  resume: String,
  data_sharing: Boolean
  // registration_status:
  // 0 = Fresh User, Only has MyMLH Data
  // 1 = Registered, filled in all Account details
  // 2 = Confirmed attendance
});

module.exports = mongoose.model('User', userSchema);

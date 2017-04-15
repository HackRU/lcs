// Dependencies
const fs        = require('fs');
const path      = require('path');
const sparkpost = require('sparkpost');
const config    = require('../config/config.js');

class EmailClient {
  constructor() {
    this.client = new sparkpost(config.SPARKPOST_KEY);
  }

  sendConfirmedEmail(email_address) {
    this.client.transmissions.send({
        options: {

        },
        content: {
          template_id: 'sp2017-confirmed'
        },
        recipients: [
          {address: email_address}
        ]
      })
      .then(data => {
        console.log(data);
      })
      .catch(err => {
        console.log(err);
      });
  }

  sendWaitlistEmail(email_address) {
    this.client.transmissions.send({
        options: {

        },
        content: {
          template_id: 'sp2017-waitlist'
        },
        recipients: [
          {address: email_address}
        ]
      })
      .then(data => {
        console.log(data);
      })
      .catch(err => {
        console.log(err);
      });
  }
}

module.exports = EmailClient;

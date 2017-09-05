// Dependencies
const fs        = require('fs');
const path      = require('path');
const sparkpost = require('sparkpost'); // Use SparkPost to send emails. Email Templates are saved in SparkPost
const config    = require('../config/config.js');

class EmailClient {
  constructor() {
    this.client = new sparkpost(config.SPARKPOST_KEY);
  }

  sendConfirmAttendanceEmail(email_address) {
    this.client.transmissions.send({
        options: {

        },
        content: {
          template_id: 'sp2017-goconfirm' // Template inside SparkPost Account
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

  sendConfirmedEmail(email_address) {
    this.client.transmissions.send({
        options: {

        },
        content: {
          template_id: 'sp2017-confirmed' // Template inside SparkPost Account
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
          template_id: 'sp2017-waitlist' // Template inside SparkPost Account
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

  sendSponsorshipEmail(sponsor_email, email_content){
    this.client.transmissions.send({
        options: {

        },
        content: {
          from: "team@hackru.org",
          text: email_content,
          subject: "Interest in HackRU sponsorship for " + config.SemesterID + " from " + sponsor_email
        },
        recipients: [
          {address: "sponsorship@hackru.org"}
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

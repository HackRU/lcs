const multer = require('multer');
const path   = require('path');

const init = function multerConfiguration(multer, config) {
  var fileLimits = {
    fileSize: '5MB'
  };

  var fileFilter = function checkFileType(req, file, callback) {
    // parse file extension
  };

  // Define Resume Storage and File naming convention
  var storage = multer.diskStorage({
    destination: function resumeLocation(req, file, callback) {
      callback(null, path.join(__dirname + '/../' + config.SemesterID + '/resumes'));
    },
    filename: function customFilename(req, file, callback) {
      console.log(file);
      callback(null, req.user.id + '_' + file.originalname);
    }
  });

  return multer({ storage: storage, limits: fileLimits });
  //return multer({ storage: storage, fileFilter: fileFilter, limits: fileLimits });
}

module.exports = init;

var React = require('react');

function normalize(time){
  var meridiem = "am";
  var colon = time.indexOf(':');
  var hours =  parseInt(time.slice(0,colon));
  if(hours >= 12){
    hours = hours % 12;
    meridiem = "pm";
  }
  if(hours == 0) hours = 12;
  return hours + time.substring(colon)+meridiem;
}

function cleanupTags(text){
  var ret = text + "";
  var indexlt = ret.indexOf('<');
  ret = ret.replace('<!channel>','');
  ret = ret.replace('<!everyone>','');
  while(indexlt != -1){
    var indexrt = ret.indexOf('>');
    if(ret.charAt(indexlt+1) == '@'){
      var slice = ret.slice(indexlt,indexrt+1);
      ret = ret.replace(slice,'');
    }
    var left = '';
    var middle = '';
    var right = '';
    if(indexlt > 0) left = ret.substring(0,indexlt);
    middle = ret.slice(indexlt+1,indexrt);
    if(indexrt < indexrt-1) right = ret.substring(indexrt);
    console.log(left+','+middle+','+right); 
    ret = left+middle+right;
    indexlt = ret.indexOf('<');
  }
  ret = ret.replace('&gt','>');
  ret = ret.replace('&lt','<');
  return ret;
}

function cleanup(text, anouncement){
  var ret =  text+" ";
  var end = anouncement.ts.indexOf('.');
  var unix = parseInt(anouncement.ts.substring(0,end));
  var date = new Date(unix *1000);
   
  var hours = date.getHours();
  var minutes = '0' + date.getMinutes();
  
  return normalize(hours + ':' + minutes.substr(-2)) + '. ' + cleanupTags(ret);
}


module.exports = Anouncement= React.createClass({
  render: function(){
    var anouncement = this.props.anouncement;
    return (
      <div className={'anouncement' + ' active'}>
        <p> {cleanup(anouncement.text,anouncement)} </p>
        <div className='short-separator'></div>
      </div>
    )
  }
});

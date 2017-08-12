$(document).ready(function () {
  $(document).keydown(function () {
    var right = 39, left = 37;
    if(event.which == 39 || event.which == 37) {
      var user_id = $('#user_id').val();
      var accept = (event.which == 39)? '1' : '0';
      var url = "/admin-swiped?user_id=" + user_id + "&accepted=" + accept;
      $.get(url).done(function(data){
        data = JSON.parse(data);
        if(data.all_done){
          window.location.reload(true);
        }else{
          console.log(data);
          $('#user_answer').text(data.user.short_answer);
          $('#user_level_of_study').text(data.user.grad_year);
          $('#user_major').text(data.user.major);
          $('#counts').text(data.counts);
          $('#user_id').val(data.user.id);
        }
      });
    }
  });
});

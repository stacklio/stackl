function myFunction() {
    document.getElementById("action_demo").innerHTML = "5";
}

////////
//Top row
///////
$(document).ready(function(){
  $.ajax({
      type : "GET",
      url : "/stacks/instances",
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
          $("#stack_instance_number").text(result.length);
      }
  });
});
$(document).ready(function(){
  $.ajax({
      type : "GET",
      url : "/types/resource_object",
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
          $("#resource_object_number").text(result.result.length);
      }
  });
});
$(document).ready(function(){
  $.ajax({
      type : "GET",
      url : "/stacks/templates",
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
          $("#stack_template_number").text(result.length);
      }
  });
});
////////
//SSL + inventory row
///////
$(document).ready(function(){
  $.ajax({
      type : "GET",
      url : "/sslinfo",
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
        console.log(result)
        console.log(result['CLIENT_SERIAL'])
        var ssl_info =  '<p>Client serial: ' + result.client_serial + "<p>";
        // ssl_info += '<p>Client verified: ' + result.client_verify +"<p>";
        ssl_info += '<p>Client fingerprint: ' + result.client_fingerprint +"<p>";
        ssl_info += '<p>Client certificate: ' + result.client_cert ;
        ssl_info += '<p>Tenant: ' + result.tenant ;
        $("#sslinfo_body").append(ssl_info);
        $("#sslinfo_footer").html('<p style="margin: 0px 0px 0px 0px" class="text-success no-padding">Client verify: ' +  result.client_verify +'</p>');

      }
  });
});
$(document).ready(function(){
  $.ajax({
      type : "GET",
      url : "/inventory/schedule",
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
        console.log(result)
        var inventory_enabled = true
        if ('inventory_enabled' in result){
            inventory_enabled = result.inventory_enabled
        }
        if (inventory_enabled){
            var splitted = result.inventory_schedule.split(' ')
            var inventory_schedule =  '<p>Date: ' + splitted[0] + "<p>";
            inventory_schedule += '<p>Time: ' + splitted[1] +"<p>";
            inventory_schedule += '<p style=\"margin:0px 0px 30px 0px\">Interval: ' + result.inventory_wait_minutes +" minutes<p>";
        } else {
            var inventory_schedule = "<p>Inventory: DISABLED<p>";
        }
        $("#inventory_schedule").prepend(inventory_schedule);
      }
  });
});

$(document).ready(function() {
    $('#inventory_collect').click(function() {
      $.ajax({
          type : "POST",
          data: JSON.stringify({}),
          url : "/inventory/schedule",
          contentType: 'application/json',
          success: function(result) {
            $("#inventory_schedule_footer").html("<font color=\"#337AB7\">Inventory collection requested<font>");
          },
          error: function(error) {
            console.log(error)
          }
      });
    });
});

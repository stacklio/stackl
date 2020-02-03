var templates = {}

$(document).ready(function(){
  $('#restoreSnapshot').on('change', function() {
      $('#restoreSnapshotDiv').toggle();
      $('#stack_snapshot').toggle();
  });
  $("#request_button").prop("disabled", true);
  $.ajax({
    type : "GET",
    url : "/stacks/templates",
    contentType: 'application/json;charset=UTF-8',
    success: function(result) {
      sorted = result
      sorted.sort(compare);
      $.each(sorted, function(k, v) {
        templates[v['name']] = v
          $('#stack_templates').append($('<option>', {value:v['name'], text:v['name']}));
            populateTemplatePanels()
          })
          $("select#stack_templates").change(function (evt) {
            populateTemplatePanels()
          });
          $( "#collapseParametersArea" ).focusout(function() {
            var text = $( "#collapseParametersArea" ).val()
            try{
              var new_text = JSON.stringify(JSON.parse(text), null, 2)
              $( "#collapseParametersArea").val(new_text)
            } catch(e){
              alert("Invalid JSON found")
            }
          });
          $( "#collapseResourcesArea" ).focusout(function() {
            var text = $( "#collapseResourcesArea" ).val()
            try{
              var new_text = JSON.stringify(JSON.parse(text), null, 2)
              $( "#collapseResourcesArea").val(new_text)
            } catch(e){
              alert("Invalid JSON found")
            }
          });
          $( "#stack_instance_name" ).on('propertychange input', function (e) {
            console.log("keypress")
            var stack_instance_name = $( "#stack_instance_name" ).val()
            console.log(stack_instance_name != '')
            console.log(stack_instance_name)
            if (stack_instance_name != ''){
              $("#request_button").prop("disabled", false);
            }
            else{
              $("#request_button").prop("disabled", true);
            }
          });
          $('#request_button').click(function() {
            var dialog = bootbox.dialog({ closeButton: false, message: '<div class="text-center"><i class="fa fa-spin fa-spinner"></i> Loading...</div>' })
            var data_object = {'instanceName': $('#stack_instance_name').val() , "templateName": $('#stack_templates option:selected').text(), "parameters": JSON.parse($( "#collapseParametersArea").val())}
            console.log('stack_snapshot: '+ $('#restoreSnapshot').is(":checked"))
            if($('#restoreSnapshot').is(":checked")){
              console.log("restoreSnapshot was true")
              if ($('#stack_snapshot').val()){
                console.log("stack_snapshot was not null")
                data_object['snapshot'] = $('#stack_snapshot').val()
                requestTemplate(dialog,data_object)
              }else{
                  console.log("stack_snapshot was null")
                  bootbox.confirm("Stack snapshot was empty. Continue request without snapshot restore?", function(result) {
                  console.log('result: '+ result)
                  console.log("wait")
                  if(result){
                    requestTemplate(dialog,data_object)
                  }else{
                    dialog.modal('hide');
                  }
                });
              }
            }else{
              requestTemplate(dialog,data_object)
            }
          })
      }
    });
});

function requestTemplate(dialog,data_object){
  console.log(data_object)
  $.ajax({
    type : "POST",
    url : "/stacks/templates",
    contentType: 'application/json;charset=UTF-8',
    data: JSON.stringify(data_object),
    success: function(result) {
      dialog.modal('hide');
      bootbox.alert({
        size: "medium",
        title: "Success",
        message: "Request is progress!<br>Track your progress here: <a href=\"/ui/stacks/instances\">Instances</a>",
        callback: function(){ location.reload(true); }
      })
    },
    error: function(result) {
      dialog.modal('hide');
      bootbox.alert({
        size: "medium",
        title: "Failure",
        message: "Request failed: "+ JSON.stringify(result),
        callback: function(){ location.reload(true); }
      })
    }
  })
}

function compare(a,b) {
  if (a.name < b.name)
    return -1;
  if (a.name > b.name)
    return 1;
  return 0;
}

function populateExistingSnapshotNames(stackTemplate){
  $("#stack_snapshot").html("");
  var params = {'stackTemplate': stackTemplate}
  $.ajax({
      type : "GET",
      url : '/stacks/snapshots',
      data: params,
      success: function(result) {
        $.each(result, function(k, v) {
          //clear option
            $('#stack_snapshot').append($('<option>', {value:v['name'], text:v['name']}));
        })
      }
    })
}

function populateTemplatePanels(){
  var stack_templates_selected = $('#stack_templates option:selected').text();
  console.log("stack_templates_selectedstack_templates_selected: "+ stack_templates_selected)
    populateExistingSnapshotNames(stack_templates_selected)
  $("#collapseParametersArea").val(JSON.stringify(templates[stack_templates_selected]['parameters'], null, 2))
  $("#collapseResourcesArea").val(JSON.stringify(templates[stack_templates_selected]['resources'], null, 2))
}

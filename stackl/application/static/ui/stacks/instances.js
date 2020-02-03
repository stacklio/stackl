$(document).ready(function(){
  $('#submitSnapshot').click(function() {
    submitSnapshotAction()
  });
  $('#snapshotModal').on('shown.bs.modal', function(e) {
    var stackTemplate = e.relatedTarget.dataset.stacktemplate;
    var stackInstance = e.relatedTarget.dataset.stackinstance;
    $('#snapshotStackInstance').val(stackInstance)
    $('#snapshotStackTemplate').val(stackTemplate)
    populateExistingSnapshotNames(stackInstance, stackTemplate)
  })
  $('#restoreSnapshot').on('change', function() {
      $('#takeSnapshotDiv').toggle();
      $('#restoreSnapshotDiv').toggle();
  });
  $.ajax({
    type : "GET",
    url : "/stacks/instances",
    contentType: 'application/json;charset=UTF-8',
    success: function(result) {
      if (typeof(result) == 'object' && !(result instanceof Array)){
        result = [result]
      }
      $.each(result, function(k, v) {
        var name = v['name']
        if(name){
          $.ajax({
            type : "GET",
            url : "/stacks/instances/"+name+'/status',
            contentType: 'application/json;charset=UTF-8',
            success: function(status) {
              $("#instances_accordion").append(createCollapseInstancesDiv(name, v,status))
              $('.button_progress_bar').popover({container: 'body' ,placement:'auto right',   html: true});
              $('.popover_resource_object').popover({trigger: 'manual' ,container: 'body' ,placement:'auto right',   html: true});
                $('#button_delete_'+name+'').click(function() {
                bootbox.confirm("Are you sure want to delete "+name+"?", function(result) {
                  deleteStackInstance(name)
                });
              })
              $('#button_refresh_'+name+'').click(function() {
                bootbox.confirm("Are you sure want to update "+name+"?", function(result) {
                  updateStackInstance(name)
                });
              })
              $( "#collapseParametersArea"+name ).focusout(function() {
                  var text = $( "#collapseParametersArea"+name ).val()
                  try{
                    var new_text = JSON.stringify(JSON.parse(text), null, 2)
                    $( "#collapseParametersArea"+name ).val(new_text)
                  } catch(e){
                    alert("Invalid JSON found")
                  }
              });
            }
          })
        }
      })
    }
  });
});

function submitSnapshotAction(){
  // console.log(document.querySelectorAll('*[id]'))
  var dialog = bootbox.dialog({ closeButton: false, message: '<div class="text-center"><i class="fa fa-spin fa-spinner"></i> Loading...</div>' })
  var snapshotDescription = $('#snapshotDescription').val()
  var snapshotName = $('#snapshotName').val()
  var restoreSnapshotName = $('#restoreSnapshotName').val()
  var snapshotStackInstance = $('#snapshotStackInstance').val()
  var snapshotStackTemplate = $('#snapshotStackTemplate').val()
  var restoreSnapshot = $('#restoreSnapshot').is(":checked");
  var action = 'snapshot-create'
  var data_object = {'name': snapshotName, 'description': snapshotDescription}
  if(restoreSnapshot){
    action = 'snapshot-restore'
    data_object = {'name': restoreSnapshotName}
  }
  $.ajax({
    type : "POST",
    url : "/stacks/instances/"+snapshotStackInstance+"/"+action,
    contentType: 'application/json;charset=UTF-8',
    data: JSON.stringify(data_object),
    success: function(result) {
      try{
        dialog.modal('hide');
      } catch(e){}
      location.reload(true)
      // bootbox.alert({
      //   size: "medium",
      //   title: "Success",
      //   message: "Admin was added!",
      //   callback: function(){ location.reload(true); }
      // })
    },
    error: function(result) {
      console.log(result)
      dialog.modal('hide');
      location.reload(true)
      // bootbox.alert({
      //   size: "medium",
      //   title: "Failure",
      //   message: "Admin was not added! "+ JSON.stringify(result),
      //   callback: function(){ location.reload(true); }
      // })
    }
  })
}

function populateExistingSnapshotNames(stackInstance, stackTemplate){
  var params = {'stackTemplate': stackTemplate}
  $.ajax({
      type : "GET",
      url : '/stacks/snapshots',
      data: params,
      success: function(result) {
        $.each(result, function(k, v) {
            $('#restoreSnapshotName').append($('<option>', {value:v['name'], text:v['name']}));
        })
      }
    })
}

function createCollapseInstancesDiv(name, stack_instance, status){
    var progress_status = 'Status:&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbspDone'
    var theme = 'success'
    var disabled = ''
    var snapshot_disabled = 'disabled'
    if (status.toLowerCase() == 'failed'){
      theme = 'danger'
      progress_status = 'Status:&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbspFailed'
    }else if(status.toLowerCase() == 'in progress'){
      theme = 'warning'
      progress_status = 'Status:&nbsp&nbsp&nbspIn progress'
      disabled = 'disabled'
    }else{
      snapshot_disabled = ''
    }
    var tmp_resource = createResourcePanels(name, stack_instance, theme)
    parameter_div = createParameterPanels(name,stack_instance, theme)
    resource_div = tmp_resource['div']
    progress = tmp_resource['progress']
    var div = ''
    div +='<div class="panel panel-'+theme+'" id="panel'+name+'">'
    div +=  '<div class="panel-heading">'
    div +=    '<div class="btn-toolbar pull-right">'
    div +=        '<div class="btn-group">'
    div +='           <button type="button" id="show_progress_'+name+'" style="margin: -7px" class="button_progress_bar btn btn-sm btn-'+theme+'" data-parent="panel-heading" data-trigger="focus" data-toggle="popover" title="'+progress_status+'" data-content=\'<div class="progress progress-striped active"> <div class="progress-bar progress-bar-'+theme+'" role="progressbar" aria-valuenow="'+progress+'" aria-valuemin="0" aria-valuemax="100" style="width: '+progress+'%"><span class="sr-only">'+progress+'% Complete </span></div></div>\'>'+status+'</button>'
    div +=        '</div>'
    div +=        '<div class="btn-group">'
    div +=          '<button type="button" id="button_delete_'+name+'" class="btn btn-sm btn-danger" style="margin: -7px 0px 10px 7px" '+disabled+'><i class="fa fa-lg fa-trash-o"></i></button>'
    div +=        '</div>'
    div +=        '<div class="btn-group">'
    div +=          '<button type="button" id="button_refresh_'+name+'" class="btn btn-sm btn-primary" style="margin: -7px 0px 10px 0px" '+disabled+'><i class="fa fa-lg fa-refresh"></i></button>'
    div +=          '<button type="button"  id="button_snapshot_'+name+'" class="btn btn-sm btn-default" style="margin: -7px 0px 10px 4px" data-toggle="modal" data-target="#snapshotModal" data-stackinstance="'+name+ '" data-stacktemplate="'+stack_instance['stackTemplate']+'" '+snapshot_disabled+'><i class="fa fa-lg fa-camera"></i></button>'
    // div +=          '<button type="button" class="btn btn-sm btn-primary" style="margin: -7px 0px 10px 0px"><i class="fa fa-lg fa-refresh"></i></button>'
    div +=        '</div>'
    div +=    '</div>'
    div +=    '<div style="float: left">'
    div +=      '<h4 class="panel-title" style="float: left">'
    div +=        '<a data-toggle="collapse" data-target="#collapse'+name+'" href="#collapse'+name+'">'
    div +=          name
    div +=        '</a>'
    div +=      '</h4>'
    div +=    '</div>'
    div +=    '<div style="margin: 0 auto; width: 100px; text-align: center">'
    div +=      '<h4 class="panel-title" style="float: right text-align:center">'
    div +=        '<a data-toggle="collapse" data-target="#collapse'+name+'" href="#collapse'+name+'">'
    div +=          stack_instance['stackTemplate']
    div +=        '</a>'
    div +=      '</h4>'
    div +=    '</div>'
    div +=  '</div>'
    div +=  '<div id="collapse'+name+'" class="panel-collapse collapse">'
    div +=    '<div class="panel-body">'
    div +=      parameter_div
    div +=      resource_div
    div +=    '</div>'
    div +=  '</div>'
    div +='</div>'

    return div
}

function createParameterPanels(name,stack_instance, theme){
  var stringify = JSON.stringify(stack_instance['parameters'], undefined, 2)
  // stringify = stringify.replace(/\n/g, "<br>").replace(/[ ]/g, "&nbsp;");
  var div = ''
  div += '<div class="row">'
  div +=  '<div class="panel-group" id="instances_parameters_accordion" style="margin: 0px 0px 0px 1% ; width:98%">'
  div +=   '<div class="panel panel-'+theme+'" id="panel1">'
  div +=    '<div class="panel-heading">'
  div +=     '<h5 class="panel-title">'
  div +=      '<a data-toggle="collapse" data-target="#collapseParameters'+name+'" href="#collapseParameters'+name+'">'
  div +=       'Parameters'
  div +=      '</a>'
  div +=     '</h5>'
  div +=    '</div>'
  div +=    '<div id="collapseParameters'+name+'" class="panel-collapse collapse">'
  div +=     '<div class="panel-body">'
  div +=        '<textarea id="collapseParametersArea'+name+'" cols=50 rows=25>'+stringify+'</textarea>'
  div +=     '</div>'
  div +=    '</div>'
  div +=   '</div>'
  div +=  '</div>'
  div += '</div>'
  return div
}

function createResourcePanels(name, stack_instance,theme){
  var counter = 0 ;
  var counter_all = 0 ;
  var resource_object_objects = null;
  progress = 100
  $.ajax({
      type : "GET",
      url : '/types/resource_object',
      async: false,
      success: function(result) {
        resource_object_objects =result['result']
      }
  })
  var div = ''
  div +='<div class="row">'
  div +='  <div class="panel-group" id="instances_resources_accordion'+name+'" style="margin: 0px 0px 0px 1% ; width:98%">'
  div +='    <div class="panel panel-'+theme+'" id="panel_resources'+name+'">'
  div +='      <div class="panel-heading">'
  div +='        <h5 class="panel-title">'
  div +='          <a data-toggle="collapse" data-target="#collapseResources'+name+'" href="#collapseResources'+name+'">'
  div +='            Resources'
  div +='          </a>'
  div +='        </h5>'
  div +='      </div>'
  div +='      <div id="collapseResources'+name+'" class="panel-collapse collapse in">'
  div +='        <div class="panel-body">'
  //loop over resources and add to list
  $.each(stack_instance['resources'], function(resource_category, resource_objects) {
    div +='          <div class="row">'
    $.each(resource_objects, function(resource_name, resource_state_object) {
      counter_all = counter_all + 1
      var subpanel_theme = 'warning'
      if (resource_state_object['state'].toLowerCase() == 'failed'){
        subpanel_theme = 'danger'
        counter = counter + 1
      }else if(resource_state_object['state'].toLowerCase() == 'done'){
        subpanel_theme = 'success'
        counter = counter + 1
      }
      resource_object_object = findresource_objectObject(resource_object_objects, resource_name )
      client_role = 'Unknown'
      client_zone = 'Unknown'
      client_environment = 'Unknown'
      client_location = 'Unknown'
      if (resource_object_object){
        client_role = resource_object_object['role']
        client_zone = resource_object_object['zone']
        client_environment = resource_object_object['environment']
        client_location = resource_object_object['location']
      }
      stringify = JSON.stringify(resource_object_object, undefined, 2),
      stringify = stringify.replace(/\n/g, "<br>").replace(/[ ]/g, "&nbsp;");
      div +='            <div id="resource_'+resource_name+'" class=" col-lg-3 col-md-6" style=" width:240px; float:left ; margin: 15px 0px 15px 0px">'
      div +='              <div class="panel panel-'+subpanel_theme+'">'
      div +='                <div class="panel-heading">'
      div +='                  <h5 class="panel-title" style="word-wrap: break-word">'
      div +=                    '<a href="#" data-toggle="popover" class="popover_resource_object" onclick="event.preventDefault() ; toggleresource_objects(this)" id="popover_'+resource_name+'" title="resource_object" data-content=\''+stringify+'\'>'+resource_name+'</a>'
      div +='                  </h5>'
      div +='                  role: '+ client_role + "<br>"
      div +='                  zone: '+ client_zone + "<br>"
      div +='                  environment: '+ client_environment + "<br>"
      div +='                  location:' + client_location + "<br>"
      div +='                </div>'
      div +='                <div class="panel-footer">'
      div +='                   <p style="margin: 0px 0px 0px 0px" class="text-'+subpanel_theme+'">'+resource_category+'</p>'
      div +='                </div>'
      div +='              </div>'
      div +='            </div>'
    })
    div +='          </div>'
  })
  div +='        </div>'
  div +='      </div>'
  div +='    </div>'
  div +='  </div>'
  div +='</div>'
  progress = (counter / counter_all) * 100
  if(progress == 0){
    progress = 1
  }
  return {'div':div, 'progress':progress}
}

function findresource_objectObject (object_list ,name) {
    for (var i = 0, len = object_list.length; i < len; i++) {
        if (object_list[i].name === name)
            return object_list[i]; // Return as soon as the object is found
    }
    return null; // The object was not found
}

function updateStackInstance( stack_instance_name){
  $.ajax({
      type : "POST",
      url : '/stacks/instances/'+stack_instance_name,
      data: JSON.stringify({}),
      contentType: 'application/json',
      success: function(result) {
        reloadPage()
      }
    })
}

function deleteStackInstance( stack_instance_name){
  $.ajax({
      type : "DELETE",
      url : '/stacks/instances/'+stack_instance_name,
      statusCode: {
            202: function() {
            }
        },
      success: function(result) {
        console.log(result)
      }
    })
}

function toggleresource_objects(e){
  if($(e).hasClass('hide_popover')){
      $(e).popover('toggle');
      $('.hide_popover').removeClass('hide_popover')
  }else{
    $('.hide_popover').popover('hide');
    $('.hide_popover').removeClass('hide_popover')
    $(e).popover('toggle');
    $(e).addClass('hide_popover')
  }
}

function reloadPage(){
  location.reload()
}

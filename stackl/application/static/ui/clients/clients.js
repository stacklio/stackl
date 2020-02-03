function getUrlVars() {
  var vars = {};
  var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
  vars[key] = value;
  });
  return vars;
}

function compare(a,b) {
  if (a.name < b.name)
    return -1;
  if (a.name > b.name)
    return 1;
  return 0;
}
$ ( document ).ready(function() {
    $('#generateCert').on('change', function() {
        $('#hidden').toggle();
        $('#shownSerial').toggle();
    });
    $('#add').click(function() {
      addClient()
    });
    $('#delete').click(function() {
      deleteClient()
    });
  populateTable()
})

function populateTable(){
    var params = {'role': client_role}
    $.ajax({
        type : "GET",
        url : '/clients',
        data: params,
        success: function(result) {
            $.each(result['result'], function(k, v) {
                $('#delete_serial').append($('<option>', {value:v['serial'], text:v['serial']}));
                var body = "<tr>";
                body    += "<td style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\">" + v['serial'] + "</td>"
                body    += "<td style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\">" + v['description']+"</td>";
                if(client_role == 'proxy'){
                  if('tags' in v){
                    var tags = v['tags']
                    tags.sort(compare);
                    body    += "<td style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\">" + tags.join()+ "</td>";
                  }
                  else{
                      body    += "<td style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\">common</td>";
                  }
                }
                body    += "<td style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\">" + v['tenant']+ "</td>";
                body    += "<td style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\"><form method=\"get\" action=\"/_download_cert/"+v['serial'] + "\"> <button id=\"add_button\" type=\"submit\" style=\"margin: 0px 10px 10px 15px\" class=\"btn btn-default\"><i class=\"fa fa-lg fa-download\"></button></form></td>";
                body    += "</tr>";
                $( body ).appendTo( $( "tbody" ) );
            });
            $( "#dataTables-example" ).DataTable();
        },
        error: function() {

        }
    });
    /*DataTables instantiation.*/
}

function deleteClient(){
    var dialog = bootbox.dialog({ closeButton: false, message: '<div class="text-center"><i class="fa fa-spin fa-spinner"></i> Loading...</div>' })
    var delete_serial = $('#delete_serial option:selected').text();
    console.log("delete_serial: "+ delete_serial)
    $.ajax({
      type : "DELETE",
      url : "/clients/"+delete_serial,
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
        dialog.modal('hide');
        bootbox.alert({
          size: "medium",
          title: "Success",
          message: "Admin was deleted!",
          callback: function(){ location.reload(true); }
        })
      },
      error: function(result) {
        dialog.modal('hide');
        bootbox.alert({
          size: "medium",
          title: "Failure",
          message: "Admin was not deleted succesfully! "+ JSON.stringify(result),
          callback: function(){ location.reload(true); }
        })
      }
    })
}

function download(serial){
  $.ajax({
    type : "GET",
    url : '/_download_cert/'+serial,
    contentType: 'application/json;charset=UTF-8',
    success: function(result) {
      console.log("success!")
    },
    error: function(result) {
      console.log("error!")
    }
  })
}

function addClient(){
  // '/_request_cert'
    var dialog = bootbox.dialog({ closeButton: false, message: '<div class="text-center"><i class="fa fa-spin fa-spinner"></i> Loading...</div>' })
    var generateCert = $('#generateCert').val()
    if(generateCert){
      data_object = {'commonName': $('#commonName').val(), 'email': $('#email').val()}
      $.ajax({
        type : "POST",
        url : "/_request_cert",
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify(data_object),
        success: function(result) {
          result_obj = JSON.parse(result)
          console.log("RESULT serial: " + result_obj['serial'])
          addClientHelper(result_obj['serial'])
        },
        error: function(result) {
          console.log("RESULT error: " + JSON.stringify(result))
          dialog.modal('hide');
          alert("RESULT error: " + result)
        }
      })
    }else{
      addClientHelper($('#serial').val())
    }
}

function addClientHelper(serial){
    var data_object = {'serial': serial,'fingerprint': '00000' ,'description': $('#description').val() , "role": client_role}
    if(client_role == 'proxy'){
      var tags = $('#tags').val()
      tags = tags.replace(/ /g,'')
      tags = tags.split(',')
      data_object['tags'] = tags
    }
    console.log(data_object)
    $.ajax({
      type : "POST",
      url : "/clients",
      contentType: 'application/json;charset=UTF-8',
      data: JSON.stringify(data_object),
      success: function(result) {
        try{
          dialog.modal('hide');
        } catch(e){}
        bootbox.alert({
          size: "medium",
          title: "Success",
          message: "Admin was added!",
          callback: function(){ location.reload(true); }
        })
      },
      error: function(result) {
        dialog.modal('hide');
        bootbox.alert({
          size: "medium",
          title: "Failure",
          message: "Admin was not added! "+ JSON.stringify(result),
          callback: function(){ location.reload(true); }
        })
      }
    })
}

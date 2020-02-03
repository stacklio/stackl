var templates = {}

$(document).ready(function(){
  $.ajax({
    type : "GET",
    url : "/types",
    contentType: 'application/json;charset=UTF-8',
    success: function(result) {
      sorted = result['types']
      removeFromArray(['all'], sorted)
      sorted.sort();
      $.each(sorted, function(k, v) {
          console.log(v)
          $('#types').append($('<option>', {value:v, text:v}));
      })
      updateTypeNameDropdown()
      $( "#document_body" ).focusout(function() {
        var text = $( "#document_body" ).val()
        try{
          var new_text = JSON.stringify(JSON.parse(text), null, 2)
          $( "#document_body").val(new_text)
        } catch(e){
          alert("Invalid JSON found")
        }
      });
    }
  })
})

$ ( document ).ready(function() {
  $("select#types").change(function (evt) {
    updateTypeNameDropdown()
  })
})

$ ( document ).ready(function() {
  $("select#type_name").change(function (evt) {
    updateTextArea()
  })
})

function updateTextArea(){
  var type = $('#types option:selected').text();
  var type_name = $('#type_name option:selected').text();
  console.log(type)
  if(type){
    $.ajax({
      type : "GET",
      // url : "/vault/"+type+"/"+type_name,
      url : "/types/"+type+"/"+type_name + '/',
      // contentType: 'application/json;charset=UTF-8',
      success: function(result) {
        var vault_doc = JSON.stringify(result, null, 2)
        console.log(vault_doc)
        $('#document_body').val(vault_doc)
      }
    })
  }
}

function updateTypeNameDropdown(){
  $("#type_name").empty();
  var type = $('#types option:selected').text();
  console.log(type)
  if(type){
    $.ajax({
      type : "GET",
      url : "/types/"+type,
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
        sorted = result['result']
        sorted.sort(compare);
        $.each(sorted, function(k, v) {
            $('#type_name').append($('<option>', {value:v['name'], text:v['name']}));
        })
        updateTextArea()
        defineUpdateButton()
      }
    })
  }
}

function removeFromArray(removeList, list){
  $.each(removeList, function(k, v) {
    var index = sorted.indexOf(v)
    if (index > -1){
      list.splice(index,1)
    }
  })
  return list
}

function compare(a,b) {
  if (a.name < b.name)
    return -1;
  if (a.name > b.name)
    return 1;
  return 0;
}

function defineUpdateButton (){
    $('#update_button').click(function() {
      bootbox.confirm("Are you sure?", function(result){
        if(result){
          var type = $('#types option:selected').text();
          var type_name = $('#type_name option:selected').text();
          var data_object = JSON.parse($('#document_body').val())
          console.log("/types/"+type)
          console.log("request: "+ data_object)
          $.ajax({
            type : "POST",
            url : "/types/"+type,
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify(data_object),
            success: function(result){
              bootbox.alert({
                size: "medium",
                title: "Success",
                message: "New data posted!",
              })
              location.reload()
            },
            error: function(result) {
              bootbox.alert({
                size: "medium",
                title: "Failure",
                message: "Request failed: "+ JSON.stringify(result),
              })
            }
          })
        }
      })
    })
}
//       }
//     });
// });

function compare(a,b) {
  if (a.name < b.name)
    return -1;
  if (a.name > b.name)
    return 1;
  return 0;
}

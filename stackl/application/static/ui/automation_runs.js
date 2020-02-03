
var x = 'test';
var term = 'x';

$(document).ready(function(){
  Terminal.applyAddon(fit);
  term = new Terminal();
  term.open(document.getElementById('terminal'));
  console.log('x: ' + x);
  x='t';
  var selectedresource_object = getUrlVars()["selectedresource_object"];
  console.log('selectedresource_object = ' + selectedresource_object);
  $.ajax({
      type : "GET",
      url : "/types/resource_object",
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
          $('#automation_runs_resource_object').append($('<option>', {selected: 'selected', value:'Select resource object', text:'Select resource object'}));
          sorted = result['result']
          sorted.sort(compare);
          var first = true
          $.each(sorted, function(k, v) {
            if (selectedresource_object == v['name'] || (first && selectedresource_object)) {
              first = false
              $('#automation_runs_resource_object').append($('<option>', {selected: 'selected', value:v['name'], text:v['name']}));
            } else {
              $('#automation_runs_resource_object').append($('<option>', {value:v['name'], text:v['name']}));
            }
          })
      }
  });
});

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
// $ ( document ).ready(function() {
//   // createTerminal()
// })
$ ( document ).ready(function() {
  // populateTable()
  $("select#automation_runs_resource_object").change(function (evt) {
              console.log('change');
              createTerminal();
         });
     });

// function createTerminal(){
//   console.log('x inner: ' + x);
//   // console.log('term inner: ' + term);
//   term.writeln('Hello World!');
//   for(var i= 0; i < 1000; i++){
//     term.writeln('hello world ' + i);
//     if(i == 500){
//         term.reset();
//     }
//   }
// }
function createTerminal(){
    term.reset()
    var tmp = $('#automation_runs_resource_object option:selected').text();
    if(!tmp){
      return
    }
    if(tmp == 'Select resource object'){
      return
    }
    console.log("trigger int " + tmp)
    // term.reset()
    var all = 'automation-endpoint'
    var url =  '/types/automation-run/'+ tmp
    console.log('url: ' + url)
    $.ajax({
      type : "GET",
      url : url,
      success: function(result) {
        console.log(result)
        if(!result || result  == {} || result['automation_run'] == null ){
          term.writeln('No automation run found');
        }
        else {
          splitted = result['automation_run'].split("\n");
          splitted.forEach(element => {
            term.writeln(element);
          });
    
        }
      },
      error: function() {

      }
  });
}


// function createTerminal(){
//     var tmp = $('#automation_runs_resource_object option:selected').text();
//     if(!tmp){
//       return
//     }
//     Terminal.applyAddon(fit);
//     term = new Terminal();
//     term.open(document.getElementById('terminal'));
//     term.clear()
//     term.reset()

//     // term.reset()
//     if(tmp == 'Select resource object'){
//       return
//     }
//     console.log("trigger int " + tmp)
//     term.writeln('Hello World!');
//     // term.reset()
//     var all = 'automation-endpoint'
//     var url =  '/types/resource_object/'+ tmp
//     console.log('url: ' + url)
//     $.ajax({
//       type : "GET",
//       url : url,
//       success: function(result) {
//           console.log(result)
//           // var resource_object_object = result[resource_object]
//           $.each(result, function(k, v) {
//             // var value =v['value']
//             // term.writeln(value);
//             term.writeln(k + ' ' + v);
//           });
//       },
//       error: function() {

//       }
//   });
// }
  //   $.ajax({
  //     type : "GET",
  //     url : "/types/resource_object/"+tmp,
  //     contentType: 'application/json;charset=UTF-8',
  //     success: function(result) {
  //       console.log(result)
  //       resource_obj = result['result']
  //       for (const key of Object.keys(resource_obj)) {
  //         term.writeln(key +' : '+ resource_obj[key]);
  //       }
  //     }
  // });
  // }

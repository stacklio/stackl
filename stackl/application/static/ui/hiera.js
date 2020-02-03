$(document).ready(function(){
  var selectedresource_object = getUrlVars()["selectedresource_object"];
  console.log('selectedresource_object = ' + selectedresource_object);
  $.ajax({
      type : "GET",
      url : "/types/resource_object",
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
          sorted = result['result']
          sorted.sort(compare);
          $.each(sorted, function(k, v) {
            if (selectedresource_object == v['name']) {
              $('#hiera_resource_object').append($('<option>', {selected: 'selected', value:v['name'], text:v['name']}));
            } else {
              $('#hiera_resource_object').append($('<option>', {value:v['name'], text:v['name']}));
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
$ ( document ).ready(function() {
  populateTable()
})
$ ( document ).ready(function() {
  // populateTable()
  $("select#hiera_resource_object").change(function (evt) {
              var table = $("#dataTables-example").dataTable()
              table.fnClearTable();
              table.fnDraw();
              table.fnDestroy();
              populateTable()
         });
     });


function populateTable(){
    var params = {'info': 'true'}
    var tmp = $('#hiera_resource_object option:selected').text();
    console.log("trigger int" + tmp)
    $.ajax({
        type : "GET",
        url : '/hiera/all',
        data: params,
        success: function(result) {
            var resource_object = $('#hiera_resource_object option:selected').text();
            var resource_object_object = result[resource_object]
            $.each(resource_object_object, function(k, v) {
              var value =v['value']
                if (typeof value === 'object' || $.isArray(value)){
                  value = JSON.stringify(v['value'], null, 2)
                }
                var body = "<tr>";
                body    += "<td style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\">" + k + "</td>"
                body    += "<td style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\">" + value+"</td>";
                body    += "<td style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\">" + v['source_name']+ "</td>";
                body    += "<td style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\">" + v['source_type'] + "</td>";
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

// $(document).ready(function() {
//     $('#dataTables-example').DataTable({
//         responsive: true
//     });
// });

// $(document).ready(function() {
//   var t = $('#dataTables-example').DataTable({
//                 responsive: true
//             });
//   var params = {'info': 'true'}
//   $.ajax({
//     type : "GET",
//     url : '/hiera/all',
//     data: params,
//     success: function(result) {
//       var resource_object_object = result['t05dsc01.nubera.local']
//       $.each(resource_object_object, function(k, v) {
//         t.row.add( [
            // k,
            // v['value'],
            // v['source_name'],
            // v['source_type']
//         ] ).draw( false );
//       })
//     }
//   })
// } );

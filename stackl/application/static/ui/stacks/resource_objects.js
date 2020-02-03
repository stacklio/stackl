var resource_objects = null
$(document).ready(function(){
  $.ajax({
      type : "GET",
      url : "/types/resource_object",
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
          sorted = result['result']
          sorted.sort(compare);
          resource_objects = sorted
          populateTable()
      }
  });
});
// $(document).ready(function(){
//   $('.collapse').on('show.bs.collapse', function() {
//     $(this).parent().removeClass("zeroPadding");
//   });
//
//   $('.collapse').on('hide.bs.collapse', function() {
//     $(this).parent().addClass("zeroPadding");
//   });
// })

function compare(a,b) {
  if (a.name < b.name)
    return -1;
  if (a.name > b.name)
    return 1;
  return 0;
}
// $ ( document ).ready(function() {
//   populateTable()
// })

function populateTable(){
    $.each(resource_objects, function(k, v) {
      var name_no_space  = v['name'].replace(/\./g, '_');
      var breaks = JSON.stringify(v, null, 2)
      var value =v['value']
      var body = "<tr data-toggle=\"collapse\" data-target=\"#" +name_no_space+ "\">";
        //body    += "<td align=\"center\" style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\">" + v['name'] + "</td>"
        body    += "<td align=\"center\" style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\">";
        body    += "<a href='/ui/hiera?selectedresource_object=" + v['name'] + "'>" + v['name'] + '</a>';
        body    += '</td>';
        body    += "<td align=\"center\" style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\">" + v['role']+"</td>";
        body    += "<td align=\"center\" style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\">" + v['environment'] + "</td>";
        body    += "<td align=\"center\" style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\">" + v['shape']+ "</td>";
        body    += "<td align=\"center\" style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\">" + v['zone'] + "</td>";
        body    += "<td align=\"center\" style=\"word-wrap: break-word;min-width: 160px;max-width: 220px;\">" + v['location'] + "</td>";
        body    += "</tr>";
        // body += '<tr>'
        // body    += "<td>cxxxxx</td><td></td><td></td><td></td><td></td><td></td>"
        // body    += "</tr>";
// body += '<tr>';
// body += '    <td style="border: none" class="hiddenRow">';
// body += '        <div id="'+name_no_space+'" class="collapse"><pre id="json">'+breaks+'</pre></div>';
// body += '    </td>';
// body += '<td style="display: none;"></td>';
// body += '<td style="display: none;"></td>';
// body += '<td style="display: none;"></td>';
// body += '<td style="display: none;"></td>';
// body += '<td style="display: none;"></td>';
// body += '</tr>';
        $( body ).appendTo( $( "tbody" ) );
    });

    $( "#dataTables-example" ).DataTable({
            responsive: true
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

'use strict';
var treeWrapper = new TreeWrapper();

(function($){
  $(function() {

      $('.modal-dialog').draggable();
      if ( !localStorage.datasource ) {
          $.getJSON($SCRIPT_ROOT + "/datasource/", function(data){
              checkGuid(data);
          });
          window.location.reload();
      }

      $('#btn-info-nodes').on('click', function() {
        $("#infoModal").modal('hide');
      });

      $('#btn-save').on('click', function() {
          var hier = $('#chart-container').orgchart('getHierarchy');
          console.log((hier));
          $.post($SCRIPT_ROOT + '/_export',
                hier,
              function(data) {
                   console.log(data.result);
              });
          return false;
      });

      $('#chart-container').orgchart({
          'data' : JSON.parse(localStorage.datasource), //$SCRIPT_ROOT + "/datasource/",
          'draggable': true,
          'parentNodeSymbol': 'fa-th-large',
          'createNode': function($node, data) {
              var addNodeIcon = $('<i>', {
                  'class': 'fa fa-plus-circle add-node-icon',
                  click: function () {
                      console.log($node.attr('id') + ' : ' + $node.attr('name'))
                      $('#node-type').find('option').remove()
                      var types = validateType($node.attr('id'));
                      types.forEach(function(type){
                          $('#node-type').append($("<option></option>").attr("value", type).text(
                              type.replace(/\b[a-z]/g,function(f){return f.toUpperCase();})
                          ));
                      });

                      $('#selected-node').attr('readOnly', 'true');
                      $("#addModal").modal('show');
                  }
              });
              var delNodeIcon = $('<i>', {
                  'class': 'fa fa-minus-circle del-node-icon',
                  click: function () {
                      $('#chart-container').orgchart('removeNodes', $node);
                      $('#selected-node').data('node', null);
                      console.log($node)
                      removeStorageNode($node[0].id)
                  }
              });
              var infoNodeIcon = $('<i>', {
                  'class': 'fa fa-cog info-node-icon',
                  click: function () {

                      var parent = $("#treeGrid").parent();
                      $("#treeGrid").jqxTreeGrid('destroy');
                      $(parent).append('<div id="treeGrid"></div>')

                      var rootWrapper = treeWrapper.wrap(JSON.parse(localStorage.datasource));
                      var sourceData = new Array();
                      rootWrapper.traverse(function(item, parent, index, depth) {
                          //console.log(item.name)
                          if (item.guid == $node[0].id){
                              var nested_objects = [];
                              delete item['children'];
                              js_traverse(item, nested_objects);
                              sourceData = nested_objects;
                          }
                      });

                      var newRowID = null;
                      var selectedRow = null;
                      var source =
                      {
                          dataType: "json",
                          dataFields: [
                              { name: "key", type: "string" },
                              { name: "value", type: "string" },
                              { name: 'children', type: 'array' }
                          ],
                          hierarchy:
                          {
                              root: 'children'
                          },
                          id: 'key',
                          localData: sourceData,
                          addRow: function (rowID, rowData, position, parentID, commit) {
                              commit(true);
                              newRowID = rowID;
                          },
                          updateRow: function (rowID, rowData, commit) {
                              console.log('update ' + rowID + ' : ' + rowData.key)
                              if (rowID != rowData.key){
                                  console.log('bugger' + rowData.value)
                                  if (rowData.parent != null){
                                      console.log('auch' + rowData.parent.key)
                                      updateNodeConfig($node.attr('name'), rowData.key, rowData.value, rowData.parent.key)
                                  } else {
                                      console.log('boaaa' + rowData.value)
                                      updateNodeConfig($node.attr('name'), rowData.key, rowData.value, null)
                                  }
                              } else{
                                  updateNodeConfig($node.attr('name'), rowData.key, rowData.value, null)
                              }

                              commit(true);
                          },
                          deleteRow: function (rowID, commit) {
                              console.log('delete: ' + rowID)
                              //console.log(selectedRow.parent.key)
                              if (selectedRow.parent != null){
                                  updateNodeConfig($node.attr('name'), rowID, null, selectedRow.parent.key);
                              } else {
                                  updateNodeConfig($node.attr('name'), rowID, null, null);
                              }

                              commit(true);
                          }
                      };

                      var dataAdapter = new $.jqx.dataAdapter(source);

                      $("#treeGrid").jqxTreeGrid(
                          {
                              width: 800,
                              source: dataAdapter,
                              pageable: true,
                              editable: true,
                              showToolbar: true,
                              altRows: true,
                              columnsResize: true,
                              sortable: true,
                              ready: function()
                              {
                                  // called when the DatatreeGrid is loaded.
                                  $("#treeGrid").jqxTreeGrid('lockRow', 2);
                              },
                              pageSize: 15,
                              pagerButtonsCount: 8,
                              toolbarHeight: 35,
                              renderToolbar: function(toolBar)
                              {
                                  // appends buttons to the status bar.
                                  var container = $("<div id='toolbar' style='overflow: hidden; position: relative; height: 100%; width: 100%;'></div>");
                                  var buttonTemplate = "<div style='float: left; padding: 3px; margin: 2px;'><div style='margin: 4px; width: 16px; height: 16px;'></div></div>";
                                  var addButton = $(buttonTemplate);
                                  var editButton = $(buttonTemplate);
                                  var deleteButton = $(buttonTemplate);
                                  var cancelButton = $(buttonTemplate);
                                  var updateButton = $(buttonTemplate);
                                  container.append(addButton);
                                  container.append(editButton);
                                  container.append(deleteButton);
                                  container.append(cancelButton);
                                  container.append(updateButton);

                                  toolBar.append(container);

                                  addButton.jqxButton({cursor: "pointer", enableDefault: true, disabled: false, height: 25, width: 25 });
                                  addButton.find('div:first').addClass('jqx-icon-plus');
                                  addButton.jqxTooltip({ position: 'bottom', content: "Add"});

                                  editButton.jqxButton({ cursor: "pointer", disabled: true, enableDefault: false,  height: 25, width: 25 });
                                  editButton.find('div:first').addClass('jqx-icon-edit');
                                  editButton.jqxTooltip({ position: 'bottom', content: "Edit"});

                                  deleteButton.jqxButton({ cursor: "pointer", disabled: true, enableDefault: false,  height: 25, width: 25 });
                                  deleteButton.find('div:first').addClass('jqx-icon-delete');
                                  deleteButton.jqxTooltip({ position: 'bottom', content: "Delete"});

                                  updateButton.jqxButton({ cursor: "pointer", disabled: true, enableDefault: false,  height: 25, width: 25 });
                                  updateButton.find('div:first').addClass('jqx-icon-save');
                                  updateButton.jqxTooltip({ position: 'bottom', content: "Save Changes"});

                                  cancelButton.jqxButton({ cursor: "pointer", disabled: true, enableDefault: false,  height: 25, width: 25 });
                                  cancelButton.find('div:first').addClass('jqx-icon-cancel');
                                  cancelButton.jqxTooltip({ position: 'bottom', content: "Cancel"});

                                  var updateButtons = function (action) {
                                      switch (action) {
                                          case "Select":
                                              addButton.jqxButton({ disabled: false });
                                              deleteButton.jqxButton({ disabled: false });
                                              editButton.jqxButton({ disabled: false });
                                              cancelButton.jqxButton({ disabled: true });
                                              updateButton.jqxButton({ disabled: true });
                                              break;
                                          case "Unselect":
                                              addButton.jqxButton({ disabled: true });
                                              deleteButton.jqxButton({ disabled: true });
                                              editButton.jqxButton({ disabled: true });
                                              cancelButton.jqxButton({ disabled: true });
                                              updateButton.jqxButton({ disabled: true });
                                              break;
                                          case "Edit":
                                              addButton.jqxButton({ disabled: true });
                                              deleteButton.jqxButton({ disabled: true });
                                              editButton.jqxButton({ disabled: true });
                                              cancelButton.jqxButton({ disabled: false });
                                              updateButton.jqxButton({ disabled: false });
                                              break;
                                          case "End Edit":
                                              addButton.jqxButton({ disabled: false });
                                              deleteButton.jqxButton({ disabled: false });
                                              editButton.jqxButton({ disabled: false });
                                              cancelButton.jqxButton({ disabled: true });
                                              updateButton.jqxButton({ disabled: true });
                                              break;
                                      }
                                  }

                                  $("#toolbar").click(function () {
                                      $("#treeGrid").jqxTreeGrid('clearSelection');
                                  })

                                  var rowKey = null;
                                  $("#treeGrid").on('rowSelect', function (event) {
                                      var args = event.args;
                                      selectedRow = args.row;
                                      rowKey = args.key;
                                      updateButtons('Select');
                                  });
                                  $("#treeGrid").on('rowUnselect', function (event) {
                                      updateButtons('Unselect');
                                  });
                                  $("#treeGrid").on('rowEndEdit', function (event) {
                                      updateButtons('End Edit');
                                  });
                                  $("#treeGrid").on('rowBeginEdit', function (event) {
                                      updateButtons('Edit');
                                  });
                                  addButton.click(function (event) {
                                      if (!addButton.jqxButton('disabled')) {
                                          $("#treeGrid").jqxTreeGrid('expandRow', rowKey);
                                          // add new empty row.
                                          $("#treeGrid").jqxTreeGrid('addRow', null, {}, 'first', rowKey);
                                          // select the first row and clear the selection.
                                          $("#treeGrid").jqxTreeGrid('clearSelection');
                                          $("#treeGrid").jqxTreeGrid('selectRow', newRowID);
                                          // edit the new row.
                                          $("#treeGrid").jqxTreeGrid('beginRowEdit', newRowID);
                                          updateButtons('add');
                                      }
                                  });

                                  cancelButton.click(function (event) {
                                      if (!cancelButton.jqxButton('disabled')) {
                                          // cancel changes.
                                          $("#treeGrid").jqxTreeGrid('endRowEdit', rowKey, true);
                                      }
                                  });

                                  updateButton.click(function (event) {
                                      if (!updateButton.jqxButton('disabled')) {
                                          // save changes.
                                          $("#treeGrid").jqxTreeGrid('endRowEdit', rowKey, false);
                                      }
                                  });

                                  editButton.click(function () {
                                      if (!editButton.jqxButton('disabled')) {
                                          $("#treeGrid").jqxTreeGrid('beginRowEdit', rowKey);
                                          updateButtons('edit');
                                      }
                                  });

                                  deleteButton.click(function () {
                                      if (!deleteButton.jqxButton('disabled')) {
                                          var selection = $("#treeGrid").jqxTreeGrid('getSelection');
                                          if (selection.length > 1) {
                                              var keys = new Array();
                                              for (var i = 0; i < selection.length; i++) {
                                                  keys.push($("#treeGrid").jqxTreeGrid('getKey', selection[i]));
                                              }
                                              $("#treeGrid").jqxTreeGrid('deleteRow', keys);
                                          } else {
                                              $("#treeGrid").jqxTreeGrid('deleteRow', rowKey);
                                          }
                                          updateButtons('delete');
                                      }
                                  });
                              },
                              columns: [
                                  { text: 'Item', dataField: 'key', width: 300 },
                                  { text: 'Value', dataField: 'value'} /*,
                                  { text: 'Type', columnType: "template", createEditor: function (row, cellvalue, editor, cellText, width, height) {
                       // construct the editor.
                       var source = ["String", "Array", "Object"];
                       editor.jqxDropDownList({autoDropDownHeight: true, source: source, width: '100%', height: '100%' });
                   },
                   initEditor: function (row, cellvalue, editor, celltext, width, height) {
                       // set the editor's current value. The callback is called each time the editor is displayed.
                       editor.jqxDropDownList('selectItem', cellvalue);
                   },
                   getEditorValue: function (row, cellvalue, editor) {
                       // return the editor's value.
                       return editor.val();
                   }

                                  } */
                              ]
                          });



                      //$("#treeGrid").jqxTreeGrid('refresh');
                      $('#selected-node-info').attr('readOnly', 'true');
                      $('#form-InfoNode').hide();
                      $("#infoModal").modal('show');
                  }
              });

              $node.on(
                  'click', function (event) {
                      if (!$(event.target).is('.edge')) {
                          $('#selected-node').val(data.name).data('node', $node);
                          $('#selected-node-info').val(data.name).data('node', $node);
                      }
                  });

              $node.append(delNodeIcon);
              $node.append(addNodeIcon);
              $node.append(infoNodeIcon);
          }
      })

      $('#btn-add-nodes').on('click', function() {
          var guid = 'id-' + Math.random().toString(36).substr(2, 16);
          var nodeVals = [];
          var validVal = $('#new-node')[0].value.trim();
          if (nodeExistwithName(validVal)){
              $.alert("Each node requires a unique name within the tree !", {
                    autoClose: true,
                    closeTime: 2000,
                    type: 'danger'
                  });
              return;
          }
          if (validVal.length) {
              nodeVals.push(validVal);
          }

          var $node = $('#selected-node').data('node');
          if (!nodeVals.length) {
              alert('Please input value for new node');
              return;
          }

          /*var nodeType = $('input[name="node-type"]:checked');
          if (nodeType.val() !== 'parent' && !$node) {
              alert('Please select one node in orgchart');
              return;
          }*/

          var hasChild = $node.parent().attr('colspan') > 0 ? true : false;
          if (!hasChild) {
              var rel = nodeVals.length > 1 ? '110' : '100';
              $('#chart-container').orgchart('addChildren', $node, {
                  'children': nodeVals.map(function(item) {
                      createStorageNode($node[0].id, item,$('#node-type')[0].value.trim(), guid)
                      return { 'guid': guid, 'name': item, 'type': $('#node-type')[0].value.trim(), 'relationship': rel };
                  })
              }, $.extend({}, $('#chart-container').data('orgchart').options, { depth: 0 }));
          } else {
              $('#chart-container').orgchart('addSiblings', $node, $node.closest('tr').siblings('.nodes').find('.node:first'),
                  {
                      'siblings': nodeVals.map(function(item) {
                          console.log($node[0].id);
                          createStorageNode($node[0].id, item,$('#node-type')[0].value.trim(), guid)
                          return { 'guid': guid, 'name': item, 'type': $('#node-type')[0].value.trim(), 'relationship': '110' };
                      })
                  });
          }

          $('#new-node').val('');
          $("#addModal").modal('hide');
          $node = null;
          //window.location.reload();
      });

      $('#btn-delete-nodes').on('click', function() {
          var $node = $('#selected-node').data('node');
          if (!$node) {
              alert('Please select one node in orgchart');
              return;
          }
          $('#chart-container').orgchart('removeNodes', $node);
          $('#selected-node').data('node', null);

      });

  });
})(jQuery);

function js_traverse(o, nested_object) {
    for (var key in o){
        if (typeof o[key] == 'object'){
            //if (o[key].children != null){
                console.log(o[key])
            //}
            var nested_object_new = [];
            nested_object.push({key: key, children: nested_object_new})
            js_traverse(o[key],nested_object_new);
        } else {
            nested_object.push({key: key, value: o[key]})
        }
    }

}

function update_traverse(o, parentKey, key, value) {

    for (var item in o){
        if (item == parentKey){
             if (value != null) {
                 console.log('update: ' + key + ':' +value + ' parent: ' + parentKey)
                 console.log(typeof value)
                 console.log('--------------')
                 console.log(o[item])
                 o[item][key] = value;
                 console.log(o[item][key])
             } else {
                 console.log('delete: ' + o[item][key])
                 delete o[item][key];
             }
            //localStorage.setItem("datasource", JSON.stringify(rootWrapper.unwrap()));
        }
        if (typeof o[item] == 'object'){
            update_traverse(o[item], parentKey, key, value);
        }
    }
}

function checkGuid(data) {
    var rootWrapper = treeWrapper.wrap(data);
    rootWrapper.traverse(function(item, parent, index, depth) {
        if (item.guid == null) {
            item['guid'] = 'id-' + Math.random().toString(36).substr(2, 16);
        }
    });
    localStorage.setItem("datasource", JSON.stringify(rootWrapper.unwrap()));
}

function getNodeConfig(node) {
    var arr = {};
    var rootWrapper = treeWrapper.wrap(JSON.parse(localStorage.datasource));
    rootWrapper.traverse(function(item, parent, index, depth) {
        if (item.guid == node) {
            for (var key in item){
                if (key != 'children' && key.length > 0){
                    arr[key] = item[key]
                }
            }
        }
    });
    return arr;
}

function nodeExistwithName(node) {
    var ret = false
    var rootWrapper = treeWrapper.wrap(JSON.parse(localStorage.datasource));
    rootWrapper.traverse(function(item, parent, index, depth) {
        if (item.name == node) {
            ret = true;
        }
    });
    return ret;
}


function updateNodeConfig(node, key, value, keyParent) {
    // I still need to remove no present keys
    console.log('test')
    var rootWrapper = treeWrapper.wrap(JSON.parse(localStorage.datasource));
    rootWrapper.traverse(function(item, parent, index, depth) {
        if (item.name == node) {
            if (keyParent != null){
                console.log('wuaaw boe ' + node + ' key: ' + key + ' val: '  + value);
                update_traverse(item, keyParent, key, value);
                console.log(item);
                console.log(JSON.stringify(rootWrapper.unwrap()))
                localStorage.setItem("datasource", JSON.stringify(rootWrapper.unwrap()));
            } else {
                if (value != null){
                    console.log('root update: ' + item[key] + ':' +value)
                    item[key] = value;
                } else{
                    console.log('root delete: ' + item[key])
                    delete item[key]
                }
            }
            localStorage.setItem("datasource", JSON.stringify(rootWrapper.unwrap()));
            //console.log(JSON.stringify(rootWrapper.unwrap()))
        }
            /*var bFound = false;
            for (var child in item) {
                if (child == key) {
                    if (value != null){
                        item[key] = value;
                        bFound = true;
                    } else {
                        console.log('wuaaw found')
                        delete item[key];
                        bFound = true;
                    }
                }
            }
            if (!bFound){
                console.log('wuaaw not found')
                for (var child in item){
                    console.log('0: ' + child + ':' + keyParent)
                    if (child == keyParent){
                         console.log('3:' + item[child])
                        if (value != null){
                            console.log('2')
                            item[child][key] = value;
                        } else {
                            console.log('3')
                            delete item[child][key];
                        }

                    }
                }
            }
        }*/
    });
}

function createStorageNode(parentNode, newNode, type, guid) {
    var rootWrapper = treeWrapper.wrap(JSON.parse(localStorage.datasource));
    rootWrapper.traverse(function(item, parent, index, depth){
        if (item.guid == parentNode){
            var childItem = {guid: guid, name: newNode, type: type};
             console.log(childItem)
            if (parent == 'Common'){
                rootWrapper.addChild(0,childItem)
            } else {
                var parentWrapper = treeWrapper.createItemWrapper(item, parent);
                parentWrapper.addChild(0, childItem)
            }

            localStorage.setItem("datasource", JSON.stringify(rootWrapper.unwrap()))
        }
    })
}

function removeStorageNode(node) {
    var rootWrapper = treeWrapper.wrap(JSON.parse(localStorage.datasource));
    console.log('delete: ' + node)
    rootWrapper.traverse(function(item, parent, index, depth){
        if (item.guid === node){
            if (parent === 'Common') {
                rootWrapper.removeChild(index - 1);
            } else {
                var item2Wrapper = treeWrapper.createItemWrapper(item, parent);
                item2Wrapper.remove();
           }
        }

    })
    localStorage.setItem("datasource", JSON.stringify(rootWrapper.unwrap()))
}

function moveStorageNode(sourceNode, sourceType, newParentNode) {

    var node = getNodeConfig(sourceNode)

    var rootWrapper = treeWrapper.wrap(JSON.parse(localStorage.datasource));
    rootWrapper.traverse(function(item, parent, index, depth){
        if (item.guid == sourceNode){
            if (parent == 'Common') {
                rootWrapper.removeChild(index - 1);
            } else {
                var parentWrapper = treeWrapper.createItemWrapper(item, parent);
                parentWrapper.remove();
           }
        }
    });

    rootWrapper.traverse(function(item, parent, index, depth){
        if (item.guid == newParentNode){
            var childItem = {id: sourceNode, name: sourceNode, type: sourceType};
            if (parent == 'Common'){
                rootWrapper.addChild(0,node)
            } else {
                var parentWrapper = treeWrapper.createItemWrapper(item, parent);
                parentWrapper.addChild(0, node)
            }
        }
    })

    localStorage.setItem("datasource", JSON.stringify(rootWrapper.unwrap()));

}

function copyStorageNode(sourceNode, sourceType, newParentNode, guid) {

    var rootWrapper = treeWrapper.wrap(JSON.parse(localStorage.datasource));
    rootWrapper.traverse(function(item, parent, index, depth){
        if (item.guid == newParentNode){
            var node = getNodeConfig(sourceNode)
            node['guid'] = guid;
            //var childItem = {id: sourceNode, name: node.name, type: sourceType};
            if (parent === 'Common'){
                rootWrapper.addChild(0, node)
            } else {
                var parentWrapper = treeWrapper.createItemWrapper(item, parent);
                parentWrapper.addChild(0, node)
            }
        }
    })

    localStorage.setItem("datasource", JSON.stringify(rootWrapper.unwrap()));

}

function validateType(sourceNode) {
    console.log('-==: ' + sourceNode)
    var arr = new Array();
    iterate(sourceNode, arr);
    return arr;
}

function iterate(node, arr) {
    /* reply with environment, location, zone or a combi depending*/
    /* Check for child Items and of which Type, if so only show Type    */
    /* Check for siblings and their types -> go to parent, get child types */
    /* Check siblings child types  */
    var arrTypes = ["environment", "location", "zone"];
    var tArr = new Array();

    var rootWrapper = treeWrapper.wrap(JSON.parse(localStorage.datasource));
    rootWrapper.traverse(function(item, parent, index, depth) {
        if (item.guid == node) {
            console.log('get child items');
            if (item.children != null && item.children.length > 0){
                console.log('\t found child items');
                arr.length = 0;
                for (var child in item.children){
                    if (arr.indexOf(item.children[child].type) == -1){
                        arr.push(item.children[child].type);
                    }
                }
                return;
            } else {
                if (parent != null && parent.children.length > 0){
                    console.log('get siblings');
                    for (var sibling in parent.children){
                        if (parent.children[sibling].children != null && parent.children[sibling].children.length > 0){
                            console.log('\t get siblings childs');
                            arr.length = 0;
                            for (var child in parent.children[sibling].children){
                                console.log('\t\t child: ' + parent.children[sibling].children[child].name );
                                if (arr.indexOf(parent.children[sibling].children[child].type) == -1){
                                    arr.push(parent.children[sibling].children[child].type)
                                };
                            };
                            return;
                        } else {
                            console.log('\t this siblings: ' + parent.children[sibling].name + ' has no child');
                            if (arrTypes.indexOf(parent.children[sibling].type) >= 0) {
                                console.log('\t remove type: ' + parent.children[sibling].type + ' from array');
                                arrTypes.splice(arrTypes.indexOf(parent.children[sibling].type), 1)

                                console.log('\t\t loop over parents and remove parent types')
                                var i = 0;
                                rootWrapper.traverse(function(itemP, parentP, indexP, depthP) {
                                    console.log('\t\t removing ' + itemP.name + ':' + node + ' depth:' + depth + ' depthp:' + depthP)
                                    if (itemP.guid != node){
                                        if (arrTypes.indexOf(itemP.type) >= 0 && depthP < depth) {
                                            arrTypes.splice(itemP.type, 1)
                                        }
                                    }
                                });
                                arrTypes.forEach(function (type){
                                    arr.push(type);
                                });

                            }
                        }
                    }
                } else {
                    arrTypes.forEach(function (type){
                        arr.push(type);
                    });
                }
            }
        }
    });

}



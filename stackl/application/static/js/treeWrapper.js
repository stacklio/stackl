(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        define(['lodash', './polyfills.js'], factory);
    } else if (typeof exports === 'object') {
        module.exports = factory(require('lodash'), require('./polyfills.js'));
    } else {
        root.TreeWrapper = factory(root._, root.jsonTreeWrapPolyfills);
    }
}(this, function (_, polyfills) {

    polyfills();

    function TreeWrapper(options) {
        options = options || {};
        var noOp = function() {};
        this.options = _.defaults(options, {
            childrenProp: 'children',
            onInit: noOp,
            onAdd: noOp,
            onRemove: noOp,
            onMove: noOp
        });

        if (options.observer) {
            if (options.observer.onInit) this.options.onInit = options.observer.onInit.bind(options.observer);
            if (options.observer.onAdd) this.options.onAdd = options.observer.onAdd.bind(options.observer);
            if (options.observer.onRemove) this.options.onRemove = options.observer.onRemove.bind(options.observer);
            if (options.observer.onMove) this.options.onMove = options.observer.onMove.bind(options.observer);
        }

        this.childrenProp = this.options.childrenProp;
    }

    TreeWrapper.prototype = {
        wrap: function(obj) {
            if (!obj) {
                throw new Error('Object to wrap was null');
            }

            var parent = null;

            if (this.options.onInit) {
                traverse(obj, parent, 0, 0, this.childrenProp, function(item, parent, index, depth) {
                    this.options.onInit(parent, index, item, depth);
                }.bind(this));
            }

            return createItemWrapper(obj, parent, this.options);
        },
        createItemWrapper: function(item, parent) {
            return createItemWrapper(item, parent, this.options);
        },
        // TODO: this is a bit of a smell. Just here to reuse the childrenProp config
        traverse: function(item, callback) {
            traverseSimple(item, null, this.childrenProp, callback);
        }
    };

    return TreeWrapper;

    function createItemWrapper(obj, parent, options) {

        function getItemIndexOrThrow(parentItems, item) {
            var thisItemIndex = parentItems.indexOf(item);
            if (thisItemIndex < 0) {
                throw new Error('Could not find item in parent items');
            }
            return thisItemIndex;
        }

        return {
            getChild: function(index) {
                var items = getOrCreateChildItems(obj, options.childrenProp);
                return createItemWrapper(items[index], obj, options);
            },
            addChild: function(index, newObj, stateObj) {
                var items = getOrCreateChildItems(obj, options.childrenProp);
                items.splice(index, null, newObj);
                options.onAdd(obj, index, newObj, stateObj);
            },
            addChildAtEnd: function(newObj, stateObj) {
                var items = getOrCreateChildItems(obj, options.childrenProp);
                this.addChild(items.length, newObj, stateObj);
            },
            addAbove: function(newObj, stateObj) {
                if (!parent) {
                    throw new Error('Cannot add above the root item');
                }
                var parentItems = getOrCreateChildItems(parent, options.childrenProp);
                var thisItemIndex = getItemIndexOrThrow(parentItems, obj);
                parentItems.splice(thisItemIndex, 0, newObj);
                options.onAdd(parent, thisItemIndex, newObj, stateObj);
            },
            addBelow: function(newObj, stateObj) {
                if (!parent) {
                    throw new Error('Cannot add below the root item');
                }
                var parentItems = getOrCreateChildItems(parent, options.childrenProp);
                var thisItemIndex = getItemIndexOrThrow(parentItems, obj);
                parentItems.splice(thisItemIndex + 1, 0, newObj);
                options.onAdd(parent, thisItemIndex + 1, newObj, stateObj);
            },
            remove: function() {
                var parentItems = getOrCreateChildItems(parent, options.childrenProp);
                var thisItemIndex = getItemIndexOrThrow(parentItems, obj);
                var removed = parentItems.splice(thisItemIndex, 1);
                if (removed.length) {
                    options.onRemove(parent, thisItemIndex, removed[0]);
                }
            },
            removeChild: function(index) {
                var items = getOrCreateChildItems(obj, options.childrenProp);
                var removed = items.splice(index, 1);
                if (removed.length) {
                    options.onRemove(obj, index, removed[0]);
                }
                return removed[0];
            },
            moveChild: function(removeIndex, insertIndexOrNewParent, newParentInsertIndex) {
                if (insertIndexOrNewParent == this) {
                    //throw new Error('Cannot move an item under itself');
                }


                var items = getOrCreateChildItems(obj, options.childrenProp);
                var removed = items.splice(removeIndex, 1);
                if (!removed.length) {
                    return;
                }
                var removedItem = removed[0];

                if (typeof insertIndexOrNewParent === 'number') {
                    items.splice(insertIndexOrNewParent, null, removedItem);
                    options.onMove(obj, removeIndex, obj, insertIndexOrNewParent, removedItem);
                } else {
                    var newParent = insertIndexOrNewParent.unwrap();

                    var newParentItems = getOrCreateChildItems(newParent, options.childrenProp);
                    newParentItems.splice(newParentInsertIndex, null, removedItem);

                    options.onMove(obj, removeIndex, newParent, newParentInsertIndex, removedItem);
                }
            },
            unwrap: function() {
                return obj;
            },
            traverse: function(callback) {
                traverse(obj, parent, 0, 0, options.childrenProp, callback);
            }
        };
    }

    function traverseSimple(item, parent, childrenProp, callback) {
        callback(item, parent);

        var children = item[childrenProp];
        if (!children) {
            return;
        }

        for (var i = 0; i < children.length; i++) {
            var child = children[i];
            traverseSimple(child, item, childrenProp, callback);
        }
    }

    function traverse(item, parent, index, depth, childrenProp, callback) {
        callback(item, parent, index++, depth);

        var children = item[childrenProp];
        if (!children) {
            return index;
        }

        for (var i = 0; i < children.length; i++) {
            var child = children[i];
            index = traverse(child, item, index, depth + 1, childrenProp, callback);
        }

        return index;
    }

    function getOrCreateChildItems(obj, childrenProp) {
        var arr = obj[childrenProp];
        if (!arr) {
            arr = [];
            obj[childrenProp] = arr;
        }
        return arr;
    }
}));

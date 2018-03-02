class NodeError(Exception):
    def __init__(self, message):
        self.message = message

    def print_message(self):
        print("Error! {}".format(self.message))


class ChildrenSettingError(NodeError):
    def __init__(self, message):
        super().__init__(message)


class ParentSettingError(NodeError):
    def __init__(self, message):
        super().__init__(message)


class Node:
    def __init__(self, data=None, parent=None, children=None, layer=None, is_root=False, is_leaf=False):
        self.data = data
        try:
            self.parent = self.set_parent(parent)
        except ParentSettingError as e:
            e.print_message()
            raise NodeError("Cannot create a node.")

        if children is None:
            self.children = []
        else:
            try:
                self.children = self.set_children(children)
            except ChildrenSettingError as e:
                e.print_message()
                raise NodeError("Cannot create a node.")

        if layer is not None:
            self.layer = layer
        else:
            self.layer = None

        self.root_attr = is_root
        self.leaf_attr = is_leaf

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def set_parent(self, parent):
        if parent is None:
            self.parent = None
        elif not isinstance(parent, Node):
            raise ParentSettingError("Cannot set a parent for the node. The given parent must have "
                                     "type 'Node'but the given has type {}".format(type(parent)))
        else:
            self.parent = parent

    def get_parent(self):
        return self.parent

    def set_children(self, children):
        if not isinstance(children, list) and not isinstance(children, tuple):
            raise ChildrenSettingError("Cannot set children for the node. The given list of children must have "
                                       "type 'list' or 'tuple'. The given has type {}".format(type(children)))
        else:
            self.children.extend(children)

    def has_one_child(self):
        if len(self.children) == 1:
            return True
        else:
            return False

    def get_children(self):
        return self.children

    def set_layer(self, layer):
        self.layer = layer

    def get_layer(self):
        return self.layer

    def set_root_attr(self, root_flag):
        self.root_attr = root_flag

    def is_root(self):
        return self.root_attr

    def set_leaf_attr(self, leaf_attr):
        self.leaf_attr = leaf_attr

    def if_leaf(self):
        return self.leaf_attr


class Graph:
    pass

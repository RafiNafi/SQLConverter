class Statement:
    def __init__(self, keyword, text):
        self.keyword = keyword
        self.text = text


class Property:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Node:
    def __init__(self, name="", label=""):
        self.name = name
        self.label = label
        self.properties = []

    def add_property(self, prop):
        self.properties.append(prop)


class Relationship:
    def __init__(self, name, label, node_l, node_r, arrow_dir):
        self.name = name
        self.label = label
        self.properties = []
        self.node_r = node_r
        self.node_l = node_l
        self.direction = dir

    def add_property(self, prop):
        self.properties.append(prop)


class MatchPart:
    def __init__(self):
        self.relationships = []
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_relationship(self, relationship):
        self.relationships.append(relationship)

    def get_node_by_label(self,label):

        for node in self.nodes:
            if node.label == label:
                return node

    def get_node_by_name(self,name):

        for node in self.nodes:
            if node.name == name:
                return node
    def generate_query_string(self):

        query = "MATCH "

        #generate query

        for n in self.nodes:
            query += "("+n.label+":"+n.name+") "

        return query

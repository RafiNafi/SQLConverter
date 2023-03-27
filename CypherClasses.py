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
        self.relationships = []

    def add_property(self, prop):
        self.properties.append(prop)

    def add_relationship(self, rel):
        self.relationships.append(rel)


class Relationship:
    def __init__(self, name, label, node_l, node_r, arrow_dir_l, arrow_dir_r):
        self.name = name
        self.label = label
        self.properties = []
        self.node_r = node_r
        self.node_l = node_l
        self.arrow_dir_l = arrow_dir_l
        self.arrow_dir_r = arrow_dir_r

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

    def get_node_by_label(self, label):

        for node in self.nodes:
            if node.label == label:
                return node

    def get_node_by_name(self, name):

        for node in self.nodes:
            if node.name == name:
                return node

    def get_index_of_obj(self,chain,node_l):

        for index,elem in enumerate(chain):
            if elem == node_l:
                return index

    def generate_query_string(self):

        query = "MATCH "

        # generate query
        chain = []

        if len(self.relationships) < 1:
            for n in self.nodes:
                chain.append(n)
        else:
            for r in self.relationships:

                if r.node_l in chain:
                    index = self.get_index_of_obj(chain, r.node_l)

                    if len(chain) == index + 1:
                        chain.insert(index + 1, r.node_r)
                        chain.insert(index + 1, r)
                    else:
                        chain.insert(index, r)
                        chain.insert(index, r.node_r)
                    continue

                elif r.node_r in chain:
                    index = self.get_index_of_obj(chain, r.node_r)

                    if len(chain) == index + 1:
                        chain.insert(index + 1, r.node_l)
                        chain.insert(index + 1, r)
                    else:
                        chain.insert(index, r)
                        chain.insert(index, r.node_l)
                    continue

                else:
                    chain.append(r.node_l)
                    chain.append(r)
                    chain.append(r.node_r)

        for elem in chain:
            if type(elem) == Relationship:
                query += elem.arrow_dir_l + "[" + elem.label + ":" + elem.name + "]" + elem.arrow_dir_r
            elif type(elem) == Node:
                query += "(" + elem.label + ":" + elem.name + ")"

        #node_l = "(" + r.node_l.label + ":" + r.node_l.name + ")"
        #node_r = "(" + r.node_r.label + ":" + r.node_r.name + ")"
        #query += node_l + r.arrow_dir_l + "[" + r.label + ":" + r.name + "]" + r.arrow_dir_r + node_r

        return query + " "

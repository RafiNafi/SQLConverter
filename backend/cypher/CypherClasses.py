class Statement:
    def __init__(self, keyword, text, array):
        self.keyword = keyword
        self.text = text
        self.array_orig = array  # contains parsed query parts (only for already existing parts in query)


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

    def get_formatted_node_string(self):
        formatted_string = "(" + self.name + ":" + self.label

        if len(self.properties) > 0:
            formatted_string += " {"
            for idx, prop in enumerate(self.properties):
                formatted_string += str(prop.name) + ": " + str(prop.value)

                if idx != len(self.properties) - 1:
                    formatted_string += ", "

            formatted_string += "}"

        formatted_string += ")"

        return formatted_string


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

    def get_index_of_obj(self, chain, node_l):

        for index, elem in enumerate(chain):
            if elem == node_l:
                return index

    def generate_query_string(self, text):

        query = text

        # generate query
        chain = []

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

        for n in self.nodes:
            if n not in chain:
                if len(chain) < 1:
                    query += "(" + n.label + ":" + n.name + ")"
                    chain.append(n)
                else:
                    query += ",(" + n.label + ":" + n.name + ")"

        query += " "

        return query


class OptionalMatchPart(MatchPart):
    pass
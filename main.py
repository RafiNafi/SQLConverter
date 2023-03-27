import sqlvalidator
import sqlparse
from CypherClasses import Node, Relationship, Property, Statement, MatchPart

keywords_all = ["SELECT", "DISTINCT", "FROM", "AS", "JOIN", "ON", "WHERE", "GROUP BY", "AND", "XOR", "OR", "NOT",
                "ORDER BY",
                "FULL JOIN", "IN", "BETWEEN", "ASC", "DESC", "LIKE", "LEFT OUTER JOIN", "RIGHT OUTER JOIN", "HAVING",
                "UNION", "LIMIT", "ALL", "ANY", "EXISTS"]

keywords_essential = ["SELECT", "FROM", "JOIN", "WHERE", "GROUP BY", "ORDER BY", "FULL JOIN", "LEFT OUTER JOIN",
                      "RIGHT OUTER JOIN", "HAVING", "UNION", "LIMIT"]

queryParts = []
sql_query_parts = []

def get_match_part():
    for query in queryParts:
        if isinstance(query, MatchPart):
            return query


def recursiveTree(tokenT):
    if type(tokenT) != sqlparse.sql.Token:
        for t in tokenT:
            if type(t) != sqlparse.sql.Token:
                recursiveTree(t)
            else:
                print(str(t))
    else:
        print(str(tokenT))
        return

def make_part_query_string(name, array):
    string_query = ""
    for token in array:
        string_query += str(token)

    statement = Statement(name, string_query)
    queryParts.append(statement)

    return statement.text

def combine_query():
    combined_query_string = ""

    for elem in queryParts:
        if type(elem) != MatchPart:
            if elem.keyword != "SELECT":
                combined_query_string += elem.text

    for elem in queryParts:
        if type(elem) == MatchPart:
            combined_query_string = elem.generate_query_string() + combined_query_string
        elif elem.keyword == "SELECT":
            combined_query_string = combined_query_string + elem.text
    return combined_query_string

def query_conversion(query):
    parsed = sqlparse.parse(query)[0]

    # cut array in multiple arrays per major keyword
    for i in parsed:
        # print(str(i))
        if str(i) in keywords_essential or type(i) == sqlparse.sql.Where:
            sql_query_parts.append([])
        sql_query_parts[len(sql_query_parts) - 1].append(i)

    # transform query parts
    for i in range(len(sql_query_parts)):
        print(transformQueryPart(str(sql_query_parts[i][0]), sql_query_parts[i]))

def transformQueryPart(text, array):
    # if WHERE clause then cut into pieces
    if str(array[0]).split(" ")[0] == "WHERE":
        text = "WHERE"
        new_array = []
        for token in array[0]:
            new_array.append(token)
        array.clear()
        array = new_array

    print("_________")
    print(text)
    print(array)

    match text:
        case "SELECT":
            statement = Statement("SELECT", "RETURN ")

            for t in array:
                if str(t) == "DISTINCT":
                    statement.text = statement.text + "DISTINCT "

                if type(t) == sqlparse.sql.IdentifierList:
                    for index, obj in enumerate(t.get_identifiers()):
                        #print(obj)
                        if (index == len(list(t.get_identifiers())) - 1):
                            statement.text = statement.text + str(obj) + " "
                        else:
                            statement.text = statement.text + str(obj) + ", "
                elif type(t) == sqlparse.sql.Identifier:
                    statement.text = statement.text + str(t) + " "

            queryParts.append(statement)

            return statement.text
        case "FROM":
            statement = MatchPart()

            for t in array:

                if type(t) == sqlparse.sql.IdentifierList:
                    for obj in enumerate(t.get_identifiers()):
                        #print(obj)
                        if "AS" in str(obj).split(" "):
                            as_parts = str(obj).split(" ")
                            statement.add_node(Node(as_parts[0], as_parts[2]))
                        else:
                            statement.add_node(Node(str(obj)))

                elif type(t) == sqlparse.sql.Identifier:
                    if "AS" in str(t).split(" "):
                        as_parts = str(t).split(" ")
                        statement.add_node(Node(as_parts[0], as_parts[2]))
                    else:
                        statement.add_node(Node(str(t)))

            queryParts.append(statement)

            return statement.generate_query_string()
        case "WHERE":
            statement = Statement("WHERE", "WHERE ")

            queryParts.append(statement)
            return statement.text
        case "AS":
            return "AS"
        case "JOIN" | "FULL JOIN":

            match_query = get_match_part()

            for token in array:
                if type(token) == sqlparse.sql.Identifier:
                    #print(token)
                    if "AS" in str(token).split(" "):
                        as_parts = str(token).split(" ")
                        match_query.add_node(Node(as_parts[0], as_parts[2]))
                    else:
                        match_query.add_node(Node(str(token)))

            for token in array:
                if type(token) == sqlparse.sql.Parenthesis:
                    for comp in token:
                        if type(comp) == sqlparse.sql.Comparison:
                            values = str(comp).split(" ")

                            # checks for name first then label

                            node1 = match_query.get_node_by_name(values[0].split(".")[0])
                            node2 = match_query.get_node_by_name(values[len(values) - 1].split(".")[0])

                            if node1 is None:
                                node1 = match_query.get_node_by_label(values[0].split(".")[0])
                            if node2 is None:
                                node2 = match_query.get_node_by_label(values[len(values) - 1].split(".")[0])

                            # relationship name
                            # direction relevant?
                            rel = Relationship("relationship", "", node2, node1, "-", "-")

                            # add relationship to node
                            node1.add_relationship(rel)
                            # add relationship to match query part
                            match_query.add_relationship(rel)

            return match_query.generate_query_string()
        case "GROUP BY":
            return ""
        case "ORDER BY":
            return make_part_query_string(text,array)
        case "LEFT OUTER JOIN" | "RIGHT OUTER JOIN":
            return "OPTIONAL MATCH"
        case "HAVING":
            return "WITH # WHERE"
        case "UNION":
            return "UNION"
        case "UNION ALL":
            return "UNION ALL"
        case "LIMIT":
            return make_part_query_string(text,array)
        case "UNION ALL":
            return "UNION ALL"
        case "ASC":
            return "ASC"
        case "DESC":
            return "DESC"

    return "not found"


if __name__ == '__main__':

    # test queries
    query2 = "SELECT e.EmployeeID, count(*) AS Count " \
            "FROM Employee AS e " \
            "JOIN ord AS o ON (o.EmployeeID = e.EmployeeID) " \
            "JOIN products AS p ON (p.ProductID = o.ProductID) " \
            "WHERE e.EmployeeID = 100 " \
            "GROUP BY e.EmployeeID " \
            "ORDER BY Count DESC " \
            "LIMIT 10;"

    query = "SELECT p.ProductName, p.UnitPrice " \
             "FROM products AS p " \
             "WHERE p.ProductName LIKE 'C%' AND p.UnitPrice > 100;"


    sql_query = sqlvalidator.parse(query)

    # check if query valid
    if not sql_query.is_valid():
        print(sql_query.errors)
    else:
        print("everything fine!")

    print("--------------------------------")

    # parse and print string
    parsed = sqlparse.parse(query)[0]
    print(parsed.tokens)

    print("--------------------------------")

    query_conversion(query)
    print(combine_query())

    print("--------------------------------")

    # for token in sqlparse.sql.IdentifierList(tokensP).get_identifiers():
    #    recursiveTree(token)

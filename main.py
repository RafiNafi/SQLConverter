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

def get_query_part_by_name(name):
    for query in queryParts:
        if isinstance(query, Statement):
            if query.keyword == name:
                return query

def get_correct_command_string(text, variable):
    text = text.replace("'", "")
    text = text.replace("\"", "")

    if text[-1] == "%" and text[0] == "%":
        return variable+" CONTAINS \"" + text[1:-1] + "\""
    elif text[0] == "%":
        return variable+" ENDS WITH \"" + text[1:] + "\""
    elif text[-1] == "%":
        return variable+" STARTS WITH \"" + text[:-1] + "\""
    elif text[-1] != "%" and text[0] != "%" and ("%" in text) and (text.count("%") == 1):
        return variable+" STARTS WITH \"" + text.split("%")[0] + "\" AND "+variable+" ENDS WITH \"" + text.split("%")[1] + "\""


def make_part_query_string(name, array):
    string_query = ""
    for token in array:
        string_query += str(token)

    if string_query[-1] != " ":
        string_query += " "

    statement = Statement(name, string_query)
    queryParts.append(statement)

    return statement.text


def combine_query():
    combined_query_string = ""

    # add all query parts except for match and return
    for elem in queryParts:
        if type(elem) != MatchPart:
            if elem.keyword != "SELECT":
                combined_query_string += elem.text

    # add match part at the beginning and return part at the end
    for elem in queryParts:
        if type(elem) == MatchPart:
            combined_query_string = elem.generate_query_string() + combined_query_string
        elif elem.keyword == "SELECT":
            combined_query_string = combined_query_string + elem.text

    # add semicolon
    combined_query_string += ";"

    return combined_query_string


def swap_text_with_previous(text, searchstring):
    # search string and swap with previous
    parts = text.split(" ")
    indexes = []

    #print(parts)
    for idx, elem in enumerate(parts):
        if elem == searchstring:
            indexes.append(idx)

    for index in indexes:
        parts[index], parts[index - 1] = parts[index - 1], parts[index]

    result = ""
    for idx,elem in enumerate(parts):
        if idx == len(parts)-1:
            result = result + elem
        else:
            result = result + elem + " "

    return result


def query_conversion(query):
    queryParts.clear()
    sql_query_parts.clear()

    parsed = sqlparse.parse(query)[0]

    # cut array in multiple arrays per major keyword
    for i in parsed:
        # if key lower case
        key = str(i).upper()
        # print(str(i))
        if key in keywords_essential or type(i) == sqlparse.sql.Where:
            sql_query_parts.append([])
        if key != ";":
            sql_query_parts[len(sql_query_parts) - 1].append(i)

    # transform query parts
    for i in range(len(sql_query_parts)):
        print(transformQueryPart(str(sql_query_parts[i][0]).upper(), sql_query_parts[i]))

    return combine_query()


def transformQueryPart(text, array):
    # if WHERE clause then cut into pieces
    if str(array[0]).split(" ")[0] == "WHERE":
        text = "WHERE"
        new_array = []
        for token in array[0]:
            new_array.append(token)
        array.clear()
        array = new_array

    print("__________")
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
                        # print(obj)
                        if (index == len(list(t.get_identifiers())) - 1):
                            statement.text = statement.text + str(obj)
                        else:
                            statement.text = statement.text + str(obj) + ", "
                elif type(t) == sqlparse.sql.Identifier:
                    statement.text = statement.text + str(t)

            queryParts.append(statement)

            return statement.text
        case "FROM":
            statement = MatchPart()

            for t in array:

                if type(t) == sqlparse.sql.IdentifierList:
                    for obj in enumerate(t.get_identifiers()):
                        # print(obj)
                        if "AS" in str(obj).split(" ") or "as" in str(obj).split(" "):
                            as_parts = str(obj).split(" ")
                            statement.add_node(Node(as_parts[0], as_parts[2]))
                        else:
                            statement.add_node(Node(str(obj)))

                elif type(t) == sqlparse.sql.Identifier:
                    if "AS" in str(t).split(" ") or "as" in str(t).split(" "):
                        as_parts = str(t).split(" ")
                        statement.add_node(Node(as_parts[0], as_parts[2]))
                    else:
                        statement.add_node(Node(str(t)))

            queryParts.append(statement)

            return statement.generate_query_string()
        case "WHERE":
            statement = Statement("WHERE", "")

            for token in array:
                if type(token) == sqlparse.sql.Comparison:
                    command_string = str(token)
                    #print(str(token))
                    for word in token:
                        if str(word).upper() == "LIKE":
                            parts = str(token).split(" ")
                            command_string = get_correct_command_string(parts[-1],parts[0])
                            # print(command_string)
                        if str(word).upper() == "IN" or str(word).upper() == "NOT IN":
                            command_string = command_string.replace("(", "[").replace(")", "]")

                    statement.text += command_string
                else:
                    if str(token) != ";":
                        statement.text += str(token)
                    else:
                        statement.text += " "

            statement.text = swap_text_with_previous(statement.text, "NOT")
            queryParts.append(statement)
            return statement.text
        case "JOIN" | "FULL JOIN":

            match_query = get_match_part()
            joined_node = Node()

            for token in array:
                if type(token) == sqlparse.sql.Identifier:
                    # print(token)
                    if "AS" in str(token).split(" ") or "as" in str(token).split(" "):
                        as_parts = str(token).split(" ")
                        joined_node = Node(as_parts[0], as_parts[2])
                        match_query.add_node(joined_node)
                    else:
                        joined_node = Node(str(token))
                        match_query.add_node(joined_node)

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

                            # relationship name variable
                            # direction is relevant
                            dir1 = "-"
                            dir2 = "-"
                            if joined_node == node1:
                                dir1 = "-"
                                dir2 = "->"
                            elif joined_node == node2:
                                dir1 = "<-"
                                dir2 = "-"

                            rel = Relationship("relationship", "", node2, node1, dir1, dir2)
                            # add relationship to node
                            node1.add_relationship(rel)
                            # add relationship to match query part
                            match_query.add_relationship(rel)

            return match_query.generate_query_string()
        case "GROUP BY":
            return ""
        case "ORDER BY":
            return make_part_query_string(text, array)
        case "LEFT OUTER JOIN" | "RIGHT OUTER JOIN":
            return "OPTIONAL MATCH"
        case "HAVING":
            statement = Statement("HAVING", "WITH ")

            # create or update where statement
            statement_where = get_query_part_by_name("WHERE")

            if statement_where is None:
                statement_where = Statement("WHERE", "WHERE")
                queryParts.append(statement_where)
            else:
                statement_where.text += ","

            for token in array[1:]:
                statement_where.text += str(token)
            statement_where.text += " "

            # copy variables from return to with clause
            statement_select = get_query_part_by_name("SELECT")

            print(statement_select.text)

            queryParts.append(statement)
            return statement.text
        case "UNION":
            return "UNION"
        case "UNION ALL":
            return "UNION ALL"
        case "LIMIT":
            return make_part_query_string(text, array)

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

    query1 = "SELECT p.ProductName, p.UnitPrice " \
             "FROM products AS p " \
             "WHERE p.Price BETWEEN 10 AND 20 " \
             "AND p.ProductName NOT IN ('Chocolade','Chai');"

    query = "SELECT zipcode AS zip, count(*) AS population " \
            "FROM Person " \
            "GROUP BY zip " \
            "HAVING population>10000;"

    query0 = "SELECT zipcode, count(*) AS population " \
             "FROM Person " \
             "WHERE e.EmployeeID = 100 " \
             "GROUP BY zipcode " \
             "HAVING population>10000;"

    sql_query = sqlvalidator.parse(query)

    # check if query valid
    if not sql_query.is_valid():
        print(sql_query.errors)
    else:
        print("query is fine!")

    print("--------------------------------")

    # parse and print string
    parsed = sqlparse.parse(query)[0]
    print(parsed.tokens)

    print("--------------------------------")

    print(query_conversion(query))

    print("--------------------------------")

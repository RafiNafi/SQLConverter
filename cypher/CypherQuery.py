import sqlparse
import re
from cypher.CypherClasses import Node, Relationship, Property, Statement, MatchPart, OptionalMatchPart

keywords_essential = ["SELECT", "INSERT", "UPDATE", "SET", "DELETE", "FROM", "JOIN", "WHERE", "GROUP BY", "ORDER BY",
                      "FULL JOIN", "FULL OUTER JOIN", "LEFT OUTER JOIN",
                      "RIGHT OUTER JOIN", "INNER JOIN", "HAVING", "UNION", "UNION ALL", "LIMIT"]

keyword_in_order = ["SUBQUERY", "INSERT", "UPDATE", "FROM", "LEFT OUTER JOIN", "RIGHT OUTER JOIN", "FULL OUTER JOIN", "FULL JOIN",
                    "HAVING", "WHERE", "SELECT", "SET", "DELETE", "ORDER BY", "LIMIT", "UNION", "UNION ALL"]

counter = 0

def convert_query(query_parts):
    queries_list = []

    print("START CONVERTING NEW QUERY")
    # check for number of whitespaces

    # parse and print string
    parsed = sqlparse.parse(query_parts)[0]
    print(parsed.tokens)

    last_index = 0
    for idx, token in enumerate(parsed.tokens):
        if str(token) == "UNION ALL" or str(token) == "UNION":

            string_query = ""
            for t in parsed.tokens[last_index:idx]:
                string_query += str(t)

            queries_list.append(string_query)
            queries_list.append(str(token) + str(parsed.tokens[idx + 1]))
            last_index = idx + 2

        if len(parsed.tokens) == idx + 1:

            string_query = ""
            for t in parsed.tokens[last_index:idx + 1]:
                string_query += str(t)

            queries_list.append(string_query)

    print(queries_list)

    print("--------------------------------")
    # combine all queries
    combined_result_query = ""
    for single_query in queries_list:
        query_main = CypherQuery()
        result = query_main.query_conversion(single_query)
        combined_result_query += result

    # add semicolon and delete unnecessary whitespace
    combined_result_query = delete_obsolete_whitespaces_and_semicolons(combined_result_query) + ";"

    return combined_result_query

def delete_obsolete_whitespaces_and_semicolons(result_query):

    result_query = result_query.replace(";","")

    return re.sub(" +"," ",result_query)

class CypherQuery:
    def __init__(self):
        self.queryParts = []
        self.sql_query_parts = []

    def get_match_part(self, typ):
        for query in self.queryParts:
            if type(query) == typ:
                return query

    def get_query_part_by_name(self, name):
        for query in self.queryParts:
            if isinstance(query, Statement):
                if query.keyword == name:
                    return query

    def check_for_subquery(self, array):
        return

    def get_correct_command_string(self, text, variable):
        text = text.replace("'", "")
        text = text.replace("\"", "")

        if text[-1] == "%" and text[0] == "%":
            return variable + " CONTAINS \"" + text[1:-1] + "\" "
        elif text[0] == "%":
            return variable + " ENDS WITH \"" + text[1:] + "\" "
        elif text[-1] == "%":
            return variable + " STARTS WITH \"" + text[:-1] + "\" "
        elif text[-1] != "%" and text[0] != "%" and ("%" in text) and (text.count("%") == 1):
            return variable + " STARTS WITH \"" + text.split("%")[0] + "\" AND " + variable + " ENDS WITH \"" + \
                   text.split("%")[1] + "\""

    def make_part_query_string(self, name, array):
        string_query = ""
        for token in array:
            string_query += str(token)

        # if union then add whitespace before
        if name == "UNION" or name == "UNION ALL":
            string_query = " " + string_query
        else:
            if string_query[0] != " ":
                string_query = " " + string_query
            if string_query[-1] == " ":
                string_query = string_query[0:-1]

        statement = Statement(name, string_query, array)
        self.queryParts.append(statement)

        return statement.text

    def get_node_from_match(self, match_query, text):
        node = match_query.get_node_by_name(text)

        if node is None:
            node = match_query.get_node_by_label(text)

        return node

    def combine_query(self):

        """
        combined_query_string = ""
        # add all query parts except for match and return
        # add optional match at the beginning
        for elem in self.queryParts:
            if type(elem) != MatchPart and type(elem) != OptionalMatchPart:
                if elem.keyword != "SELECT" and elem.keyword != "DELETE" and elem.keyword != "SET" \
                        and elem.keyword != "ORDER BY" and elem.keyword != "LIMIT":
                    if elem.keyword == "HAVING":
                        combined_query_string = elem.text + combined_query_string
                    else:
                        combined_query_string += elem.text
            elif type(elem) == OptionalMatchPart:
                combined_query_string = elem.generate_query_string("OPTIONAL MATCH ") + combined_query_string

        # add match part at the beginning and return or delete part at the end
        for elem in self.queryParts:
            if type(elem) == MatchPart:
                combined_query_string = elem.generate_query_string("MATCH ") + combined_query_string
            elif type(elem) != OptionalMatchPart:
                if elem.keyword == "SELECT" or elem.keyword == "DELETE" or elem.keyword == "SET":
                    combined_query_string = combined_query_string + elem.text

        for elem in self.queryParts:
            if type(elem) != MatchPart and type(elem) != OptionalMatchPart:
                if elem.keyword == "ORDER BY":
                    combined_query_string += elem.text
                elif elem.keyword == "LIMIT":
                    combined_query_string += elem.text
        """

        combined_query_string = ""

        for key in keyword_in_order:
            for elem in self.queryParts:
                if type(elem) != MatchPart and type(elem) != OptionalMatchPart:
                    if elem.keyword == key:
                        combined_query_string += elem.text
                        self.queryParts.remove(elem)
                        break
                else:
                    if type(elem) == MatchPart and key == "FROM" or type(elem) == MatchPart and key == "UPDATE":
                        combined_query_string += elem.generate_query_string("MATCH ")
                        self.queryParts.remove(elem)
                        break
                    elif type(elem) == OptionalMatchPart:
                        if key == "LEFT OUTER JOIN" or key == "RIGHT OUTER JOIN" or \
                                key == "FULL OUTER JOIN" or key == "FULL JOIN":
                            combined_query_string += elem.generate_query_string("OPTIONAL MATCH ")
                            self.queryParts.remove(elem)
                            break

        return combined_query_string

    def swap_text_with_previous(self, text, searchstring):
        # search string token and swap with previous
        parts = text.split(" ")
        indexes = []

        # print(parts)
        for idx, elem in enumerate(parts):
            if elem == searchstring and parts[idx - 1] not in ["WHERE", "OR", "AND"]:
                indexes.append(idx)

        for index in indexes:
            parts[index], parts[index - 1] = parts[index - 1], parts[index]

        result = ""
        for idx, elem in enumerate(parts):
            if idx == len(parts) - 1:
                result = result + elem
            else:
                result = result + elem + " "

        return result

    def query_conversion(self, query):
        self.queryParts.clear()
        self.sql_query_parts.clear()

        parsed = sqlparse.parse(query)[0]

        # cut array in multiple arrays per major keyword
        for i in parsed:
            # if key lower case
            key = str(i).upper()
            # print(str(i))
            if key in keywords_essential or type(i) == sqlparse.sql.Where:
                self.sql_query_parts.append([])
            if key != ";":
                self.sql_query_parts[len(self.sql_query_parts) - 1].append(i)

        # transform query parts
        for i in range(len(self.sql_query_parts)):
            print(self.transformQueryPart(str(self.sql_query_parts[i][0]).upper(), self.sql_query_parts[i]))

        return self.combine_query()

    def put_array_together_into_string(self, array):
        combined_result = ""
        for single in array:
            combined_result += single
        return combined_result

    def cutout_keyword_parts_from_array(self, keywords, array):
        last_index = 0
        added_conditions_list = []

        for idx, token in enumerate(array):
            if str(token) in keywords:

                string_query = ""
                for t in array[last_index:idx]:
                    string_query += str(t)

                added_conditions_list.append(string_query)
                added_conditions_list.append(str(token) + str(array[idx + 1]))
                last_index = idx + 2

            if len(array) == idx + 1:

                string_query = ""
                for t in array[last_index:idx + 1]:
                    string_query += str(t)

                added_conditions_list.append(string_query)

        return added_conditions_list

    def update_where_clause(self, array, index, text):

        statement_where = self.get_query_part_by_name("WHERE")

        if statement_where is None:
            statement_where = Statement("WHERE", "WHERE ", [])
            self.queryParts.append(statement_where)
        else:
            statement_where.text += text

        for token in array[index:]:
            statement_where.text += str(token)
        statement_where.text += " "

        return

    def create_match_clause(self, array):
        statement = MatchPart()
        opt_delete_statement = self.get_query_part_by_name("DELETE")

        for t in array:

            if type(t) == sqlparse.sql.IdentifierList:
                for obj in enumerate(t.get_identifiers()):
                    # print(obj[1])
                    if "AS" in str(obj[1]).split(" ") or "as" in str(obj[1]).split(" "):
                        as_parts = str(obj[1]).split(" ")
                        statement.add_node(Node(as_parts[0], as_parts[2]))
                    else:
                        statement.add_node(Node(str(obj[1]), str(obj[1])[0].lower()))

            elif type(t) == sqlparse.sql.Identifier:
                if "AS" in str(t).split(" ") or "as" in str(t).split(" "):
                    as_parts = str(t).split(" ")
                    statement.add_node(Node(as_parts[0], as_parts[2]))
                    # if this from is part of a delete statement
                    if opt_delete_statement is not None:
                        opt_delete_statement.text += as_parts[2]
                else:
                    statement.add_node(Node(str(t), str(t)[0].lower()))
                    # if this from is part of a delete statement
                    if opt_delete_statement is not None:
                        opt_delete_statement.text += str(t)[0].lower()

        self.queryParts.append(statement)
        return statement

    def get_node_prefix_from_match(self):

        statement_match = self.get_match_part(MatchPart)
        prefix = ""
        # get prefix from match statement
        if statement_match is not None:
            if len(statement_match.nodes) > 0:
                prefix = statement_match.nodes[0].label

        return prefix

    def transformQueryPart(self, text, array):
        # if WHERE clause then cut into further pieces
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
                statement = Statement("SELECT", "RETURN ", array)

                for t in array:
                    if str(t) == "DISTINCT":
                        statement.text = statement.text + "DISTINCT "

                    if type(t) == sqlparse.sql.IdentifierList:
                        for index, obj in enumerate(t.get_identifiers()):
                            # print(obj)
                            item = str(obj)
                            # check for wildcards in identifiers
                            if type(obj) == sqlparse.sql.Identifier and obj.is_wildcard() and len(str(obj)) > 1:
                                item = str(obj).split(".")[0]
                            if index == len(list(t.get_identifiers())) - 1:
                                statement.text = statement.text + item
                            else:
                                statement.text = statement.text + item + ", "
                    elif type(t) == sqlparse.sql.Identifier or type(t) == sqlparse.sql.Function or str(t) == "*":

                        if len(str(t)) > 1 and "*" in str(t):
                            statement.text = statement.text + str(t).split(".")[0]
                        else:
                            statement.text = statement.text + str(t)

                self.queryParts.append(statement)

                return statement.text
            case "FROM":

                statement = self.create_match_clause(array)

                return statement.generate_query_string("MATCH ")
            case "WHERE":

                statement = self.get_query_part_by_name("WHERE")
                prefix = ""
                if self.get_query_part_by_name("DELETE") is not None or self.get_query_part_by_name("SET") is not None:
                    prefix = self.get_node_prefix_from_match() + "."

                if statement is None:
                    statement = Statement("WHERE", "WHERE", array)
                    self.queryParts.append(statement)
                else:
                    statement.text += "AND"

                skip_index = 0
                for idx, token in enumerate(array[1:]):
                    if skip_index > idx:
                        continue
                    if type(token) == sqlparse.sql.Comparison:
                        # check if alias exists already
                        if "." in str(token):
                            prefix = ""

                        # check for subquery
                        check = str(token).partition("(")[2]
                        print(check)
                        if check.split(" ")[0] == "SELECT":
                            command_string = prefix + str(token).partition("(")[0]
                        else:
                            command_string = prefix + str(token)

                        print(str(token))
                        # for LIKE and IN keywords
                        for word in token:

                            if type(word) == sqlparse.sql.Parenthesis:

                                sub_clause = str(word)[1:-1]
                                if sub_clause.split(" ")[0] == "SELECT":
                                    print("Subquery: " + sub_clause)

                                    result = convert_query(sub_clause)

                                    global counter
                                    counter = counter + 1

                                    sub_result_string = "CALL{" + result + " AS sub" + str(
                                        counter) + "} WITH * "

                                    print("RESULT: " + sub_result_string)

                                    sub_statement = Statement("SUBQUERY", sub_result_string, [])
                                    self.queryParts.append(sub_statement)

                                    command_string += "sub"+str(counter) + " "
                                    print("COMMAND_STRING: " + command_string)
                                    print("-+-+-+-")

                            elif str(word).upper() == "LIKE" or str(word).upper() == "NOT LIKE":
                                parts = str(command_string).split(" ")
                                command_string = self.get_correct_command_string(parts[-1], parts[0])
                                # print(command_string)
                            elif str(word).upper() == "IN" or str(word).upper() == "NOT IN":
                                command_string = command_string.replace("(", "[").replace(")", "]")

                        statement.text += command_string
                    # for BETWEEN keyword
                    elif type(token) == sqlparse.sql.Identifier:
                        # check if alias exists already
                        if "." in str(token):
                            prefix = ""
                        # BETWEEN with NOT
                        if str(array[idx + 3]) == "NOT":
                            statement.text += str(array[idx + 3])
                            if str(array[idx + 5]).upper() == "BETWEEN":
                                statement.text = statement.text + " " + str(array[idx + 7]) + " <= " + \
                                                 prefix + str(token) + " =< " + str(array[idx + 11])
                                skip_index = idx + 11
                        else:
                            if str(array[idx + 3]).upper() == "BETWEEN":
                                statement.text = statement.text + "" + str(array[idx + 5]) + " <= " + \
                                                 prefix + str(token) + " =< " + str(array[idx + 9])
                                skip_index = idx + 9
                    # other words
                    else:
                        if str(token) != ";":
                            statement.text += str(token)
                        else:
                            statement.text += " "

                # change position of NOT
                statement.text = self.swap_text_with_previous(statement.text, "NOT")

                return statement.text
            case "JOIN" | "INNER JOIN" | "FULL JOIN" | "FULL OUTER JOIN" | "LEFT OUTER JOIN" | "RIGHT OUTER JOIN":

                if text == "LEFT OUTER JOIN" or text == "RIGHT OUTER JOIN" \
                        or text == "FULL JOIN" or text == "FULL OUTER JOIN":
                    match_query = self.get_match_part(OptionalMatchPart)

                    if match_query is None:
                        match_query = OptionalMatchPart()
                        # for n in get_match_part(MatchPart).nodes:
                        #    match_query.add_node(n)

                        self.queryParts.append(match_query)

                    query_text = "OPTIONAL MATCH "
                else:
                    match_query = self.get_match_part(MatchPart)
                    query_text = "MATCH "

                joined_node = Node()

                for token in array:
                    if type(token) == sqlparse.sql.Identifier:
                        # print(token)
                        if "AS" in str(token).split(" ") or "as" in str(token).split(" "):
                            as_parts = str(token).split(" ")
                            joined_node = Node(as_parts[0], as_parts[2])
                            match_query.add_node(joined_node)
                        else:
                            joined_node = Node(str(token), str(token)[0].lower())
                            match_query.add_node(joined_node)

                for idx, token in enumerate(array):
                    if type(token) == sqlparse.sql.Parenthesis:
                        for comp in token:
                            if type(comp) == sqlparse.sql.Comparison:
                                values = str(comp).split(" ")

                                # checks for name first then label

                                node1 = self.get_node_from_match(match_query, values[0].split(".")[0])
                                node2 = self.get_node_from_match(match_query, values[len(values) - 1].split(".")[0])

                                # for one match and one optional match
                                query_other_match = self.get_match_part(MatchPart)

                                if type(match_query) == MatchPart:
                                    query_other_match = self.get_match_part(OptionalMatchPart)

                                if query_other_match is not None:
                                    if node1 is None:
                                        node1 = self.get_node_from_match(query_other_match, values[0].split(".")[0])
                                    if node2 is None:
                                        node2 = self.get_node_from_match(query_other_match,
                                                                         values[len(values) - 1].split(".")[0])

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

                # look for other conditions in join
                parts = self.cutout_keyword_parts_from_array(["AND", "OR"], array)
                print(parts)

                if len(parts) > 1:
                    # create new or update existing where statement
                    self.update_where_clause(parts, 2, "")

                return match_query.generate_query_string(query_text)
            case "GROUP BY":
                return ""
            case "ORDER BY":
                return self.make_part_query_string(text, array)
            case "HAVING":
                statement = Statement("HAVING", "WITH", array)

                # create or update where statement

                self.update_where_clause(array, 1, "AND")

                # copy variables from return to with clause
                statement_select = self.get_query_part_by_name("SELECT")

                # print(statement_select.text)
                statement.text += statement_select.text.split("RETURN")[1] + " "

                parsed = sqlparse.parse(statement_select.text)[0]

                # assumes that every variable or aggregation has an alias
                new_return_text = ""
                for token in parsed.tokens:
                    if type(token) == sqlparse.sql.IdentifierList:
                        for idf in token:
                            if type(idf) == sqlparse.sql.Identifier:
                                new_return_text += str(idf).split(" ")[2]
                            else:
                                new_return_text += str(idf)
                    elif type(token) == sqlparse.sql.Identifier:
                        new_return_text += str(token).split(" ")[2]
                    else:
                        new_return_text += str(token)

                statement_select.text = new_return_text

                self.queryParts.append(statement)
                return statement.text
            case "UNION" | "UNION ALL":
                return self.make_part_query_string(text, array)
            case "LIMIT":
                return self.make_part_query_string(text, array)
            case "INSERT":
                statement = Statement("INSERT", "CREATE ", array)

                properties_list = []
                new_node = Node()

                for token in array:
                    if type(token) == sqlparse.sql.Function:
                        for func_parts in token:
                            if type(func_parts) == sqlparse.sql.Identifier:
                                new_node.label = str(func_parts)
                            if type(func_parts) == sqlparse.sql.Parenthesis:
                                for col in func_parts:
                                    if type(col) == sqlparse.sql.IdentifierList:
                                        for idf in col.get_identifiers():
                                            properties_list.append(idf)

                    elif type(token) == sqlparse.sql.Identifier:
                        new_node.label = str(token)

                    elif type(token) == sqlparse.sql.Values:
                        for value_parts in token:
                            if type(value_parts) == sqlparse.sql.Parenthesis:
                                for value in value_parts:
                                    if type(value) == sqlparse.sql.IdentifierList:
                                        for idx, idf in enumerate(value.get_identifiers()):
                                            if len(properties_list) > 0:
                                                new_node.add_property(Property(properties_list[idx], idf))
                                            else:
                                                new_node.add_property(Property("var" + str(idx), idf))

                statement.text += new_node.get_formatted_node_string()
                self.queryParts.append(statement)
                return statement.text
            case "DELETE":
                statement = Statement("DELETE", "DELETE ", array)

                self.queryParts.append(statement)
                return statement.text
            case "UPDATE":

                statement = self.create_match_clause(array)

                return statement.generate_query_string("MATCH ")
            case "SET":
                statement = Statement("SET", "SET ", array)

                # get prefix from match statement
                node_name = self.get_node_prefix_from_match() + "."
                # add prefix to identifiers
                for token in array:
                    if type(token) == sqlparse.sql.IdentifierList:
                        for idx, val in enumerate(token.get_identifiers()):
                            if "." in str(val):
                                node_name = ""
                            statement.text += node_name + str(val)
                            if idx != len(list(token.get_identifiers())) - 1:
                                statement.text += ", "
                    elif type(token) == sqlparse.sql.Identifier:
                        if "." in str(token):
                            node_name = ""
                        statement.text += node_name + str(token)

                self.queryParts.append(statement)
                return statement.text

        return "not found"

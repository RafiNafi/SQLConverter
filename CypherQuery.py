import sqlvalidator
import sqlparse
from CypherClasses import Node, Relationship, Property, Statement, MatchPart, OptionalMatchPart

keywords_essential = ["SELECT", "INSERT", "UPDATE", "DELETE", "FROM", "JOIN", "WHERE", "GROUP BY", "ORDER BY",
                      "FULL JOIN", "FULL OUTER JOIN", "LEFT OUTER JOIN",
                      "RIGHT OUTER JOIN", "INNER JOIN", "HAVING", "UNION", "UNION ALL", "LIMIT"]


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
            return variable + " CONTAINS \"" + text[1:-1] + "\""
        elif text[0] == "%":
            return variable + " ENDS WITH \"" + text[1:] + "\""
        elif text[-1] == "%":
            return variable + " STARTS WITH \"" + text[:-1] + "\""
        elif text[-1] != "%" and text[0] != "%" and ("%" in text) and (text.count("%") == 1):
            return variable + " STARTS WITH \"" + text.split("%")[0] + "\" AND " + variable + " ENDS WITH \"" + \
                   text.split("%")[1] + "\""

    def make_part_query_string(self, name, array):
        string_query = ""
        for token in array:
            string_query += str(token)

        if string_query[-1] != " ":
            string_query += " "

        statement = Statement(name, string_query, array)
        self.queryParts.append(statement)

        # if union then add whitespace before
        if name == "UNION" or name == "UNION ALL":
            statement.text = " " + statement.text

        return statement.text

    def get_node_from_match(self, match_query, text):
        node = match_query.get_node_by_name(text)

        if node is None:
            node = match_query.get_node_by_label(text)

        return node

    def combine_query(self):
        combined_query_string = ""
        # add all query parts except for match and return
        # add optional match at the beginning
        for elem in self.queryParts:
            if type(elem) != MatchPart and type(elem) != OptionalMatchPart:
                if elem.keyword != "SELECT" and elem.keyword != "DELETE":
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
            elif type(elem) != OptionalMatchPart and elem.keyword == "SELECT" or \
                    type(elem) != OptionalMatchPart and elem.keyword == "DELETE":
                combined_query_string = combined_query_string + elem.text

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
                    elif type(t) == sqlparse.sql.Identifier or str(t) == "*":

                        if len(str(t)) > 1:
                            statement.text = statement.text + str(t).split(".")[0]
                        else:
                            statement.text = statement.text + str(t)

                self.queryParts.append(statement)

                return statement.text
            case "FROM":
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
                                statement.add_node(Node(str(obj[1])))

                    elif type(t) == sqlparse.sql.Identifier:
                        if "AS" in str(t).split(" ") or "as" in str(t).split(" "):
                            as_parts = str(t).split(" ")
                            statement.add_node(Node(as_parts[0], as_parts[2]))
                            # if this from is part of a delete statement
                            if opt_delete_statement is not None:
                                opt_delete_statement.text += as_parts[0]
                        else:
                            # if this from is part of a delete statement
                            if opt_delete_statement is not None:
                                statement.add_node(Node(str(t), str(t)[0].lower()))
                                opt_delete_statement.text += str(t)[0].lower()
                            else:
                                statement.add_node(Node(str(t)))

                self.queryParts.append(statement)

                return statement.generate_query_string("MATCH ")
            case "WHERE":

                statement = self.get_query_part_by_name("WHERE")

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
                        command_string = str(token)
                        # for LIKE and IN keywords
                        for word in token:
                            if str(word).upper() == "LIKE" or str(word).upper() == "NOT LIKE":
                                parts = str(token).split(" ")
                                command_string = self.get_correct_command_string(parts[-1], parts[0])
                                # print(command_string)
                            if str(word).upper() == "IN" or str(word).upper() == "NOT IN":
                                command_string = command_string.replace("(", "[").replace(")", "]")
                        statement.text += command_string
                    # for BETWEEN keyword
                    elif type(token) == sqlparse.sql.Identifier:
                        if str(array[idx + 3]) == "NOT":
                            statement.text += str(array[idx + 3])
                            if str(array[idx + 5]).upper() == "BETWEEN":
                                statement.text = statement.text + " " + str(array[idx + 7]) + " <= " + str(token) \
                                                 + " =< " + str(array[idx + 11])
                                skip_index = idx + 11
                        else:
                            if str(array[idx + 3]).upper() == "BETWEEN":
                                statement.text = statement.text + "" + str(array[idx + 5]) + " <= " + str(token) \
                                                 + " =< " + str(array[idx + 9])
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
                            joined_node = Node(str(token))
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
                                                new_node.add_property(Property("var"+str(idx), idf))

                statement.text += new_node.get_formatted_node_string()
                self.queryParts.append(statement)
                return statement.text
            case "DELETE":
                statement = Statement("DELETE", "DELETE ", array)

                self.queryParts.append(statement)
                return statement.text

        return "not found"

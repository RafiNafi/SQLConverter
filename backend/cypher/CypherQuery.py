import sqlparse
import re
from backend.cypher.CypherClasses import Node, Relationship, Property, Statement, MatchPart, OptionalMatchPart

keywords_essential = ["SELECT", "INSERT", "UPDATE", "SET", "DELETE", "FROM", "JOIN", "WHERE", "GROUP BY", "ORDER BY",
                      "FULL JOIN", "FULL OUTER JOIN", "LEFT OUTER JOIN", "LEFT JOIN",
                      "RIGHT OUTER JOIN", "RIGHT JOIN", "INNER JOIN", "HAVING", "UNION", "UNION ALL", "LIMIT"]

keyword_in_order = ["SUBQUERY", "INSERT", "UPDATE", "FROM", "LEFT OUTER JOIN", "LEFT JOIN",
                    "RIGHT OUTER JOIN", "RIGHT JOIN", "FULL OUTER JOIN", "FULL JOIN",
                    "HAVING", "WHERE", "SELECT", "SET", "DELETE", "ORDER BY", "LIMIT", "UNION", "UNION ALL"]

counter = 0
subquery_depth = 0
form = ""
previous_name = ""
formatted = False
has_union = False


# wrapper to set initial variables
def init_convert(query_parts, formats):
    global counter, form, subquery_depth, formatted, has_union
    counter = 0
    subquery_depth = 0
    has_union = False

    if formats == 1:
        form = "\n"
        formatted = True
    else:
        form = ""
        formatted = False

    return convert_query(query_parts, False, False)


def convert_query(query_parts, is_subquery, is_exists_subquery):
    queries_list = []

    global has_union

    print("START CONVERTING NEW QUERY")

    if not len(sqlparse.parse(query_parts)) > 0:
        return ""

    # parse and print string
    parsed = sqlparse.parse(query_parts)[0]
    print(parsed.tokens)

    # check for union
    last_index = 0
    for idx, token in enumerate(parsed.tokens):
        if str(token) == "UNION ALL" or str(token) == "UNION":

            string_query = ""
            for t in parsed.tokens[last_index:idx]:
                string_query += str(t)

            queries_list.append(string_query)
            queries_list.append(str(token) + str(parsed.tokens[idx + 1]))
            last_index = idx + 2

            has_union = True

        if len(parsed.tokens) == idx + 1:

            string_query = ""
            for t in parsed.tokens[last_index:idx + 1]:
                string_query += str(t)

            queries_list.append(string_query)

    print("QUERIES LIST: " + str(queries_list))

    print("--------------------------------")
    # combine all queries
    combined_result_query = ""
    for single_query in queries_list:
        query_main = CypherQuery(is_subquery, is_exists_subquery)
        result = query_main.query_conversion(single_query)
        combined_result_query += result

    # add semicolon and delete unnecessary whitespace
    combined_result_query = delete_obsolete_whitespaces_and_semicolons(combined_result_query)

    # semicolon management
    if len(combined_result_query) > 0:
        if combined_result_query[-1] == "\n":
            combined_result_query = combined_result_query[0:-1] + ";"
        else:
            combined_result_query += ";"

    return combined_result_query


def delete_obsolete_whitespaces_and_semicolons(result_query):
    result_query = result_query.replace(";", "")

    return re.sub(" +", " ", result_query)


class CypherQuery:
    def __init__(self, is_subquery=False, is_exists_subquery=False):
        self.queryParts = []
        self.sql_query_parts = []
        self.is_subquery = is_subquery
        self.is_exists_subquery = is_exists_subquery

    def get_match_part(self, typ):
        for query in self.queryParts:
            if type(query) == typ:
                return query

    def get_query_part_by_name(self, name):
        for query in self.queryParts:
            if isinstance(query, Statement):
                if query.keyword == name:
                    return query

    def remove_query_part_by_name(self, name):
        for query in self.queryParts:
            if isinstance(query, Statement):
                if query.keyword == name:
                    self.queryParts.remove(query)
                    return True

        return False

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

    def add_subquery_name(self):
        # add subquery name to RETURN before combining
        if self.is_subquery and not self.is_exists_subquery:
            statement_r = self.get_query_part_by_name("SELECT")

            # works at the moment only for one variable in select
            if "AS" not in [x.upper() for x in statement_r.text.split(" ")]:
                statement_r.text += " AS sub" + str(counter)

            parsed = sqlparse.parse(statement_r.text)[0]
            for token in parsed.tokens:
                if type(token) == sqlparse.sql.Identifier:
                    temp_arr = str(token).split(" ")
                    if "AS" in [x.upper() for x in temp_arr]:
                        global previous_name
                        previous_name = temp_arr[-1]
        elif self.is_exists_subquery:
            self.remove_query_part_by_name("SELECT")
        return

    def check_for_linebreak(self, combined_query_string, text, addition):

        if combined_query_string[-1] == "\n" and text[0] == " ":
            return text[1:] + addition
        else:
            return text + addition

    def add_subquery_indent(self, combined_query_string, query_text):

        if len(combined_query_string) > 0:
            combined_query_string += "\t" * subquery_depth + self.check_for_linebreak(
                combined_query_string, query_text, form)
        else:
            combined_query_string += "\t" * subquery_depth + query_text + form
        return combined_query_string

    def combine_query(self):

        self.add_subquery_name()
        combined_query_string = ""
        global subquery_depth

        # combine query based on keyword order in array
        for key in keyword_in_order:
            for elem in self.queryParts:
                if type(elem) != MatchPart and type(elem) != OptionalMatchPart:
                    if elem.keyword == key:
                        combined_query_string = self.add_subquery_indent(combined_query_string, elem.text)
                        # self.queryParts.remove(elem)

                else:
                    if type(elem) == MatchPart and key in ["FROM", "UPDATE"]:
                        combined_query_string = self.add_subquery_indent(combined_query_string,
                                                                         elem.generate_query_string("MATCH "))
                        self.queryParts.remove(elem)

                    elif type(elem) == OptionalMatchPart:
                        if key in ["LEFT OUTER JOIN", "RIGHT OUTER JOIN",
                                   "FULL OUTER JOIN", "FULL JOIN"]:
                            combined_query_string = self.add_subquery_indent(combined_query_string,
                                                                             elem.generate_query_string(
                                                                                 "OPTIONAL MATCH "))
                            self.queryParts.remove(elem)

        if formatted and subquery_depth > 0:
            subquery_depth -= 1

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
                if len(self.sql_query_parts) - 1 >= 0:
                    self.sql_query_parts[len(self.sql_query_parts) - 1].append(i)

        # transform query parts
        for i in range(len(self.sql_query_parts)):
            print(self.transform_query_part(str(self.sql_query_parts[i][0]).upper(), self.sql_query_parts[i]))

        return self.combine_query()

    def put_array_together_into_string(self, array):
        combined_result = ""
        for single in array:
            combined_result += str(single)
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
        # updates or creates new where clause
        global counter
        statement_where = self.get_query_part_by_name("WHERE")

        if statement_where is None:
            statement_where = Statement("WHERE", "WHERE ", [])
            self.queryParts.append(statement_where)
        else:
            statement_where.text += text

        for token in array[index:]:

            # check for subquery
            if type(token) == sqlparse.sql.Comparison:
                for word in token:
                    if type(word) == sqlparse.sql.Parenthesis:
                        if self.create_subquery(word, False):
                            statement_where.text += self.get_correct_subquery_alias() + " "
                            counter += 1

                    else:
                        statement_where.text += str(word)
            else:
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
                    if "AS" in [x.upper() for x in str(obj[1]).split(" ")]:
                        as_parts = str(obj[1]).split(" ")
                        statement.add_node(Node(as_parts[0], as_parts[2]))
                    elif len(str(obj[1]).split(" ")) == 2 and type(obj[1]) == sqlparse.sql.Identifier:
                        as_parts = str(obj[1]).split(" ")
                        statement.add_node(Node(as_parts[0], as_parts[1]))
                    else:
                        statement.add_node(Node(str(obj[1]), str(obj[1])))

            elif type(t) == sqlparse.sql.Identifier:
                if "AS" in [x.upper() for x in str(t).split(" ")]:
                    as_parts = str(t).split(" ")
                    statement.add_node(Node(as_parts[0], as_parts[2]))
                    # if this from is part of a delete statement
                    if opt_delete_statement is not None:
                        opt_delete_statement.text += as_parts[2]
                elif len(str(t).split(" ")) == 2:
                    as_parts = str(t).split(" ")
                    statement.add_node(Node(as_parts[0], as_parts[1]))
                else:
                    statement.add_node(Node(str(t), str(t)))
                    # if this from is part of a delete statement
                    if opt_delete_statement is not None:
                        opt_delete_statement.text += str(t)

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

    def create_subquery(self, text, collected):

        global subquery_depth
        sub_clause = str(text)[1:-1].lstrip()

        if sub_clause.split(" ")[0] == "SELECT":

            if formatted:
                subquery_depth += 1
            # recursion
            result = convert_query(sub_clause, True, False)

            if collected:
                sub_result_string = "\t" * subquery_depth + "CALL{" + form + "" + result + "} WITH " \
                                                                                           "collect(" + self.get_correct_subquery_alias() + ") AS coll_list "
            else:
                sub_result_string = "\t" * subquery_depth + "CALL{" + form + "" + result + "} WITH * "

            sub_statement = Statement("SUBQUERY", sub_result_string, [])
            self.queryParts.append(sub_statement)
            return True

        return False

    def get_correct_subquery_alias(self):
        global previous_name

        if previous_name != "":
            name = previous_name
            previous_name = ""
            return name
        else:
            return " sub" + str(counter)

    def check_for_identifier_positions(self, array, pos, text):

        for index, token in enumerate(array):
            if type(token) == sqlparse.sql.IdentifierList or type(token) == sqlparse.sql.Identifier:
                if index < pos:
                    text = ", " + text
                elif index > pos:
                    text += ", "

        return text

    def add_join(self, match_query, comp, joined_node, join_type):

        values = comp.split(" ")

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
        # direction is relevant for outer joins

        directions = self.caluclate_directions(joined_node, node1, node2, join_type)

        dir1 = directions["dir1"]
        dir2 = directions["dir2"]

        rel = Relationship("relationship", "", node2, node1, dir1, dir2)
        # add relationship to match query part
        match_query.add_relationship(rel)

        #for i in match_query.relationships:
        #    print(i.node_r.name + " " + i.node_l.name)

        return

    def caluclate_directions(self, joined_node, node1, node2, join_type):

        dir1 = "-"
        dir2 = "-"

        if join_type == "LEFT OUTER JOIN" or join_type == "LEFT JOIN" or \
            join_type == "INNER JOIN" or join_type == "JOIN" or \
                join_type == "FULL JOIN" or join_type == "FULL OUTER JOIN":
            if joined_node == node1:
                dir1 = "-"
                dir2 = "->"  # ->
            elif joined_node == node2:
                dir1 = "<-"  # <-
                dir2 = "-"
        elif join_type == "RIGHT OUTER JOIN" or join_type == "RIGHT JOIN":
            if joined_node == node1:
                dir1 = "<-"
                dir2 = "-"  # ->
            elif joined_node == node2:
                dir1 = "-"  # <-
                dir2 = "->"

        return {"dir1": dir1, "dir2": dir2}

    def create_any_all_list_string(self, typ, list_name, operator, param):
        return "" + typ + "(var IN " + list_name + " WHERE " + param + " " + operator + " var)"

    def get_array_parts(self, array, mode):
        filled_array = []

        if mode == "types":
            if type(array) != sqlparse.sql.Token:
                for i in array:
                    filled_array.append(i)
            else:
                filled_array.append(str(array))
        elif mode == "string":
            if type(array) != sqlparse.sql.Token:
                for i in array:
                    filled_array.append(str(i))
            else:
                filled_array.append(str(array))

        return filled_array

    def check_for_missing_whitespace(self, text):
        if text != " ":
            return " "
        return ""

    def transform_query_part(self, text, array):
        global counter
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
                statement = Statement("SELECT", " RETURN ", array)

                for pos, t in enumerate(array):
                    if str(t).upper() == "DISTINCT":
                        statement.text = statement.text + "DISTINCT "

                    if type(t) == sqlparse.sql.IdentifierList:
                        for index, obj in enumerate(t.get_identifiers()):

                            item = str(obj)

                            array_parts = self.get_array_parts(obj, "types")

                            # check for wildcards in identifiers
                            if type(obj) == sqlparse.sql.Identifier and obj.is_wildcard() and len(str(obj)) > 1:
                                item = str(obj).split(".")[0]
                            elif len(str(obj).split(" ")) == 2 and type(obj) == sqlparse.sql.Identifier:
                                item = str(obj).split(" ")[0] + " AS " + str(obj).split(" ")[1]
                            elif len(array_parts) > 2 and type(obj[0]) == sqlparse.sql.Function:
                                item = str(obj[0]) + " AS " + str(obj[len(array_parts) - 1])
                            elif has_union and len(str(obj).split(" ")) < 2 and len(str(obj).split(".")) > 1:
                                item = str(obj) + " AS " + str(obj).split(".")[1]

                            if index == len(list(t.get_identifiers())) - 1:
                                statement.text = statement.text + item
                            else:
                                statement.text = statement.text + item + ", "

                    elif type(t) == sqlparse.sql.Identifier or type(t) == sqlparse.sql.Function \
                            or str(t) == "*" or type(t) == sqlparse.sql.Case:

                        array_parts = self.get_array_parts(t, "types")

                        if len(str(t)) > 1 and "*" in str(t):
                            statement.text = statement.text + str(t).split(".")[0]
                        elif len(str(t).split(" ")) == 2 and type(t) == sqlparse.sql.Identifier:
                            statement.text = statement.text + str(t).split(" ")[0] + " AS " + str(t).split(" ")[1]
                        elif len(array_parts) > 2 and type(t) == sqlparse.sql.Function:
                            statement.text = statement.text + str(t[0]) + " AS " + str(t[len(array_parts) - 1])
                        else:
                            if has_union and len(str(t).split(" ")) < 2 and len(str(t).split(".")) > 1:
                                statement.text = statement.text + str(t) + " AS " + str(t).split(".")[1]
                            else:
                                statement.text = statement.text + str(t)

                    elif type(t) == sqlparse.sql.Parenthesis:
                        if self.create_subquery(t, False):
                            statement.text += self.check_for_identifier_positions(array, pos,
                                                                                  self.get_correct_subquery_alias())
                            counter += 1

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
                        check = str(token).partition("(")[2].lstrip()

                        if check.split(" ")[0] == "SELECT":
                            comp_part = str(token).partition("(")[0]

                            if comp_part[-3:].upper() in ["ANY", "ALL"]:
                                command_string = prefix
                            else:
                                command_string = prefix + str(token).partition("(")[0]
                        else:
                            command_string = prefix + str(token)

                        print(str(token))
                        for index, word in enumerate(token):

                            # create sub queries
                            if type(word) == sqlparse.sql.Parenthesis:
                                if self.create_subquery(word, False):

                                    array = self.get_array_parts(token, "string")

                                    if "IN" in array or "NOT IN" in array:
                                        command_string += "[" + self.get_correct_subquery_alias() + "]"
                                    else:
                                        command_string += self.get_correct_subquery_alias()
                                    counter += 1
                            # for an and all statements
                            if type(word) == sqlparse.sql.Function:

                                keyword = str(word)[0:3]
                                if str(word).upper()[0:3] in ["ANY", "ALL"]:
                                    if self.create_subquery(str(word)[3:], True):
                                        if comp_part is not None:
                                            temp_array = sqlparse.parse(comp_part.replace(" ", ""))[0].tokens
                                            print(temp_array)
                                            command_string += self.create_any_all_list_string(keyword, "coll_list",
                                                                                              str(temp_array[1]),
                                                                                              str(temp_array[0]))

                            # for LIKE and IN keywords
                            elif str(word).upper() == "LIKE" or str(word).upper() == "NOT LIKE":
                                parts = str(command_string).split(" ")
                                command_string = self.get_correct_command_string(parts[-1], parts[0])
                                # print(command_string)
                            elif str(word).upper() == "IN" or str(word).upper() == "NOT IN":
                                command_string += self.check_for_missing_whitespace(str(token[index + 1]))
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
                                                 prefix + str(token) + " <= " + str(array[idx + 11])
                                skip_index = idx + 11
                        elif str(array[idx + 3]).upper() == "BETWEEN":
                            statement.text = statement.text + "" + str(array[idx + 5]) + " <= " + \
                                             prefix + str(token) + " <= " + str(array[idx + 9])
                            skip_index = idx + 9
                        else:
                            statement.text += str(token)

                    # exists
                    elif type(token) == sqlparse.sql.Function or str(token) == "EXISTS":

                        exists_array = token

                        if str(token) == "EXISTS" and type(array[idx + 3]) == sqlparse.sql.Parenthesis:
                            skip_index = idx + 4
                            exists_array = sqlparse.parse(str(token) + str(array[idx + 3]))[0].tokens[0]

                        for index, part in enumerate(exists_array):
                            print(part)
                            if str(part) == "EXISTS":
                                sub_clause = str(exists_array[index + 1])[1:-1]
                                print(sub_clause)

                                if sub_clause.split(" ")[0] == "SELECT":
                                    # recursion
                                    result = convert_query(sub_clause, True, True)

                                    statement.text += "\t" * subquery_depth + "EXISTS{" + form + result + "}"

                    # other words
                    else:
                        if str(token) != ";":
                            statement.text += str(token)
                        else:
                            statement.text += " "

                # change position of NOT
                statement.text = self.swap_text_with_previous(statement.text, "NOT")

                return statement.text
            case "JOIN" | "INNER JOIN" | "FULL JOIN" | "FULL OUTER JOIN" | "LEFT OUTER JOIN" | "RIGHT OUTER JOIN" | "LEFT JOIN" | "RIGHT JOIN":

                if text == "LEFT OUTER JOIN" or text == "RIGHT OUTER JOIN" \
                        or text == "FULL JOIN" or text == "FULL OUTER JOIN" \
                        or text == "LEFT JOIN" or text == "RIGHT JOIN":

                    match_query = self.get_match_part(OptionalMatchPart)

                    if match_query is None:
                        match_query = OptionalMatchPart()
                        # for n in self.get_match_part(MatchPart).nodes:
                        #    match_query.add_node(n)

                        self.queryParts.append(match_query)

                    query_text = "OPTIONAL MATCH "

                else:
                    match_query = self.get_match_part(MatchPart)
                    query_text = "MATCH "

                joined_node = Node()

                for token in array:
                    if type(token) == sqlparse.sql.Identifier:
                        as_parts = str(token).split(" ")

                        if "AS" in [x.upper() for x in str(token).split(" ")]:
                            joined_node = Node(as_parts[0], as_parts[2])
                        elif len(str(token).split(" ")) == 2:
                            joined_node = Node(as_parts[0], as_parts[1])
                        else:
                            joined_node = Node(str(token), str(token))

                        match_query.add_node(joined_node)

                for idx, token in enumerate(array):
                    if type(token) == sqlparse.sql.Parenthesis or type(token) == sqlparse.sql.Function:
                        comp_array = token

                        if type(token) == sqlparse.sql.Function:
                            comp_array = token[1]

                        for comp in comp_array:
                            if type(comp) == sqlparse.sql.Comparison:
                                self.add_join(match_query, str(comp), joined_node, text)
                    elif type(token) == sqlparse.sql.Comparison:
                        self.add_join(match_query, str(token), joined_node, text)

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

                # copy variables from return to with clause
                statement_select = self.get_query_part_by_name("SELECT")

                updated_having_text = self.put_array_together_into_string(array)

                parsed = sqlparse.parse(statement_select.text)[0]

                number = 1
                new_return_text = ""

                # add alias for every return value without alias
                for token in parsed.tokens:
                    if type(token) == sqlparse.sql.IdentifierList:
                        for idf in token:
                            if type(idf) == sqlparse.sql.Identifier or type(idf) == sqlparse.sql.Function:
                                if len(str(idf).split(" ")) < 2:
                                    new_return_text += str(idf) + " AS alias" + str(number)
                                    number += 1
                                else:
                                    new_return_text += str(idf)
                            else:
                                new_return_text += str(idf)
                    elif type(token) == sqlparse.sql.Identifier or type(token) == sqlparse.sql.Function:
                        if len(str(token).split(" ")) < 2:
                            new_return_text += str(token) + " AS alias" + str(number)
                            number += 1
                        else:
                            new_return_text += str(token)
                    else:
                        new_return_text += str(token)

                statement_select.text = new_return_text

                statement.text += statement_select.text.split("RETURN")[1] + " "

                parsed = sqlparse.parse(statement_select.text)[0]

                # assumes that every variable or aggregation has an alias
                new_return_text = ""
                for token in parsed.tokens:
                    if type(token) == sqlparse.sql.IdentifierList:
                        for idf in token:
                            if type(idf) == sqlparse.sql.Identifier or type(token) == sqlparse.sql.Function:
                                alias = str(idf).split(" ")[2]
                                new_return_text += alias

                                array_having = sqlparse.parse(updated_having_text)[0].tokens
                                updated_having_text = ""

                                for comp in array_having:
                                    if type(comp) == sqlparse.sql.Comparison:
                                        if str(comp[0]) == str(idf).split(" ")[0]:
                                            updated_having_text += alias + self.put_array_together_into_string(comp[1:])
                                        else:
                                            updated_having_text += str(comp)
                                    else:
                                        updated_having_text += str(comp)

                            else:
                                new_return_text += str(idf)
                    elif type(token) == sqlparse.sql.Identifier or type(token) == sqlparse.sql.Function:
                        new_return_text += str(token).split(" ")[2]
                    else:
                        new_return_text += str(token)

                temp_text = ""
                for having_part in sqlparse.parse(updated_having_text)[0].tokens:
                    flag = False
                    if type(having_part) == sqlparse.sql.Comparison:
                        comp = str(having_part).split(" ")[0]
                        for text in sqlparse.parse(new_return_text)[0].tokens:
                            if type(text) == sqlparse.sql.IdentifierList:
                                for idf in text:
                                    if type(idf) == sqlparse.sql.Identifier or type(text) == sqlparse.sql.Function:
                                        if comp == str(idf):
                                            flag = True

                            elif type(text) == sqlparse.sql.Identifier or type(text) == sqlparse.sql.Function:
                                if comp == str(text):
                                    flag = True

                        if not flag:
                            temp_text += "alias" + str(number) + self.put_array_together_into_string(having_part[1:])
                            statement.text += ", " + str(comp) + " AS " + " alias" + str(number)
                            number += 1
                        else:
                            temp_text += str(having_part)
                    else:
                        temp_text += str(having_part)

                statement_select.text = new_return_text

                # create or update where statement
                self.update_where_clause(sqlparse.parse(temp_text)[0].tokens, 1, "AND")

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
                    elif type(token) == sqlparse.sql.Identifier or type(token) == sqlparse.sql.Function or type(
                            token) == sqlparse.sql.Comparison:
                        if "." in str(token):
                            node_name = ""
                        statement.text += node_name + str(token)

                self.queryParts.append(statement)
                return statement.text

        return "not found"

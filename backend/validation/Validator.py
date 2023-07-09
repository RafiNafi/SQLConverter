import sqlparse
import json
import backend

class Validator:

    global pos, return_pos
    pos = 1
    return_pos = 1

    def __init__(self):
        self.function_flag = False
        self.misuse_keyword_flag = False
        self.function_param_flag = False
        f = open(backend.DATA_DIR)
        self.functions = json.load(f)['functions']
        self.is_insert_statement = False

    def recursiveTree(self, tokenT):
        global pos
        if type(tokenT) != sqlparse.sql.Token:
            for t in tokenT:
                if type(t) != sqlparse.sql.Token:

                    if type(t) == sqlparse.sql.Function:
                        if not self.is_insert_statement:
                            self.function_check(t)

                    self.recursiveTree(t)
                else:
                    pos += len(str(t))
                    pass
        else:
            pos += len(str(tokenT))
            return

    def query_syntax_validation(self, query):
        global return_pos

        self.init_validation()

        print("----------- VALIDATION -----------")
        parsed = sqlparse.parse(query)[0]
        print(parsed.tokens)

        if str(parsed.tokens[0]) == "INSERT":
            self.is_insert_statement = True

        return_pos = self.check_keyword_usage(parsed.tokens)

        self.recursiveTree(parsed.tokens)

        print("--------------------------------")
        valid, error_message = self.check_flags()

        return valid, error_message, return_pos

    def init_validation(self):
        self.function_flag = False
        self.is_insert_statement = False
        global pos, return_pos
        pos = 1
        return_pos = 1
        return

    def check_flags(self):
        if self.function_flag:
            return False, "Function name not correct."
        elif self.misuse_keyword_flag:
            return False, "Misuse of keyword."
        elif self.function_param_flag:
            return False, "Wrong number of function parameter."
        else:
            return True, ""

    def check_keyword_usage(self, tokens):
        # checks if there are too many keywords back to back
        count = 0
        pos = 1
        previous_keyword = ""

        for i in tokens:
            if i.is_keyword:
                count += 1
            elif i.is_whitespace:
                pass
            else:
                if count > 0:
                    count = 0

            if not i.is_whitespace and (count > 2 or (previous_keyword == "FROM" and count > 1)):
                self.misuse_keyword_flag = True
                break

            if i.is_keyword:
                previous_keyword = str(i).upper()

            pos += len(str(i))

        return pos

    def function_check(self, query_part):
        global return_pos

        self.function_param_flag = self.check_param_count(query_part)

        if self.function_param_flag:
            return_pos = pos
            return

        for obj in self.functions:
            if str(query_part[0]).upper() == obj['name']:
                return

        return_pos = pos

        self.function_flag = True
        return

    def check_param_count(self, query_part):

        for func_part in query_part:
            if type(func_part) == sqlparse.sql.Parenthesis:
                for text in func_part:
                    if type(text) == sqlparse.sql.IdentifierList:
                        idf_count = self.get_id_count(text.get_identifiers())

                        for obj in self.functions:
                            if str(query_part[0]).upper() == obj['name']:
                                if obj['max_param_count'] != idf_count and obj['max_param_count'] != "*":
                                    return True

                    elif type(text) == sqlparse.sql.Identifier:

                        for obj in self.functions:
                            if str(query_part[0]).upper() == obj['name']:
                                if (len(str(text).split(" ")) > 1 or obj['max_param_count'] != "1") and obj['max_param_count'] != "*":
                                    return True

    def get_id_count(self, idf):
        count = 0
        for id in idf:
            count += 1
        return count
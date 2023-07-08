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
        else:
            return True, ""

    def check_keyword_usage(self, tokens):
        # checks if there are too many keywords back to back
        count = 0
        pos = 1

        for i in tokens:
            if i.is_keyword:
                count += 1
            elif i.is_whitespace:
                pass
            else:
                if count > 0:
                    count -= 1
            if count > 2:
                self.misuse_keyword_flag = True
                break
            pos += len(str(i))

        return pos

    def function_check(self, query_part):
        global return_pos

        for obj in self.functions:
            if str(query_part[0]).upper() == obj['name']:
                return

        return_pos = pos

        self.function_flag = True
        return


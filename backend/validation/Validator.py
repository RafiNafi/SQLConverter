import sqlparse
import json
import backend

class Validator:

    def __init__(self):
        self.function_flag = False
        self.misuse_keyword_flag = False
        f = open(backend.DATA_DIR)
        self.functions = json.load(f)['functions']
        self.is_insert_statement = False

    def recursiveTree(self, tokenT):

        if type(tokenT) != sqlparse.sql.Token:
            for t in tokenT:
                if type(t) != sqlparse.sql.Token:

                    if type(t) == sqlparse.sql.Function:
                        if not self.is_insert_statement:
                            self.function_check(t)

                    self.recursiveTree(t)
                else:
                    pass
        else:
            return

    def query_syntax_validation(self, query):
        self.init_validation()

        print("----------- VALIDATION -----------")
        parsed = sqlparse.parse(query)[0]
        print(parsed.tokens)

        if str(parsed.tokens[0]) == "INSERT":
            self.is_insert_statement = True

        self.recursiveTree(parsed.tokens)

        print("--------------------------------")
        valid = self.check_flags()
        return valid

    def init_validation(self):
        self.function_flag = False
        self.misuse_keyword_flag = False
        self.is_insert_statement = False
        return

    def check_flags(self):
        if self.function_flag or self.misuse_keyword_flag:
            return False
        else:
            return True

    def function_check(self, query_part):

        for obj in self.functions:
            if str(query_part[0]).upper() == obj['name']:
                return

        self.function_flag = True
        return

    def keyword_check(self, query_part):


        #self.misuse_keyword_flag = True
        return


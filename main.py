import sqlvalidator
import sqlparse
from Classes import Node, Relationship, Property, Statement

keywords_all = ["SELECT", "DISTINCT", "FROM", "AS", "JOIN", "ON", "WHERE", "GROUP BY", "AND", "XOR", "OR", "NOT",
                "ORDER BY",
                "FULL JOIN", "IN", "BETWEEN", "ASC", "DESC", "LIKE", "LEFT OUTER JOIN", "RIGHT OUTER JOIN", "HAVING",
                "UNION", "LIMIT", "ALL", "ANY", "EXISTS"]

keywords_essential = ["SELECT", "FROM", "JOIN", "WHERE", "GROUP BY", "ORDER BY", "FULL JOIN", "LEFT OUTER JOIN",
                      "RIGHT OUTER JOIN", "HAVING", "UNION", "LIMIT"]

nodes = []
relationship = []
queryParts = []


def recursiveTree(tokenT):
    print("----")

    if type(tokenT) != sqlparse.sql.Token:
        for t in tokenT:
            if type(t) != sqlparse.sql.Token:
                recursiveTree(t)
            else:
                print(str(t))
    else:
        print(str(tokenT))
        return


def transformQueryPart(text, array):
    print(array)

    match text:
        case "SELECT":
            statement = Statement("SELECT", "RETURN ")

            for t in array:
                if str(t) == "DISTINCT":
                    statement.text = statement.text + " DISTINCT "

                if type(t) == sqlparse.sql.IdentifierList:
                    for index, obj in enumerate(t.get_identifiers()):
                        print(obj)
                        if(index == len(list(t.get_identifiers()))-1):
                            statement.text = statement.text + str(obj) + " "
                        else:
                            statement.text = statement.text + str(obj) + ", "


            queryParts.append(statement)

            return statement.text
        case "DISTINCT":
            return "DISTINCT"
        case "FROM":
            statement = Statement("FROM", "MATCH")
            queryParts.append(statement)

            return statement.text
        case "AS":
            return "AS"
        case "JOIN" | "FULL JOIN":
            return ""
        case "ON":
            return ""
        case "WHERE":
            return "WHERE"
        case "GROUP BY":
            return ""
        case "ORDER BY":
            return "ORDER BY"
        case "LEFT OUTER JOIN" | "RIGHT OUTER JOIN":
            return "OPTIONAL MATCH"
        case "HAVING":
            return "WITH # WHERE"
        case "UNION":
            return "UNION"
        case "UNION ALL":
            return "UNION ALL"
        case "LIMIT":
            return "LIMIT"
        case "UNION ALL":
            return "UNION ALL"
        case "ASC":
            return "ASC"
        case "DESC":
            return "DESC"

    return "not found"


if __name__ == '__main__':

    query = "SELECT c.CompanyName, COUNT(*) FROM customers AS c " \
            "WHERE c.CompanyName == 'Chocolate'"

    sql_query = sqlvalidator.parse(query)

    if not sql_query.is_valid():
        print(sql_query.errors)
    else:
        print("everything fine!")

    print("--------------------------------")

    parsed = sqlparse.parse(query)[0]
    tokensP = parsed.tokens
    print(tokensP)

    print("--------------------------------")

    queryParts = []

    for i in parsed:
        # print(str(i))
        if str(i) in keywords_essential or type(i) == sqlparse.sql.Where:
            queryParts.append([])
        queryParts[len(queryParts) - 1].append(i)

    # print(queryParts)

    for i in range(len(queryParts)):
        print(transformQueryPart(str(queryParts[i][0]), queryParts[i]))

    print("--------------------------------")

    # for token in sqlparse.sql.IdentifierList(tokensP).get_identifiers():
    #    recursiveTree(token)

    print("--------------------------------")

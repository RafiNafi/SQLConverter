import sqlvalidator
import sqlparse

from CypherQuery import CypherQuery


def convert_query(query_parts):
    queries_list = []

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

    # add semicolon
    combined_result_query += ";"

    return combined_result_query


if __name__ == '__main__':

    # test queries

    query2 = "SELECT e.EmployeeID, count(*) AS Count " \
             "FROM Employee AS e, test " \
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

    query3 = "SELECT zipcode AS zip, count(*) AS population " \
             "FROM Person " \
             "GROUP BY zip " \
             "HAVING population>10000;"

    query0 = "SELECT zipcode AS zip, count(*) AS population " \
             "FROM Person " \
             "WHERE e.EmployeeID = 100 " \
             "GROUP BY zip " \
             "HAVING population>10000;"

    query4 = "SELECT a.studentid, a.name, b.total_marks " \
             "FROM student AS a, marks " \
             "WHERE a.studentid = b.studentid " \
             "AND b.total_marks > (SELECT total_marks FROM marks WHERE studentid =  'V002');"

    query6 = "SELECT e.EmployeeID, count(*) AS Count " \
             "FROM Employee AS e " \
             "JOIN ord AS o ON (o.EmployeeID = e.EmployeeID) " \
             "RIGHT OUTER JOIN products AS p ON (p.ProductID = o.ProductID) " \
             "WHERE e.EmployeeID = 100;"

    query7 = "SELECT DISTINCT e.EmployeeID, count(*) AS Count " \
             "FROM Employee AS e " \
             "WHERE e.EmployeeID = 100 " \
             "UNION ALL " \
             "SELECT p.ProductName, p.UnitPrice " \
             "FROM products AS p " \
             "WHERE p.ProductName NOT IN ('Chocolade','Chai');"

    query8 = "SELECT e.EmployeeID, count(*) AS Count " \
             "FROM Employee AS e " \
             "JOIN ord AS o ON (o.EmployeeID = e.EmployeeID) " \
             "AND e.EmployeeID = 100 " \
             "OR e.name = 'Test' " \
             "WHERE e.price = 10;"

    query = "DELETE FROM Customers WHERE CustomerName='Alfred';"

    # sql_query = sqlvalidator.parse(query)

    # check if query valid
    # if not sql_query.is_valid():
        # print("ERROR: " + str(sql_query.errors))
    # else:

    print("query is fine!")

    print("--------------------------------")

    print(convert_query(query))

    print("--------------------------------")

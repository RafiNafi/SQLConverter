import sqlvalidator
from conversion import convert_query

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

    query9 = "SELECT e.EmployeeID, count(*) AS Count " \
             "FROM Employee AS e " \
             "JOIN ord ON (ord.EmployeeID = e.EmployeeID) " \
             "JOIN products AS p ON (p.ProductID = o.ProductID) " \
             "WHERE e.EmployeeID = 100 " \
             "GROUP BY e.EmployeeID " \
             "ORDER BY Count DESC " \
             "LIMIT 10;"

    query12 = "DELETE FROM Customers AS cust " \
            "WHERE cust.CustomerID BETWEEN 1 and 100 " \
            "AND cust.CustomerName='Alfred' " \
            "AND cust.City NOT IN ('Stuttgart') " \
            "AND cust.Service LIKE '%ool';"

    query = "SELECT e.EmployeeID, count(*) AS Count " \
             "FROM Employee AS e " \
             "JOIN ord AS o ON (o.EmployeeID = e.EmployeeID) " \
             "AND e.EmployeeID = 100 " \
             "OR e.name = 'Test' " \
             "WHERE e.price = 10;"

    # sql_query = sqlvalidator.parse(query)

    # check if query valid
    # if not sql_query.is_valid():
        # print("ERROR: " + str(sql_query.errors))
    # else:

    print("query is fine!")

    print("--------------------------------")

    print(convert_query(query))

    print("--------------------------------")

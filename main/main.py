import sqlvalidator
from cypher.CypherQuery import convert_query

if __name__ == '__main__':

    # test queries

    query1 = "SELECT e.EmployeeID, count(*) AS Count " \
             "FROM Employee AS e, test " \
             "JOIN ord AS o ON (o.EmployeeID = e.EmployeeID) " \
             "JOIN products AS p ON (p.ProductID = o.ProductID) " \
             "WHERE e.EmployeeID = 100 " \
             "GROUP BY e.EmployeeID " \
             "ORDER BY Count DESC " \
             "LIMIT 10;"

    query2 = "SELECT p.ProductName, p.UnitPrice " \
             "FROM products AS p " \
             "WHERE p.Price BETWEEN 10 AND 20 " \
             "AND p.ProductName NOT IN ('Chocolade','Chai');"

    query3 = "SELECT a.studentid, a.name, b.total_marks " \
             "FROM student AS a, marks " \
             "WHERE a.studentid = b.studentid " \
             "AND b.total_marks > (SELECT total_marks FROM marks WHERE studentid =  'V002');"

    query4 = "SELECT e.EmployeeID, count(*) AS Count " \
             "FROM Employee AS e " \
             "JOIN ord AS o ON (o.EmployeeID = e.EmployeeID) " \
             "RIGHT OUTER JOIN products AS p ON (p.ProductID = o.ProductID) " \
             "WHERE e.EmployeeID = 100;"

    query5 = "SELECT DISTINCT e.EmployeeID, count(*) AS Count " \
             "FROM Employee AS e " \
             "WHERE e.EmployeeID = 100 " \
             "UNION ALL " \
             "SELECT p.ProductName, p.UnitPrice " \
             "FROM products AS p " \
             "WHERE p.ProductName NOT IN ('Chocolade','Chai');"

    query6 = "SELECT e.EmployeeID, count(*) AS Count " \
             "FROM Employee AS e " \
             "JOIN ord ON (ord.EmployeeID = e.EmployeeID) " \
             "JOIN products AS p ON (p.ProductID = o.ProductID) " \
             "WHERE e.EmployeeID = 100 " \
             "GROUP BY e.EmployeeID " \
             "ORDER BY Count DESC " \
             "LIMIT 10;"

    query7 = "SELECT e.EmployeeID, count(*) AS Count " \
             "FROM Employee AS e " \
             "JOIN ord AS o ON (o.EmployeeID = e.EmployeeID) " \
             "AND e.EmployeeID = 100 " \
             "OR e.name = 'Test' " \
             "WHERE e.price = 10;"

    query8 = "SELECT p.product_name AS name,COUNT(p.unit_price) AS numb FROM products AS p GROUP BY name HAVING numb>0;"

    query9 = "SELECT supp.SupplierName " \
            "FROM Suppliers AS supp " \
            "WHERE EXISTS(SELECT ProductName FROM Products WHERE Products.SupplierID = supp.supplierID);"

    query10 = "SELECT p.product_name, p.unit_price FROM products AS p WHERE p.unit_price > (SELECT avg(b.unit_price) FROM products AS b);"

    query = "SELECT product_name, unit_price FROM products WHERE unit_price > (SELECT avg(unit_price) FROM products " \
           "WHERE product_name IN (SELECT product_name FROM products WHERE product_name LIKE 'T%'));"

    # sql_query = sqlvalidator.parse(query)

    # check if query valid
    # if not sql_query.is_valid():
        # print("ERROR: " + str(sql_query.errors))
    # else:

    # print("query is fine!")

    print("--------------------------------")

    print(convert_query(query))

    print("--------------------------------")

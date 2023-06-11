from Converter import convert_type
import sqlfluff

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

    query8 = "SELECT p.product_name AS name,COUNT(p.unit_price) AS numb FROM products AS p GROUP BY name HAVING numb>10;"

    query10 = "SELECT product_name, unit_price FROM products, (SELECT avg(unit_price) AS test FROM products) AS avr WHERE unit_price < avr.test"

    query13 = "SELECT product_name, unit_price FROM products WHERE unit_price > (SELECT avg(unit_price) AS aver FROM products " \
              "WHERE product_name IN (SELECT product_name AS pname FROM products WHERE product_name LIKE 'T%'));"

    query18 = "SELECT product_name, unit_price FROM products WHERE unit_price > (SELECT avg(unit_price) FROM products " \
              "WHERE product_name IN (SELECT product_name FROM products WHERE product_name LIKE 'T%')) AND unit_price < (SELECT sum(unit_price) FROM products);"

    query12 = "SELECT PersNr, (SELECT SWS AS Lehrbelastung FROM Vorlesungen WHERE gelesenVon=PersNr ORDER BY PersNr) FROM Professoren;"

    query9 = "SELECT supp.SupplierName " \
             "FROM Suppliers AS supp " \
             "WHERE EXISTS(SELECT ProductName FROM Products WHERE Products.SupplierID = supp.supplierID);"

    query14 = "SELECT s.company_name " \
              "FROM suppliers AS s " \
              "WHERE EXISTS(SELECT x.company_name FROM suppliers AS x WHERE x.company_name LIKE '%e');"

    query15 = "SELECT PersNr, " \
              "(SELECT SWS FROM Vorlesungen WHERE EXISTS(SELECT x.company_name FROM suppliers AS x WHERE x.company_name LIKE '%e')) " \
              "FROM Professoren;"

    query16 = "SELECT p.product_name " \
              "FROM products AS p " \
              "WHERE p.product_id > ALL(SELECT s.supplier_id FROM suppliers AS s WHERE s.company_name LIKE 'S%');"

    query22 = "SELECT product_name, unit_price FROM products WHERE product_name IN (SELECT product_name FROM products WHERE product_name LIKE 'T%') " \
            "AND unit_price > (SELECT avg(unit_price) FROM products) ORDER BY unit_price;"

    query11 = "SELECT s.suppliername " \
            "FROM Suppliers AS s " \
            "WHERE s.suppliername = 'Adidas' " \
            "AND s.suppliername LIKE 'a%';"

    query = "SELECT product_name, unit_price FROM products " \
            "WHERE product_name IN (SELECT product_name FROM products WHERE product_name LIKE 'T%') AND unit_price < (SELECT avg(unit_price) FROM products) " \
            "UNION ALL " \
            "SELECT product_name, unit_price FROM products " \
            "WHERE product_name IN (SELECT product_name FROM products WHERE product_name LIKE 'T%') AND unit_price > (SELECT sum(unit_price) FROM products) ORDER BY unit_price;"

    print("--------------------------------")

    query_sting = convert_type("Cypher", query)

    print("\nQUERY:")
    print(query_sting)

    print("\n")
    for line in sqlfluff.lint(query):
        print(line)

    print("--------------------------------")

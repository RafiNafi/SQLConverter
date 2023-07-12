import sqlfluff
import backend.validation.Validator as validator
import Converter

# sqlfluff error codes
serious_error_codes = ["PRS", "RF01", "RF04", "AL04", "CV03", "CV07", "LT06", "RF02", "RF03", "RF05", "ST07", "AM07"]

# this file is just for testing and debugging purposes
if __name__ == '__main__':

    # test queries

    queryJoinOrderLimit = "SELECT e.EmployeeID, count(*) AS Count " \
             "FROM Employee AS e, test " \
             "JOIN ord AS o ON (o.EmployeeID = e.EmployeeID) " \
             "JOIN products AS p ON (p.ProductID = o.ProductID) " \
             "WHERE e.EmployeeID = 100 " \
             "GROUP BY e.EmployeeID " \
             "ORDER BY Count DESC " \
             "LIMIT 10;"

    queryBetweenAndIn = "SELECT p.ProductName, p.UnitPrice " \
             "FROM products AS p " \
             "WHERE p.Price BETWEEN 10 AND 20 " \
             "AND p.ProductName NOT IN ('Chocolade','Chai');"

    querySub = "SELECT a.studentid, a.name, b.total_marks " \
             "FROM student AS a, marks " \
             "WHERE a.studentid = b.studentid " \
             "AND b.total_marks > (SELECT total_marks FROM marks WHERE studentid =  'V002');"

    queryOuterJoin = "SELECT e.EmployeeID, count(*) AS Count " \
             "FROM Employee AS e " \
             "JOIN ord AS o ON (o.EmployeeID = e.EmployeeID) " \
             "RIGHT OUTER JOIN products AS p ON (p.ProductID = o.ProductID) " \
             "WHERE e.EmployeeID = 100;"

    queryUnion = "SELECT DISTINCT e.EmployeeID, count(*) AS Count " \
             "FROM Employee AS e " \
             "WHERE e.EmployeeID = 100 " \
             "UNION ALL " \
             "SELECT p.ProductName, p.UnitPrice " \
             "FROM products AS p " \
             "WHERE p.ProductName NOT IN ('Chocolade','Chai');"

    queryJoinMultiple = "SELECT e.EmployeeID, count(*) AS Count " \
             "FROM Employee AS e " \
             "JOIN ord ON (ord.EmployeeID = e.EmployeeID) " \
             "JOIN products AS p ON (p.ProductID = o.ProductID) " \
             "WHERE e.EmployeeID = 100 " \
             "GROUP BY e.EmployeeID " \
             "ORDER BY Count DESC " \
             "LIMIT 10;"

    queryJoin = "SELECT e.EmployeeID, count(*) AS Count " \
             "FROM Employee AS e " \
             "JOIN ord AS o ON (o.EmployeeID = e.EmployeeID) " \
             "AND e.EmployeeID = 100 " \
             "OR e.name = 'Test' " \
             "WHERE e.price = 10;"

    querySubFrom = "SELECT product_name, unit_price FROM products, (SELECT avg(unit_price) AS test FROM products) AS avr WHERE unit_price < avr.test"

    queryNestedSub = "SELECT product_name, unit_price FROM products WHERE unit_price > (SELECT avg(unit_price) AS aver FROM products " \
              "WHERE product_name IN (SELECT product_name AS pname FROM products WHERE product_name LIKE 'T%'));"

    queryNestedParallelSubWhere = "SELECT product_name, unit_price FROM products WHERE unit_price > (SELECT avg(unit_price) FROM products " \
              "WHERE product_name IN (SELECT product_name FROM products WHERE product_name LIKE 'T%')) AND unit_price < (SELECT sum(unit_price) FROM products);"

    querySubSelect1 = "SELECT PersNr, (SELECT SWS AS Lehrbelastung FROM Vorlesungen WHERE gelesenVon=PersNr ORDER BY PersNr) FROM Professoren;"

    queryExists = "SELECT supp.SupplierName " \
             "FROM Suppliers AS supp " \
             "WHERE EXISTS(SELECT ProductName FROM Products WHERE Products.SupplierID = supp.supplierID);"

    queryExistsSub = "SELECT s.company_name " \
              "FROM suppliers AS s " \
              "WHERE EXISTS(SELECT x.company_name FROM suppliers AS x WHERE x.company_name LIKE '%e');"

    querySubSelect2 = "SELECT PersNr, " \
              "(SELECT SWS FROM Vorlesungen WHERE EXISTS(SELECT x.company_name FROM suppliers AS x WHERE x.company_name LIKE '%e')) " \
              "FROM Professoren;"

    queryALL = "SELECT p.product_name " \
              "FROM products AS p " \
              "WHERE p.product_id > ALL(SELECT s.supplier_id FROM suppliers AS s WHERE s.company_name LIKE 'S%');"

    querySub1 = "SELECT product_name, unit_price FROM products WHERE product_name IN (SELECT product_name FROM products WHERE product_name LIKE 'T%') " \
              "AND unit_price > (SELECT avg(unit_price) FROM products) ORDER BY unit_price;"

    querySub2 = "SELECT product_name, unit_price FROM products " \
            "WHERE product_name IN (SELECT product_name FROM products WHERE product_name LIKE 'T%') AND unit_price < (SELECT avg(unit_price) FROM products) " \
            "UNION ALL " \
            "SELECT product_name, unit_price FROM products " \
            "WHERE product_name IN (SELECT product_name FROM products WHERE product_name LIKE 'T%') AND unit_price > (SELECT sum(unit_price) FROM products) ORDER BY unit_price;"

    queryWhere = "SELECT s.suppliername " \
              "FROM Suppliers AS s " \
              "WHERE s.suppliername = 'Adidas' " \
              "AND s.suppliername LIKE 'a%';"

    queryHaving = "SELECT COUNT(s.supplier_id), s.country AS c FROM suppliers AS s GROUP BY c HAVING COUNT(s.supplier_id) > 2;"

    queryHaving2 = "SELECT p.product_name AS name,COUNT(p.unit_price) FROM products AS p GROUP BY name HAVING COUNT(p.unit_price) > (SELECT avg(products.unit_price) FROM products);"

    queryUNION = "SELECT e.city FROM employees AS e UNION SELECT s.city FROM suppliers AS s ORDER BY city;"

    queryMultiple = "SELECT e.first_name AS Employee, manager.first_name AS Manager, o.order_id FROM employees AS e " \
                    "LEFT OUTER JOIN employees AS manager ON (e.reports_to = manager.employee_id) " \
                    "JOIN orders As o ON (e.employee_id = o.employee_id);"

    queryMULTIPLEJoins = "SELECT p.product_name AS n FROM products AS p " \
            "JOIN suppliers AS s ON (s.supplier_id = p.supplier_id) " \
            "JOIN categories AS c ON (c.category_id = p.category_id) " \
            "JOIN order_details AS od ON (od.product_id = p.products_id) " \
    "LEFT JOIN suppliers2 AS s2 ON (s2.supplier_id = s.supplier_id) " \
    "LEFT JOIN categories2 AS c2 ON (c2.category_id = p.category_id) " \
    "LEFT JOIN order_details2 AS od2 ON (od2.product_id = p.products_id);"

    queryJOINS = "SELECT p.product_name AS n FROM products AS p " \
            "JOIN categories AS c ON (c.category_id = p.category_id) " \
            "JOIN suppliers AS s ON (s.supplier_id = p.supplier_id) " \
            "JOIN order_details AS od ON (od.product_id = p.products_id);"

    queryErrorLike = "SELECT e.first_name AS Employee, manager.first_name AS Manager FROM employees AS e " \
            "INNER JOIN employees AS manager ON e.reports_to = manager.employee_id AND e.first_name LIKE 'M%' WHERE manager.first_name = 'C';"

    queryParenthesis = "SELECT e.employee_id FROM Employee AS e JOIN orders ON orders.employee_id = e.employee_id AND (e.employee_id >= 2 OR e.employee_id >= 3) " \
            "WHERE e.first_name = 'C' AND e.first_name LIKE 'M%';"

    queryKeywordError1 = "SELECT column, cast FROM table;"

    queryKeywordError2 = "SELECT e.first_name, alter.first_name FROM employees AS e " \
            "INNER JOIN alter ON e.reports_to = alter.employee_id;"

    queryFuncParameter = "SELECT COUNT(s.supplier_id, s.supplier_id) AS numb, s.country AS c FROM suppliers AS s;"

    queryDotError = "SELECT tabelle.spalte1, tabelle.spalte2 FROM tabelle WHERE tabelle..spalte2 > 2;"

    queryHaving3 = "SELECT p.product_name AS pname,COUNT(p.unit_price) FROM products AS p GROUP BY pname HAVING COUNT(p.unit_price) > (SELECT avg(products.unit_price) FROM products);"

    queryHavingMultiple = "SELECT p.product_name AS pname,COUNT(p.unit_price) FROM products AS p " \
            "WHERE pname < (SELECT p.product_name AS pname,COUNT(p.unit_price) FROM products AS p GROUP BY pname " \
            "HAVING COUNT(p.unit_price) > 3) HAVING COUNT(p.unit_price) > " \
            "(SELECT p.product_name AS pname,COUNT(p.unit_price) FROM products AS p GROUP BY pname HAVING COUNT(p.unit_price) > 2) ;"

    query = "SELECT e.first_name AS Employee, manager.first_name AS Manager FROM employees AS e " \
            "LEFT OUTER JOIN employees AS manager ON e.reports_to = manager.employee_id;"

    print("--------------------------------")

    checker = validator.Validator()
    print("VALID: " + str(checker.query_syntax_validation(query)))

    query_sting = Converter.convert_type("Cypher", query)

    print("\nQUERY:")
    print(query_sting)

    print("\n")
    for line in sqlfluff.lint(query):
        if line["code"] in serious_error_codes:
            print("\u001b[31m" + str(line))
        else:
            print("\u001b[33m" + str(line))

    print("--------------------------------")

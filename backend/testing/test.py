from backend.main.Converter import convert_type
import backend.validation.Validator as validator

def test_simple_select():
    query = "SELECT *, p.name " \
            "FROM products as p;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (p:products) " \
                                            "RETURN *, p.name;"

def test_implicit_aliasing_from():

    query = "SELECT tab.col, tab2.var FROM tabelle tab, tabelle2 tab2, tabelle3 as tab3, tabelle4;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (tab:tabelle),(tab2:tabelle2),(tab3:tabelle3),(tabelle4:tabelle4) " \
                                               "RETURN tab.col, tab2.var;"

def test_implicit_aliasing_functions():

    query = "SELECT e.employee_id id, COALESCE(e.region,'no region') col FROM employees e;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (e:employees) RETURN e.employee_id AS id, COALESCE(e.region,'no region') AS col;"

def test_implicit_aliasing_select():

    query = "SELECT tab.val wert, tab.val2 AS variable FROM tabelle AS tab;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (tab:tabelle) " \
                                               "RETURN tab.val AS wert, tab.val2 AS variable;"

def test_simple_orderby():
    query = "SELECT tb.var FROM tabelle AS tb ORDER BY tb.var ASC;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (tb:tabelle) " \
                                               "RETURN tb.var " \
                                               "ORDER BY tb.var ASC;"

def test_missing_whitespaces():

    query = "SELECT unit_price FROM products " \
            "WHERE product_name IN( SELECT product_name FROM products WHERE product_name LIKE 'T%');"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "CALL{MATCH (products:products) " \
                                               "WHERE product_name STARTS WITH \"T\" " \
                                               "RETURN product_name AS sub0} WITH * " \
                                               "MATCH (products:products) " \
                                               "WHERE product_name IN [sub0] RETURN unit_price;"

def test_simple_select_wildcard():
    query = "SELECT p.* " \
            "FROM products as p;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (p:products) " \
                                            "RETURN p;"


def test_simple_where():
    query = "SELECT supp.SupplierName " \
            "FROM Suppliers AS supp " \
            "WHERE supp.SupplierName = 'Adidas';"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (supp:Suppliers) " \
                                            "WHERE supp.SupplierName = 'Adidas' " \
                                            "RETURN supp.SupplierName;"


def test_check_simple_join():
    query = "SELECT e.EmployeeID, count(*) AS Count " \
            "FROM Employee AS e " \
            "INNER JOIN ord AS o ON (o.EmployeeID = e.EmployeeID);"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (e:Employee)-[:relationship]-(o:ord) " \
                                            "RETURN e.EmployeeID, count(*) AS Count;"

def test_check_simple_implicit_join():
    query = "SELECT emp.EmployeeID " \
            "FROM Employee AS emp " \
            "INNER JOIN ord o ON (o.EmployeeID = emp.EmployeeID);"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (emp:Employee)-[:relationship]-(o:ord) " \
                                               "RETURN emp.EmployeeID;"

def test_check_simple_join_without_parenthesis():
    query = "SELECT e.EmployeeID, count(*) AS Count " \
            "FROM Employee AS e " \
            "JOIN ord AS o ON o.EmployeeID = e.EmployeeID;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (e:Employee)-[:relationship]-(o:ord) " \
                                            "RETURN e.EmployeeID, count(*) AS Count;"


def test_mult_joins():
    query = "SELECT e.EmployeeID, count(*) AS numb " \
            "FROM Employee AS e " \
            "JOIN ord AS o ON (o.EmployeeID = e.EmployeeID) " \
            "JOIN products AS p ON (p.ProductID = o.ProductID) " \
            "WHERE e.EmployeeID = 100 " \
            "GROUP BY e.EmployeeID " \
            "ORDER BY numb DESC " \
            "LIMIT 10;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (e:Employee)-[:relationship]-(o:ord)-[:relationship]-(p:products) " \
                                            "WHERE e.EmployeeID = 100 " \
                                            "RETURN e.EmployeeID, count(*) AS numb " \
                                            "ORDER BY numb DESC " \
                                            "LIMIT 10;"

def test_mult_joins_mixed_alias():
    query = "SELECT EmployeeID, count(*) " \
                "FROM Employee " \
                "JOIN ord ON (ord.EmployeeID = Employee.EmployeeID) " \
                "JOIN products AS p ON (p.ProductID = ord.ProductID) " \
                "WHERE EmployeeID = 100 " \
                "GROUP BY EmployeeID " \
                "ORDER BY count(*) DESC;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher",
                            query, 0) == "MATCH (Employee:Employee)-[:relationship]-(ord:ord)-[:relationship]-(p:products) " \
                                      "WHERE EmployeeID = 100 " \
                                      "RETURN EmployeeID, count(*) " \
                                      "ORDER BY count(*) DESC;"

def test_join_with_mult_conditions():

    query = "SELECT e.first_name AS Employee, manager.first_name AS Manager FROM employees AS e " \
            "INNER JOIN employees AS manager ON e.reports_to = manager.employee_id AND e.first_name = 'A' OR e.first_name = 'B';"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (manager:employees)-[:relationship]-(e:employees) " \
                                               "WHERE e.first_name = 'A' OR e.first_name = 'B' " \
                                               "RETURN e.first_name AS Employee, manager.first_name AS Manager;"

def test_join_with_mult_conditions_and_where():

    query = "SELECT e.first_name AS Employee, manager.first_name AS Manager FROM employees AS e " \
            "INNER JOIN employees AS manager ON e.first_name = 'A' AND e.reports_to = manager.employee_id WHERE manager.first_name = 'C';"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (manager:employees)-[:relationship]-(e:employees) " \
                                               "WHERE e.first_name = 'A' AND manager.first_name = 'C' " \
                                               "RETURN e.first_name AS Employee, manager.first_name AS Manager;"

def test_where_not_in_and_not_between():
    query = "SELECT p.ProductName, p.UnitPrice " \
            "FROM products AS p " \
            "WHERE p.ProductName NOT IN ('Chocolade','Chai') " \
            "AND p.Price NOT BETWEEN 10 AND 20;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (p:products) " \
                                            "WHERE NOT p.ProductName IN ['Chocolade','Chai'] AND NOT 10 <= p.Price <= 20 " \
                                            "RETURN p.ProductName, p.UnitPrice;"


def test_where_like():
    query = "SELECT p.ProductName, p.UnitPrice " \
            "FROM products AS p " \
            "WHERE p.ProductName LIKE 'C%ool';"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (p:products) " \
                                            "WHERE p.ProductName STARTS WITH \"C\" AND p.ProductName ENDS WITH \"ool\" " \
                                            "RETURN p.ProductName, p.UnitPrice;"


def test_outer_join():
    query = "SELECT e.EmployeeID, count(*) AS Count " \
            "FROM Employee AS e " \
            "LEFT OUTER JOIN ord AS o ON (o.EmployeeID = e.EmployeeID) " \
            "LEFT OUTER JOIN products AS p ON (p.ProductID = o.ProductID) " \
            "WHERE e.EmployeeID = 100;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (e:Employee) " \
                                            "OPTIONAL MATCH (e:Employee)-[:relationship]->(o:ord)-[:relationship]->(p:products) " \
                                            "WHERE e.EmployeeID = 100 " \
                                            "RETURN e.EmployeeID, count(*) AS Count;"

def test_outer_join_and_is_null():

    query = "SELECT c.company_name, o.order_id FROM customers AS c FULL OUTER JOIN orders AS o ON (c.customer_id = o.customer_id) WHERE o.order_id IS NULL ORDER BY c.company_name;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (c:customers) " \
                                               "OPTIONAL MATCH (o:orders)<-[:relationship]-(c:customers) " \
                                               "WHERE o.order_id IS NULL " \
                                               "RETURN c.company_name, o.order_id " \
                                               "ORDER BY c.company_name;"

def test_mixed_multiple_joins():
    query = "SELECT p.product_name AS n FROM products AS p " \
            "JOIN suppliers AS s ON (s.supplier_id = p.supplier_id) " \
            "JOIN categories AS c ON (c.category_id = p.category_id) " \
            "JOIN order_details AS od ON (od.product_id = p.products_id) " \
    "LEFT JOIN suppliers2 AS s2 ON (s2.supplier_id = s.supplier_id) " \
    "LEFT JOIN categories2 AS c2 ON (c2.category_id = p.category_id) " \
    "LEFT JOIN order_details2 AS od2 ON (od2.product_id = p.products_id);"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (c:categories)-[:relationship]-(p:products)-[:relationship]-(s:suppliers) " \
                                               "\nMATCH (p:products)-[:relationship]-(od:order_details) " \
                                               "OPTIONAL MATCH (s:suppliers)-[:relationship]->(s2:suppliers2) \nOPTIONAL MATCH " \
                                               "(od2:order_details2)-[:relationship]->(p:products)-[:relationship]->(c2:categories2) " \
                                               "RETURN p.product_name AS n;"

def test_union_without_alias():
    query = "SELECT e.city FROM employees AS e UNION SELECT s.city FROM suppliers AS s ORDER BY city;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (e:employees) RETURN e.city AS city UNION MATCH (s:suppliers) RETURN s.city AS city ORDER BY city;"

def test_union_query():
    query = "SELECT DISTINCT e.ProductName AS name, e.UnitPrice " \
            "FROM Employee AS e " \
            "WHERE e.EmployeeID = 100 " \
            "UNION ALL " \
            "SELECT p.ProductName AS name, p.UnitPrice " \
            "FROM products AS p " \
            "WHERE p.ProductName NOT IN ('Chocolade','Chai') " \
            "UNION " \
            "SELECT p.ProductName AS name, p.UnitPrice " \
            "FROM products AS p " \
            "WHERE p.ProductName = 'Test';"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (e:Employee) " \
                                            "WHERE e.EmployeeID = 100 " \
                                            "RETURN DISTINCT e.ProductName AS name, e.UnitPrice AS UnitPrice " \
                                            "UNION ALL " \
                                            "MATCH (p:products) " \
                                            "WHERE NOT p.ProductName IN ['Chocolade','Chai'] " \
                                            "RETURN p.ProductName AS name, p.UnitPrice AS UnitPrice " \
                                            "UNION " \
                                            "MATCH (p:products) " \
                                            "WHERE p.ProductName = 'Test' " \
                                            "RETURN p.ProductName AS name, p.UnitPrice AS UnitPrice;"


def test_between():
    query = "SELECT p.ProductName, p.UnitPrice " \
            "FROM products AS p " \
            "WHERE p.Price BETWEEN 1 AND 15 " \
            "AND p.ProductName IN ('Chocolade');"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (p:products) " \
                                            "WHERE 1 <= p.Price <= 15 AND p.ProductName IN ['Chocolade'] " \
                                            "RETURN p.ProductName, p.UnitPrice;"


def test_where_not():
    query = "SELECT * FROM Customers " \
            "WHERE NOT Customers.Country='Germany' AND NOT Customers.Country='USA';"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (Customers:Customers) " \
                                            "WHERE NOT Customers.Country='Germany' AND NOT Customers.Country='USA' " \
                                            "RETURN *;"


def test_insert():
    query = "INSERT INTO Customers (CustomerName, ContactName, Address, City, PostalCode, Country) " \
            "VALUES ('Cardinal', 'Tom B. Erichsen', 'Skagen 21', 'Stavanger', '4006', 'Norway');"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher",
                        query, 0) == "CREATE (:Customers {CustomerName: 'Cardinal', ContactName: 'Tom B. Erichsen', " \
                                  "Address: 'Skagen 21', City: 'Stavanger', PostalCode: '4006', Country: 'Norway'});"


def test_insert_without_columns():
    query = "INSERT INTO Customers " \
            "VALUES ('Cardinal', 'Tom B. Erichsen', 'Skagen 21', 'Stavanger', '4006', 'Norway');"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "CREATE (:Customers {var0: 'Cardinal', var1: 'Tom B. Erichsen', " \
                                            "var2: 'Skagen 21', var3: 'Stavanger', var4: '4006', var5: 'Norway'});"


def test_delete_node():
    query = "DELETE FROM Customers WHERE CustomerName='Alfred';"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (Customers:Customers) WHERE Customers.CustomerName='Alfred' DELETE Customers;"


def test_delete_with_alias():
    query = "DELETE FROM Customers AS cust WHERE cust.CustomerName='Alfred';"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "MATCH (cust:Customers) WHERE cust.CustomerName='Alfred' DELETE cust;"


def test_delete_with_many_conditions():
    query = "DELETE FROM Customers AS c WHERE CustomerName='Alfred' AND City NOT IN ('Stuttgart') AND Service LIKE '%ool' AND CustomerID BETWEEN 1 and 100;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher",
                        query, 0) == "MATCH (c:Customers) WHERE c.CustomerName='Alfred' AND NOT c.City IN ['Stuttgart'] AND c.Service ENDS WITH \"ool\" AND 1 <= c.CustomerID <= 100 DELETE c;"


def test_update_node():
    query = "UPDATE Customers AS c " \
            "SET ContactName = 'Alfred Schmidt', City= 'Frankfurt' " \
            "WHERE CustomerID = 1;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher",
                        query, 0) == "MATCH (c:Customers) WHERE c.CustomerID = 1 SET c.ContactName = 'Alfred Schmidt', c.City= 'Frankfurt';"


def test_update_with_alias():
    query = "UPDATE Customers " \
            "SET ContactName = 'Alfred Schmidt', City= 'Frankfurt' " \
            "WHERE CustomerID = 1;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher",
                        query, 0) == "MATCH (Customers:Customers) WHERE Customers.CustomerID = 1 SET Customers.ContactName = 'Alfred Schmidt', Customers.City= 'Frankfurt';"


def test_simple_having():
    query = "SELECT p.zipcode AS zip, count(*) " \
            "FROM Person as p " \
            "WHERE p.EmployeeID = 100 " \
            "GROUP BY zip " \
            "HAVING count(*) > 10000;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher",
                        query, 0) == "MATCH (p:Person) WITH p.zipcode AS zip, count(*) AS alias1 WHERE p.EmployeeID = 100 AND alias1 > 10000 RETURN zip, alias1;"


def test_having_multiple_aggregations():
    query = "SELECT COUNT(Cust.CustomerID) AS numb, SUM(Cust.price) AS sum, Cust.Country AS c " \
            "FROM Customers AS Cust " \
            "GROUP BY c " \
            "HAVING numb > 5 AND sum < 10 " \
            "ORDER BY numb DESC;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher",
                        query, 0) == "MATCH (Cust:Customers) WITH COUNT(Cust.CustomerID) AS numb, SUM(Cust.price) AS sum, Cust.Country AS c WHERE numb > 5 AND sum < 10 RETURN numb, sum, c ORDER BY numb DESC;"


def test_switch_case():
    query = "SELECT od.OrderID, od.Quantity, " \
            "CASE " \
            "WHEN od.Quantity > 30 THEN 'greater 30' " \
            "WHEN od.Quantity = 30 THEN 'is 30' " \
            "ELSE 'under 30' " \
            "END AS QuantityText " \
            "FROM OrderDetails AS od;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher",
                        query, 0) == "MATCH (od:OrderDetails) RETURN od.OrderID, od.Quantity, CASE WHEN od.Quantity > 30 THEN 'greater 30' WHEN od.Quantity = 30 THEN 'is 30' ELSE 'under 30' END AS QuantityText;"


def test_switch_case_single_select():
    query = "SELECT " \
            "CASE " \
            "WHEN od.Quantity > 30 THEN 'greater 30' " \
            "WHEN od.Quantity = 30 THEN 'is 30' " \
            "ELSE 'under 30' " \
            "END " \
            "FROM OrderDetails AS od;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher",
                        query, 0) == "MATCH (od:OrderDetails) RETURN CASE WHEN od.Quantity > 30 THEN 'greater 30' WHEN od.Quantity = 30 THEN 'is 30' ELSE 'under 30' END;"



def test_subquery_one_statement():
    query = "SELECT p.product_name, p.unit_price " \
            "FROM products AS p " \
            "WHERE p.unit_price > (SELECT avg(b.unit_price) FROM products AS b);"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "CALL{MATCH (b:products) RETURN avg(b.unit_price) AS sub0} WITH * " \
                                            "MATCH (p:products) WHERE p.unit_price > sub0 RETURN p.product_name, p.unit_price;"


def test_subquery_where_nested_statements():
    query = "SELECT p.product_name, p.unit_price FROM products AS p WHERE p.unit_price > (SELECT avg(products.unit_price) FROM products " \
            "WHERE products.product_name NOT IN (SELECT p.product_name FROM products AS p WHERE p.product_name LIKE 'T%'));"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher",
                        query, 0) == "CALL{CALL{MATCH (p:products) WHERE p.product_name STARTS WITH \"T\" RETURN p.product_name AS sub0} WITH * " \
                                  "MATCH (products:products) WHERE NOT products.product_name IN [sub0] RETURN avg(products.unit_price) AS sub1} WITH * " \
                                  "MATCH (p:products) WHERE p.unit_price > sub1 RETURN p.product_name, p.unit_price;"


def test_subquery_where_multiple_statement():
    query = "SELECT p.product_name, p.unit_price FROM products AS p WHERE p.unit_price > (SELECT avg(p.unit_price) FROM products AS p) " \
            "AND p.product_name IN (SELECT p.product_name FROM products AS p WHERE p.product_name LIKE 'T%');"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "CALL{MATCH (p:products) RETURN avg(p.unit_price) AS sub0} WITH * " \
                                            "CALL{MATCH (p:products) WHERE p.product_name STARTS WITH \"T\" RETURN p.product_name AS sub1} WITH * " \
                                            "MATCH (p:products) WHERE p.unit_price > sub0 AND p.product_name IN [sub1] RETURN p.product_name, p.unit_price;"


def test_subquery_select():
    query = "SELECT Professoren.name, (SELECT sum(v.SWS) AS Lehrbelastung FROM Vorlesungen AS v WHERE v.gelesenVon=Professoren.PersNr), Professoren.PersNr FROM Professoren;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher",
                        query, 0) == "CALL{MATCH (v:Vorlesungen) WHERE v.gelesenVon=Professoren.PersNr RETURN sum(v.SWS) AS Lehrbelastung} WITH * " \
                                  "MATCH (Professoren:Professoren) RETURN Professoren.name, Lehrbelastung, Professoren.PersNr;"


def test_subquery_having():
    query = "SELECT p.product_name AS name,COUNT(p.unit_price) FROM products AS p GROUP BY name HAVING COUNT(p.unit_price) > (SELECT avg(products.unit_price) FROM products);"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "CALL{MATCH (products:products) RETURN avg(products.unit_price) AS sub0} WITH * " \
                                            "MATCH (p:products) WITH p.product_name AS name, COUNT(p.unit_price) AS alias1 WHERE alias1 > sub0 RETURN name, alias1;"


def test_subquery_exists():
    query = "SELECT s.company_name " \
            "FROM suppliers AS s " \
            "WHERE EXISTS(SELECT x.company_name FROM suppliers AS x WHERE x.company_name LIKE '%e');"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher",
                        query, 0) == "MATCH (s:suppliers) WHERE EXISTS{MATCH (x:suppliers) WHERE x.company_name ENDS WITH \"e\" } RETURN s.company_name;"


def test_mixed_select_subquery_and_exists_subquery():
    query = "SELECT Professoren.PersNr, " \
            "(SELECT v.SWS AS Lehrbelastung FROM Vorlesungen AS v WHERE " \
            "EXISTS(SELECT x.company_name FROM suppliers AS x WHERE x.company_name LIKE '%e')) " \
            "FROM Professoren;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher",
                        query, 0) == "CALL{MATCH (v:Vorlesungen) WHERE EXISTS{MATCH (x:suppliers) WHERE x.company_name ENDS WITH \"e\" } RETURN v.SWS AS Lehrbelastung}" \
                                  " WITH * MATCH (Professoren:Professoren) RETURN Professoren.PersNr, Lehrbelastung;"

def test_whitespaces_after_exists_clause():
    query = "SELECT s.company_name " \
            "FROM suppliers AS s " \
            "WHERE EXISTS (SELECT x.company_name FROM suppliers AS x WHERE x.company_name LIKE '%e');"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher",
                        query, 0) == "MATCH (s:suppliers) WHERE " \
                                     "EXISTS{MATCH (x:suppliers) WHERE x.company_name ENDS WITH \"e\" } " \
                                     "RETURN s.company_name;"


def test_simple_all_subquery():
    query = "SELECT p.product_name,p.product_id " \
            "FROM products AS p " \
            "WHERE p.product_id < ALL(SELECT supp.supplier_id FROM suppliers AS supp WHERE supp.company_name LIKE 'S%') " \
            "ORDER BY p.product_id;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "CALL{MATCH (supp:suppliers) WHERE supp.company_name STARTS WITH \"S\" " \
                                            "RETURN supp.supplier_id AS sub0} WITH collect(sub0) AS coll_list " \
                                            "MATCH (p:products) WHERE ALL(var IN coll_list WHERE p.product_id < var) " \
                                            "RETURN p.product_name, p.product_id ORDER BY p.product_id;"


def test_simple_any_subquery():
    query = "SELECT prod.product_name,prod.product_id " \
            "FROM products AS prod " \
            "WHERE prod.product_name = 'test' AND prod.product_id < ANY(SELECT suppliers.supplier_id FROM suppliers WHERE suppliers.company_name LIKE 'S%') " \
            "ORDER BY prod.product_id;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "CALL{MATCH (suppliers:suppliers) WHERE suppliers.company_name STARTS WITH \"S\" " \
                                            "RETURN suppliers.supplier_id AS sub0} WITH collect(sub0) AS coll_list " \
                                            "MATCH (prod:products) WHERE prod.product_name = 'test' AND ANY(var IN coll_list WHERE prod.product_id < var) " \
                                            "RETURN prod.product_name, prod.product_id ORDER BY prod.product_id;"

def test_any_all_missing_whitespaces():
    query = "SELECT p.product_name,p.product_id " \
            "FROM products AS p " \
            "WHERE p.product_id>ANY(SELECT suppliers.supplier_id FROM suppliers WHERE suppliers.company_name LIKE 'S%') " \
            "ORDER BY p.product_id;"

    assert validator.Validator().query_syntax_validation(query)[0]

    assert convert_type("Cypher", query, 0) == "CALL{MATCH (suppliers:suppliers) " \
                                               "WHERE suppliers.company_name STARTS WITH \"S\" " \
                                               "RETURN suppliers.supplier_id AS sub0} WITH collect(sub0) AS coll_list MATCH (p:products) " \
                                               "WHERE ANY(var IN coll_list WHERE p.product_id > var) " \
                                               "RETURN p.product_name, p.product_id " \
                                               "ORDER BY p.product_id;"

def test_simple_missing_error():
    query = " "

    assert convert_type("Cypher", query, 0) == ""


def test_simple_function_spelling_error():
    query = "SELECT suum(p.price) FROM products p;"

    value = validator.Validator().query_syntax_validation(query)

    assert not value[0]
    assert value[2] == 8


def test_misuse_keyword_error():
    query = "SELECT e.first_name, alter.first_name FROM employees AS e " \
            "INNER JOIN alter ON e.reports_to = alter.employee_id;"

    value = validator.Validator().query_syntax_validation(query)

    assert not value[0]
    assert value[2] == 76

def test_misuse_keyword_error_from():
    query = "SELECT column, cast FROM table;"

    value = validator.Validator().query_syntax_validation(query)

    assert not value[0]
    assert value[2] == 26

def test_wrong_function_parameter_number():
    query = "SELECT COUNT(s.supplier_id, s.supplier_id) AS numb, s.country AS c FROM suppliers AS s;"

    value = validator.Validator().query_syntax_validation(query)

    assert not value[0]
    assert value[2] == 8


def test_too_many_dots():
    query = "SELECT tabelle.spalte1, tabelle..spalte2 FROM tabelle;"

    value = validator.Validator().query_syntax_validation(query)

    assert not value[0]
    assert value[2] == 8



from backend.main.Converter import convert_type
import backend.validation.Validator as validator

def test_simple_select():
    query = "SELECT *, p.name " \
            "FROM products as p;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (p:products) " \
                                            "RETURN *, p.name;"

def test_implicit_aliasing_from():

    query = "SELECT tab.col, tab2.var FROM tabelle tab, tabelle2 tab2, tabelle3 as tab3, tabelle4;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (tab:tabelle),(tab2:tabelle2),(tab3:tabelle3),(tabelle4:tabelle4) " \
                                               "RETURN tab.col, tab2.var;"

def test_implicit_aliasing_select():

    query = "SELECT tab.val wert, tab.val2 AS variable FROM tabelle AS tab;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (tab:tabelle) " \
                                               "RETURN tab.val AS wert, tab.val2 AS variable;"

def test_simple_orderby():
    query = "SELECT tb.var FROM tabelle AS tb ORDER BY tb.var ASC;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (tb:tabelle) " \
                                               "RETURN tb.var " \
                                               "ORDER BY tb.var ASC;"

def test_simple_select_wildcard():
    query = "SELECT p.* " \
            "FROM products as p;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (p:products) " \
                                            "RETURN p;"


def test_simple_where():
    query = "SELECT supp.SupplierName " \
            "FROM Suppliers AS supp " \
            "WHERE supp.SupplierName = 'Adidas';"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (supp:Suppliers) " \
                                            "WHERE supp.SupplierName = 'Adidas' " \
                                            "RETURN supp.SupplierName;"


def test_check_simple_join():
    query = "SELECT e.EmployeeID, count(*) AS Count " \
            "FROM Employee AS e " \
            "INNER JOIN ord AS o ON (o.EmployeeID = e.EmployeeID);"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (e:Employee)-[:relationship]->(o:ord) " \
                                            "RETURN e.EmployeeID, count(*) AS Count;"

def test_check_simple_implicit_join():
    query = "SELECT emp.EmployeeID " \
            "FROM Employee AS emp " \
            "INNER JOIN ord o ON (o.EmployeeID = emp.EmployeeID);"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (emp:Employee)-[:relationship]->(o:ord) " \
                                               "RETURN emp.EmployeeID;"

def test_check_simple_join_without_parenthesis():
    query = "SELECT e.EmployeeID, count(*) AS Count " \
            "FROM Employee AS e " \
            "JOIN ord AS o ON o.EmployeeID = e.EmployeeID;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (e:Employee)-[:relationship]->(o:ord) " \
                                            "RETURN e.EmployeeID, count(*) AS Count;"


def test_mult_joins():
    query = "SELECT e.EmployeeID, count(*) AS Count " \
            "FROM Employee AS e " \
            "JOIN ord AS o ON (o.EmployeeID = e.EmployeeID) " \
            "JOIN products AS p ON (p.ProductID = o.ProductID) " \
            "WHERE e.EmployeeID = 100 " \
            "GROUP BY e.EmployeeID " \
            "ORDER BY Count DESC " \
            "LIMIT 10;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (e:Employee)-[:relationship]->(o:ord)-[:relationship]->(p:products) " \
                                            "WHERE e.EmployeeID = 100 " \
                                            "RETURN e.EmployeeID, count(*) AS Count " \
                                            "ORDER BY Count DESC " \
                                            "LIMIT 10;"

def test_mult_joins_mixed_alias():
    query = "SELECT EmployeeID, count(*) " \
                "FROM Employee " \
                "JOIN ord ON (ord.EmployeeID = Employee.EmployeeID) " \
                "JOIN products AS p ON (p.ProductID = ord.ProductID) " \
                "WHERE EmployeeID = 100 " \
                "GROUP BY EmployeeID " \
                "ORDER BY count(*) DESC;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher",
                            query, 0) == "MATCH (Employee:Employee)-[:relationship]->(ord:ord)-[:relationship]->(p:products) " \
                                      "WHERE EmployeeID = 100 " \
                                      "RETURN EmployeeID, count(*) " \
                                      "ORDER BY count(*) DESC;"


def test_where_not_in_and_not_between():
    query = "SELECT p.ProductName, p.UnitPrice " \
            "FROM products AS p " \
            "WHERE p.ProductName NOT IN ('Chocolade','Chai') " \
            "AND p.Price NOT BETWEEN 10 AND 20;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (p:products) " \
                                            "WHERE NOT p.ProductName IN ['Chocolade','Chai'] AND NOT 10 <= p.Price =< 20 " \
                                            "RETURN p.ProductName, p.UnitPrice;"


def test_where_like():
    query = "SELECT p.ProductName, p.UnitPrice " \
            "FROM products AS p " \
            "WHERE p.ProductName LIKE 'C%ool';"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (p:products) " \
                                            "WHERE p.ProductName STARTS WITH \"C\" AND p.ProductName ENDS WITH \"ool\" " \
                                            "RETURN p.ProductName, p.UnitPrice;"


def test_outer_join():
    query = "SELECT e.EmployeeID, count(*) AS Count " \
            "FROM Employee AS e " \
            "LEFT OUTER JOIN ord AS o ON (o.EmployeeID = e.EmployeeID) " \
            "LEFT OUTER JOIN products AS p ON (p.ProductID = o.ProductID) " \
            "WHERE e.EmployeeID = 100;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (e:Employee) " \
                                            "OPTIONAL MATCH (e:Employee)-[:relationship]->(o:ord)-[:relationship]->(p:products) " \
                                            "WHERE e.EmployeeID = 100 " \
                                            "RETURN e.EmployeeID, count(*) AS Count;"


def test_union_query():
    query = "SELECT DISTINCT e.EmployeeID, count(*) AS Count " \
            "FROM Employee AS e " \
            "WHERE e.EmployeeID = 100 " \
            "UNION ALL " \
            "SELECT p.ProductName, p.UnitPrice " \
            "FROM products AS p " \
            "WHERE p.ProductName NOT IN ('Chocolade','Chai') " \
            "UNION " \
            "SELECT * " \
            "FROM products AS p " \
            "WHERE p.ProductName = 'Test';"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (e:Employee) " \
                                            "WHERE e.EmployeeID = 100 " \
                                            "RETURN DISTINCT e.EmployeeID, count(*) AS Count " \
                                            "UNION ALL " \
                                            "MATCH (p:products) " \
                                            "WHERE NOT p.ProductName IN ['Chocolade','Chai'] " \
                                            "RETURN p.ProductName, p.UnitPrice " \
                                            "UNION " \
                                            "MATCH (p:products) " \
                                            "WHERE p.ProductName = 'Test' " \
                                            "RETURN *;"


def test_between():
    query = "SELECT p.ProductName, p.UnitPrice " \
            "FROM products AS p " \
            "WHERE p.Price BETWEEN 1 AND 15 " \
            "AND p.ProductName IN ('Chocolade');"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (p:products) " \
                                            "WHERE 1 <= p.Price =< 15 AND p.ProductName IN ['Chocolade'] " \
                                            "RETURN p.ProductName, p.UnitPrice;"


def test_where_not():
    query = "SELECT * FROM Customers " \
            "WHERE NOT Customers.Country='Germany' AND NOT Customers.Country='USA';"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (Customers:Customers) " \
                                            "WHERE NOT Customers.Country='Germany' AND NOT Customers.Country='USA' " \
                                            "RETURN *;"


def test_insert():
    query = "INSERT INTO Customers (CustomerName, ContactName, Address, City, PostalCode, Country) " \
            "VALUES ('Cardinal', 'Tom B. Erichsen', 'Skagen 21', 'Stavanger', '4006', 'Norway');"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher",
                        query, 0) == "CREATE (:Customers {CustomerName: 'Cardinal', ContactName: 'Tom B. Erichsen', " \
                                  "Address: 'Skagen 21', City: 'Stavanger', PostalCode: '4006', Country: 'Norway'});"


def test_insert_without_columns():
    query = "INSERT INTO Customers " \
            "VALUES ('Cardinal', 'Tom B. Erichsen', 'Skagen 21', 'Stavanger', '4006', 'Norway');"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "CREATE (:Customers {var0: 'Cardinal', var1: 'Tom B. Erichsen', " \
                                            "var2: 'Skagen 21', var3: 'Stavanger', var4: '4006', var5: 'Norway'});"


def test_delete_node():
    query = "DELETE FROM Customers WHERE CustomerName='Alfred';"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (Customers:Customers) WHERE Customers.CustomerName='Alfred' DELETE Customers;"


def test_delete_with_alias():
    query = "DELETE FROM Customers AS cust WHERE cust.CustomerName='Alfred';"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "MATCH (cust:Customers) WHERE cust.CustomerName='Alfred' DELETE cust;"


def test_delete_with_many_conditions():
    query = "DELETE FROM Customers AS c WHERE CustomerName='Alfred' AND City NOT IN ('Stuttgart') AND Service LIKE '%ool' AND CustomerID BETWEEN 1 and 100;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher",
                        query, 0) == "MATCH (c:Customers) WHERE c.CustomerName='Alfred' AND NOT c.City IN ['Stuttgart'] AND c.Service ENDS WITH \"ool\" AND 1 <= c.CustomerID =< 100 DELETE c;"


def test_update_node():
    query = "UPDATE Customers AS c " \
            "SET ContactName = 'Alfred Schmidt', City= 'Frankfurt' " \
            "WHERE CustomerID = 1;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher",
                        query, 0) == "MATCH (c:Customers) WHERE c.CustomerID = 1 SET c.ContactName = 'Alfred Schmidt', c.City= 'Frankfurt';"


def test_update_with_alias():
    query = "UPDATE Customers AS cust " \
            "SET cust.ContactName = 'Alfred Schmidt', cust.City= 'Frankfurt' " \
            "WHERE cust.CustomerID = 1;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher",
                        query, 0) == "MATCH (cust:Customers) WHERE cust.CustomerID = 1 SET cust.ContactName = 'Alfred Schmidt', cust.City= 'Frankfurt';"


def test_simple_having():
    query = "SELECT p.zipcode AS zip, count(*) AS population " \
            "FROM Person as p " \
            "WHERE p.EmployeeID = 100 " \
            "GROUP BY zip " \
            "HAVING population>10000;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher",
                        query, 0) == "MATCH (p:Person) WITH p.zipcode AS zip, count(*) AS population WHERE p.EmployeeID = 100 AND population>10000 RETURN zip, population;"


def test_having_multiple_aggregations():
    query = "SELECT COUNT(Cust.CustomerID) AS count, SUM(Cust.price) As sum, Cust.Country AS c " \
            "FROM Customers AS Cust " \
            "GROUP BY c " \
            "HAVING count > 5 AND sum < 10 " \
            "ORDER BY count DESC;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher",
                        query, 0) == "MATCH (Cust:Customers) WITH COUNT(Cust.CustomerID) AS count, SUM(Cust.price) As sum, Cust.Country AS c WHERE count > 5 AND sum < 10 RETURN count, sum, c ORDER BY count DESC;"


def test_switch_case():
    query = "SELECT od.OrderID, od.Quantity, " \
            "CASE " \
            "WHEN od.Quantity > 30 THEN 'greater 30' " \
            "WHEN od.Quantity = 30 THEN 'is 30' " \
            "ELSE 'under 30' " \
            "END AS QuantityText " \
            "FROM OrderDetails AS od;"

    assert validator.Validator().query_syntax_validation(query)

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

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher",
                        query, 0) == "MATCH (od:OrderDetails) RETURN CASE WHEN od.Quantity > 30 THEN 'greater 30' WHEN od.Quantity = 30 THEN 'is 30' ELSE 'under 30' END;"



def test_subquery_one_statement():
    query = "SELECT p.product_name, p.unit_price " \
            "FROM products AS p " \
            "WHERE p.unit_price > (SELECT avg(b.unit_price) FROM products AS b);"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "CALL{MATCH (b:products) RETURN avg(b.unit_price) AS sub0} WITH * " \
                                            "MATCH (p:products) WHERE p.unit_price > sub0 RETURN p.product_name, p.unit_price;"


def test_subquery_where_nested_statements():
    query = "SELECT p.product_name, p.unit_price FROM products AS p WHERE p.unit_price > (SELECT avg(products.unit_price) FROM products " \
            "WHERE products.product_name NOT IN (SELECT p.product_name FROM products AS p WHERE p.product_name LIKE 'T%'));"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher",
                        query, 0) == "CALL{CALL{MATCH (p:products) WHERE p.product_name STARTS WITH \"T\" RETURN p.product_name AS sub0} WITH * " \
                                  "MATCH (products:products) WHERE NOT products.product_name IN [sub0] RETURN avg(products.unit_price) AS sub1} WITH * " \
                                  "MATCH (p:products) WHERE p.unit_price > sub1 RETURN p.product_name, p.unit_price;"


def test_subquery_where_multiple_statement():
    query = "SELECT p.product_name, p.unit_price FROM products AS p WHERE p.unit_price > (SELECT avg(p.unit_price) FROM products AS p) " \
            "AND p.product_name IN (SELECT p.product_name FROM products AS p WHERE p.product_name LIKE 'T%');"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "CALL{MATCH (p:products) RETURN avg(p.unit_price) AS sub0} WITH * " \
                                            "CALL{MATCH (p:products) WHERE p.product_name STARTS WITH \"T\" RETURN p.product_name AS sub1} WITH * " \
                                            "MATCH (p:products) WHERE p.unit_price > sub0 AND p.product_name IN [sub1] RETURN p.product_name, p.unit_price;"


def test_subquery_select():
    query = "SELECT Professoren.name, (SELECT sum(v.SWS) AS Lehrbelastung FROM Vorlesungen AS v WHERE v.gelesenVon=Professoren.PersNr), Professoren.PersNr FROM Professoren;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher",
                        query, 0) == "CALL{MATCH (v:Vorlesungen) WHERE v.gelesenVon=Professoren.PersNr RETURN sum(v.SWS) AS Lehrbelastung} WITH * " \
                                  "MATCH (Professoren:Professoren) RETURN Professoren.name, Lehrbelastung, Professoren.PersNr;"


def test_subquery_having():
    query = "SELECT p.product_name AS name,COUNT(p.unit_price) AS numb FROM products AS p GROUP BY name HAVING numb>(SELECT avg(products.unit_price) FROM products);"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "CALL{MATCH (products:products) RETURN avg(products.unit_price) AS sub0} WITH * " \
                                            "MATCH (p:products) WITH p.product_name AS name, COUNT(p.unit_price) AS numb WHERE numb>sub0 RETURN name, numb;"


def test_subquery_exists():
    query = "SELECT s.company_name " \
            "FROM suppliers AS s " \
            "WHERE EXISTS(SELECT x.company_name FROM suppliers AS x WHERE x.company_name LIKE '%e');"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher",
                        query, 0) == "MATCH (s:suppliers) WHERE EXISTS{MATCH (x:suppliers) WHERE x.company_name ENDS WITH \"e\" } RETURN s.company_name;"


def test_mixed_select_subquery_and_exists_subquery():
    query = "SELECT Professoren.PersNr, " \
            "(SELECT v.SWS AS Lehrbelastung FROM Vorlesungen AS v WHERE " \
            "EXISTS(SELECT x.company_name FROM suppliers AS x WHERE x.company_name LIKE '%e')) " \
            "FROM Professoren;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher",
                        query, 0) == "CALL{MATCH (v:Vorlesungen) WHERE EXISTS{MATCH (x:suppliers) WHERE x.company_name ENDS WITH \"e\" } RETURN v.SWS AS Lehrbelastung}" \
                                  " WITH * MATCH (Professoren:Professoren) RETURN Professoren.PersNr, Lehrbelastung;"


def test_simple_all_subquery():
    query = "SELECT p.product_name,p.product_id " \
            "FROM products AS p " \
            "WHERE p.product_id < ALL(SELECT supp.supplier_id FROM suppliers AS supp WHERE supp.company_name LIKE 'S%') " \
            "ORDER BY p.product_id;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "CALL{MATCH (supp:suppliers) WHERE supp.company_name STARTS WITH \"S\" " \
                                            "RETURN supp.supplier_id AS sub0} WITH collect(sub0) AS coll_list " \
                                            "MATCH (p:products) WHERE ALL(var IN coll_list WHERE p.product_id < var) " \
                                            "RETURN p.product_name, p.product_id ORDER BY p.product_id;"


def test_simple_any_subquery():
    query = "SELECT prod.product_name,prod.product_id " \
            "FROM products AS prod " \
            "WHERE prod.product_name = 'test' AND prod.product_id < ANY(SELECT suppliers.supplier_id FROM suppliers WHERE suppliers.company_name LIKE 'S%') " \
            "ORDER BY prod.product_id;"

    assert validator.Validator().query_syntax_validation(query)

    assert convert_type("Cypher", query, 0) == "CALL{MATCH (suppliers:suppliers) WHERE suppliers.company_name STARTS WITH \"S\" " \
                                            "RETURN suppliers.supplier_id AS sub0} WITH collect(sub0) AS coll_list " \
                                            "MATCH (prod:products) WHERE prod.product_name = 'test' AND ANY(var IN coll_list WHERE prod.product_id < var) " \
                                            "RETURN prod.product_name, prod.product_id ORDER BY prod.product_id;"

def test_simple_missing_error():
    query = " "

    assert convert_type("Cypher", query, 0) == ""


def test_simple_function_spelling_error():
    query = "SELECT suum(p.price) FROM products p;"

    assert not validator.Validator().query_syntax_validation(query)

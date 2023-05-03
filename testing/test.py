from cypher.CypherQuery import convert


def test_simple_select():
    query = "SELECT *, p.name " \
            "FROM products as p;"

    assert convert(query) == "MATCH (p:products) " \
                                   "RETURN *, p.name;"


def test_simple_select_wildcard():
    query = "SELECT p.* " \
            "FROM products as p;"

    assert convert(query) == "MATCH (p:products) " \
                                   "RETURN p;"

def test_simple_where():
    query = "SELECT supp.SupplierName " \
            "FROM Suppliers AS supp " \
            "WHERE supp.SupplierName = 'Adidas';"

    assert convert(query) ==  "MATCH (supp:Suppliers) " \
                                    "WHERE supp.SupplierName = 'Adidas' " \
                                    "RETURN supp.SupplierName;"

def test_check_simple_join():
    query = "SELECT e.EmployeeID, count(*) AS Count " \
            "FROM Employee AS e " \
            "JOIN ord AS o ON (o.EmployeeID = e.EmployeeID);"

    assert convert(query) == "MATCH (e:Employee)-[:relationship]->(o:ord) " \
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

    assert convert(query) == "MATCH (e:Employee)-[:relationship]->(o:ord)-[:relationship]->(p:products) " \
                                   "WHERE e.EmployeeID = 100 " \
                                   "RETURN e.EmployeeID, count(*) AS Count " \
                                   "ORDER BY Count DESC " \
                                   "LIMIT 10;" \


def test_mult_joins_mixed_alias():
    query = "SELECT EmployeeID, count(*) " \
            "FROM Employee " \
            "JOIN ord ON (ord.EmployeeID = Employee.EmployeeID) " \
            "JOIN products AS p ON (p.ProductID = ord.ProductID) " \
            "WHERE EmployeeID = 100 " \
            "GROUP BY EmployeeID " \
            "ORDER BY count(*) DESC;"

    assert convert(query) == "MATCH (e:Employee)-[:relationship]->(o:ord)-[:relationship]->(p:products) " \
                                   "WHERE EmployeeID = 100 " \
                                   "RETURN EmployeeID, count(*) " \
                                   "ORDER BY count(*) DESC;"
def test_where_not_in_and_not_between():
    query = "SELECT p.ProductName, p.UnitPrice " \
            "FROM products AS p " \
            "WHERE p.ProductName NOT IN ('Chocolade','Chai') " \
            "AND p.Price NOT BETWEEN 10 AND 20;"

    assert convert(query) == "MATCH (p:products) " \
                                   "WHERE NOT p.ProductName IN ['Chocolade','Chai'] AND NOT 10 <= p.Price =< 20 " \
                                   "RETURN p.ProductName, p.UnitPrice;"


def test_where_like():
    query = "SELECT p.ProductName, p.UnitPrice " \
            "FROM products AS p " \
            "WHERE p.ProductName LIKE 'C%ool';"

    assert convert(query) == "MATCH (p:products) " \
                                   "WHERE p.ProductName STARTS WITH \"C\" AND p.ProductName ENDS WITH \"ool\" " \
                                   "RETURN p.ProductName, p.UnitPrice;"


def test_outer_join():
    query = "SELECT e.EmployeeID, count(*) AS Count " \
            "FROM Employee AS e " \
            "LEFT OUTER JOIN ord AS o ON (o.EmployeeID = e.EmployeeID) " \
            "LEFT OUTER JOIN products AS p ON (p.ProductID = o.ProductID) " \
            "WHERE e.EmployeeID = 100;"

    assert convert(query) == "MATCH (e:Employee) " \
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

    assert convert(query) == "MATCH (e:Employee) " \
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

    assert convert(query) == "MATCH (p:products) " \
                                   "WHERE 1 <= p.Price =< 15 AND p.ProductName IN ['Chocolade'] " \
                                   "RETURN p.ProductName, p.UnitPrice;"


def test_where_not():
    query = "SELECT * FROM Customers " \
            "WHERE NOT Country='Germany' AND NOT Country='USA';"

    assert convert(query) == "MATCH (c:Customers) " \
                                   "WHERE NOT Country='Germany' AND NOT Country='USA' " \
                                   "RETURN *;"


def test_insert():
    query = "INSERT INTO Customers (CustomerName, ContactName, Address, City, PostalCode, Country) " \
            "VALUES ('Cardinal', 'Tom B. Erichsen', 'Skagen 21', 'Stavanger', '4006', 'Norway');"

    assert convert(query) == "CREATE (:Customers {CustomerName: 'Cardinal', ContactName: 'Tom B. Erichsen', " \
                                   "Address: 'Skagen 21', City: 'Stavanger', PostalCode: '4006', Country: 'Norway'});"


def test_insert_without_columns():
    query = "INSERT INTO Customers " \
            "VALUES ('Cardinal', 'Tom B. Erichsen', 'Skagen 21', 'Stavanger', '4006', 'Norway');"

    assert convert(query) == "CREATE (:Customers {var0: 'Cardinal', var1: 'Tom B. Erichsen', " \
                                   "var2: 'Skagen 21', var3: 'Stavanger', var4: '4006', var5: 'Norway'});"

def test_delete_node():
    query = "DELETE FROM Customers WHERE CustomerName='Alfred';"

    assert convert(query) == "MATCH (c:Customers) WHERE c.CustomerName='Alfred' DELETE c;"

def test_delete_with_alias():
    query = "DELETE FROM Customers AS cust WHERE cust.CustomerName='Alfred';"

    assert convert(query) == "MATCH (cust:Customers) WHERE cust.CustomerName='Alfred' DELETE cust;"
def test_delete_with_many_conditions():
    query = "DELETE FROM Customers WHERE CustomerName='Alfred' AND City NOT IN ('Stuttgart') AND Service LIKE '%ool' AND CustomerID BETWEEN 1 and 100;"

    assert convert(query) == "MATCH (c:Customers) WHERE c.CustomerName='Alfred' AND NOT c.City IN ['Stuttgart'] AND c.Service ENDS WITH \"ool\" AND 1 <= c.CustomerID =< 100 DELETE c;"

def test_update_node():

    query = "UPDATE Customers " \
            "SET ContactName = 'Alfred Schmidt', City= 'Frankfurt' " \
            "WHERE CustomerID = 1;"

    assert convert(query) == "MATCH (c:Customers) WHERE c.CustomerID = 1 SET c.ContactName = 'Alfred Schmidt', c.City= 'Frankfurt';"

def test_update_with_alias():

    query = "UPDATE Customers AS cust " \
            "SET cust.ContactName = 'Alfred Schmidt', cust.City= 'Frankfurt' " \
            "WHERE cust.CustomerID = 1;"

    assert convert(query) == "MATCH (cust:Customers) WHERE cust.CustomerID = 1 SET cust.ContactName = 'Alfred Schmidt', cust.City= 'Frankfurt';"

def test_simple_having():

    query = "SELECT p.zipcode AS zip, count(*) AS population " \
             "FROM Person as p " \
             "WHERE p.EmployeeID = 100 " \
             "GROUP BY zip " \
             "HAVING population>10000;"

    assert convert(query) == "MATCH (p:Person) WITH p.zipcode AS zip, count(*) AS population WHERE p.EmployeeID = 100 AND population>10000 RETURN zip, population;"

def test_having_multiple_aggregations():

    query = "SELECT COUNT(Cust.CustomerID) AS count, SUM(Cust.price) As sum, Cust.Country AS c " \
            "FROM Customers AS Cust " \
            "GROUP BY c " \
            "HAVING count > 5 AND sum < 10 " \
            "ORDER BY count DESC;"

    assert convert(query) == "MATCH (Cust:Customers) WITH COUNT(Cust.CustomerID) AS count, SUM(Cust.price) As sum, Cust.Country AS c WHERE count > 5 AND sum < 10 RETURN count, sum, c ORDER BY count DESC;"

def test_switch_case():

    query = "SELECT od.OrderID, od.Quantity, " \
            "CASE " \
            "WHEN od.Quantity > 30 THEN 'greater 30' " \
            "WHEN od.Quantity = 30 THEN 'is 30' " \
            "ELSE 'under 30' " \
            "END AS QuantityText " \
            "FROM OrderDetails AS od;"

    assert convert(query) == "MATCH (od:OrderDetails) RETURN od.OrderID, od.Quantity, CASE WHEN od.Quantity > 30 THEN 'greater 30' WHEN od.Quantity = 30 THEN 'is 30' ELSE 'under 30' END AS QuantityText;"

def test_subquery_one_statement():

    query = "SELECT p.product_name, p.unit_price " \
              "FROM products AS p " \
              "WHERE p.unit_price > (SELECT avg(b.unit_price) FROM products AS b);"

    assert convert(query) == "CALL{MATCH (b:products) RETURN avg(b.unit_price) AS sub0} WITH * " \
                                   "MATCH (p:products) WHERE p.unit_price > sub0 RETURN p.product_name, p.unit_price;"

def test_subquery_where_nested_statements():

    query = "SELECT product_name, unit_price FROM products WHERE unit_price > (SELECT avg(unit_price) FROM products " \
           "WHERE product_name IN (SELECT product_name FROM products WHERE product_name LIKE 'T%'));"


    assert convert(query) == "CALL{CALL{MATCH (p:products) WHERE product_name STARTS WITH \"T\" RETURN product_name AS sub0} WITH * " \
                                    "MATCH (p:products) WHERE product_name IN sub0 RETURN avg(unit_price) AS sub1} WITH * " \
                                    "MATCH (p:products) WHERE unit_price > sub1 RETURN product_name, unit_price;"

def test_subquery_where_multiple_statement():

    query = "SELECT product_name, unit_price FROM products WHERE unit_price > (SELECT avg(unit_price) FROM products) " \
            "AND product_name IN (SELECT product_name FROM products WHERE product_name LIKE 'T%');"

    assert convert(query) == "CALL{MATCH (p:products) RETURN avg(unit_price) AS sub0} WITH * " \
                                   "CALL{MATCH (p:products) WHERE product_name STARTS WITH \"T\" RETURN product_name AS sub1} WITH * " \
                                   "MATCH (p:products) WHERE unit_price > sub0 AND product_name IN sub1 RETURN product_name, unit_price;"

def test_subquery_select():

    query = "SELECT name, (SELECT sum(SWS) AS Lehrbelastung FROM Vorlesungen WHERE gelesenVon=PersNr), PersNr FROM Professoren;"

    assert convert(query) == "CALL{MATCH (v:Vorlesungen) WHERE gelesenVon=PersNr RETURN sum(SWS) AS Lehrbelastung} WITH * " \
                             "MATCH (p:Professoren) RETURN name, Lehrbelastung, PersNr;"

def test_subquery_having():

    query = "SELECT p.product_name AS name,COUNT(p.unit_price) AS numb FROM products AS p GROUP BY name HAVING numb>(SELECT avg(unit_price) FROM products);"

    assert convert(query) == "CALL{MATCH (p:products) RETURN avg(unit_price) AS sub0} WITH * " \
                             "MATCH (p:products) WITH p.product_name AS name, COUNT(p.unit_price) AS numb WHERE numb>sub0 RETURN name, numb;"

def test_subquery_exists():

    query = "SELECT s.company_name " \
            "FROM suppliers AS s " \
            "WHERE EXISTS(SELECT x.company_name FROM suppliers AS x WHERE x.company_name LIKE '%e');"

    assert convert(query) == "MATCH (s:suppliers) WHERE EXISTS{MATCH (x:suppliers) WHERE x.company_name ENDS WITH \"e\" } RETURN s.company_name;"

def test_mixed_select_subquery_and_exists_subquery():

    query = "SELECT PersNr, " \
            "(SELECT SWS AS Lehrbelastung FROM Vorlesungen WHERE " \
            "EXISTS(SELECT x.company_name FROM suppliers AS x WHERE x.company_name LIKE '%e')) " \
            "FROM Professoren;"

    assert convert(query) == "CALL{MATCH (v:Vorlesungen) WHERE EXISTS{MATCH (x:suppliers) WHERE x.company_name ENDS WITH \"e\" } RETURN SWS AS Lehrbelastung}" \
                              " WITH * MATCH (p:Professoren) RETURN PersNr, Lehrbelastung;"

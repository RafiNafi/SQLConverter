from main.conversion import convert_query


def test_simple_select():
    query = "SELECT *, p.name " \
            "FROM products as p;"

    assert convert_query(query) == "MATCH (p:products) " \
                                   "RETURN *, p.name;"


def test_simple_select_wildcard():
    query = "SELECT p.* " \
            "FROM products as p;"

    assert convert_query(query) == "MATCH (p:products) " \
                                   "RETURN p;"

def test_simple_where():
    query = "SELECT supp.SupplierName " \
            "FROM Suppliers AS supp " \
            "WHERE supp.SupplierName = 'Adidas';"

    assert convert_query(query) ==  "MATCH (supp:Suppliers) " \
                                    "WHERE supp.SupplierName = 'Adidas' " \
                                    "RETURN supp.SupplierName;"

def test_check_simple_join():
    query = "SELECT e.EmployeeID, count(*) AS Count " \
            "FROM Employee AS e " \
            "JOIN ord AS o ON (o.EmployeeID = e.EmployeeID);"

    assert convert_query(query) == "MATCH (e:Employee)-[:relationship]->(o:ord) " \
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

    assert convert_query(query) == "MATCH (e:Employee)-[:relationship]->(o:ord)-[:relationship]->(p:products) " \
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

    assert convert_query(query) == "MATCH (e:Employee)-[:relationship]->(o:ord)-[:relationship]->(p:products) " \
                                   "WHERE EmployeeID = 100 " \
                                   "RETURN EmployeeID, count(*) " \
                                   "ORDER BY count(*) DESC;"
def test_where_not_in_and_not_between():
    query = "SELECT p.ProductName, p.UnitPrice " \
            "FROM products AS p " \
            "WHERE p.ProductName NOT IN ('Chocolade','Chai') " \
            "AND p.Price NOT BETWEEN 10 AND 20;"

    assert convert_query(query) == "MATCH (p:products) " \
                                   "WHERE NOT p.ProductName IN ['Chocolade','Chai'] AND NOT 10 <= p.Price =< 20 " \
                                   "RETURN p.ProductName, p.UnitPrice;"


def test_where_like():
    query = "SELECT p.ProductName, p.UnitPrice " \
            "FROM products AS p " \
            "WHERE p.ProductName LIKE 'C%ool';"

    assert convert_query(query) == "MATCH (p:products) " \
                                   "WHERE p.ProductName STARTS WITH \"C\" AND p.ProductName ENDS WITH \"ool\" " \
                                   "RETURN p.ProductName, p.UnitPrice;"


def test_outer_join():
    query = "SELECT e.EmployeeID, count(*) AS Count " \
            "FROM Employee AS e " \
            "LEFT OUTER JOIN ord AS o ON (o.EmployeeID = e.EmployeeID) " \
            "LEFT OUTER JOIN products AS p ON (p.ProductID = o.ProductID) " \
            "WHERE e.EmployeeID = 100;"

    assert convert_query(query) == "MATCH (e:Employee) " \
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

    assert convert_query(query) == "MATCH (e:Employee) " \
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

    assert convert_query(query) == "MATCH (p:products) " \
                                   "WHERE 1 <= p.Price =< 15 AND p.ProductName IN ['Chocolade'] " \
                                   "RETURN p.ProductName, p.UnitPrice;"


def test_where_not():
    query = "SELECT * FROM Customers " \
            "WHERE NOT Country='Germany' AND NOT Country='USA';"

    assert convert_query(query) == "MATCH (c:Customers) " \
                                   "WHERE NOT Country='Germany' AND NOT Country='USA' " \
                                   "RETURN *;"


def test_insert():
    query = "INSERT INTO Customers (CustomerName, ContactName, Address, City, PostalCode, Country) " \
            "VALUES ('Cardinal', 'Tom B. Erichsen', 'Skagen 21', 'Stavanger', '4006', 'Norway');"

    assert convert_query(query) == "CREATE (:Customers {CustomerName: 'Cardinal', ContactName: 'Tom B. Erichsen', " \
                                   "Address: 'Skagen 21', City: 'Stavanger', PostalCode: '4006', Country: 'Norway'});"


def test_insert_without_columns():
    query = "INSERT INTO Customers " \
            "VALUES ('Cardinal', 'Tom B. Erichsen', 'Skagen 21', 'Stavanger', '4006', 'Norway');"

    assert convert_query(query) == "CREATE (:Customers {var0: 'Cardinal', var1: 'Tom B. Erichsen', " \
                                   "var2: 'Skagen 21', var3: 'Stavanger', var4: '4006', var5: 'Norway'});"

def test_delete_node():
    query = "DELETE FROM Customers WHERE CustomerName='Alfred';"

    assert convert_query(query) == "MATCH (c:Customers) WHERE c.CustomerName='Alfred' DELETE c;"

def test_delete_with_alias():
    query = "DELETE FROM Customers AS cust WHERE cust.CustomerName='Alfred';"

    assert convert_query(query) == "MATCH (cust:Customers) WHERE cust.CustomerName='Alfred' DELETE cust;"
def test_delete_with_many_conditions():
    query = "DELETE FROM Customers WHERE CustomerName='Alfred' AND City NOT IN ('Stuttgart') AND Service LIKE '%ool' AND CustomerID BETWEEN 1 and 100;"

    assert convert_query(query) == "MATCH (c:Customers) WHERE c.CustomerName='Alfred' AND NOT c.City IN ['Stuttgart'] AND c.Service ENDS WITH \"ool\" AND 1 <= c.CustomerID =< 100 DELETE c;"

def test_update_node():

    query = "UPDATE Customers " \
            "SET ContactName = 'Alfred Schmidt', City= 'Frankfurt' " \
            "WHERE CustomerID = 1;"

    assert convert_query(query) == "MATCH (c:Customers) WHERE c.CustomerID = 1 SET c.ContactName = 'Alfred Schmidt', c.City= 'Frankfurt';"

def test_update_with_alias():

    query = "UPDATE Customers AS cust " \
            "SET cust.ContactName = 'Alfred Schmidt', cust.City= 'Frankfurt' " \
            "WHERE cust.CustomerID = 1;"

    assert convert_query(query) == "MATCH (cust:Customers) WHERE cust.CustomerID = 1 SET cust.ContactName = 'Alfred Schmidt', cust.City= 'Frankfurt';"

def test_simple_having():

    query = "SELECT p.zipcode AS zip, count(*) AS population " \
             "FROM Person as p " \
             "WHERE p.EmployeeID = 100 " \
             "GROUP BY zip " \
             "HAVING population>10000;"

    assert convert_query(query) == "MATCH (p:Person) WITH p.zipcode AS zip, count(*) AS population WHERE p.EmployeeID = 100 AND population>10000 RETURN zip, population;"

def test_having_multiple_aggregations():

    query = "SELECT COUNT(Cust.CustomerID) AS count, SUM(Cust.price) As sum, Cust.Country AS c " \
            "FROM Customers AS Cust " \
            "GROUP BY c " \
            "HAVING count > 5 AND sum < 10 " \
            "ORDER BY count DESC;"

    assert convert_query(query) == "MATCH (Cust:Customers) WITH COUNT(Cust.CustomerID) AS count, SUM(Cust.price) As sum, Cust.Country AS c WHERE  count > 5 AND sum < 10  RETURN count, sum, c ORDER BY count DESC;"
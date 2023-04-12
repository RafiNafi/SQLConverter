import pytest
from main import convert_query


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
                                      "ORDER BY Count DESC " \
                                      "LIMIT 10 " \
                                      "RETURN e.EmployeeID, count(*) AS Count;"


def test_mult_joins_mixed_alias():
    query = "SELECT EmployeeID, count(*) " \
            "FROM Employee " \
            "JOIN ord ON (ord.EmployeeID = Employee.EmployeeID) " \
            "JOIN products AS p ON (p.ProductID = ord.ProductID) " \
            "WHERE EmployeeID = 100 " \
            "GROUP BY EmployeeID " \
            "ORDER BY Count DESC;"

    assert convert_query(query) == "MATCH (:Employee)-[:relationship]->(:ord)-[:relationship]->(p:products) " \
                                      "WHERE EmployeeID = 100 " \
                                      "ORDER BY Count DESC " \
                                      "RETURN EmployeeID, count(*);"


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

    assert convert_query(query) == "MATCH (:Customers) " \
                                   "WHERE NOT Country='Germany' AND NOT Country='USA' " \
                                   "RETURN *;"
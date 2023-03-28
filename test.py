import pytest
from main import query_conversion


def test_check_simple_join():
    query = "SELECT e.EmployeeID, count(*) AS Count " \
            "FROM Employee AS e " \
            "JOIN ord AS o ON (o.EmployeeID = e.EmployeeID);"

    assert query_conversion(query) == "MATCH (e:Employee)-[:relationship]->(o:ord) " \
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

    assert query_conversion(query) == "MATCH (e:Employee)-[:relationship]->(o:ord)-[:relationship]->(p:products) " \
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

    assert query_conversion(query) == "MATCH (:Employee)-[:relationship]->(:ord)-[:relationship]->(p:products) " \
                                      "WHERE EmployeeID = 100 " \
                                      "ORDER BY Count DESC " \
                                      "RETURN EmployeeID, count(*);"

def test_where_in_and_between():

    query = "SELECT p.ProductName, p.UnitPrice " \
             "FROM products AS p " \
             "WHERE p.ProductName NOT IN ('Chocolade','Chai') " \
             "AND p.Price NOT BETWEEN 10 AND 20;"

    assert query_conversion(query) == "MATCH (p:products) " \
                                      "WHERE NOT p.ProductName IN ['Chocolade','Chai'] AND NOT p.Price BETWEEN 10 AND 20 " \
                                      "RETURN p.ProductName, p.UnitPrice;"


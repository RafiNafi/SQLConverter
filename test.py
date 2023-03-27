import pytest
from main import query_conversion

def test_check_simple_join():
    query = "SELECT e.EmployeeID, count(*) AS Count " \
            "FROM Employee AS e " \
            "JOIN ord AS o ON (o.EmployeeID = e.EmployeeID);"

    assert query_conversion(query) == "MATCH (e:Employee)-[:relationship]-(o:ord) RETURN e.EmployeeID, count(*) AS Count "
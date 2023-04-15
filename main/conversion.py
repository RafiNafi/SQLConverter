import sqlparse
from cypher.CypherQuery import CypherQuery

def convert_query(query_parts):
    queries_list = []

    # parse and print string
    parsed = sqlparse.parse(query_parts)[0]
    print(parsed.tokens)

    last_index = 0
    for idx, token in enumerate(parsed.tokens):
        if str(token) == "UNION ALL" or str(token) == "UNION":

            string_query = ""
            for t in parsed.tokens[last_index:idx]:
                string_query += str(t)

            queries_list.append(string_query)
            queries_list.append(str(token) + str(parsed.tokens[idx + 1]))
            last_index = idx + 2

        if len(parsed.tokens) == idx + 1:

            string_query = ""
            for t in parsed.tokens[last_index:idx + 1]:
                string_query += str(t)

            queries_list.append(string_query)

    print(queries_list)

    print("--------------------------------")
    # combine all queries
    combined_result_query = ""
    for single_query in queries_list:
        query_main = CypherQuery()
        result = query_main.query_conversion(single_query)
        combined_result_query += result

    # add semicolon
    combined_result_query += ";"

    return combined_result_query
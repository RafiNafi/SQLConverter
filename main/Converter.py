import cypher.CypherQuery as Cypher


def convert_type(conversion_type, query):
    match conversion_type:
        case 'Cypher':
            return Cypher.init_convert(query)

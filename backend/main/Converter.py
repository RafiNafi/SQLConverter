from backend.cypher import CypherQuery as Cypher


def convert_type(conversion_type, query, formatted=1):
    match conversion_type:
        case 'Cypher':
            return Cypher.init_convert(query, formatted)

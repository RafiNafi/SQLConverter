from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from backend.main.Converter import convert_type
import sqlfluff
import backend.validation.Validator as val

app = Flask(__name__)
api = Api(app)
cors = CORS(app)

parser = reqparse.RequestParser()
parser.add_argument('query')
parser.add_argument('language')

serious_error_codes = ["PRS", "RF01", "RF04", "AL04", "CV03", "CV07", "LT06", "RF02", "RF03", "RF05", "ST07"] # maybe skip RF03
ignore_error_codes = ["AL07", "AM01", "AM02", "LT05", "LT07", "LT09", "LT12"]

class Converter(Resource):

    def post(self):
        args = parser.parse_args()
        print(args)
        heavy_errors = False

        errors = sqlfluff.lint(args.query, "ansi", None, ignore_error_codes)
        if len(errors) > 0:
            for line in errors:
                print(line)
                if line['code'] in serious_error_codes:
                    heavy_errors = True

        if heavy_errors:
            return ["", errors]
        else:
            validator = val.Validator()
            valid = validator.query_syntax_validation(args.query)
            if not valid:
                errors.append({'line_no': 1, 'line_pos': 1, 'code': 'PRS', 'description': 'syntax error in query', 'name': 'error'})
                return ["", errors]

        return [convert_type(args.language, args.query), errors]


api.add_resource(Converter, '/convert')

if __name__ == '__main__':
    app.run(debug=True)

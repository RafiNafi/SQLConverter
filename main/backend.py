from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from main.Converter import convert_type
import sqlfluff

app = Flask(__name__)
api = Api(app)
cors = CORS(app)

parser = reqparse.RequestParser()
parser.add_argument('query')
parser.add_argument('language')


class Converter(Resource):

    def post(self):
        args = parser.parse_args()
        print(args)
        heavy_errors = False

        errors = sqlfluff.lint(args.query)
        if len(errors) > 0:
            for line in errors:
                print(line)
                if line['code'] == "PRS":
                    heavy_errors = True

        if heavy_errors:
            return ["", errors]

        return [convert_type(args.language, args.query), errors]


api.add_resource(Converter, '/convert')

if __name__ == '__main__':
    app.run(debug=True)

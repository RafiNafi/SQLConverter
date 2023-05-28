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

        errors = sqlfluff.lint(args.query)
        if len(errors) > 1:
            for line in errors:
                print(line)
            return errors

        return convert_type(args.language, args.query)


api.add_resource(Converter, '/convert')

if __name__ == '__main__':
    app.run(debug=True)

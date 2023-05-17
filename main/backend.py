from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from main.Converter import convert_type

app = Flask(__name__)
api = Api(app)
cors = CORS(app)

parser = reqparse.RequestParser()
parser.add_argument('query')


class Converter(Resource):

    def post(self):
        # print("get query")
        args = parser.parse_args()
        print(args)
        return convert_type("Cypher", args.query)


api.add_resource(Converter, '/convert')

if __name__ == '__main__':
    app.run(debug=True)

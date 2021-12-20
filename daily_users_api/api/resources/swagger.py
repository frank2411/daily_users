from flask import render_template, make_response
from flask_restful import Resource


class SwaggerView(Resource):  # pragma: no cover
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("swagger/index.html"), 200, headers)

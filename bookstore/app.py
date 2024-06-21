from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from api.routes import api_blueprint

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = '1234'  
jwt = JWTManager(app)

app.register_blueprint(api_blueprint, url_prefix='/api')

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    if username != 'test' or password != 'test':
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

if __name__ == '__main__':
    app.run(debug=True)

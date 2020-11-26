import jwt

from flask import jsonify, request
from functools import wraps
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "Authorization" in request.headers:
            # Check whether token was sent
            authorization_header = request.headers["Authorization"]

            # Check whether token is valid
            try:
                token = authorization_header.split(" ")[1]
                user = jwt.decode(token, app.config["SECRET_KEY"])
            except:
                return jsonify({"error": "you are not logged in"}), 401

            return f(userid=user["userid"], *args, **kwargs)
        else:
            return jsonify({"error": "you are not logged in"}), 401
    return wrap

from app import app
@app.route("/mp/v1_0/authorizations", methods=["POST"])
def login():
    # hashed_password = generate_password_hash('246810')
    # User(
    #     mobile='13711111111',
    #     code = hashed_password,
    #     photo = 'https://p2.ssl.qhimgs1.com/sdr/400__/t01baa117299ef7aae8.jpg',
    #     gender = 1,
    #     name = 'zhangsanfeng',
    #     intro = 'zhangsanfeng',
    #     email = '2464792390@qq.com',
    # ).save()
    if not request.json.get("mobile"):
        return jsonify({"error": "Username not specified"}), 409
    if not request.json.get("code"):
        return jsonify({"error": "Password not specified"}), 409

    try:
        mobile = request.json.get("mobile")
        print(mobile)
        users = User.objects(mobile=mobile)
    except:
        print('error')

    user = users.first()

    if user == None:
        return jsonify({"error": "User not found"}), 403



    if not check_password_hash(user.code, request.json.get("code")):
        return jsonify({"error": "Invalid password"}), 401

    token = jwt.encode({
        "name": user.name,
        "email": user.email,
        "code": user.code,
        "created": str(user.created)
    }, app.config["SECRET_KEY"])

    return jsonify({
        # "success": True,
        "message": 'OK',
        "data": {
            "user": user.name,
            "token": token.decode("UTF-8"), # token.decode("UTF-8")
            # "email": user.email,
            # "password": user.password,
            # "created": str(user.created)
        },
    })
@app.route('/mp/v1_0/user/profile',methods=['GET'])
@login_required
def get_user_profile(userid):
    user = User.objects(id=userid).first()
    return jsonify({
        "message": 'OK',
        "data": user.to_public_json()
    })




import jwt

from flask import jsonify, request
from functools import wraps
from models import User
from werkzeug.security import generate_password_hash, check_password_hash


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
def get_user_profile():
    user = User.objects(name='zhangsanfeng').first()
    return jsonify({
        "message": 'OK',
        "data": user.to_public_json()
    })




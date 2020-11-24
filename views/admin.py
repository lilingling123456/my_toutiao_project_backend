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
    #     photo = 'https://image.so.com/view?q=%E5%8F%AE%E5%BD%93%E7%8C%AB%E5%9B%BE%E7%89%87&listsrc=sobox&listsign=26fc7d8ebfd21d493a300af9a7a1ea17&src=360pic_strong&correct=%E5%8F%AE%E5%BD%93%E7%8C%AB%E5%9B%BE%E7%89%87&ancestor=list&cmsid=abe9f60fb0e83117f8c7dfa3b8db68b8&cmras=6&cn=0&gn=0&kn=50&crn=0&bxn=20&fsn=130&cuben=0&pornn=0&manun=0&adstar=0&clw=233#id=fa72ec92e710b9f388321c0cf16573a8&currsn=0&ps=93&pc=93',
    #     gender = 1,
    #     name = 'zhangsanfeng',
    #     intro = 'zhangsanfeng',
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

    # token = jwt.encode({
    #     "userid": str(user.id),
    #     "username": user.username,
    #     "email": user.email,
    #     "password": user.password,
    #     "created": str(user.created)
    # }, app.config["SECRET_KEY"])

    return jsonify({
        # "success": True,
        "message": 'OK',
        "data": {
            "user": user.name,
            "token": 'xxxxxx', # token.decode("UTF-8")
            # "email": user.email,
            # "password": user.password,
            # "created": str(user.created)
        },
    })





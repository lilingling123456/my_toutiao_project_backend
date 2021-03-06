import os
import uuid

import jwt

from flask import jsonify, request, send_from_directory
from functools import wraps

from mongoengine import Q

import config
from models import User, Channel, Img
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
        "userid":str(user.id),
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
@app.route('/mp/v1_0/channels',methods=['GET'])
@login_required
def get_channels(userid):
    # channel1 = Channel(
    #     name='python'
    # )
    # channel1.save()
    # channel2 = Channel(
    #     name='java'
    # )
    # channel2.save()
    # channel3 = Channel(
    #     name='mysql'
    # )
    # channel3.save()
    channels = Channel.objects
    return  jsonify({
        "message": 'OK',
        "data": {
            "channels": channels.to_public_json()
        }
    })
@app.route('/mp/v1_0/user/images',methods=['POST'])
@login_required
def upload(userid):
    user = User.objects(id=userid).first()
    image = request.files.get("image")
    if image:
        if not image.filename.endswith(tuple([".jpg", ".png"])):
            return jsonify({"error": "Image is not valid"}), 409

        # Generate random filename
        filename = str(uuid.uuid4()).replace("-", "") + "." + image.filename.split(".")[-1]

        if not os.path.isdir(config.image_upload_folder):
            os.makedirs(config.image_upload_folder)

        image.save(os.path.join(config.image_upload_folder, filename))
        img = Img(
            url=filename,
            user=user
        ).save()
    else:
        filename = None

    return jsonify({
        "message": 'OK',
        "data": img.to_public_json()
    })

@app.route("/file/<string:filename>")
def images_rsp(filename):
    return send_from_directory(config.image_upload_folder, filename)
@app.route("/mp/v1_0/user/images")
@login_required
def get_images(userid):
    user = User.objects(id=userid).first()
    collect = request.args.get("collect")
    if collect == 'true':
        imgs = Img.objects(Q(user=user) & Q(is_collected=True))# 多条件查询
    elif collect == 'false':
        imgs = Img.objects(user=user)

    page = int(request.args.get("page"))
    per_page = int(request.args.get("per_page"))

    paginated_imgs = imgs.skip((page - 1) * per_page).limit(per_page)

    return jsonify({
        "message": 'OK',
        "data": {
            "total_count": imgs.count(),
            "page": page,
            "per_page": per_page,
            "results": paginated_imgs.to_public_json()
        }
    })
@app.route("/mp/v1_0/user/images/<string:imageId>",methods=['PUT','DELETE'])
@login_required
def collectImage(userid, imageId):
    if request.method == 'PUT':
        img= Img.objects(id=imageId).first()
        img.is_collected = request.json.get('collect')
        img.save()
        return jsonify({
            "message": 'OK',
            "data": {
                "id": str(img.id),
                "collect": img.is_collected
            }
        })
    elif request.method == 'DELETE':
        img = Img.objects(id=imageId).first()
        img.delete()

        return jsonify({
            "message": 'OK',
            "data": {
                "id": str(img.id),
                "collect": img.is_collected
            }
        })
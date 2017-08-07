# _*_ coding:utf-8 _*_

from nowstagram import app, db, mail
from flask import render_template, redirect, request, flash, get_flashed_messages, send_from_directory
from nowstagram.models import User, Image, Comment
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from qiniusdk import qiniu_upload_file
import random, hashlib, json, os, uuid, re




@app.route('/')
def index():
    images = Image.query.order_by('id desc').paginate(page=1, per_page=5, error_out=True)
    return render_template('index.html', images=images.items, has_next=images.has_next)

@app.route('/index/images/<int:page>/<int:per_page>/')
def index_images(page, per_page):
    paginate = Image.query.order_by('id desc').paginate(page=page, per_page=per_page)
    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id': image.id, 'url': image.url, 'comment_count': len(image.comment)}
        map.append(imgvo)
    map['images'] = images
    return json.dumps(map)

@app.route('/image/<int:image_id>')
@login_required
def image(image_id):
    image = Image.query.get(image_id)
    if image == None:
        return redirect('/')
    return render_template('pageDetail.html', image=image)

@app.route('/profile/<int:user_id>')
@login_required   # 这句修饰一定要在app_route()下面，否则不能生效
def profile(user_id):
    user = User.query.get(user_id)
    if user == None:
        return redirect('/')
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=1, per_page=3, error_out=False)
    return render_template('profile.html', user=user, images=paginate.items, has_next=paginate.has_next)

# 通过ajax请求加载图片
@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id, page, per_page):
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page)
    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id': image.id, 'url': image.url, 'comment_count': len(image.comment)}
        images.append(imgvo)

    map['images'] = images
    return json.dumps(map)

# --------------------------------------------------登陆/注册/登出------------------------------------------

@app.route('/regloginpage/')
def regloginpage():
    msg = ''
    for m in get_flashed_messages(with_categories=False, category_filter=['reglog']):
        msg = msg + m
    return render_template('login.html', msg=msg, next=request.values.get('next'))

# 利用flash传递消息
def redirect_with_message(target, msg, category):
    if msg != None:
        flash(msg, category=category)
    return redirect(target)

# 验证邮箱格式
def check_mail(mail):
    rule = re.compile(r'^[a-zA-Z0-9]+[a-zA-Z0-9_].*@([A-Za-z\d]+[-.])+[A-Za-z\d]{2,4}$ ')
    if rule.match(mail) != None:
        return True
    return False

@app.route('/login/', methods={'post', 'get'})
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username == '' or password == '':
        return redirect_with_message('/regloginpage/', u'用户名或密码不能为空', 'reglog')

    user = User.query.filter_by(username=username).first()
    if user == None:
        return redirect_with_message('/regloginpage/', u'用户名不存在', 'reglog')

    m = hashlib.md5()
    m.update((password+user.salt).encode('utf-8'))
    if (m.hexdigest() != user.password):
        return redirect_with_message('/regloginpage/', u'密码错误', 'reglog')

    login_user(user)  # 验证通过之后将用户添加到已登录

    next = request.values.get('next')
    if next != None and next.startswith('/'):
        return redirect(next)

    return redirect('/')

@app.route('/reg/', methods={'post', 'get'})
def reg():
    # request.args
    # request.form
    # reuqest.values中包含了所有的参数，用strip()去掉空格
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    # mail = request.values.get('mail').strip()
    #
    # if check_mail(mail) == False:
    #     return redirect_with_message('/regloginpage/', u'邮箱格式不正确', 'reglog')

    if username == '' or password == '':
        return redirect_with_message('/regloginpage/', u'用户名或密码不能为空', 'reglog')

    user = User.query.filter_by(username=username).first()
    if user != None:
        # flash(u'用户名已经存在', category='reglogin')
        # return redirect('/regloginpage')
         return redirect_with_message('/regloginpage/', u'用户名已经存在', 'reglog')

    salt = '.'.join(random.sample('asdfqweryuioplkjhnmzxcv124567890SDVGHFC', 10))
    m = hashlib.md5()
    m.update((password + salt).encode('utf-8'))
    password = m.hexdigest()
    user = User(username, password, salt)
    db.session.add(user)
    db.session.commit()

    login_user(user)

    next = request.values.get('next')
    if next != None and next.startswith('/'):
        return redirect(next)

    return redirect('/')

@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')

# -------------------------------------------添加评论----------------------------------

@app.route('/recomment/')
def recomment():
    msg = ''
    for m in get_flashed_messages(with_categories=False, category_filter=['recomment']):
        msg = msg + m
    return render_template('pageDetail.html', msg=msg)

@app.route('/addcomment/<int:image_id>/<int:user_id>/')
# @login_required
def add_comment(image_id, user_id):
    comment_content = request.values.get('comments')
    print(comment_content)
    # if comment_content == '':
    #     return redirect_with_message('/recomment/%s' % current_user.id, u'评论不能为空', 'recomment')

    comment = Comment(comment_content, image_id, user_id)
    db.session.add(comment)
    db.session.commit()


    return redirect('/image/%s' % str(image_id))


# -------------------------------------------图片上传----------------------------------

def save_to_local(file, file_name):
    save_dir = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir, file_name))
    return '/image/' + file_name

@app.route('/image/<image_name>')
def show_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'], image_name)

@app.route('/upload', methods={'post'})
def upload():
    # request.files得到一个字典，保存了所有的请求参数
    file = request.files['file']
    if file.filename.find('.') > 0:
        file_ext = file.filename.rsplit('.', 1)[1].strip().lower()
    if file_ext in app.config['ALLOWED_EXT']:
        file_name = str(uuid.uuid1()).replace('-', '') + '.' + file_ext
        # url = save_to_local(file, file_name)   # 保存到本地
        url = qiniu_upload_file(file, file_name)   # 保存到云端
        if url != None:
            db.session.add(Image(url, current_user.id))
            db.session.commit()

    return redirect('/profile/%d' % current_user.id)



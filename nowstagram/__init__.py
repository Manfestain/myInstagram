# _*_ encoding:utf-8 _*_

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../nowstagram.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config.from_pyfile('app.conf')   # 读取数据库配置文件
app.jinja_env.add_extension('jinja2.ext.loopcontrols')   # jinja2必须引入扩展，否则break不可用
app.secret_key = 'nowcoder'
db = SQLAlchemy(app)
login_manager = LoginManager(app)   # 登陆时可直接记录用户信息
login_manager.login_view = '/regloginpage/'  # 当用户未登陆时访问权限页面就会跳转至'/regloginpage'

app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.163.com',
    MAIL_PROT=25,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='lovebeans007@163.com',
    MAIL_PASSWORD='surface129',
    MAIL_DEBUG=True
)

mail = Mail(app)



from nowstagram import views, models
# _*_ encoding:utf-8 _*_

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../nowstagram.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config.from_pyfile('app.conf')   # 读取数据库配置文件
app.jinja_env.add_extension('jinja2.ext.loopcontrols')   # jinja2必须引入扩展，否则break不可用
db = SQLAlchemy(app)

from nowstagram import views, models
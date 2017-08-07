# _*_ coding:utf-8　_*_

from nowstagram import app, db
from flask_script import Manager
from nowstagram.models import User, Image, Comment
import random

manager = Manager(app)

def get_image_url():
    return 'http://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 'm.png'

@manager.command
def init_database():


    for i in range(0, 10):   # 添加用户
        db.session.add(User('user' + str(i), 'a' + str(i)))
        for j in range(0, 3):
            db.session.add(Image(get_image_url(), i + 1))
            for k in range(0, 3):
                db.session.add(Comment('This is a comment' + str(k), 1+3*i+j, j+1))
    db.session.commit()

    for i in range(5, 10):
        user = User.query.get(i)
        user.username = '[new]' + user.username
    db.session.commit()

    print(1, User.query.all())
    print(2, User.query.get(4))

    image = Image.query.get(26)
    image.url = 'https://ss3.bdstatic.com/70cFv8Sh_Q1YnxGkpoWK1HF6hhy/it/u=1268348955,3754655044&fm=26&gp=0.jpg'
    db.session.commit()

    for i in range(0, 10):
        image = Image(get_image_url(), 10)
        db.session.add(image)
        db.session.commit()

    xx_url = 'https://ss3.bdstatic.com/70cFv8Sh_Q1YnxGkpoWK1HF6hhy/it/u=1268348955,3754655044&fm=26&gp=0.jpg'
    xx_image = Image(xx_url, 11)
    db.session.add(xx_image)
    db.session.commit()






if __name__ == '__main__':
    manager.run()

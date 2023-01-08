import os
from threading import Thread
from flask import (
    Flask, redirect,
    render_template, request
)
from flask_mail import (Mail, Message )

def create_app(test_config=None):
    mail = Mail()
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['MAIL_SERVER']= os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail.init_app(app)
    app.config.from_mapping(
        SECRET_KEY= os.getenv('SECRET_KEY'),
        DATABASE=os.path.join(app.instance_path, 'moyodfa.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    def send_async_email(app, msg):
        with app.app_context():
            try:
                mail.send(msg)

            except Exception as e:
                print(str(e))

    @app.route('/', methods=('GET', 'POST'))
    def index():
        return render_template('index.html')

    @app.route('/send_email', methods=('GET', 'POST'))
    def send_email():

        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            subject = request.form['subject']
            content = request.form['message']
            message = 'My name is ' + name + ' and email is ' + email + '\n' +  content
            recipient = os.getenv('MAIL_RECIPIENTS').split(",")

            if name is not None and email is not None and subject is not None and content is not None:
                msg = Message(subject, sender=email, recipients=recipient)
                msg.body=message
                thr = Thread(target=send_async_email, args=[app, msg])
                thr.start()
                return redirect(request.host_url + '#footer')

        return render_template('index.html')

    return app
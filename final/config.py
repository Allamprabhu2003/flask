import os

# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'dshjkdshfkldjklfkj'
#     # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://root:1234@localhost/abd'
#     SQLALCHEMY_DATABASE_URI = 'mysql://root:1234@localhost/abd'
#     MAIL_SERVER = 'smtp.googlemail.com'
#     MAIL_PORT = 587
#     MAIL_USE_TLS = True
#     MAIL_USERNAME = os.environ.get('allamprabhuhiremath9@outlook.conm')  # your email address
#     # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # your email password
#     MAIL_PASSWORD = '6363@colab!' # your email password
#     MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')  # your default sender email


class Config:
    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'dshjkdshfkldjklfkj'
    SECRET_KEY = 'dshjkdshfkldjklfkj'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:1234@localhost/abd'
    MAIL_SERVER =  "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USERNAME = "allamprabhuhiremath2003@gmail.com"  # your email address
    # MAIL_USERNAME = os.environ.get('allamprabhuhiremath9@outlook.conm')  # your email address
    MAIL_PASSWORD =  "mfqa ufqt ziah qjfp" # your email password
    # MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_DEFAULT_SENDER = "allamprabhuhiremath2003@gmail.com"
    WTF_CSRF_ENABLED = True



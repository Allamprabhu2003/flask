import os


class Config:
    SECRET_KEY = 'dshjkdshfkldjklfkj'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:1234@localhost/abd'
    MAIL_SERVER =  "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "allamprabhuhiremath2003@gmail.com"  # your email address
    MAIL_PASSWORD =  "mfqa ufqt ziah qjfp" # your email password
    MAIL_DEFAULT_SENDER = "allamprabhuhiremath2003@gmail.com"
    WTF_CSRF_ENABLED = True



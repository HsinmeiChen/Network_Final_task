# users.py
from datetime import datetime
from ..db_connection import Base, session_scope
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Unicode
import os, hashlib, string, random

class User(Base):
    __tablename__ = 'USERS'
    
    USERID = Column(String(50), primary_key=True)
    USERNAME = Column(Unicode(20), nullable=False)
    EMAIL = Column(String(255), nullable=False)
    PASSWORD_HASH = Column(String(64), nullable=False)
    SALT = Column(String(32), nullable=False)
    ROLE = Column(String(20), nullable=False)
    IS_ACTIVE = Column(Boolean, default=True)
    FAILED_ATTEMPTS = Column(Integer, default=0)
    LAST_LOGIN = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User(USERID={self.USERID}, USERNAME={self.USERNAME}, EMAIL={self.EMAIL})>"

    @staticmethod
    def generate_salt():
        return os.urandom(16).hex()

    @staticmethod
    def hash_password(password, salt):
        return hashlib.sha256((password + salt).encode()).hexdigest()

    @staticmethod
    def generate_random_password(length=10):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=length))

    @classmethod
    def create_user(cls, userid, username, email, password, role='user'):
        salt = cls.generate_salt()
        password_hash = cls.hash_password(password, salt)
        user = cls(
            USERID=userid,
            USERNAME=username,
            EMAIL=email,
            PASSWORD_HASH=password_hash,
            SALT=salt,
            ROLE=role
        )
        with session_scope() as session:
            session.add(user)
        print(f"User {username} added successfully.")
        return user

    @classmethod
    def delete_user(cls, userid):
        with session_scope() as session:
            user = session.query(cls).filter_by(USERID=userid).first()
            if user:
                session.delete(user)
                print(f"User with ID {userid} deleted successfully.")
            else:
                print(f"User with ID {userid} does not exist.")

    @classmethod
    def update_user(cls, userid, username=None, email=None, password=None, role=None):
        with session_scope() as session:
            user = session.query(cls).filter_by(USERID=userid).first()
            if not user:
                print("User not found.")
                return None

            if username:
                user.USERNAME = username
            if email:
                user.EMAIL = email
            if password:
                new_salt = cls.generate_salt()
                user.PASSWORD_HASH = cls.hash_password(password, new_salt)
                user.SALT = new_salt
            if role:
                user.ROLE = role

            print(f"User with ID {userid} updated successfully.")
            return user

    @classmethod
    def verify_login(cls, userid, password):
        with session_scope() as session:
            user = session.query(cls).filter_by(USERID=userid).first()
            if not user:
                return False, None
            if not user.IS_ACTIVE:
                return False, user
            
            input_password_hash = cls.hash_password(password, user.SALT)
            if user.PASSWORD_HASH == input_password_hash:
                user.FAILED_ATTEMPTS = 0
                user.LAST_LOGIN = datetime.now()
                print("Login successful.")
                user_data = {
                    'USERID': user.USERID,
                    'LAST_LOGIN': user.LAST_LOGIN,
                    'FAILED_ATTEMPTS': user.FAILED_ATTEMPTS,
                    # 其他需要的欄位...
                }
                return True, user.USERNAME
            else:
                user.FAILED_ATTEMPTS += 1
                print("Login failed.")
                return False, user

    @classmethod
    def deactivate_user(cls, userid):
        with session_scope() as session:
            user = session.query(cls).filter_by(USERID=userid).first()
            if user:
                user.IS_ACTIVE = False
                print(f"User with ID {userid} has been deactivated.")
            else:
                print(f"User with ID {userid} does not exist.")

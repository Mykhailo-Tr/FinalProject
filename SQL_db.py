import sqlite3
import config


class DataBase:
    obj = None
    

    def __init__(self, db_filename: str):
        self.filename = db_filename
        self.connect = sqlite3.connect(db_filename, check_same_thread=False)
        self.cursor = self.connect.cursor()
        
    # def __new__(cls, *args, **kwargs):
    #     if cls.obj is None:
    #         cls.obj = super().__new__(cls, cls.filename , *args, **kwargs)
    #     return cls.obj
        
    def add_user(self, username: str, email: str, password: str) -> None:
        with self.connect:
            user = self.cursor.execute("SELECT 1 FROM users WHERE username == '{key}'".format(key=username)).fetchone()
            if not user:
                role = "admin" if username in config.ADMINS_USERNAMES else "user"
                
                self.cursor.execute("""INSERT INTO users (username, email, password, role) VALUES(?, ?, ?, ?)""",
                                    (username, email, password, role))

                self.connect.commit()
                
    def get_user(self, user_id: int):
        with self.connect:
            return self.cursor.execute("""SELECT * FROM users WHERE user_id=(?)""", [user_id]).fetchall()
        
    def get_users(self):
        with self.connect:
            return self.cursor.execute("""SELECT * FROM users ORDER BY role DESC, username ASC""").fetchall()
        
    def get_user_id(self, username: str):
        with self.connect:
            return self.cursor.execute('''SELECT id FROM users WHERE username=(?)''', [username]).fetchone()
        
    def delete_user(self, user_id: int):
        with self.connect as conn:
            self.cursor.execute('DELETE FROM users WHERE id=(?)', [user_id])
            conn.commit()
            
            
    def get_email(self, username: str):
        with self.connect as conn:
            return self.cursor.execute('''SELECT email FROM users WHERE username=(?)''', [username]).fetchone()

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


    def get_news(self):
        """Get all news from database."""
        with self.connect:
            return self.cursor.execute('''SELECT * FROM news''').fetchall()
        
    def add_news(self, title: str, content: str, img_path: str):
        """Add a new news to the database."""
        with self.connect as connect:
            query = '''INSERT INTO news (title, content, img_path) VALUES(?, ?, ?)'''
            self.cursor.execute(query, (title, content, img_path))
            connect.commit()
                   
    def get_news_post(self, post_id: int):
        """Get a news post by its ID."""
        with self.connect:
            return self.cursor.execute('''SELECT * FROM news WHERE id=?''', [post_id]).fetchone()
          
    def update_news(self, post_id: int, title: str, content: str):
        """Update an existing news post in the database."""
        with self.connect as connect:
            query = '''UPDATE news SET title = ?, content = ? WHERE id = ?'''
            self.cursor.execute(query, [title, content, post_id])
            connect.commit()
            
    def delete_news_post(self, post_id: int):
        """Delete a news post from the database."""
        with self.connect as connect:
            self.cursor.execute('DELETE FROM news WHERE id = ?', (post_id,))
            connect.commit()
    
    
    def get_olympiads(self):
        """Get all olympiads from database."""
        with self.connect:
            return self.cursor.execute('''SELECT * from olympiads''').fetchall()
        
    def get_olympiad_post(self, post_id: int):
        """Get data about one specific olympiad."""
        with self.connect:
            return self.cursor.execute('''SELECT * FROM olympiads WHERE id=?''', [post_id]).fetchone()
        
    def add_olympiad(self, content: str, img_path: str):
        """Add a new olympiad to the database."""
        with self.connect as connect:
            query = '''INSERT INTO olympiads (content, img_path) VALUES(?, ?)'''
            self.cursor.execute(query, (content, img_path))
            connect.commit()
            
    def update_olympiad(self, post_id: int, content: str):
        """Update an existing olympiads post in the database."""
        with self.connect as connect:
            query = '''UPDATE olympiads SET content = ? WHERE id = ?'''
            self.cursor.execute(query, [content, post_id])
            connect.commit()
            
    def delete_olympiad_post(self, post_id: int):
        """Delete a news post from the database."""
        with self.connect as connect:
            self.cursor.execute('DELETE FROM olympiads WHERE id = ?', (post_id,))
            connect.commit()
    
    
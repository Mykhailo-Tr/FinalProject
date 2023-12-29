import sqlite3
import config


class DataBase:
    _instance = None
    
    def __new__(cls, db_filename: str):
        if cls._instance is None:
            cls._instance = super(DataBase, cls).__new__(cls)
        return cls._instance
    
    
    def __init__(self, db_filename: str):
        self.filename = db_filename
        self.connect = sqlite3.connect(db_filename, check_same_thread=False)
        self.cursor = self.connect.cursor()
        
    
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
            
            
            
if __name__ == '__main__':
    o1 = DataBase('database.db')
    o2 = DataBase('database.db')
    print(o1 is o2)

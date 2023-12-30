import json


class JsonDatabase:
    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.data = self.load_data()

    def load_data(self):
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_data(self):
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def get_all(self):
        return self.data

    def get_title(self, page_name: str, default="Site Page") -> str:
        return self.data.get(page_name, default)

    def add_title(self, page_name: str, title: str):
        self.data[page_name] = title
        self.save_data()

    def update_title(self, page_name: str, title: str) -> bool:
        if self.data.get(page_name):
            self.data[page_name] = title
            self.save_data()
            return True
        return False

    def delete_title(self, page_name) -> bool:
        if page_name in self.data:
            del self.data[page_name]
            self.save_data()
            return True
        return False



if __name__ == '__main__':
    db = JsonDatabase('titles.json')
    print(db.get_all())
    print((db.get_title("index")))

    db.add_title("hello", "Hello PAge")
    print(db.get_all())
    print((db.get_title("hello")))

    a = db.update_title("hello", "Hello Page V0.2")
    print(a)
    print(db.get_all())
    print((db.get_title("hello")))

    b = db.delete_title("helo")
    print(b)
    print(db.get_all())
    print((db.get_title("hello")))

    a = db.update_title("nopage", "TEXTTEXTTEXT")
    print(a)
    print(db.get_all())
    print((db.get_title("nopage")))

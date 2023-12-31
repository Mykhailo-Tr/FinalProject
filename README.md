<h1 align="center">
  School Site
  <br>
</h1>

<h4 align="center">A school website with the possibility of editing and a registration system build on <a href="https://pypi.org/project/Flask" target="_blank">Flask</a>.</h4>
[![Licence](https://img.shields.io/github/license/Ileriayo/markdown-badges?style=for-the-badge)](./LICENSE)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Jinja](https://img.shields.io/badge/jinja-white.svg?style=for-the-badge&logo=jinja&logoColor=black)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#license">License</a>
</p>


## I utilize: 
- `flask` as the web framework.
- `jinja` templates the site and makes it dynamic.
- `SQLite` for our database.
- `flask-sqlalchemy` as our ORM.
- `bootstrap` makes site beautiful.
- `json` for simplify site editing.
- `regex` for validation.
- `logging` makes it easier to track changes and errors



## Key Features

* EaseEdit - Intuitive site editing interface
* DataBase - All data is stored in a database protected from sql injection
* PrettyLogs - Logs are stored in several files to simplify analysis
* No errors - all program errors are tracked
* Less code - all html pages are templated
* Responsive design - the interface is correctly displayed on any devices


## How To Use

To clone and run this application, you'll need [Git](https://git-scm.com) and [Python](https://www.python.org/) (which comes with [pip](https://pypi.org/project/pip/)) installed on your computer. From your command line:

```bash
# Clone this repository
$ git clone https://github.com/Mykhailo-Tr/FinalProject.git

# Go into the repository
$ cd FinalProject

# Install dependencies
$ pip3 install -r requirements.txt 
```

> **Set up your config file**
> 
> Create config.py
```
UPLOAD_FOLDER = '/static/img' # or your path for images
ALLOWED_EXTENSIONS = {'png'} # you can add others
DATABASE_FILE = '<database file>'
SQLALCHEMY_DATABASE = 'sqlite:///<database file>'
JSON_FILE = '<json file>'
SECRET_KEY = '<your secret key for flask app>'

```

```bash
# Run the main.py
$ python3 main.py
```

## Support

<a href="https://www.buymeacoffee.com/mykhailo_tr" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/purple_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>



## License

MIT

---



from  flask  import Flask

app= Flask(__name__)

@app.route('/')
def home():
    return "Hello  from flask"

@app.route('/about')
def about():
    return "This  is flask app"

@app.route('/hello/<name>')
def hello(name):
    return f"hello myself {name} !"

if __name__ == '__main__':
    app.run(debug=True)
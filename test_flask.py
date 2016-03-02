from flask import Flask
from flask import request
import webbrowser

app = Flask(__name__)

@app.route('/find_article', methods=['POST'])
def hello():
    print(request.form.get('text'))
    webbrowser.open("https://google.com",new=2)
    return "hello world"

if __name__ == "__main__":
    app.run(debug=True)

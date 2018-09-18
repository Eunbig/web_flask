from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    req = requests.get('https://movie.naver.com/movie/sdb/rank/rmovie.nhn')
    soup = BeautifulSoup(req.text, 'html.parser')
    res = []
    for i in soup.find_all('td','title'):
        res.append(i.text.replace('\n',''))
    return render_template('index.html', data=res)

if __name__ == '__main__':
    app.run(debug=True , port=8989, host='0.0.0.0')


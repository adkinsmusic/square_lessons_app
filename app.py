from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "🎵 Square Lessons Automation App is Running!"

if __name__ == '__main__':
    app.run(debug=True)

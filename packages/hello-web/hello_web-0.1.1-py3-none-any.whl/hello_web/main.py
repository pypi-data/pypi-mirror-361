import flask

app = flask.Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"

def main():
    """Entry point for the hello-web command."""
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()
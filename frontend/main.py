# Importing necessary libraries
from flask import Flask, render_template

# Creating flask app
app  = Flask(__name__, static_url_path='/static')

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Main function
if __name__ == '__main__':
    app.run(debug=True, port=8000)
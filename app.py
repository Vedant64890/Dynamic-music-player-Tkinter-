from neww import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Basic HTML template with some styling
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f0f0f0;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 { color: #333; }
        .nav { margin-bottom: 20px; }
        .nav a {
            color: #0066cc;
            text-decoration: none;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/about">About</a>
            <a href="/hello/Guest">Hello</a>
        </div>
        <h1>{{ title }}</h1>
        <p>{{ content }}</p>
        {% if form %}
        <form method="post" action="/submit">
            <input type="text" name="name" placeholder="Enter your name">
            <button type="submit">Submit</button>
        </form>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(
        HOME_TEMPLATE,
        title="Welcome to Flask",
        content="This is a basic Flask application.",
        form=True
    )

@app.route('/about')
def about():
    return render_template_string(
        HOME_TEMPLATE,
        title="About",
        content="This is a demo Flask application.",
        form=False
    )

@app.route('/hello/<name>')
def hello(name):
    return render_template_string(
        HOME_TEMPLATE,
        title=f"Hello, {name}!",
        content="Welcome to our Flask application.",
        form=False
    )

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name', 'Guest')
    return redirect(url_for('hello', name=name))

if __name__ == '__main__':
    app.run(debug=True)
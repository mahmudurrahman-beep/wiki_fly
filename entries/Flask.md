# Flask

**Flask** is a lightweight, open-source **Python web framework** designed for building web applications quickly and with flexibility. It is classified as a **microframework** because it does not require particular tools or libraries, giving developers freedom to choose components.

## History
- Created by **Armin Ronacher** in **2010** as part of the **Pocoo** project.  
- Initially developed as a wrapper around the Werkzeug toolkit and Jinja2 template engine.  
- Gained popularity for its simplicity and extensibility.  

## Key Features
- **Minimalistic design:** Core is simple, with optional extensions for added functionality.  
- **Routing system:** Maps URLs to Python functions.  
- **Template engine:** Uses **Jinja2** for rendering HTML with dynamic content.  
- **Built-in development server and debugger.**  
- **Extensible:** Supports plugins for databases, authentication, and more.  
- **RESTful request handling:** Ideal for APIs and microservices.  
- **WSGI compliant:** Works with any WSGI server.  

## Example
```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True)
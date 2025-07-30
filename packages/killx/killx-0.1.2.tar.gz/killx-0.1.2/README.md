# ⚡ Killx Framework 🔥  
A **lightning-fast**, **modern**, and **zero-dependency** Python web framework that's **easier than Flask** and built for speed & fun 🏎️💨

---

## ✨ Features
✅ URL parameters support (`/user/<id>`)  
✅ JSON response helper  
✅ Form data parsing (POST + JSON + Query)  
✅ CORS enabled by default 🛡️  
✅ Built-in minimalist template engine 🧠  
✅ Static file serving (`/static`)  
✅ Auto-reload (Realtime™) 🔁  
✅ Debug mode logging 🐞  
✅ **No dependencies!** (Pure Python Standard Library) 🐍
✅ **You can support me on Github (github.com/Pavitroo)**

---

## 🚀 What's New in `v0.1.2`?

### 🐛 Bug Fixes
- 🧹 Fixed issue where pressing `Ctrl+C` wouldn’t gracefully kill the server.

### 🆕 New Features
- 🐞 **Debug Mode**: See what Killx is doing step-by-step with `.log()`.
- 🔁 **RealTime™ Reloading**: Automatically restart the server when files change!

```python
from killx import Killx

# Enable debug logging + auto-reload
app = Killx(Debug=True, RealTime=True) # Depend on You if you want it enable so do True and if not Do False. Done Simple.

# Root route using template
@app.route("/", methods=["GET"])
def homepage(request):
    app.log("Rendering homepage with template")
    return app.render_template("index.html", message="Welcome to Killx! 🚀")

# JSON API route with path and query params
@app.route("/api/user/<id>", methods=["GET"])
def get_user(request):
    user_id = request["url_params"]["id"]
    name = request["query_params"].get("name", ["Unknown"])[0]
    app.log(f"Fetching user: {user_id} with name: {name}")
    return app.json({"id": user_id, "name": name})

# POST route to receive form data
@app.route("/submit", methods=["POST"])
def submit(request):
    form = request["form_data"]
    app.log(f"Received form: {form}")
    return app.json({
        "status": "received",
        "form": form
    })

# Static file test (optional)
@app.route("/static-test", methods=["GET"])
def static_test(request):
    return """
    <html>
      <head><link rel="stylesheet" href="/static/style.css"></head>
      <body><h1>Static File Test</h1><script src="/static/script.js"></script></body>
    </html>
    """

if __name__ == "__main__":
    app.run(port=8080)

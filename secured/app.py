from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

USERS = {
    "alice": {"password": "password123", "role": "user", "email": "alice@lab.local"},
    "admin": {"password": "adminsecret", "role": "admin", "email": "admin@lab.local"}
}

ALLOWED_FIELDS = {"email"}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Lab: Secured App (Port 5001)</title>
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --muted: #94a3b8;
      --success: #10b981;
      --success-hover: #059669;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background-color: var(--bg); color: var(--text); padding: 2rem 1rem; display: flex; justify-content: center; }
    .container { width: 100%; max-width: 800px; display: flex; flex-direction: column; gap: 1.5rem; }
    .badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; background: rgba(16, 185, 129, 0.2); color: var(--success); border: 1px solid var(--success); }
    .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 0.75rem; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); }
    h1 { font-size: 1.5rem; font-weight: 700; margin-top: 0.5rem; }
    p { color: var(--muted); font-size: 0.875rem; margin-top: 0.25rem; }
    .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem; }
    .status-item { background: rgba(15, 23, 42, 0.6); padding: 0.75rem 1rem; border-radius: 0.5rem; border: 1px solid var(--border); }
    .status-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; }
    .status-value { font-size: 1rem; font-weight: 600; margin-top: 0.25rem; color: #38bdf8; }
    form { display: flex; flex-direction: column; gap: 1rem; margin-top: 1rem; }
    .field { display: flex; flex-direction: column; gap: 0.35rem; }
    label { font-size: 0.8rem; font-weight: 500; color: var(--muted); }
    input { background: #0f172a; border: 1px solid var(--border); color: #fff; padding: 0.6rem 0.75rem; border-radius: 0.375rem; font-size: 0.875rem; outline: none; }
    input:focus { border-color: var(--success); }
    .btn-group { display: flex; gap: 0.75rem; }
    button { cursor: pointer; border: none; padding: 0.65rem 1.25rem; border-radius: 0.375rem; font-size: 0.875rem; font-weight: 600; transition: background 0.15s ease; }
    .btn-save { background: var(--success); color: white; }
    .btn-save:hover { background: var(--success-hover); }
    .btn-test { background: var(--border); color: white; }
    .btn-test:hover { background: #475569; }
    pre { background: #0b1120; border: 1px solid var(--border); border-radius: 0.5rem; padding: 1rem; font-family: monospace; font-size: 0.8rem; color: #a5f3fc; overflow-x: auto; white-space: pre-wrap; margin-top: 1rem; }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <span class="badge">Protected Service (Port 5001)</span>
      <h1>Remediated Access Control Lab</h1>
      <p>Simulating user <strong>alice</strong> with strict field allowlisting enforced.</p>
      
      <div class="status-grid">
        <div class="status-item">
          <div class="status-label">Current Role</div>
          <div id="display-role" class="status-value">{{ user.role }}</div>
        </div>
        <div class="status-item">
          <div class="status-label">Registered Email</div>
          <div id="display-email" class="status-value">{{ user.email }}</div>
        </div>
      </div>
    </div>

    <div class="card">
      <h2>Profile Settings (Allowlist Enforced)</h2>
      <p>Only designated parameters (email) are processed; extra keys are discarded.</p>
      
      <form id="profile-form">
        <div class="field">
          <label>Email Address</label>
          <input type="email" id="email" value="{{ user.email }}">
        </div>
        <div class="field">
          <label>Role Injection Attempt (Ignored Server-Side)</label>
          <input type="text" id="role" value="admin">
        </div>
        <div class="btn-group">
          <button type="submit" class="btn-save">Submit Profile Update</button>
          <button type="button" class="btn-test" onclick="testAdmin()">Test Admin Access</button>
        </div>
      </form>

      <pre id="output">// Results will appear here...</pre>
    </div>
  </div>

  <script>
    document.getElementById('profile-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('email').value;
      const role = document.getElementById('role').value;
      const res = await fetch('/profile/update', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ username: 'alice', email, role })
      });
      const data = await res.json();
      document.getElementById('output').textContent = JSON.stringify(data, null, 2);
      if (data.updated_fields && data.updated_fields.email) {
        document.getElementById('display-email').textContent = data.updated_fields.email;
      }
      document.getElementById('display-role').textContent = data.role;
    });

    async function testAdmin() {
      const res = await fetch('/admin/metrics', {
        headers: { 'X-User': 'alice' }
      });
      const data = await res.json();
      document.getElementById('output').textContent = JSON.stringify(data, null, 2);
    }
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, user=USERS["alice"])

@app.route("/profile/update", methods=["POST"])
def update_profile():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "alice")

    if username not in USERS:
        return jsonify({"error": "User not found"}), 404

    # Defense: Discard any fields not in the allowlist
    updated = {}
    for field in ALLOWED_FIELDS:
        if field in data:
            USERS[username][field] = data[field]
            updated[field] = data[field]

    return jsonify({
        "status": "success",
        "message": "Only allowlisted fields processed",
        "updated_fields": updated,
        "role": USERS[username]["role"]
    }), 200

@app.route("/admin/metrics", methods=["GET"])
def admin_metrics():
    username = request.headers.get("X-User", "alice")
    user = USERS.get(username)

    if not user or user.get("role") != "admin":
        return jsonify({"status": "error", "error": "403 Forbidden: Standard user cannot access metrics"}), 403

    return jsonify({
        "status": "success",
        "clearance": "Administrator",
        "metrics": {"secure_status": "nominal"}
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
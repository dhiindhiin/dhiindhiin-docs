from flask import Flask, render_template_string, jsonify, request
import csv
import json
import os
from collections import Counter
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='/static')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'user_status_data.csv')
UPDATED_CSV_FILE = os.path.join(BASE_DIR, 'user_status_data.csv')
LOGO_PATH = os.path.join(BASE_DIR, 'static', 'logo.png')

# Initialize the updated CSV file if it doesn't exist
def initialize_csv():
    if not os.path.exists(UPDATED_CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8') as infile:
            with open(UPDATED_CSV_FILE, 'w', encoding='utf-8') as outfile:
                reader = csv.DictReader(infile)
                fieldnames = ['First Name [Required]', 'Last Name [Required]', 'Email Address [Required]', 'Active']
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in reader:
                    row['Active'] = 'true'
                    writer.writerow(row)

# Load users from CSV
def load_users():
    users = []
    csv_to_read = UPDATED_CSV_FILE if os.path.exists(UPDATED_CSV_FILE) else CSV_FILE
    with open(csv_to_read, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            active = row.get('Active', 'true').lower() == 'true'
            users.append({
                'id': idx,
                'first_name': row['First Name [Required]'],
                'last_name': row['Last Name [Required]'],
                'email': row['Email Address [Required]'],
                'active': active
            })
    return users

# Save users to CSV
def save_users(users):
    with open(UPDATED_CSV_FILE, 'w', encoding='utf-8') as f:
        fieldnames = ['First Name [Required]', 'Last Name [Required]', 'Email Address [Required]', 'Active']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for user in users:
            writer.writerow({
                'First Name [Required]': user['first_name'],
                'Last Name [Required]': user['last_name'],
                'Email Address [Required]': user['email'],
                'Active': 'true' if user['active'] else 'false'
            })

# API endpoint to get all users
@app.route('/api/users', methods=['GET'])
def get_users():
    users = load_users()
    return jsonify(users)

# API endpoint to update user status
@app.route('/api/users/<int:user_id>/status', methods=['POST'])
def update_user_status(user_id):
    data = request.get_json()
    users = load_users()
    
    if user_id < len(users):
        users[user_id]['active'] = data.get('active', True)
        save_users(users)
        return jsonify({'success': True, 'message': 'User status updated'})
    
    return jsonify({'success': False, 'message': 'User not found'}), 404

# API endpoint to reset all users
@app.route('/api/users/reset/all', methods=['POST'])
def reset_all_users():
    users = load_users()
    for user in users:
        user['active'] = True
    save_users(users)
    return jsonify({'success': True, 'message': 'All users reset to active'})

# API endpoint to get CSV download
@app.route('/api/export-csv', methods=['GET'])
def export_csv():
    users = load_users()
    csv_data = 'First Name [Required],Last Name [Required],Email Address [Required],Active\n'
    for user in users:
        first_name = escape_csv_field(user['first_name'])
        last_name = escape_csv_field(user['last_name'])
        email = escape_csv_field(user['email'])
        active = 'true' if user['active'] else 'false'
        csv_data += f'{first_name},{last_name},{email},{active}\n'
    return csv_data, 200, {'Content-Disposition': 'attachment; filename=user_status.csv', 'Content-Type': 'text/csv'}

def escape_csv_field(field):
    if ',' in field or '"' in field or '\n' in field:
        return '"' + field.replace('"', '""') + '"'
    return field

# Serve the main webpage
@app.route('/', methods=['GET'])
def index():
    users = load_users()
    total_users = len(users)
    domains = [user['email'].split('@')[-1] for user in users]
    domain_counts = Counter(domains)
    active_count = sum(1 for user in users if user['active'])
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Summary Report - DhiinDhiin</title>
    <style>
        :root {
            --primary-gold: #d4a574;
            --dark-gold: #b8860b;
            --text-dark: #1a1a1a;
            --text-light: #4a4a4a;
            --bg-light: #faf8f3;
            --card-bg: #ffffff;
            --border-color: #e8dcc8;
            --accent-gold: #c9a961;
            --accent-dark: #2c2c2c;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #faf8f3 0%, #f5f1e8 100%);
            min-height: 100vh;
            padding: 20px;
            color: var(--text-dark);
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
        }

        .header {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 24px rgba(180, 134, 11, 0.15);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
            border-top: 4px solid var(--primary-gold);
        }

        .logo-section {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .logo {
            height: 60px;
            width: auto;
            object-fit: contain;
        }

        .header-content h1 {
            font-size: 1.8rem;
            margin-bottom: 5px;
            color: var(--text-dark);
            font-weight: 700;
        }

        .header p {
            color: var(--text-light);
            font-size: 0.9rem;
        }

        .button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .save-btn, .reset-btn {
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            white-space: nowrap;
        }

        .save-btn {
            background: linear-gradient(135deg, var(--primary-gold) 0%, var(--dark-gold) 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(180, 134, 11, 0.3);
        }

        .save-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(180, 134, 11, 0.4);
            background: linear-gradient(135deg, var(--dark-gold) 0%, #9a6f0a 100%);
        }

        .reset-btn {
            background: #f0f0f0;
            color: var(--text-dark);
            border: 1px solid var(--border-color);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .reset-btn:hover {
            background: #e8e8e8;
            transform: translateY(-2px);
        }

        .save-btn:active, .reset-btn:active {
            transform: translateY(0);
        }

        .save-btn:disabled, .reset-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--primary-gold);
            color: white;
            padding: 15px 20px;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            display: none;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        }

        .notification.show {
            display: block;
        }

        .notification.error {
            background: #dc2626;
        }

        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }

        .notification.hide {
            animation: slideOut 0.3s ease forwards;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(180, 134, 11, 0.1);
            text-align: center;
            border-left: 4px solid var(--primary-gold);
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(180, 134, 11, 0.15);
        }

        .stat-card.active {
            border-left-color: var(--dark-gold);
        }

        .stat-card.domain {
            border-left-color: var(--accent-gold);
        }

        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-gold);
            margin-bottom: 5px;
        }

        .stat-card.active .stat-number {
            color: var(--dark-gold);
        }

        .stat-card.domain .stat-number {
            color: var(--accent-gold);
        }

        .stat-label {
            font-size: 0.85rem;
            color: var(--text-light);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }

        .section {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(180, 134, 11, 0.1);
        }

        .section h2 {
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: var(--text-dark);
            border-bottom: 3px solid var(--primary-gold);
            padding-bottom: 10px;
            font-weight: 700;
        }

        .domain-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }

        .domain-table th,
        .domain-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }

        .domain-table th {
            background: linear-gradient(135deg, #faf8f3 0%, #f5f1e8 100%);
            font-weight: 600;
            color: var(--text-dark);
            border-bottom: 2px solid var(--primary-gold);
        }

        .domain-table tr:hover {
            background-color: #faf8f3;
        }

        .user-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
            gap: 15px;
            transition: all 0.2s ease;
        }

        .user-row:hover {
            background-color: #faf8f3;
        }

        .user-info {
            flex: 1;
            min-width: 0;
        }

        .user-name {
            font-weight: 600;
            color: var(--text-dark);
            margin-bottom: 4px;
        }

        .user-email {
            color: var(--text-light);
            font-size: 0.9rem;
            word-break: break-all;
        }

        .user-controls {
            display: flex;
            align-items: center;
            gap: 12px;
            flex-shrink: 0;
        }

        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            white-space: nowrap;
        }

        .status-active {
            background-color: #e8f5e9;
            color: #2e7d32;
        }

        .status-inactive {
            background-color: #ffebee;
            color: #c62828;
        }

        /* Toggle Switch Styles */
        .switch {
            position: relative;
            display: inline-block;
            width: 50px;
            height: 26px;
        }

        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 18px;
            width: 18px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }

        input:checked + .slider {
            background: linear-gradient(135deg, var(--primary-gold) 0%, var(--dark-gold) 100%);
        }

        input:focus + .slider {
            box-shadow: 0 0 1px var(--primary-gold);
        }

        input:checked + .slider:before {
            transform: translateX(24px);
        }

        .footer {
            text-align: center;
            color: var(--text-light);
            font-size: 0.85rem;
            margin-top: 30px;
            padding: 20px;
        }

        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                align-items: flex-start;
            }

            .logo-section {
                width: 100%;
            }

            .logo {
                height: 50px;
            }

            .header-content h1 {
                font-size: 1.5rem;
            }

            .button-group {
                width: 100%;
            }

            .button-group button {
                flex: 1;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }

            .section {
                padding: 15px;
            }

            .section h2 {
                font-size: 1.25rem;
            }

            .domain-table th,
            .domain-table td {
                padding: 8px;
                font-size: 0.9rem;
            }

            .user-row {
                padding: 10px;
                flex-wrap: wrap;
            }

            .user-info {
                width: 100%;
            }

            .user-controls {
                width: 100%;
                justify-content: space-between;
            }

            .notification {
                right: 10px;
                left: 10px;
            }
        }

        @media (max-width: 480px) {
            body {
                padding: 10px;
            }

            .header {
                padding: 15px;
            }

            .logo {
                height: 45px;
            }

            .header-content h1 {
                font-size: 1.25rem;
            }

            .section {
                padding: 12px;
            }

            .domain-table th,
            .domain-table td {
                padding: 6px;
                font-size: 0.8rem;
            }

            .user-row {
                padding: 8px;
                flex-direction: column;
                align-items: flex-start;
            }

            .user-controls {
                width: 100%;
                justify-content: flex-start;
            }

            .switch {
                width: 45px;
                height: 24px;
            }

            .slider:before {
                height: 16px;
                width: 16px;
            }

            input:checked + .slider:before {
                transform: translateX(21px);
            }

            .button-group {
                width: 100%;
                flex-direction: column;
            }

            .button-group button {
                width: 100%;
                padding: 12px 16px;
                font-size: 0.95rem;
            }
        }
    </style>
</head>
<body>
    <div id="notification" class="notification"></div>

    <div class="container">
        <div class="header">
            <div class="logo-section">
                <img src="/static/logo.png" alt="DhiinDhiin Logo" class="logo">
                <div class="header-content">
                    <h1>User Summary Report</h1>
                    <p>Generated on April 4, 2026 | User Management System</p>
                </div>
            </div>
            <div class="button-group">
                <button class="save-btn" id="save-csv-btn">💾 Save to CSV</button>
                <button class="reset-btn" id="reset-btn">🔄 Reset All</button>
            </div>
        </div>

        <!-- Confirm Modal -->
        <div id="confirm-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:2000;align-items:center;justify-content:center;">
            <div style="background:#fff;border-radius:12px;padding:30px;max-width:380px;width:90%;box-shadow:0 10px 40px rgba(0,0,0,0.2);">
                <h3 style="margin-bottom:12px;color:#1a1a1a;">Reset All Users?</h3>
                <p style="color:#4a4a4a;margin-bottom:24px;font-size:0.95rem;">This will set all users back to <strong>Active</strong>. This action cannot be undone.</p>
                <div style="display:flex;gap:10px;justify-content:flex-end;">
                    <button id="modal-cancel" style="padding:10px 20px;border-radius:6px;border:1px solid #e8dcc8;background:#f0f0f0;font-weight:600;cursor:pointer;">Cancel</button>
                    <button id="modal-confirm" style="padding:10px 20px;border-radius:6px;border:none;background:linear-gradient(135deg,#d4a574,#b8860b);color:white;font-weight:600;cursor:pointer;">Reset All</button>
                </div>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">""" + str(total_users) + """</div>
                <div class="stat-label">Total Users</div>
            </div>
            <div class="stat-card active">
                <div class="stat-number" id="active-count">""" + str(active_count) + """</div>
                <div class="stat-label">Active Users</div>
            </div>
            <div class="stat-card domain">
                <div class="stat-number">""" + str(len(domain_counts)) + """</div>
                <div class="stat-label">Email Domains</div>
            </div>
        </div>

        <div class="section">
            <h2>Domain Distribution</h2>
            <table class="domain-table">
                <thead>
                    <tr>
                        <th>Domain</th>
                        <th>User Count</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_users) * 100
        html_content += f"""
                    <tr>
                        <td>{domain}</td>
                        <td>{count}</td>
                        <td>{percentage:.1f}%</td>
                    </tr>
"""

    html_content += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>User Directory</h2>
            <div id="user-list">
"""

    for user in users:
        status_class = 'status-active' if user['active'] else 'status-inactive'
        status_text = 'Active' if user['active'] else 'Inactive'
        checked = 'checked' if user['active'] else ''
        html_content += f"""
                <div class="user-row">
                    <div class="user-info">
                        <div class="user-name">{user['first_name']} {user['last_name']}</div>
                        <div class="user-email">{user['email']}</div>
                    </div>
                    <div class="user-controls">
                        <span class="status-badge {status_class}" data-user-id="{user['id']}">{status_text}</span>
                        <label class="switch">
                            <input type="checkbox" {checked} data-user-id="{user['id']}">
                            <span class="slider"></span>
                        </label>
                    </div>
                </div>
"""

    html_content += """
            </div>
        </div>

        <div class="footer">
            <p>This report was automatically generated based on user data. Toggle switches to manage user status and click "Save to CSV" to download the updated data. Changes are synced to the server in real-time.</p>
        </div>
    </div>

    <script>
        // Handle toggle switch changes
        document.querySelectorAll('.switch input').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const userId = this.getAttribute('data-user-id');
                const isActive = this.checked;
                const statusBadge = document.querySelector(`.status-badge[data-user-id="${userId}"]`);
                
                // Update UI immediately
                if (isActive) {
                    statusBadge.textContent = 'Active';
                    statusBadge.classList.remove('status-inactive');
                    statusBadge.classList.add('status-active');
                } else {
                    statusBadge.textContent = 'Inactive';
                    statusBadge.classList.remove('status-active');
                    statusBadge.classList.add('status-inactive');
                }
                
                // Send update to server
                fetch(`/api/users/${userId}/status`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ active: isActive })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateActiveCount();
                        showNotification('✓ Changes synced to server');
                    } else {
                        showNotification('✗ Error syncing changes', true);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('✗ Connection error', true);
                });
            });
        });

        // Update the active count in the stats
        function updateActiveCount() {
            const activeCount = document.querySelectorAll('.switch input:checked').length;
            document.getElementById('active-count').textContent = activeCount;
        }

        // Show notification
        function showNotification(message, isError = false) {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.classList.remove('hide');
            notification.classList.add('show');
            if (isError) {
                notification.classList.add('error');
            } else {
                notification.classList.remove('error');
            }
            
            setTimeout(() => {
                notification.classList.add('hide');
                setTimeout(() => {
                    notification.classList.remove('show', 'hide');
                }, 300);
            }, 2000);
        }

        // Modal logic
        const modal = document.getElementById('confirm-modal');
        document.getElementById('reset-btn').addEventListener('click', function() {
            modal.style.display = 'flex';
        });
        document.getElementById('modal-cancel').addEventListener('click', function() {
            modal.style.display = 'none';
        });
        modal.addEventListener('click', function(e) {
            if (e.target === modal) modal.style.display = 'none';
        });
        document.getElementById('modal-confirm').addEventListener('click', function() {
            modal.style.display = 'none';
            fetch('/api/users/reset/all', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.querySelectorAll('.switch input').forEach(checkbox => {
                        checkbox.checked = true;
                        const userId = checkbox.getAttribute('data-user-id');
                        const statusBadge = document.querySelector(`.status-badge[data-user-id="${userId}"]`);
                        if (statusBadge) {
                            statusBadge.textContent = 'Active';
                            statusBadge.classList.remove('status-inactive');
                            statusBadge.classList.add('status-active');
                        }
                    });
                    updateActiveCount();
                    showNotification('✓ All users reset to Active');
                } else {
                    showNotification('✗ Error resetting users', true);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('✗ Connection error', true);
            });
        });

        // Save to CSV functionality
        document.getElementById('save-csv-btn').addEventListener('click', function() {
            const button = this;
            button.disabled = true;
            button.textContent = '⏳ Generating...';

            fetch('/api/export-csv')
                .then(response => response.text())
                .then(csvContent => {
                    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                    const link = document.createElement('a');
                    const url = URL.createObjectURL(blob);
                    
                    link.setAttribute('href', url);
                    link.setAttribute('download', `user_status_${new Date().toISOString().split('T')[0]}.csv`);
                    link.style.visibility = 'hidden';
                    
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    button.disabled = false;
                    button.textContent = '💾 Save to CSV';
                    showNotification('✓ CSV file downloaded');
                })
                .catch(error => {
                    console.error('Error:', error);
                    button.disabled = false;
                    button.textContent = '💾 Save to CSV';
                    showNotification('✗ Error downloading CSV', true);
                });
        });
    </script>
</body>
</html>
"""
    return html_content



import os as _os

# ── Multi-page Intune Documentation (English) ──
DOCS_PAGES = ['overview','phase1','phase2','phase3','phase4','phase5','phase6','next-steps','checklist']

@app.route('/intune-docs')
@app.route('/intune-docs/overview')
def intune_docs_overview():
    with open(os.path.join(BASE_DIR, 'docs', 'overview.html'), 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/intune-docs/<page>')
def intune_docs_page(page):
    path = os.path.join(BASE_DIR, 'docs', f'{page}.html')
    if _os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return 'Page not found', 404

# ── Multi-page Intune Documentation (Arabic) ──
@app.route('/intune-docs-ar')
@app.route('/intune-docs-ar/overview')
def intune_docs_ar_overview():
    with open(os.path.join(BASE_DIR, 'docs-ar', 'overview.html'), 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/intune-docs-ar/<page>')
def intune_docs_ar_page(page):
    path = os.path.join(BASE_DIR, 'docs-ar', f'{page}.html')
    if _os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return 'Page not found', 404

if __name__ == '__main__':
    initialize_csv()
    app.run(debug=False, host='0.0.0.0', port=5000)

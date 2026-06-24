import time

def handle_report_save(output_text, metrics):
    """
    Generate and save an HTML report with the current results.
    
    Args:
        output_text (str): The attack output text
        metrics (dict): The metrics data
    
    Returns:
        str: The full HTML content
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Start with the header
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ROSE GUARD Security Report</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; 
            margin: 0;
            background: #f8f9fa;
            color: #333;
            line-height: 1.6;
        }
        .container {
            max-width: 1000px;
            margin: 40px auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1, h2 { 
            color: #2c3e50;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
            margin-top: 30px;
        }
        .success { 
            color: #28a745;
            font-weight: bold;
        }
        .warning { 
            color: #dc3545;
            font-weight: bold;
        }
        .metric { 
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }
        pre {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            white-space: pre-wrap;
            font-family: 'Consolas', 'Monaco', monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ ROSE GUARD Security Report</h1>
        <p class="timestamp">Generated on: """ + timestamp + """</p>
        
        <!-- Summary Section -->
        <div class="section">
            <h2>📊 Summary</h2>"""
    
    # Add summary content
    if metrics.get('successful_attacks', 0) > 0:
        html += """
            <p class='warning'>⚠️ CRITICAL: Password was successfully cracked!</p>
            <p>This password is vulnerable and should be changed immediately.</p>"""
    else:
        html += """
            <p class='success'>✅ Password has successfully resisted all attacks.</p>
            <p>Continue monitoring and periodic testing is recommended.</p>"""
    
    html += f"""
            <p>Total Attacks Run: {metrics.get('total_attacks', 0)}</p>
            <p>Overall Success Rate: {metrics.get('success_rate', 0):.1f}%</p>
            <p>Total Attempts: {metrics.get('total_attempts', 0):,}</p>
        </div>
        
        <!-- Performance Metrics -->
        <div class="section">
            <h2>⚡ Performance Analysis</h2>"""
    
    # Add metrics
    for key, value in metrics.items():
        if isinstance(value, float):
            html += f"""
            <div class='metric'><b>{key}:</b> {value:.2f}</div>"""
        else:
            html += f"""
            <div class='metric'><b>{key}:</b> {value}</div>"""
    
    # Add attack history
    html += """
        </div>
        
        <!-- Attack History -->
        <div class="section">
            <h2>📝 Attack History</h2>
            <pre>""" + output_text.replace("<", "&lt;").replace(">", "&gt;") + """</pre>
        </div>"""
    
    # Add recommendations
    html += """
        <!-- Recommendations -->
        <div class="section">
            <h2>💡 Recommendations</h2>
            <ul>"""
    
    if metrics.get('successful_attacks', 0) > 0:
        html += """
                <li>🚨 Change this password immediately</li>
                <li>⚠️ Avoid using similar patterns in new passwords</li>
                <li>📈 Consider using a password manager</li>"""
    else:
        html += """
                <li>✅ Password shows good resistance to attacks</li>
                <li>🔄 Regular security audits recommended</li>
                <li>📝 Document password policy success</li>"""
    
    html += """
            </ul>
        </div>
    </div>
</body>
</html>"""
    
    return html
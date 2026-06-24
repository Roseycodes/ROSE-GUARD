import os
import time
import webbrowser
import csv

class FileManager:
    @staticmethod
    def export_csv(filename, data):
        """Export data to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value'])
                for key, value in data.items():
                    writer.writerow([key, value])
            FileManager.open_file(filename)
            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _generate_summary(metrics):
        """Generate summary section of the report"""
        successful = metrics.get('successful_attacks', 0)
        total = metrics.get('total_attacks', 0)
        
        if successful > 0:
            return f"""
                <div class="alert alert-danger">
                    <span style="font-size: 2em;">⚠️</span>
                    <div>
                        <strong>Security Alert:</strong> Password was successfully cracked in {successful} out of {total} attack(s).
                        This indicates the password may be vulnerable to attack.
                    </div>
                </div>
            """
        return f"""
            <div class="alert alert-success">
                <span style="font-size: 2em;">✅</span>
                <div>
                    <strong>Excellent:</strong> Password successfully resisted all {total} attack attempt(s).
                    The password demonstrates good security characteristics.
                </div>
            </div>
        """

    @staticmethod
    def _generate_metrics_cards(metrics):
        """Generate metrics cards section"""
        successful = metrics.get('successful_attacks', 0)
        metric_config = [
            ('total_attacks', 'Total Attacks', 'info', '🎯', ''),
            ('successful_attacks', 'Successful Cracks', 'danger' if successful > 0 else 'success', '🔓' if successful > 0 else '🔒', ''),
            ('success_rate', 'Success Rate', 'warning' if metrics.get('success_rate', 0) > 50 else 'success', '📊', '%'),
            ('total_attempts', 'Total Attempts', 'info', '⚡', ''),
            ('total_time', 'Total Time', 'info', '⏱️', 's'),
            ('overall_attempts_per_second', 'Avg Speed', 'success', '🚀', ' att/s'),
        ]
        
        metrics_html = ""
        for key, label, style, icon, unit in metric_config:
            if key in metrics:
                value = metrics[key]
                formatted_value = f"{value:,.2f}" if isinstance(value, float) and value < 1000 else f"{value:,}"
                metrics_html += f"""
                    <div class="metric-card {style}">
                        <div class="metric-label">{icon} {label}</div>
                        <div class="metric-value">{formatted_value}<span class="metric-unit">{unit}</span></div>
                    </div>
                """
        
        return metrics_html

    @staticmethod
    def _generate_additional_metrics(metrics):
        """Generate additional metrics table"""
        main_metrics = {'total_attacks', 'successful_attacks', 'success_rate', 
                       'total_attempts', 'total_time', 'overall_attempts_per_second'}
        additional_metrics = {k: v for k, v in metrics.items() if k not in main_metrics}
        
        if not additional_metrics:
            return ""
            
        html = """
            <div style="grid-column: 1 / -1;">
                <h3 style="margin: 20px 0 15px 0; color: #1e293b;">Additional Metrics</h3>
                <table class="stats-table">
                    <thead><tr><th>Metric</th><th>Value</th></tr></thead>
                    <tbody>
        """
        
        for key, value in additional_metrics.items():
            formatted_key = key.replace('_', ' ').title()
            formatted_value = f"{value:.2f}" if isinstance(value, float) else str(value)
            html += f"<tr><td>{formatted_key}</td><td><strong>{formatted_value}</strong></td></tr>"
        
        return html + "</tbody></table></div>"

    @staticmethod
    def _generate_recommendations(successful):
        """Generate recommendations section"""
        recommendations = ["<ul class='recommendation-list'>"]
        
        if successful > 0:
            recommendations.extend([
                """<li class="recommendation-item">
                    <span class="recommendation-icon">🔐</span>
                    <strong>Use Stronger Passwords:</strong> Consider using longer passwords (12+ characters) with a mix of uppercase, lowercase, numbers, and symbols.
                </li>""",
                """<li class="recommendation-item">
                    <span class="recommendation-icon">🎲</span>
                    <strong>Avoid Common Patterns:</strong> Don't use dictionary words, common substitutions (@ for a), or predictable patterns.
                </li>""",
                """<li class="recommendation-item">
                    <span class="recommendation-icon">🔄</span>
                    <strong>Use Password Manager:</strong> Consider using a password manager to generate and store strong, unique passwords.
                </li>"""
            ])
        else:
            recommendations.extend([
                """<li class="recommendation-item">
                    <span class="recommendation-icon">✅</span>
                    <strong>Good Password Strength:</strong> Your password demonstrated good resistance to attacks.
                </li>""",
                """<li class="recommendation-item">
                    <span class="recommendation-icon">🔄</span>
                    <strong>Regular Updates:</strong> Continue to update passwords regularly (every 90 days recommended).
                </li>"""
            ])
        
        recommendations.extend([
            """<li class="recommendation-item">
                <span class="recommendation-icon">🛡️</span>
                <strong>Enable 2FA:</strong> Always enable two-factor authentication when available for additional security.
            </li>""",
            """<li class="recommendation-item">
                <span class="recommendation-icon">🔒</span>
                <strong>Use Strong Hash Algorithms:</strong> For developers: Use bcrypt or Argon2 for password hashing, avoid MD5 and SHA-256.
            </li>"""
        ])
        
        return "".join(recommendations) + "</ul>"

    @staticmethod
    def save_html_report(filename, metrics, output_text):
        """Save beautiful HTML report using template"""
        try:
            timestamp = time.strftime('%B %d, %Y at %I:%M %p')
            
            # Load template
            template_path = os.path.join('templates', 'report_template.html')
            if not os.path.exists(template_path):
                # Fallback to simple report if template not found
                return FileManager._save_simple_report(filename, metrics, output_text, timestamp)
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            successful = metrics.get('successful_attacks', 0)
            
            # Generate all sections
            summary = FileManager._generate_summary(metrics)
            metrics_html = FileManager._generate_metrics_cards(metrics)
            metrics_html += FileManager._generate_additional_metrics(metrics)
            recommendations_html = FileManager._generate_recommendations(successful)
            
            # Generate analysis text
            analysis_html = "<p>This security assessment tested password strength against various attack methods. "
            analysis_html += "The results indicate vulnerabilities that could be exploited by attackers.</p>" if successful > 0 else \
                           "The password demonstrated strong resistance to common attack patterns.</p>"
            
            # Escape output text for HTML
            import html
            escaped_output = html.escape(output_text)
            
            # Replace placeholders in template
            replacements = {
                '{timestamp}': timestamp,
                '{summary_content}': summary,
                '{metrics_content}': metrics_html,
                '{attack_history}': escaped_output,
                '{recommendations}': recommendations_html,
                '{detailed_analysis}': analysis_html
            }
            
            html_report = template
            for key, value in replacements.items():
                html_report = html_report.replace(key, value)
            
            # Save report
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_report)
            
            FileManager.open_file(filename)
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def _save_simple_report(filename, metrics, output_text, timestamp):
        """Fallback simple report if template is not available"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ROSE GUARD Report</title>
    <style>
        body {{ font-family: -apple-system, system-ui, sans-serif; margin: 40px auto; max-width: 1000px; line-height: 1.6; }}
        .success {{ color: #28a745; }} .warning {{ color: #dc3545; }}
        pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>🛡️ ROSE GUARD Security Report</h1>
    <p>Generated on: {timestamp}</p>
    
    <h2>📊 Results Summary</h2>
    {"<p class='warning'>⚠️ Password was cracked!</p>" if metrics.get('successful_attacks', 0) > 0 
     else "<p class='success'>✅ Password resisted all attacks</p>"}
    
    <h2>📈 Performance Metrics</h2>
    {"".join(f"<p><b>{k}:</b> {v if isinstance(v, int) else f'{v:.2f}'}</p>" for k, v in metrics.items())}
    
    <h2>📝 Attack History</h2>
    <pre>{output_text}</pre>
</body>
</html>
"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        FileManager.open_file(filename)
        return True, None
    
    @staticmethod
    def open_file(filepath):
        """Open a file using the system's default program"""
        try:
            os.startfile(filepath)  # Windows
        except AttributeError:
            try:
                webbrowser.open(f"file://{os.path.abspath(filepath)}")
            except webbrowser.Error:
                # Last resort: try opening the file directly
                try:
                    webbrowser.open(filepath)
                except webbrowser.Error as e:
                    print(f"Failed to open file: {e}")
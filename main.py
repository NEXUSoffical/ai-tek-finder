from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import datetime

app = Flask(__name__)
CORS(app)

def calculate_health(repo):
    score = 100
    try:
        last_push = repo.get('pushed_at', '')
        last_push_date = datetime.datetime.strptime(last_push, "%Y-%m-%dT%H:%M:%SZ")
        days_since_update = (datetime.datetime.utcnow() - last_push_date).days
        if days_since_update > 365:
            score -= 40
        elif days_since_update > 180:
            score -= 20
    except:
        score -= 10
    
    open_issues = repo.get('open_issues_count', 0)
    stars = repo.get('stargazers_count', 1)
    if open_issues > (stars * 0.5):
        score -= 30
    return max(0, score)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"results": "<span style='color: red;'>[-] ERROR: Empty query.</span>"})
    
    gh_search_url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=3"
    
    try:
        response = requests.get(gh_search_url, headers={"Accept": "application/vnd.github.v3+json"})
        data = response.json()
        
        if 'items' not in data or len(data['items']) == 0:
            return jsonify({"results": "<span style='color: yellow;'>[!] NO TARGETS FOUND.</span>"})
        
        results_html = f"<span style='color: #00ff00;'>[+] MAINFRAME QUERY: '{query}'</span><br><br>"

        for repo in data['items']:
            health = calculate_health(repo)
            color = "#00ff00" if health > 70 else "#ffff00" if health > 40 else "#ff0000"
            
            # Grabs the actual GitHub website link
            repo_url = repo.get('html_url', '#')
            
            # Wraps the target name in a clickable HTML link that opens in a new tab
            results_html += f"<span style='color: {color};'>TARGET: <a href='{repo_url}' target='_blank' style='color: {color}; text-decoration: underline;'>{repo['full_name']}</a></span><br>"
            results_html += f"<span>HEALTH SCORE: {health}/100</span><br>"
            results_html += f"<span>STARS: {repo['stargazers_count']}</span><br>"
            results_html += "<span style='color: #444;'>--------------------------</span><br><br>"

        return jsonify({"results": results_html})
        
    except Exception as e:
        return jsonify({"results": f"<span style='color: red;'>[-] FATAL ERROR: {str(e)}</span>"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
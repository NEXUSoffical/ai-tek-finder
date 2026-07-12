from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64

app = Flask(__name__)
# Allow your GitHub Pages frontend to talk to this backend
CORS(app)

def fetch_readme_snippet(repo_full_name):
    """Secretly fetches the README file from the target repo to act as the 'AI Analysis'"""
    try:
        url = f"https://api.github.com/repos/{repo_full_name}/readme"
        headers = {"Accept": "application/vnd.github.v3+json"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # GitHub sends READMEs encoded in base64, so we have to decode it
            content = base64.b64decode(data['content']).decode('utf-8')
            # Grab the first 150 characters to act as the summary
            clean_text = content.replace('\n', ' ')[:150] + "..."
            return clean_text
        return "No readable manifest found."
    except:
        return "Manifest decryption failed."

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    
    if not query:
        return jsonify({"results": "<span style='color: red;'>[-] ERROR: Query missing.</span>"})

    # 1. Search GitHub for the best matching repositories
    gh_search_url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=3"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    try:
        response = requests.get(gh_search_url, headers=headers)
        data = response.json()
        
        if 'items' not in data or len(data['items']) == 0:
            return jsonify({"results": "<span style='color: yellow;'>[!] NO TARGETS FOUND. Adjust search parameters.</span>"})
        
        # 2. Build the visual output for the frontend terminal
        results_html = f"<span style='color: #00ff00;'>[+] MAINFRAME QUERY COMPILED: Extracted '{query}'</span><br>"
        results_html += "<span>[i] Pulling top matching platforms from GitHub...</span><br><br>"
        results_html += "<span style='color: #00ff00;'>================================================</span><br><br>"

        for idx, repo in enumerate(data['items']):
            name = repo.get('full_name', 'Unknown')
            stars = repo.get('stargazers_count', 0)
            desc = repo.get('description', 'No description provided.')
            url = repo.get('html_url', '#')
            
            # 3. Trigger the README analysis for each repo
            readme_summary = fetch_readme_snippet(name)
            
            # 4. Format the final output block
            results_html += f"<span style='color: #00ff00;'>TARGET IDENTIFIED ({idx+1}): <a href='{url}' target='_blank' style='color: #00FF33; text-decoration: underline;'>{name}</a></span><br>"
            results_html += f"<span style='color: #00aaff;'>METRIC INDEX:</span> ⭐ {stars} Stars<br>"
            results_html += f"<span style='color: #88FF88;'>CORE MANIFEST:</span> {desc}<br>"
            results_html += f"<span style='color: #777777;'>DEEP READ: {readme_summary}</span><br><br>"

        return jsonify({"results": results_html})
        
    except Exception as e:
        return jsonify({"results": "<span style='color: red;'>[-] FATAL ERROR: GitHub API connection failed.</span>"})

if __name__ == '__main__':
    # Runs the server on Render's required ports
    app.run(host='0.0.0.0', port=5000)
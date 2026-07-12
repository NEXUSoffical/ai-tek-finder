from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
def search_and_analyze(query: str):
    filler_words = {"find", "me", "an", "ai", "for", "building", "a", "the", "to", "in", "with", "out", "making", "game", "games"}
    words = query.lower().split()
    clean_words = [w for w in words if w not in filler_words]
    search_query = "+".join(clean_words) if clean_words else query
    
    github_url = f"https://api.github.com/search/repositories?q={search_query}&per_page=3"
    
    try:
        github_response = requests.get(github_url).json()
        items = github_response.get('items', [])
        
        if not items:
            return {"results": "<span style='color: #ef4444;'>[-] No matching repositories found in the Matrix.</span>"}
        
        output_html = f"<span style='color: #00FF00;'>[+] MAINFRAME QUERY COMPILED: Extracted '{search_query}'</span><br>"
        output_html += f"<span style='color: #00FF00;'>[i] Pulling top {len(items)} matching platforms from GitHub...</span><br><br>"
        output_html += "==================================================<br>"
        
        for idx, repo in enumerate(items, 1):
            name = repo.get('full_name')
            stars = repo.get('stargazers_count')
            desc = repo.get('description') or "No entry manifest provided."
            url = repo.get('html_url')
            
            output_html += f"<br><span style='color: #00FF03;'>TARGET IDENTIFIED ({idx}): {name}</span><br>"
            output_html += f"<span style='color: #00FFFF;'>METRIC INDEX: ⭐ {stars} Stars</span><br>"
            output_html += f"<span style='color: #88FF88;'>CORE MANIFEST: {desc}</span><br>"
            output_html += f"<span style='color: #4488FF;'>ACCESS POINT: <a href='{url}' target='_blank' style='color: #4488FF;'>{url}</a></span><br>"
            output_html += "--------------------------------------------------<br>"
            
        return {"results": output_html}
        
    except Exception as e:
        return {"results": f"<span style='color: #ef4444;'>[-] SYSTEM ERROR: {str(e)}</span>"}

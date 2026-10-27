import requests

class GitHubClient:
    def __init__(self):
        pass

    def fetch_user_repos(self, username):
        if not username.strip():
            return []
            
        url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Resume-Studio"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 404:
                raise ValueError("GitHub username not found.")
            elif response.status_code != 200:
                raise ValueError(f"GitHub API error (Status Code: {response.status_code}).")
                
            repos = response.json()
            if not isinstance(repos, list):
                return []
                
            processed_repos = []
            for r in repos:
                # Filter out forks to focus on original repositories
                if r.get("fork", False):
                    continue
                    
                processed_repos.append({
                    "name": r.get("name", ""),
                    "description": r.get("description", "") or "No description provided.",
                    "stars": r.get("stargazers_count", 0),
                    "language": r.get("language") or "Other",
                    "url": r.get("html_url", ""),
                    "updated_at": r.get("updated_at", "")[:10]  # YYYY-MM-DD
                })
                
            # Sort by stargazers count first, then update date
            processed_repos.sort(key=lambda x: (x["stars"], x["updated_at"]), reverse=True)
            return processed_repos
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Network error while connecting to GitHub: {e}")
        except Exception as e:
            raise ValueError(f"An unexpected error occurred: {e}")

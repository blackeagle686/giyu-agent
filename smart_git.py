import os
import time
import subprocess
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Configuration
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY", "ak_2yp3Xw1Ny7ky2pF7er9x93ZO9jj6G")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.longcat.chat/openai")
MODEL = os.getenv("OPENAI_LLM_MODEL", "LongCat-Flash-Lite")
INTERVAL = 5  # Seconds
MAX_DIFF_BYTES = int(os.getenv("SMART_GIT_MAX_DIFF_BYTES", "12000"))
MAX_DIFF_FILES = int(os.getenv("SMART_GIT_MAX_DIFF_FILES", "30"))
LLM_TIMEOUT = float(os.getenv("SMART_GIT_LLM_TIMEOUT", "12.0"))

client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=LLM_TIMEOUT) if API_KEY else None

def run_command(command):
    """Runs a shell command and returns stdout."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        return (result.stdout or "").strip()
    except Exception as e:
        stderr = getattr(e, "stderr", str(e))
        print(f"Error running command {' '.join(command)}: {stderr}")
        return ""


def run_command_ok(command):
    """Runs a shell command and returns True on success."""
    try:
        subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        return True
    except Exception as e:
        stderr = getattr(e, "stderr", str(e))
        print(f"Error: {e}")
        print(f"Error running command {' '.join(command)}: {stderr}")
        return False


def get_current_branch():
    return run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])

def get_status_porcelain():
    return run_command(["git", "status", "--porcelain=v1"])

def has_changes(status_text):
    return bool(status_text.strip())

def stage_all():
    return run_command_ok(["git", "add", "."])

def build_fast_diff_payload():
    """
    Build a compact, high-signal payload for faster commit generation:
    - name/status list (cheap, structured)
    - shortstat summary
    - patch with zero context and file cap
    """
    names = run_command(["git", "diff", "--cached", "--name-status"])
    shortstat = run_command(["git", "diff", "--cached", "--shortstat"])
    patch = run_command(
        ["git", "diff", "--cached", "--unified=0", "--", "."]
    )

    if not names and not patch:
        return ""

    # Cap number of files considered for speed and token control
    lines = names.splitlines()[:MAX_DIFF_FILES] if names else []
    names = "\n".join(lines)

    if len(patch) > MAX_DIFF_BYTES:
        patch = patch[:MAX_DIFF_BYTES] + "\n...[truncated for speed]"

    return f"Changed files:\n{names}\n\nSummary:\n{shortstat}\n\nPatch:\n{patch}"

import sys
import json
import urllib.request
import urllib.error

def generate_commit_message(payload):
    if not payload:
        return None
    if client is None:
        return None

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Write a 1-line git commit message (<50 chars). No quotes, no markdown, plain text only."},
                {"role": "user", "content": payload},
            ],
            max_tokens=30,
            temperature=0,
            stream=True,
        )
        
        full_message = ""
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                sys.stdout.write(content)
                sys.stdout.flush()
                full_message += content
        sys.stdout.write("\n")
        sys.stdout.flush()
        return full_message.strip()
    except Exception as e:
        print(f"\nLLM Error: {e}")
        return None

def commit_with_message(message):
    return run_command_ok(["git", "commit", "-m", message])


def _parse_owner_repo_from_remote():
    """Return (owner, repo) parsed from remote.origin.url or (None, None)."""
    url = run_command(["git", "config", "--get", "remote.origin.url"]) or ""
    url = url.strip()
    if not url:
        return (None, None)

    # git@github.com:owner/repo.git or https://github.com/owner/repo.git
    if url.startswith("git@"):
        # git@github.com:owner/repo.git
        parts = url.split(":", 1)
        if len(parts) == 2:
            path = parts[1]
        else:
            path = ""
    else:
        # https://github.com/owner/repo.git or https://github.com/owner/repo
        try:
            path = urllib.request.urlparse(url).path
        except Exception:
            path = url

    if path.endswith(".git"):
        path = path[:-4]
    path = path.lstrip("/")
    if "/" in path:
        owner, repo = path.split("/", 1)
        return (owner, repo)
    return (None, None)


def _get_default_branch_via_api(owner, repo, token):
    if not owner or not repo or not token:
        return None
    url = f"https://api.github.com/repos/{owner}/{repo}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
            return data.get("default_branch")
    except Exception:
        return None


def _create_pr_via_api(title, body, head, base=None):
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not token:
        print("[!] No GH_TOKEN/GITHUB_TOKEN found; cannot create PR via API.")
        return False

    owner, repo = _parse_owner_repo_from_remote()
    if not owner or not repo:
        print("[!] Could not parse owner/repo from remote.origin.url; skipping API PR creation.")
        return False

    if base is None:
        base = _get_default_branch_via_api(owner, repo, token) or "main"

    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    payload = {"title": title, "body": body, "head": head, "base": base}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, method="POST")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("Authorization", f"token {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if 200 <= resp.status < 300:
                print("[v] Pull request created via GitHub API.")
                return True
            else:
                print(f"[!] GitHub API returned status {resp.status}")
                return False
    except urllib.error.HTTPError as e:
        try:
            err = e.read().decode()
        except Exception:
            err = str(e)
        print(f"[!] GitHub API error creating PR: {err}")
        return False
    except Exception as e:
        print(f"[!] Unexpected error creating PR via API: {e}")
        return False

def smart_sync():
    print(f"[*] Checking for changes at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")

    status = get_status_porcelain()
    if not has_changes(status):
        print("[ ] No changes detected.")
        return

    print("[+] Changes detected. Staging files...")
    if not stage_all():
        print("[!] Staging failed. Skipping this cycle.")
        return

    payload = build_fast_diff_payload()
    print("[*] Generating commit message...")
    message = generate_commit_message(payload)

    if not message:
        message = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"[!] LLM failed or no message generated. Using fallback: {message}")
    else:
        print(f"[v] Generated message: {message.splitlines()[0]}")

    print("[*] Committing...")
    if not commit_with_message(message):
        print("[!] Commit failed (or nothing staged). Skipping push.")
        return

    branch = get_current_branch()
    if branch:
        print(f"[*] Pushing to origin {branch} (setting upstream)...")
        # set upstream for the branch and push
        if run_command_ok(["git", "push", "-u", "origin", branch]):
            print("[v] Pushed and set upstream.")

            # Try to create a pull request using GitHub CLI if available
            if run_command_ok(["gh", "--version"]):
                print("[*] Creating pull request via gh...")
                # Use generated commit message as PR title when available
                pr_cmd = ["gh", "pr", "create", "--fill"]
                if message:
                    title = message.splitlines()[0]
                    pr_cmd = ["gh", "pr", "create", "--title", title, "--body", "Auto-generated by smart_git.py"]

                if run_command_ok(pr_cmd):
                    print("[v] Pull request created.")
                else:
                    print("[!] Pull request creation failed via gh. Trying API fallback...")
                    # Attempt API fallback using GH_TOKEN/GITHUB_TOKEN if available
                    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
                    if token:
                        title = message.splitlines()[0] if message else "Automated PR"
                        body = "Auto-generated by smart_git.py"
                        head = branch
                        if _create_pr_via_api(title, body, head):
                            print("[v] Pull request created via API fallback.")
                        else:
                            print("[!] API fallback failed to create PR.")
                    else:
                        print("[!] No GH_TOKEN/GITHUB_TOKEN set; cannot attempt API PR creation.")
            else:
                print("[!] GitHub CLI 'gh' not available; skipping PR creation. Run 'gh pr create' manually.")
        else:
            print("[!] Push failed.")
    else:
        print("[!] Could not determine current branch. Skipping push.")

def main():
    print("=== Smart Git Automator Started ===")
    print(f"Interval: {INTERVAL} seconds")
    print(f"Target: {os.getcwd()}")
    
    # Check if this is a git repo
    if not os.path.exists(".git"):
        print("[!] Error: Not a Git repository. Please run in a git project root.")
        return

    try:
        while True:
            smart_sync()
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\n[!] Stopped by user.")

if __name__ == "__main__":
    main()

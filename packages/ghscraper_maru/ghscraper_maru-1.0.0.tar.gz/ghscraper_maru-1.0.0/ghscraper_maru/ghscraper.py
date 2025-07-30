import os
import requests
import subprocess
import click
# I want to make a flag to clone EVERY COMMIT, but I have no clue where to start, and that would DEFINITELY require an api key
art="""        .__                                                    
   ____ |  |__   ______ ________________  ______   ___________ 
  / ___\\|  |  \\ /  ___// ___\\_  __ \\__  \\ \\____ \\_/ __ \\_  __ \\
 / /_/  >   Y  \\\\___ \\  \\___|  | \\// __ \\|  |_> >  ___/|  | \\/
 \\___  /|___|  /____  >\\___  >__|  (____  /   __/ \\___  >__|   
/_____/      \\/     \\/     \\/           \\/|__|        \\/       """
click.echo(art)

@click.command()
@click.option('--token', '-t', help='Your GitHub API token')
@click.option('--user', '-u', required=True, help='GitHub username')
@click.option('--exclude-non-github', is_flag=True, help='Exclude commits from non-GitHub users')
@click.option('--allow-forks', is_flag=True, help='Allow cloning of forked repositories')
@click.option('--email-scrape', '--e', is_flag=True, help='Fetch all commits and scrape their pages')
@click.option('--contrib-check', '--cc', is_flag=True, help='Dont scrape repos with multiple contributors, REQUIRES PAT')


def main(user, token, exclude_non_github, allow_forks, email_scrape, contrib_check):
    """
    email: maru@lithium-dev.xyz (pgp attached in my github readme)
    signal: maru.222
    BTC: 16innLYQtz123HTwNLY3vScPmEVP7tob8u
    ETH: 0x48994D78B7090367Aa20FD5470baDceec42cAF62 
    XMR: 49dNpgP5QSpPDF1YUVuU3ST2tUWng32m8crGQ4NuM6U44CG1ennTvESWbwK6epkfJ6LuAKYjSDKqKNtbtJnU71gi6GrF4Wh
    """
    
    """
    Main function to fetch and clone GitHub repositories for a given user.
    """
   
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    os.chdir(temp_dir)

    click.echo("Fetching repositories...")
    repos = fetch_repos(user, token)
    click.echo(f"Found {len(repos)} repositories.")
    clone(repos, exclude_non_github, token, allow_forks, email_scrape, contrib_check)

def fetch_repos(user, token):
    headers = {}
    if token:
        headers = {"Authorization": f"token {token}"}

    api = f"https://api.github.com/users/{user}/repos"
    repos = []
    page = 1
    while True:
        response = requests.get(api, headers=headers, params={"per_page": 100, "page": page})
        if response.status_code != 200:
            click.echo(f"Failed to fetch repositories: {response.status_code}")
            break
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def contributorcheck(owner, repo_name, token):
    headers = {}
    if token:
        headers = {"Authorization": f"token {token}"}
    api = f"https://api.github.com/repos/{owner}/{repo_name}/contributors"
    response = requests.get(api, headers=headers, params={"per_page": 2})
    if response.status_code != 200:
        click.echo(f"Failed to fetch contributors for {repo_name}: {response.status_code}")
        return False
    data = response.json()
    return len(data) > 1

def clone(repos, exclude_non_github, token, allow_forks, email_scrape, contrib_check):
    emails_file_path = os.path.join("..", "Emails.txt")
    email_counts = {}

    for repo in repos:
        repo_name = repo["name"]
        repo_description = repo.get("description")  

        if repo_description:
            repo_description = repo_description.lower()
        else:
            repo_description = ""
        if not allow_forks and repo.get("fork", False):
            click.echo(f"Skipping forked repository '{repo_name}'.")
            continue

        if not allow_forks and "fork" in repo_description or "original repository" in repo_description:
            click.echo(f"Skipping repository '{repo_name}' as it appears to be a fork based on its description.")
            continue
        #NEED TO ADD A PRIVATE CHECK!!!
        if repo_name == 'ghscraper' or repo_name == 'DeepFaceLab':
            click.echo(f"Skipping repository '{repo_name}' to avoid scraping itself/giving credential loop.")
            continue
        owner = repo["owner"]["login"]
        if contrib_check and contributorcheck(owner, repo_name, token):
            click.echo(f"Skipping repository '{repo_name}' because it has multiple contributors.")
            continue

        clone_url = repo["clone_url"]
        click.echo(f"Cloning {repo_name}...")

        try:
            subprocess.run(["git", "clone", "--quiet", clone_url], check=True)
        except subprocess.CalledProcessError as e:
            click.echo(f"Failed to clone repository '{repo_name}': {e}")
            continue

        try:
            os.chdir(repo_name)
        except FileNotFoundError:
            click.echo(f"Repository directory '{repo_name}' not found. Skipping...")
            continue

        # Fetch all branches
        click.echo(f"Fetching all branches for {repo_name}...")
        subprocess.run(["git", "fetch", "--all"], check=False)

        # Fetch commit details if --email-scrape is set
        if email_scrape:
            click.echo(f"Fetching commits for {repo_name}...")
            commits = fetch_commits(repo["owner"]["login"], repo_name, exclude_non_github, token)

            # Write commits to a text file
            with open("commits.txt", "w") as f:
                for commit in commits:
                    if commit['email'].endswith("@users.noreply.github.com"):
                        continue

                    f.write(f"Author: {commit['author']}\n")
                    f.write(f"Email: {commit['email']}\n")
                    f.write(f"Message: {commit['message']}\n")
                    f.write(f"Date: {commit['date']}\n")
                    f.write(f"URL: {commit['url']}\n")
                    f.write("-" * 40 + "\n")

                    # Count email occurrences
                    if commit['email'] != "Unknown":
                        email_counts[commit['email']] = email_counts.get(commit['email'], 0) + 1

        os.chdir("..")
    sorted_emails = sorted(email_counts.items(), key=lambda x: x[1], reverse=True)

    with open(emails_file_path, "w") as emails_file:
        for email, count in sorted_emails:
            emails_file.write(f"{email} ({count})\n")
    click.echo(f"Added {len(email_counts)} unique emails to Emails.txt, sorted by frequency.")

def fetch_commits(owner, repo_name, exclude_non_github, token):

    headers = {}
    if token:
        headers = {"Authorization": f"token {token}"}

    api = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
    commits = []
    page = 1
    while True:
        response = requests.get(api, headers=headers, params={"per_page": 100, "page": page})
        if response.status_code != 200:
            click.echo(f"Failed to fetch commits: {response.status_code}")
            break
        data = response.json()
        if not data:
            break
        for commit in data:
            author = commit["commit"]["author"]
            if exclude_non_github and commit["author"] is None:
                continue

            email = author["email"] if author and "email" in author else "Unknown"
            click.echo(f"Found email: {email}")

            commits.append({
                "author": author["name"] if author else "Unknown",
                "email": email,
                "message": commit["commit"]["message"],
                "date": author["date"] if author else "Unknown",
                "url": commit["html_url"]
            })
        page += 1
    return commits

if __name__ == "__main__":
    main()
    click.echo("Done!")

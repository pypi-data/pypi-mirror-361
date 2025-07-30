#!/usr/bin/env python3
"""
GitHub Repository Creation Script

This script automates the creation of a GitHub repository for the GIMP MCP Server project.
It handles repository creation, initial setup, and configuration.

Usage:
    python scripts/create_github_repo.py --token YOUR_GITHUB_TOKEN --org gimp-mcp

Requirements:
    - GitHub personal access token with repo creation permissions
    - PyGithub library: pip install PyGithub
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from github import Github, Repository
    from github.GithubException import GithubException
except ImportError:
    print("Error: PyGithub library not found. Install with: pip install PyGithub")
    sys.exit(1)


class GitHubRepoCreator:
    """Handles GitHub repository creation and configuration."""
    
    def __init__(self, token: str, organization: Optional[str] = None):
        """
        Initialize GitHub repository creator.
        
        Args:
            token: GitHub personal access token
            organization: GitHub organization name (optional)
        """
        self.github = Github(token)
        self.organization = organization
        self.user = self.github.get_user()
        
    def get_repo_config(self) -> Dict[str, Any]:
        """Get repository configuration from pyproject.toml."""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                print("Error: tomllib/tomli not available. Install with: pip install tomli")
                sys.exit(1)
        
        pyproject_path = Path("pyproject.toml")
        if not pyproject_path.exists():
            print("Error: pyproject.toml not found. Run from project root.")
            sys.exit(1)
            
        with open(pyproject_path, "rb") as f:
            config = tomllib.load(f)
            
        project = config.get("project", {})
        
        return {
            "name": project.get("name", "gimp-mcp-server"),
            "description": project.get("description", ""),
            "homepage": project.get("urls", {}).get("Homepage", ""),
            "keywords": project.get("keywords", []),
            "license": project.get("license", {}).get("text", "MIT"),
        }
        
    def create_repository(self, repo_name: str, config: Dict[str, Any]) -> Repository.Repository:
        """
        Create GitHub repository.
        
        Args:
            repo_name: Repository name
            config: Repository configuration
            
        Returns:
            Created repository object
        """
        repo_config = {
            "name": repo_name,
            "description": config["description"],
            "homepage": config["homepage"],
            "private": False,
            "has_issues": True,
            "has_projects": True,
            "has_wiki": False,
            "has_downloads": True,
            "has_discussions": True,
            "auto_init": False,  # We'll push existing content
            "allow_squash_merge": True,
            "allow_merge_commit": True,
            "allow_rebase_merge": True,
            "delete_branch_on_merge": True,
        }
        
        try:
            if self.organization:
                org = self.github.get_organization(self.organization)
                repo = org.create_repo(**repo_config)
                print(f"✅ Created repository: {self.organization}/{repo_name}")
            else:
                repo = self.user.create_repo(**repo_config)
                print(f"✅ Created repository: {self.user.login}/{repo_name}")
                
            return repo
            
        except GithubException as e:
            if e.status == 422 and "already exists" in str(e):
                print(f"⚠️  Repository {repo_name} already exists")
                if self.organization:
                    return self.github.get_repo(f"{self.organization}/{repo_name}")
                else:
                    return self.github.get_repo(f"{self.user.login}/{repo_name}")
            else:
                print(f"❌ Error creating repository: {e}")
                sys.exit(1)
                
    def configure_repository(self, repo: Repository.Repository, config: Dict[str, Any]):
        """
        Configure repository settings.
        
        Args:
            repo: Repository object
            config: Configuration dictionary
        """
        print("🔧 Configuring repository...")
        
        # Set topics (keywords)
        if config["keywords"]:
            try:
                repo.replace_topics(config["keywords"])
                print(f"✅ Set topics: {', '.join(config['keywords'])}")
            except GithubException as e:
                print(f"⚠️  Could not set topics: {e}")
        
        # Create branch protection rules
        try:
            main_branch = repo.get_branch("main")
            main_branch.edit_protection(
                strict=True,
                contexts=[
                    "lint",
                    "security", 
                    "test",
                    "integration",
                    "build"
                ],
                enforce_admins=False,
                dismiss_stale_reviews=True,
                require_code_owner_reviews=True,
                required_approving_review_count=1,
            )
            print("✅ Configured branch protection for main")
        except GithubException as e:
            print(f"⚠️  Could not set branch protection: {e}")
            
    def setup_secrets(self, repo: Repository.Repository):
        """
        Set up repository secrets for CI/CD.
        
        Args:
            repo: Repository object
        """
        print("🔐 Setting up repository secrets...")
        
        secrets_needed = [
            "PYPI_API_TOKEN",
            "CODECOV_TOKEN",
        ]
        
        print("📋 Required secrets for CI/CD:")
        for secret in secrets_needed:
            print(f"  - {secret}")
            
        print("\n💡 You'll need to manually add these secrets in:")
        print(f"   {repo.html_url}/settings/secrets/actions")
        
    def create_labels(self, repo: Repository.Repository):
        """
        Create issue labels.
        
        Args:
            repo: Repository object
        """
        print("🏷️  Creating issue labels...")
        
        labels = [
            # Type labels
            ("bug", "d73a49", "Something isn't working"),
            ("enhancement", "a2eeef", "New feature or request"),
            ("documentation", "0075ca", "Improvements or additions to documentation"),
            ("question", "d876e3", "Further information is requested"),
            
            # Priority labels
            ("priority:low", "e6f3ff", "Low priority"),
            ("priority:medium", "b3d9ff", "Medium priority"),
            ("priority:high", "80ccff", "High priority"),
            ("priority:critical", "ff4d4d", "Critical priority"),
            
            # Status labels
            ("needs-triage", "fbca04", "Needs to be triaged"),
            ("good first issue", "7057ff", "Good for newcomers"),
            ("help wanted", "008672", "Extra attention is needed"),
            ("wontfix", "ffffff", "This will not be worked on"),
            ("duplicate", "cfd3d7", "This issue or pull request already exists"),
            
            # Platform labels
            ("platform:linux", "28a745", "Linux-specific"),
            ("platform:windows", "0969da", "Windows-specific"),
            ("platform:macos", "6f42c1", "macOS-specific"),
            
            # Component labels
            ("component:core", "ff6b6b", "Core server functionality"),
            ("component:tools", "4ecdc4", "MCP tools"),
            ("component:resources", "45b7d1", "Resource providers"),
            ("component:docs", "96ceb4", "Documentation"),
            ("component:tests", "feca57", "Testing"),
            ("component:ci", "ff9ff3", "CI/CD"),
        ]
        
        for name, color, description in labels:
            try:
                repo.create_label(name, color, description)
                print(f"  ✅ Created label: {name}")
            except GithubException as e:
                if "already_exists" in str(e):
                    print(f"  ⚠️  Label already exists: {name}")
                else:
                    print(f"  ❌ Error creating label {name}: {e}")
                    
    def print_next_steps(self, repo: Repository.Repository):
        """Print next steps for repository setup."""
        print("\n" + "="*60)
        print("🎉 REPOSITORY CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"📍 Repository URL: {repo.html_url}")
        print(f"📋 Clone URL: {repo.clone_url}")
        print(f"🔗 SSH URL: {repo.ssh_url}")
        
        print("\n📝 NEXT STEPS:")
        print("1. Add remote to your local repository:")
        print(f"   git remote add origin {repo.ssh_url}")
        print("   git branch -M main")
        print("   git push -u origin main")
        
        print("\n2. Set up repository secrets for CI/CD:")
        print(f"   {repo.html_url}/settings/secrets/actions")
        print("   Required secrets:")
        print("   - PYPI_API_TOKEN (for PyPI publishing)")
        print("   - CODECOV_TOKEN (for code coverage)")
        
        print("\n3. Configure GitHub Pages (optional):")
        print(f"   {repo.html_url}/settings/pages")
        print("   Source: GitHub Actions")
        
        print("\n4. Enable Discussions (optional):")
        print(f"   {repo.html_url}/settings")
        print("   Features > Discussions")
        
        print("\n5. Review and customize:")
        print("   - Branch protection rules")
        print("   - Issue templates")
        print("   - Pull request template")
        print("   - Repository topics/tags")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Create GitHub repository for GIMP MCP Server"
    )
    parser.add_argument(
        "--token",
        required=True,
        help="GitHub personal access token"
    )
    parser.add_argument(
        "--org",
        help="GitHub organization name (optional)"
    )
    parser.add_argument(
        "--repo-name",
        default="gimp-mcp-server",
        help="Repository name (default: gimp-mcp-server)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        
    print("🚀 GitHub Repository Creation Script")
    print("====================================")
    
    # Initialize creator
    try:
        creator = GitHubRepoCreator(args.token, args.org)
        print(f"✅ Authenticated as: {creator.user.login}")
        if args.org:
            print(f"📁 Target organization: {args.org}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        sys.exit(1)
    
    # Get repository configuration
    config = creator.get_repo_config()
    print(f"📋 Repository: {args.repo_name}")
    print(f"📝 Description: {config['description']}")
    
    if args.dry_run:
        print("\n📋 DRY RUN SUMMARY:")
        print(f"   Would create repository: {args.repo_name}")
        print(f"   Organization: {args.org or 'Personal'}")
        print(f"   Topics: {', '.join(config['keywords'])}")
        return
    
    # Create repository
    repo = creator.create_repository(args.repo_name, config)
    
    # Configure repository
    creator.configure_repository(repo, config)
    
    # Create labels
    creator.create_labels(repo)
    
    # Set up secrets info
    creator.setup_secrets(repo)
    
    # Print next steps
    creator.print_next_steps(repo)


if __name__ == "__main__":
    main()
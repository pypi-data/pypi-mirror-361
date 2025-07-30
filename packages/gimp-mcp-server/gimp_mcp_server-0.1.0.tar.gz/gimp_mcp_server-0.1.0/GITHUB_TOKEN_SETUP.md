# GitHub Personal Access Token Setup Guide

This guide will walk you through creating a GitHub personal access token needed for repository creation and management.

## 📋 What You'll Need

- A GitHub account
- Administrative access to create repositories
- About 5 minutes to complete the setup

## 🔑 Creating a Personal Access Token

### Step 1: Access GitHub Settings

1. **Log in to GitHub** at [https://github.com](https://github.com)
2. **Click your profile picture** in the top-right corner
3. **Select "Settings"** from the dropdown menu

### Step 2: Navigate to Developer Settings

1. **Scroll down** to the bottom of the left sidebar
2. **Click "Developer settings"**
3. **Click "Personal access tokens"**
4. **Select "Tokens (classic)"** or **"Fine-grained tokens"** (recommended)

## 🎯 Option A: Fine-grained Personal Access Tokens (Recommended)

Fine-grained tokens provide better security and more precise permissions.

### Create Fine-grained Token

1. **Click "Generate new token"** → **"Generate new token (fine-grained)"**
2. **Fill in the details**:
   - **Token name**: `GIMP MCP Server Repository Management`
   - **Expiration**: Choose your preferred duration (90 days recommended)
   - **Description**: `Token for creating and managing GIMP MCP Server repository`

### Set Resource Owner

- **Select the account/organization** where you want to create the repository
- If creating under your personal account, select your username
- If creating under an organization, select the organization name

### Configure Repository Access

Choose one of these options:

**Option 1: All repositories** (if you have few repositories)
- Select "All repositories" 

**Option 2: Selected repositories** (recommended)
- Select "Selected repositories"
- Click "Select repositories" 
- Choose existing repositories you want to manage (you can add the new repository later)

### Set Permissions

Configure these **Repository permissions**:

| Permission | Access Level | Purpose |
|------------|--------------|---------|
| **Actions** | Write | For GitHub Actions workflows |
| **Administration** | Write | For repository settings and branch protection |
| **Contents** | Write | For reading/writing repository content |
| **Issues** | Write | For issue management and templates |
| **Metadata** | Read | For repository metadata |
| **Pages** | Write | For GitHub Pages deployment |
| **Pull requests** | Write | For PR management |
| **Secrets** | Write | For repository secrets management |

### Account Permissions (if needed)

If you plan to create repositories under an organization:

| Permission | Access Level | Purpose |
|------------|--------------|---------|
| **Members** | Read | For organization member access |
| **Organization administration** | Read | For organization settings |

## 🔧 Option B: Classic Personal Access Tokens

If you prefer the classic approach:

### Create Classic Token

1. **Click "Generate new token"** → **"Generate new token (classic)"**
2. **Fill in the details**:
   - **Note**: `GIMP MCP Server Repository Management`
   - **Expiration**: Choose your preferred duration

### Select Scopes

Check these scopes for repository creation and management:

#### Essential Scopes
- ✅ **`repo`** - Full control of private repositories
  - Includes: `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`
- ✅ **`workflow`** - Update GitHub Action workflows
- ✅ **`write:packages`** - Upload packages to GitHub Package Registry
- ✅ **`delete:packages`** - Delete packages from GitHub Package Registry

#### Optional Scopes (for organizations)
- ✅ **`admin:org`** - Full control of orgs and teams (if creating in organization)
  - Or just `read:org` for reading organization data

### Generate and Save Token

1. **Click "Generate token"**
2. **⚠️ IMPORTANT**: Copy the token immediately - you won't see it again!
3. **Save it securely** - consider using a password manager

## 🔒 Security Best Practices

### Token Storage
- **Never commit tokens to code repositories**
- **Use environment variables** for token storage
- **Consider using a password manager** for secure storage
- **Regularly rotate tokens** (every 90 days recommended)

### Environment Variable Setup

**Windows (PowerShell)**:
```powershell
$env:GITHUB_TOKEN = "your_token_here"
```

**Windows (Command Prompt)**:
```cmd
set GITHUB_TOKEN=your_token_here
```

**macOS/Linux (Bash)**:
```bash
export GITHUB_TOKEN="your_token_here"
```

**Permanent Setup** (add to your shell profile):
```bash
# Add to ~/.bashrc, ~/.zshrc, or ~/.profile
export GITHUB_TOKEN="your_token_here"
```

## 🧪 Testing Your Token

Test your token with our validation script:

```bash
# Navigate to project directory
cd gimp-mcp-server

# Test token (dry run mode)
python scripts/create_github_repo.py --token $GITHUB_TOKEN --dry-run
```

Or test with a simple API call:
```bash
curl -H "Authorization: token YOUR_TOKEN_HERE" https://api.github.com/user
```

## 🚀 Using the Token for Repository Creation

Once you have your token, you can create the repository:

### For Personal Account
```bash
python scripts/create_github_repo.py --token YOUR_TOKEN_HERE
```

### For Organization
```bash
python scripts/create_github_repo.py --token YOUR_TOKEN_HERE --org your-org-name
```

### With Custom Repository Name
```bash
python scripts/create_github_repo.py --token YOUR_TOKEN_HERE --repo-name custom-repo-name
```

## 🔧 Troubleshooting

### Common Issues

**"Bad credentials" error**:
- Verify token is copied correctly (no extra spaces)
- Check token hasn't expired
- Ensure token has required permissions

**"Not Found" error when creating in organization**:
- Verify you have admin access to the organization
- Check organization name is spelled correctly
- Ensure token has organization permissions

**Permission denied errors**:
- Review token scopes/permissions
- For fine-grained tokens, check repository access settings
- Verify you have the necessary permissions in the target account/organization

### Getting Help

If you encounter issues:

1. **Check the GitHub documentation**: [GitHub Token Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
2. **Verify permissions**: Ensure your token has all required scopes
3. **Test with GitHub CLI**: `gh auth status` to verify authentication
4. **Contact support**: GitHub support for account-specific issues

## 📋 Quick Reference

### Fine-grained Token Permissions Checklist
- [ ] Actions: Write
- [ ] Administration: Write  
- [ ] Contents: Write
- [ ] Issues: Write
- [ ] Metadata: Read
- [ ] Pages: Write
- [ ] Pull requests: Write
- [ ] Secrets: Write

### Classic Token Scopes Checklist
- [ ] repo (full repository access)
- [ ] workflow (GitHub Actions)
- [ ] write:packages (package publishing)
- [ ] admin:org (if using organization)

### Ready to Proceed?

Once you have your token:

1. **Set environment variable**: `export GITHUB_TOKEN="your_token"`
2. **Test the token**: Run dry-run mode first
3. **Create repository**: Use the creation script
4. **Verify setup**: Check repository was created successfully

---

**Next Step**: Once you have your token, return to the repository creation process!
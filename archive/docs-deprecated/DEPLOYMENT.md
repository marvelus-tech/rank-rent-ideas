# GitHub Pages Deployment Process

## How to Deploy Projects to GitHub Pages

### Current Setup
- **Repository**: `marvelus-tech/rank-rent-ideas`
- **GitHub Pages URL**: `https://marvelus-tech.github.io/rank-rent-ideas/`
- **Configured Branch**: `main` (root `/`)

### Deployment Steps

1. **Ensure file is in the correct location**
   - For root site: `index.html` at repository root
   - For subdirectories: `project-name/index.html`

2. **Commit and push to main branch**
   ```bash
   cd ~/.openclaw/workspace
   git add .
   git commit -m "Deploy [project-name] to GitHub Pages"
   git push origin main
   ```

3. **Verify GitHub Pages configuration**
   ```bash
   gh api repos/marvelus-tech/rank-rent-ideas/pages
   ```
   Should show:
   - `source.branch`: "main"
   - `source.path`: "/"
   - `status`: "built" (not "errored")

4. **Trigger rebuild if needed**
   ```bash
   # Make a small change to force rebuild
   echo "<!-- Build: $(date) -->" >> index.html
   git add index.html
   git commit -m "Trigger GitHub Pages rebuild"
   git push origin main
   ```

5. **Check build status**
   ```bash
   gh api repos/marvelus-tech/rank-rent-ideas/pages/builds | grep -E '"status"|"commit"'
   ```

6. **Test the live URL**
   ```
   https://marvelus-tech.github.io/rank-rent-ideas/[project-name]/
   ```

### Troubleshooting

- **Build errors**: Check if there are any Jekyll build errors (even for HTML files)
- **404 errors**: Ensure the file path matches the URL path exactly
- **Cache issues**: GitHub Pages can take 2-5 minutes to propagate changes
- **Branch issues**: Make sure GitHub Pages is configured to serve from the correct branch

### Previous Patterns (from git history)
- `046652b`: Moved `index.html` to root for GitHub Pages
- `be38f40`: Triggered rebuild with timestamp
- `3573cd8`: Forced rebuild
- Pattern: Simple HTML files work best when placed at root or in subdirectories

### Notes
- GitHub Pages serves static HTML/CSS/JS files
- No server-side processing needed
- Files in subdirectories are served at corresponding URL paths
- Build process is automatic on push to configured branch

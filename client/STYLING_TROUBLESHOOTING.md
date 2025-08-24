# Styling Troubleshooting Guide

This guide addresses common styling inconsistencies that may occur across different development environments.

## 🚨 Common Issues

### Issue: Styles not appearing consistently across team members

**Symptoms:**
- Chat interface displays differently on different machines
- Fonts don't load properly
- Tailwind classes seem inconsistent
- Dark/light theme switching issues

## 🔧 Solutions

### 1. **Clear All Caches (Most Important)**

**Windows (PowerShell):**
```powershell
.\reset-project.ps1
```

**Mac/Linux (Bash):**
```bash
chmod +x reset-project.sh
./reset-project.sh
```

**Manual Steps:**
```bash
# Clear Next.js cache
rm -rf .next

# Clear node modules
rm -rf node_modules
rm package-lock.json

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
npm install
```

### 2. **Browser Cache Issues**

Force refresh your browser:
- **Chrome/Edge:** `Ctrl+Shift+R` or `Ctrl+F5`
- **Firefox:** `Ctrl+Shift+R` 
- **Safari:** `Cmd+Option+R`

Or disable cache in DevTools:
1. Open DevTools (`F12`)
2. Go to Network tab
3. Check "Disable cache"

### 3. **Environment Consistency**

Ensure all team members:
- Use the same Node.js version (check with `node --version`)
- Use npm (not yarn) for consistency
- Have the same environment variables

### 4. **Tailwind Configuration Issues**

Check if all directories are included in `tailwind.config.js`:
```javascript
content: [
  './pages/**/*.{js,ts,jsx,tsx,mdx}',
  './components/**/*.{js,ts,jsx,tsx,mdx}',
  './chat-components/**/*.{js,ts,jsx,tsx,mdx}', // Important!
  './app/**/*.{js,ts,jsx,tsx,mdx}',
],
```

### 5. **Font Loading Issues**

If Inter font doesn't load:
1. Check network requests in DevTools
2. Try clearing browser cache
3. Check if Google Fonts is blocked

## 🔍 Diagnostic Tools

We've added a diagnostic component that shows in development mode:
- Look for "🔍 Style Diagnostics" in the bottom-right corner
- Click to expand and check:
  - Tailwind CSS loading status
  - Font loading status
  - Theme detection
  - Browser information

## 🎨 CSS Architecture

### File Structure
```
app/
├── globals.css          # Global styles and Tailwind
├── layout.js           # Root layout with theme provider
chat-components/
├── EmptyState.jsx      # Main chat empty state component
├── InputArea.jsx       # Chat input component
└── ...
```

### Key Classes Used
- `bg-slate-900 dark:bg-slate-100` - Background colors
- `text-slate-900 dark:text-slate-100` - Text colors
- `font-inter` - Font family
- `gradient-to-r from-indigo-500 to-cyan-500` - Gradient backgrounds

## 🐛 Debugging Steps

### Step 1: Check Diagnostics
1. Run the app in development mode
2. Look for the diagnostic panel in bottom-right
3. Check all status indicators

### Step 2: Inspect Elements
1. Right-click on problematic elements
2. Select "Inspect Element"
3. Check computed styles
4. Look for missing CSS classes

### Step 3: Network Tab
1. Open DevTools → Network
2. Refresh the page
3. Check if all CSS files load (200 status)
4. Look for failed font requests

### Step 4: Console Errors
1. Open DevTools → Console
2. Look for CSS-related errors
3. Check for theme provider errors

## 🎯 Quick Fixes

### Fix 1: Hard Refresh
```
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

### Fix 2: Clear Storage
```
DevTools → Application → Storage → Clear Site Data
```

### Fix 3: Reset Project
```bash
# Run the reset script
.\reset-project.ps1  # Windows
./reset-project.sh   # Mac/Linux
```

### Fix 4: Check Theme
```javascript
// In browser console
console.log(document.documentElement.classList)
// Should show 'dark' or 'light'
```

## 📋 Checklist for Team Members

Before reporting styling issues:

- [ ] Cleared browser cache (hard refresh)
- [ ] Ran reset script to clear all caches
- [ ] Checked diagnostic panel
- [ ] Verified same Node.js version as team
- [ ] Used `npm install` (not yarn)
- [ ] Checked for console errors
- [ ] Tested in incognito/private mode

## 🚀 Prevention

To prevent future styling inconsistencies:

1. **Use Version Control for Lock Files**
   - Commit `package-lock.json`
   - Use exact versions in `package.json`

2. **Document Environment Setup**
   - Share Node.js version
   - Share environment variables
   - Use the reset scripts regularly

3. **Regular Cache Clearing**
   - Clear browser cache weekly
   - Run reset script after major changes
   - Use incognito mode for testing

4. **Monitor Diagnostics**
   - Check diagnostic panel regularly
   - Share diagnostic info when reporting issues

## 📞 Getting Help

If styling issues persist:

1. Share diagnostic panel output
2. Share screenshots of the issue
3. Include browser and OS information
4. Share console errors if any

Remember: Most styling inconsistencies are due to caching issues and can be resolved by clearing all caches!

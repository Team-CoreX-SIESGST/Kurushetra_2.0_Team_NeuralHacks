# File Processing Utils

This directory contains utilities for handling file processing in both client-side and server-side environments.

## Files

### `fileProcessors.js` (Server-side only)
- Contains full file processing logic with Node.js dependencies
- Uses `mammoth` for DOCX processing and `Pptx2json` for PowerPoint files
- Should only be used in server-side contexts (API routes, server components)
- Has runtime checks to prevent client-side usage

### `fileProcessors-browser.js` (Client-side compatible)
- Browser-compatible version without Node.js dependencies
- Uses dynamic imports and graceful fallbacks
- Suitable for client-side React components
- Limited processing capabilities compared to server version

## Solution for "Module not found: Can't resolve 'fs'" Error

The error occurs because Node.js modules like `fs`, `mammoth`, and `pptx2json` are being imported in client-side code. Here's how we solved it:

### 1. Created Separate Files
- **Server-side**: `fileProcessors.js` with full functionality
- **Client-side**: `fileProcessors-browser.js` with browser-compatible code

### 2. Updated Next.js Config
Added webpack configuration to ignore Node.js modules on client-side:

```javascript
webpack: (config, { isServer }) => {
  if (!isServer) {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      net: false,
      tls: false,
    };
  }
  return config;
},
```

### 3. Modified Chat Components
- Removed import of `fileProcessors.js` in client components
- Created `processFileSimple()` function directly in the component
- This function creates basic file metadata without complex processing
- Actual file content processing is deferred to the server

### 4. Fallback Strategy
For client-side file handling, we use a simplified approach:
- Extract basic file metadata (name, type, size, lastModified)
- Set `data: null` to indicate server-side processing is needed
- Server will handle the actual file content extraction

## Usage

### Client-side (React Components)
```javascript
// Use the simple version for basic metadata
const processFileSimple = (file) => {
  return Promise.resolve({
    name: file.name,
    type: file.type,
    size: file.size,
    lastModified: file.lastModified,
    data: null // Server will process content
  });
};
```

### Server-side (API Routes)
```javascript
import { processFile } from '@/utils/fileProcessors';
// Full file processing with content extraction
```

This architecture separates concerns and ensures that Node.js-specific modules are only used on the server where they belong.

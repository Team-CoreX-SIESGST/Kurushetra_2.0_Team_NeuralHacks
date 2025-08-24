"use client";

import { useState, useEffect } from 'react';

export default function StyleDiagnostic() {
  const [diagnostics, setDiagnostics] = useState(null);
  
  useEffect(() => {
    const runDiagnostics = () => {
      const results = {
        // Check if Tailwind CSS is loaded
        tailwindLoaded: !!document.querySelector('style[data-emotion]') || 
                       getComputedStyle(document.documentElement).getPropertyValue('--tw-content') !== '',
        
        // Check if Inter font is loaded
        fontLoaded: document.fonts ? document.fonts.check('16px Inter') : 'unknown',
        
        // Check theme
        theme: document.documentElement.classList.contains('dark') ? 'dark' : 'light',
        
        // Check viewport
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight,
          ratio: window.devicePixelRatio || 1
        },
        
        // Check if styles are being applied
        testElement: (() => {
          const test = document.createElement('div');
          test.className = 'bg-blue-500 text-white p-4';
          test.style.position = 'absolute';
          test.style.left = '-9999px';
          document.body.appendChild(test);
          
          const styles = getComputedStyle(test);
          const result = {
            backgroundColor: styles.backgroundColor,
            color: styles.color,
            padding: styles.padding,
          };
          
          document.body.removeChild(test);
          return result;
        })(),
        
        // Browser info
        browser: {
          userAgent: navigator.userAgent,
          platform: navigator.platform,
          language: navigator.language,
        },
        
        // Performance timing
        timing: performance.timing ? {
          domComplete: performance.timing.domComplete - performance.timing.navigationStart,
          loadComplete: performance.timing.loadEventEnd - performance.timing.navigationStart,
        } : null,
      };
      
      setDiagnostics(results);
    };
    
    // Run diagnostics after a short delay to ensure DOM is ready
    const timer = setTimeout(runDiagnostics, 100);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Only show in development
  if (process.env.NODE_ENV === 'production') {
    return null;
  }
  
  return (
    <div className="fixed bottom-4 right-4 z-50">
      <details className="bg-gray-900 text-white p-4 rounded-lg shadow-lg max-w-xs text-xs">
        <summary className="cursor-pointer font-semibold mb-2">
          🔍 Style Diagnostics
        </summary>
        
        {diagnostics && (
          <div className="space-y-2">
            <div>
              <strong>Tailwind:</strong> {diagnostics.tailwindLoaded ? '✅' : '❌'}
            </div>
            
            <div>
              <strong>Inter Font:</strong> {
                diagnostics.fontLoaded === true ? '✅' : 
                diagnostics.fontLoaded === false ? '❌' : '❓'
              }
            </div>
            
            <div>
              <strong>Theme:</strong> {diagnostics.theme}
            </div>
            
            <div>
              <strong>Viewport:</strong> {diagnostics.viewport.width}×{diagnostics.viewport.height} 
              ({diagnostics.viewport.ratio}x)
            </div>
            
            <div>
              <strong>Test Styles:</strong>
              <ul className="ml-2 mt-1 space-y-1">
                <li>BG: {diagnostics.testElement.backgroundColor}</li>
                <li>Color: {diagnostics.testElement.color}</li>
                <li>Padding: {diagnostics.testElement.padding}</li>
              </ul>
            </div>
            
            <div>
              <strong>Browser:</strong> {
                diagnostics.browser.userAgent.includes('Chrome') ? 'Chrome' :
                diagnostics.browser.userAgent.includes('Firefox') ? 'Firefox' :
                diagnostics.browser.userAgent.includes('Safari') ? 'Safari' :
                'Other'
              }
            </div>
            
            {diagnostics.timing && (
              <div>
                <strong>Load Time:</strong> {diagnostics.timing.loadComplete}ms
              </div>
            )}
          </div>
        )}
      </details>
    </div>
  );
}

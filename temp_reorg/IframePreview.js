// IframePreview.js
// Reusable React component for secure iframe-based previews
import React from 'react';

/**
 * IframePreview
 * Renders a secure, responsive iframe preview for external or internal URLs.
 *
 * Props:
 *   url (string): The URL to display in the iframe
 *   title (string): Accessible title for the iframe
 *   height (string|number): Height of the iframe (default: 480)
 *   width (string|number): Width of the iframe (default: 100%)
 *   sandbox (string): Optional sandbox attributes (default: 'allow-scripts allow-same-origin')
 */
function IframePreview({ url, title = 'Preview', height = 480, width = '100%', sandbox = 'allow-scripts allow-same-origin' }) {
  if (!url) return <div className="iframe-preview-error">No URL provided</div>;

  return (
    <div className="iframe-preview-wrapper" style={{ width: '100%', border: '1px solid #eee', borderRadius: 8, overflow: 'hidden', margin: '1em 0' }}>
      <iframe
        src={url}
        title={title}
        width={width}
        height={height}
        frameBorder="0"
        allowFullScreen
        sandbox={sandbox}
        style={{ display: 'block', width: '100%', minHeight: height }}
      />
    </div>
  );
}

export default IframePreview;

// Utility functions shared across the application

// SHA256 hash function
export function sha256_digest(message) {
  const msgUint8 = new TextEncoder().encode(message);
  return crypto.subtle.digest('SHA-256', msgUint8)
    .then(hashBuffer => {
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
      return hashHex;
    })
}

// Show toast notification
export function showToast(message) {
  const copyToast = document.getElementById('copy-toast')
  copyToast.textContent = message
  copyToast.classList.add('show')
  setTimeout(() => {
    copyToast.classList.remove('show')
  }, 2000)
}

// Copy text to clipboard
export function copyToClipboard(text, element) {
  navigator.clipboard.writeText(text).then(() => {
    showToast('Copied to clipboard!')
    element.classList.add('copied')
    setTimeout(() => {
      element.classList.remove('copied')
    }, 500)
  }).catch(err => {
    console.error('Failed to copy:', err)
    showToast('Failed to copy')
  })
}

// Check if text is truncated and apply ticker animation
export function checkAndApplyTicker(element) {
  // Wait for next frame to ensure content is rendered
  requestAnimationFrame(() => {
    const textSpan = element.querySelector('.label-text')
    if (!textSpan) return
    
    // Check if text width exceeds container width
    const containerWidth = element.offsetWidth
    const textWidth = textSpan.scrollWidth
    
    if (textWidth > containerWidth) {
      element.classList.add('ticker')
    } else {
      element.classList.remove('ticker')
    }
  })
}

// Update Open Graph metadata for social sharing (when track changes)
export function updateMetadata(trackName) {
  if (trackName) {
    const ogTitle = document.querySelector('meta[property="og:title"]')
    const twitterTitle = document.querySelector('meta[name="twitter:title"]')
    const newTitle = 'Morph Ovum - ' + trackName
    
    if (ogTitle) ogTitle.setAttribute('content', newTitle)
    if (twitterTitle) twitterTitle.setAttribute('content', newTitle)
  } else {
    const ogTitle = document.querySelector('meta[property="og:title"]')
    const twitterTitle = document.querySelector('meta[name="twitter:title"]')
    const defaultTitle = 'Morph Ovum - FOSS Radio'
    
    if (ogTitle) ogTitle.setAttribute('content', defaultTitle)
    if (twitterTitle) twitterTitle.setAttribute('content', defaultTitle)
  }
}

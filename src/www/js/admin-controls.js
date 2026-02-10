// Admin controls functionality

import { sha256_digest, showToast } from './utils.js'

export class AdminControls {
  constructor(trackManager) {
    this.trackManager = trackManager
    this.lockButton = document.getElementById('admin-lock-button')
    this.adminSection = document.getElementById('admin-controls-section')
    this.modal = document.getElementById('admin-password-modal')
    this.passwordInput = document.getElementById('admin-password-input')
    this.cancelBtn = document.getElementById('admin-modal-cancel')
    this.submitBtn = document.getElementById('admin-modal-submit')
    this.errorDiv = document.getElementById('admin-modal-error')
  }
  
  initialize() {
    this.setupEventListeners()
    this.checkAdminAuth()
  }
  
  setupEventListeners() {
    // Lock button click
    this.lockButton.addEventListener('click', () => {
      // If already authenticated (has unlocked class), toggle visibility
      if (this.lockButton.classList.contains('unlocked')) {
        if (!this.adminSection.classList.contains('hidden')) {
          this.adminSection.classList.add('hidden')
          this.lockButton.classList.remove('pressed')
        } else {
          this.adminSection.classList.remove('hidden')
          this.lockButton.classList.add('pressed')
          this.updateToggleButtonStates()
        }
      } else {
        // Not authenticated yet, show password modal
        this.showPasswordModal()
      }
    })
    
    // Cancel button
    this.cancelBtn.addEventListener('click', () => this.hidePasswordModal())
    
    // Submit button
    this.submitBtn.addEventListener('click', () => this.submitAdminPassword())
    
    // Enter key in password input
    this.passwordInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.submitAdminPassword()
      }
    })
    
    // Escape key to close modal
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
        this.hidePasswordModal()
      }
    })
    
    // Click outside modal to close
    this.modal.addEventListener('click', (e) => {
      if (e.target === this.modal) {
        this.hidePasswordModal()
      }
    })
    
    // Admin control buttons
    const adminButtons = document.querySelectorAll('.admin-control-btn')
    adminButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const endpoint = btn.dataset.endpoint
        const label = btn.dataset.label
        
        // Check if any button is on cooldown
        if (btn.classList.contains('disabled')) {
          return // Still on cooldown
        }
        
        // Disable all admin buttons for 3 seconds
        adminButtons.forEach(b => b.classList.add('disabled'))
        setTimeout(() => {
          adminButtons.forEach(b => b.classList.remove('disabled'))
        }, 3000)
        
        this.callAdminAPI(endpoint, label)
      })
    })
  }
  
  // Check if user is authenticated
  checkAdminAuth() {
    fetch('./api/admin')
      .then(response => response.json())
      .then(json => {
        if (json.data === true) {
          this.showAdminControls()
        }
      })
      .catch(err => {
        console.log('Not authenticated')
      })
  }
  
  // Show admin controls section
  showAdminControls() {
    this.adminSection.classList.remove('hidden')
    this.lockButton.classList.add('unlocked')
    this.lockButton.classList.add('pressed')
    
    // Update lock icon to unlocked
    this.lockButton.innerHTML = `
      <svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M18,8h-1V6c0-2.76-2.24-5-5-5S7,3.24,7,6H9c0-1.66,1.34-3,3-3s3,1.34,3,3v2H6c-1.1,0-2,0.9-2,2v10c0,1.1,0.9,2,2,2h12c1.1,0,2-0.9,2-2V10C20,8.9,19.1,8,18,8z M12,17c-1.1,0-2-0.9-2-2s0.9-2,2-2s2,0.9,2,2S13.1,17,12,17z"/>
      </svg>
    `
    
    // Update toggle button states
    this.updateToggleButtonStates()
  }
  
  // Update toggle button icons based on current state
  updateToggleButtonStates() {
    // Check music status
    fetch('./api/music/currenttrack')
      .then(response => response.json())
      .then(json => {
        const musicBtn = document.getElementById('music-toggle-btn')
        const svg = musicBtn.querySelector('svg')
        if (json.data.is_playing) {
          // Music note in full green (playing)
          svg.innerHTML = '<path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z" fill="#a0ff50"/>'
          musicBtn.classList.add('state-on')
        } else {
          // Music note plain (stopped) - shows you can click to turn ON
          svg.innerHTML = '<path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>'
          musicBtn.classList.remove('state-on')
        }
      })
      .catch(err => console.log('Could not check music status'))
    
    // Check ambience status
    fetch('./api/ambience/currenttrack')
      .then(response => response.json())
      .then(json => {
        const ambienceBtn = document.getElementById('ambience-toggle-btn')
        const svg = ambienceBtn.querySelector('svg')
        if (json.data.is_playing) {
          // Storm cloud in full green (playing)
          svg.innerHTML = '<path d="M19.35 10.04C18.67 6.59 15.64 4 12 4c-1.48 0-2.85.43-4.01 1.17C6.65 5.7 5.31 6.96 4.56 8.58 2.61 9.08 1 10.88 1 13c0 2.76 2.24 5 5 5h13c2.21 0 4-1.79 4-4 0-2.05-1.54-3.73-3.54-3.96-.03-.32-.07-.64-.11-.96z" fill="#a0ff50"/><line x1="8" y1="18" x2="8" y2="21" stroke="#a0ff50" stroke-width="1.5" stroke-linecap="round"/><line x1="12" y1="18" x2="12" y2="22" stroke="#a0ff50" stroke-width="1.5" stroke-linecap="round"/><line x1="16" y1="18" x2="16" y2="21" stroke="#a0ff50" stroke-width="1.5" stroke-linecap="round"/>'
          ambienceBtn.classList.add('state-on')
        } else {
          // Storm cloud plain with green rain (stopped) - shows you can click to turn ON
          svg.innerHTML = '<path d="M19.35 10.04C18.67 6.59 15.64 4 12 4c-1.48 0-2.85.43-4.01 1.17C6.65 5.7 5.31 6.96 4.56 8.58 2.61 9.08 1 10.88 1 13c0 2.76 2.24 5 5 5h13c2.21 0 4-1.79 4-4 0-2.05-1.54-3.73-3.54-3.96-.03-.32-.07-.64-.11-.96z" fill="currentColor"/><line x1="8" y1="18" x2="8" y2="21" stroke="#a0ff50" stroke-width="1.5" stroke-linecap="round"/><line x1="12" y1="18" x2="12" y2="22" stroke="#a0ff50" stroke-width="1.5" stroke-linecap="round"/><line x1="16" y1="18" x2="16" y2="21" stroke="#a0ff50" stroke-width="1.5" stroke-linecap="round"/>'
          ambienceBtn.classList.remove('state-on')
        }
      })
      .catch(err => console.log('Could not check ambience status'))
  }
  
  // Show password modal
  showPasswordModal() {
    this.modal.classList.remove('hidden')
    this.errorDiv.classList.add('hidden')
    this.passwordInput.value = ''
    this.passwordInput.focus()
  }
  
  // Hide password modal
  hidePasswordModal() {
    this.modal.classList.add('hidden')
  }
  
  // Submit admin password
  submitAdminPassword() {
    const password = this.passwordInput.value
    
    if (!password) {
      this.errorDiv.textContent = 'Please enter a password'
      this.errorDiv.classList.remove('hidden')
      return
    }
    
    sha256_digest(password).then(hashedPassword => {
      const formData = new FormData()
      formData.append('password_hash', hashedPassword)
      
      fetch('./api/admin', {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(json => {
        if (json.msg === 'ok!') {
          this.hidePasswordModal()
          this.showAdminControls()
        } else {
          this.errorDiv.textContent = 'Incorrect password'
          this.errorDiv.classList.remove('hidden')
        }
      })
      .catch(err => {
        this.errorDiv.textContent = 'Error: ' + err.message
        this.errorDiv.classList.remove('hidden')
      })
    })
  }
  
  // Call admin API endpoint
  callAdminAPI(endpoint, label) {
    fetch(endpoint)
      .then(response => response.json())
      .then(json => {
        // Don't show toast notifications for admin actions
        // The visual feedback is immediate via the player state changes
        
        // Update toggle button states after toggle actions
        if (endpoint.includes('/toggle')) {
          setTimeout(() => this.updateToggleButtonStates(), 500)
          // Also update the current track/ambience labels
          setTimeout(() => this.trackManager.updateCurrentTrack(), 500)
          setTimeout(() => this.trackManager.updateCurrentAmbience(), 500)
        }
        
        // Update after skip
        if (endpoint.includes('/skip')) {
          setTimeout(() => this.trackManager.updateCurrentTrack(), 500)
        }
      })
      .catch(err => {
        // Only show errors
        showToast('Error: ' + err.message)
      })
  }
}

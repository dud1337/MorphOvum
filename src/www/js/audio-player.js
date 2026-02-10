// Audio player core functionality

export class AudioPlayer {
  constructor(audioElement, visualizer) {
    this.audioElement = audioElement
    this.visualizer = visualizer
    this.isPlaying = false
    this.audioResource = './listen.mp3'
    
    // DOM elements
    this.playButton = document.querySelector('.play.button')
    this.volumeControl = document.getElementById('volume-control')
    this.volumeIcon = document.getElementById('volume-icon')
    this.volumePercentage = document.getElementById('volume-percentage')
    
    // Load saved volume from localStorage or use default
    const savedVolume = localStorage.getItem('morphovum_volume')
    const initialVolume = savedVolume ? parseInt(savedVolume) : 40
    this.audioElement.volume = (initialVolume / 100) ** 2  // Quadratic curve for more natural volume feel
    this.volumeControl.value = initialVolume
    this.updateVolumeDisplay(initialVolume)
    
    this.setupEventListeners()
  }
  
  setupEventListeners() {
    // Play/pause button
    this.playButton.addEventListener('click', () => this.togglePlayPause())
    
    // Volume control handlers
    this.volumeControl.addEventListener("input", () => this.handleVolumeChange())
    this.volumeControl.addEventListener("change", () => this.handleVolumeChange())
    this.volumeControl.addEventListener("click", () => this.handleVolumeChange())
    
    // Click volume icon to mute/unmute
    this.volumeIcon.addEventListener('click', () => this.toggleMute())
    
    // Mouse wheel scroll on volume control
    const playerLayout = document.querySelector('.player-layout')
    playerLayout.addEventListener('wheel', (e) => this.handleVolumeWheel(e))
    
    // Keyboard shortcuts
    this.setupKeyboardShortcuts()
  }
  
  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ignore if typing in an input field
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return
      }
      
      switch(e.key) {
        case ' ': // Space - play/pause
          e.preventDefault()
          this.playButton.click()
          break
        case 'ArrowUp': // Arrow Up - volume up
          e.preventDefault()
          this.adjustVolume(5)
          break
        case 'ArrowDown': // Arrow Down - volume down
          e.preventDefault()
          this.adjustVolume(-5)
          break
        case 'm':
        case 'M': // M - mute/unmute
          e.preventDefault()
          this.volumeIcon.click()
          break
      }
    })
  }
  
  togglePlayPause() {
    const element = document.getElementById('play_button')
    
    if (!this.isPlaying) {
      // Initialize audio context on user interaction (required by browsers)
      this.visualizer.initAudioContext(this.audioElement)
      this.visualizer.resumeAudioContext()
      
      this.audioElement.src = `${this.audioResource}?${Date.now()}`
      this.audioElement.load()
      this.audioElement.play()
      this.isPlaying = true
      element.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg>'
      element.classList.remove('playing-icon')
      element.classList.add('paused-icon')
      
      // Start visualization
      this.visualizer.start()
      return
    }

    this.audioElement.pause()
    element.innerHTML = '&#9654;'
    element.classList.remove('paused-icon')
    element.classList.add('playing-icon')
    this.isPlaying = false
    
    // Stop visualization
    this.visualizer.stop()
  }
  
  // Update volume icon based on level
  updateVolumeDisplay(value) {
    const volume = parseInt(value)
    this.volumePercentage.textContent = volume + '%'
    
    // Update icon based on volume level
    if (volume === 0) {
      this.volumeIcon.textContent = '🔇'
    } else if (volume < 33) {
      this.volumeIcon.textContent = '🔉'
    } else if (volume < 66) {
      this.volumeIcon.textContent = '🔊'
    } else {
      this.volumeIcon.textContent = '🔊'
    }
    
    // Update slider background using CSS variable (works in Firefox)
    const percentage = volume
    this.volumeControl.style.setProperty('--volume-percentage', percentage + '%')
  }
  
  // Volume control handler with Firefox delay fix
  handleVolumeChange() {
    // Use setTimeout to ensure Firefox has updated the value
    setTimeout(() => {
      const value = this.volumeControl.value
      this.audioElement.volume = (value / 100) ** 2  // Quadratic curve for more natural volume feel
      this.updateVolumeDisplay(value)
      localStorage.setItem('morphovum_volume', value)
    }, 0)
  }
  
  // Mouse wheel scroll on volume control
  handleVolumeWheel(e) {
    e.preventDefault()
    const currentVolume = parseInt(this.volumeControl.value)
    const delta = e.deltaY < 0 ? 5 : -5 // Scroll up increases, scroll down decreases
    const newVolume = Math.max(0, Math.min(100, currentVolume + delta))
    this.volumeControl.value = newVolume
    this.audioElement.volume = (newVolume / 100) ** 2
    this.updateVolumeDisplay(newVolume)
    localStorage.setItem('morphovum_volume', newVolume)
  }
  
  // Adjust volume by delta
  adjustVolume(delta) {
    const newVolume = Math.max(0, Math.min(100, parseInt(this.volumeControl.value) + delta))
    this.volumeControl.value = newVolume
    this.audioElement.volume = (newVolume / 100) ** 2
    this.updateVolumeDisplay(newVolume)
    localStorage.setItem('morphovum_volume', newVolume)
  }
  
  // Toggle mute/unmute
  toggleMute() {
    if (this.audioElement.volume > 0) {
      this.volumeIcon.dataset.previousVolume = this.volumeControl.value
      this.volumeControl.value = 0
      this.audioElement.volume = 0
      this.updateVolumeDisplay(0)
      localStorage.setItem('morphovum_volume', '0')
    } else {
      const previousVolume = this.volumeIcon.dataset.previousVolume || '40'
      this.volumeControl.value = previousVolume
      this.audioElement.volume = (previousVolume / 100) ** 2
      this.updateVolumeDisplay(previousVolume)
      localStorage.setItem('morphovum_volume', previousVolume)
    }
  }
}

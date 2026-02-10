// Main application entry point

import { AudioVisualizer } from './visualizer.js'
import { AudioPlayer } from './audio-player.js'
import { TrackManager } from './track-manager.js'
import { AdminControls } from './admin-controls.js'
import { connectWebSocket } from './websocket.js'
import { checkAndApplyTicker } from './utils.js'

// Initialize application
(() => {
  // Create audio element
  const audioElement = new Audio()
  
  // Initialize visualizer
  const visualizer = new AudioVisualizer('spectrum-canvas')
  
  // Initialize audio player
  const player = new AudioPlayer(audioElement, visualizer)
  
  // Initialize track manager
  const trackManager = new TrackManager()
  
  // Initialize admin controls
  const adminControls = new AdminControls(trackManager)
  adminControls.initialize()
  
  // Setup click-to-copy for spectrum labels
  trackManager.setupClickToCopy()
  
  // Initial updates
  trackManager.updateCurrentTrack()
  trackManager.updateCurrentAmbience()
  trackManager.buildPlaylist()
  
  // Draw initial idle spectrum
  visualizer.drawSpectrum()
  
  // Connect WebSocket with callbacks
  connectWebSocket({
    onMusicChanged: () => {
      trackManager.updateCurrentTrack()
      trackManager.buildPlaylist()
    },
    onAmbienceChanged: () => {
      trackManager.updateCurrentAmbience()
    },
    onUpdateToggleStates: () => {
      adminControls.updateToggleButtonStates()
    }
  })
  
  // Handle window resize with debouncing to prevent lag
  let resizeTimeout = null
  window.addEventListener('resize', () => {
    // Clear any existing timeout
    if (resizeTimeout) {
      clearTimeout(resizeTimeout)
    }
    
    // Debounce: wait 150ms after last resize event before updating
    resizeTimeout = setTimeout(() => {
      visualizer.resize()
      
      // Only redraw once without starting a new animation loop
      if (!player.isPlaying) {
        // Only call drawSpectrum if not playing (no loop running)
        visualizer.drawSpectrum()
      }
      // If playing, the existing requestAnimationFrame loop will pick up new dimensions
      
      // Recheck ticker on resize
      const spectrumSongLabel = document.getElementById('spectrum-song-label')
      const spectrumAmbienceLabel = document.getElementById('spectrum-ambience-label')
      checkAndApplyTicker(spectrumSongLabel)
      checkAndApplyTicker(spectrumAmbienceLabel)
    }, 150)
  })
})()

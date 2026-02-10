// Track management and display

import { copyToClipboard, checkAndApplyTicker, updateMetadata } from './utils.js'

export class TrackManager {
  constructor() {
    this.spectrumSongLabel = document.getElementById('spectrum-song-label')
    this.spectrumAmbienceLabel = document.getElementById('spectrum-ambience-label')
  }
  
  updateCurrentTrack() {
    fetch('./api/music/currenttrack')
      .then(response => response.json())
      .then(json => {
        if (json.data.is_playing) {
          // Remove ticker class first to reset animation
          this.spectrumSongLabel.classList.remove('ticker')
          const songText = '♫ ' + json.msg
          this.spectrumSongLabel.innerHTML = '<span class="label-text">' + songText + '</span>'
          this.spectrumSongLabel.dataset.fullText = json.msg
          checkAndApplyTicker(this.spectrumSongLabel)
          
          // Update page title and metadata with currently playing track
          document.title = 'Morph Ovum - ' + json.msg
          updateMetadata(json.msg)
        } else {
          // Show "Music is paused" when not playing
          this.spectrumSongLabel.classList.remove('ticker')
          this.spectrumSongLabel.innerHTML = '<span class="label-text">♫ Music is paused</span>'
          this.spectrumSongLabel.dataset.fullText = 'Music is paused'
          
          // Reset page title and metadata when nothing is playing
          document.title = 'Morph Ovum'
          updateMetadata(null)
        }
      })
  }

  updateCurrentAmbience() {
    fetch('./api/ambience/currenttrack')
      .then(response => response.json())
      .then(json => {
        if (json.data.is_playing) {
          // Remove ticker class first to reset animation
          this.spectrumAmbienceLabel.classList.remove('ticker')
          const ambienceText = '☮ ' + json.msg
          this.spectrumAmbienceLabel.innerHTML = '<span class="label-text">' + ambienceText + '</span>'
          this.spectrumAmbienceLabel.dataset.fullText = json.msg
          checkAndApplyTicker(this.spectrumAmbienceLabel)
        } else {
          // Show "Ambience is paused" when not playing
          this.spectrumAmbienceLabel.classList.remove('ticker')
          this.spectrumAmbienceLabel.innerHTML = '<span class="label-text">☮ Ambience is paused</span>'
          this.spectrumAmbienceLabel.dataset.fullText = 'Ambience is paused'
        }
      })
  }
  
  buildPlaylist() {
    fetch('./api/music/history')
      .then(response => response.json())
      .then(json => {
        const listItems = json.data.reverse().slice(1).map(track => {
          const li = document.createElement('li')
          li.className = 'track-list__track'
          
          const trackText = document.createElement('span')
          trackText.className = 'track-text'
          trackText.textContent = track
          
          const copyIcon = document.createElement('span')
          copyIcon.className = 'track-copy-icon'
          copyIcon.innerHTML = '📋'
          copyIcon.setAttribute('aria-label', 'Copy')
          
          li.appendChild(trackText)
          li.appendChild(copyIcon)
          
          // Click to copy functionality
          li.addEventListener('click', function() {
            copyToClipboard(track, li)
          })
          
          return li
        })
        const trackList = document.querySelector('.track-list')
        trackList.innerHTML = ''

        const trackListEnding = trackList.querySelector('br')

        listItems.forEach(li => {
          trackList.insertBefore(li, trackListEnding)
        })
      })
  }
  
  // Setup click-to-copy for spectrum labels
  setupClickToCopy() {
    this.spectrumSongLabel.addEventListener('click', function() {
      if (this.dataset.fullText) {
        copyToClipboard(this.dataset.fullText, this)
      }
    })
    
    this.spectrumAmbienceLabel.addEventListener('click', function() {
      if (this.dataset.fullText) {
        copyToClipboard(this.dataset.fullText, this)
      }
    })
  }
}

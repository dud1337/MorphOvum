// Audio spectrum visualizer

export class AudioVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId)
    this.canvasCtx = this.canvas.getContext('2d')
    this.audioContext = null
    this.analyser = null
    this.dataArray = null
    this.bufferLength = null
    this.animationId = null
    this.peakValues = [] // For peak hold mode
    this.isPlaying = false
    
    // Set canvas size
    this.canvas.width = this.canvas.offsetWidth || 600
    this.canvas.height = this.canvas.offsetHeight || 120
  }
  
  // Initialize Web Audio API for visualization
  initAudioContext(audioElement) {
    if (this.audioContext) return
    
    this.audioContext = new (window.AudioContext || window.webkitAudioContext)()
    this.analyser = this.audioContext.createAnalyser()
    this.analyser.fftSize = 512
    this.analyser.smoothingTimeConstant = 0.8
    this.analyser.minDecibels = -90
    this.analyser.maxDecibels = -10
    
    const source = this.audioContext.createMediaElementSource(audioElement)
    source.connect(this.analyser)
    this.analyser.connect(this.audioContext.destination)
    
    this.bufferLength = this.analyser.frequencyBinCount
    this.dataArray = new Uint8Array(this.bufferLength)
    
    // Initialize peak values array
    this.peakValues = new Array(64).fill(0)
  }
  
  // Resume audio context if suspended
  resumeAudioContext() {
    if (this.audioContext && this.audioContext.state === 'suspended') {
      this.audioContext.resume()
    }
  }
  
  // Get frequency data with peak hold
  getFrequencyData() {
    this.analyser.getByteFrequencyData(this.dataArray)
    
    const barCount = 64
    const values = []
    const nyquist = this.audioContext.sampleRate / 2
    
    // Balanced semi-log: 40% linear + 60% log with peak hold
    const minFreq = 30
    const maxFreq = Math.min(12000, nyquist)
    
    for (let i = 0; i < barCount; i++) {
      const t = i / barCount
      const linearPos = minFreq + t * (maxFreq - minFreq)
      const logPos = minFreq * Math.pow(maxFreq / minFreq, t)
      const freq = linearPos * 0.4 + logPos * 0.6
      
      const binIndex = Math.floor(freq / nyquist * this.bufferLength)
      const dataIndex = Math.min(binIndex, this.bufferLength - 1)
      
      let sum = 0
      const avgRange = 2
      for (let j = -avgRange; j <= avgRange; j++) {
        const idx = Math.max(0, Math.min(this.bufferLength - 1, dataIndex + j))
        sum += this.dataArray[idx]
      }
      const avgValue = sum / (avgRange * 2 + 1)
      const freqBoost = 1 + (t * 0.35)
      const currentValue = avgValue * freqBoost
      
      // Update peak with decay
      if (currentValue > this.peakValues[i]) {
        this.peakValues[i] = currentValue
      } else {
        this.peakValues[i] *= 0.985 // Much slower decay - peaks stay longer
      }
      
      values.push(currentValue)
    }
    
    return values
  }
  
  // Draw spectrum visualization
  drawSpectrum() {
    if (!this.analyser || !this.isPlaying) {
      // Draw idle state with dim bars
      this.canvasCtx.fillStyle = '#1a1b1e'
      this.canvasCtx.fillRect(0, 0, this.canvas.width, this.canvas.height)
      
      const barCount = 64
      // Adjust gap based on canvas width (tighter on smaller screens)
      const gapRatio = this.canvas.width < 500 ? 0.15 : 0.2
      const barWidth = (this.canvas.width / barCount) * (1 - gapRatio)
      const gap = (this.canvas.width / barCount) * gapRatio
      
      for (let i = 0; i < barCount; i++) {
        const x = i * (barWidth + gap)
        const barHeight = 8
        const y = this.canvas.height - barHeight
        
        // Dim light gray bars for idle state
        const gradient = this.canvasCtx.createLinearGradient(0, y, 0, this.canvas.height)
        gradient.addColorStop(0, 'rgba(139, 157, 195, 0.3)')
        gradient.addColorStop(1, 'rgba(184, 197, 214, 0.3)')
        this.canvasCtx.fillStyle = gradient
        this.canvasCtx.fillRect(x, y, barWidth, barHeight)
      }
      
      if (this.isPlaying) {
        this.animationId = requestAnimationFrame(() => this.drawSpectrum())
      }
      return
    }
    
    this.animationId = requestAnimationFrame(() => this.drawSpectrum())
    
    this.canvasCtx.fillStyle = '#1a1b1e'
    this.canvasCtx.fillRect(0, 0, this.canvas.width, this.canvas.height)
    
    const values = this.getFrequencyData()
    const barCount = values.length
    
    // Adjust gap based on canvas width (tighter on smaller screens)
    const gapRatio = this.canvas.width < 500 ? 0.15 : 0.2
    const barWidth = (this.canvas.width / barCount) * (1 - gapRatio)
    const gap = (this.canvas.width / barCount) * gapRatio
    
    for (let i = 0; i < barCount; i++) {
      const barHeight = Math.min((values[i] / 255) * this.canvas.height * 0.9, this.canvas.height * 0.95)
      
      const x = i * (barWidth + gap)
      const y = this.canvas.height - barHeight
      
      // Create smooth gradient for light bars
      const gradient = this.canvasCtx.createLinearGradient(0, y, 0, this.canvas.height)
      const intensity = barHeight / (this.canvas.height * 0.9)
      
      // Light gray gradient - softer, more subdued
      const topBrightness = 0.35 + (intensity * 0.55) // 35% to 90% brightness at top
      const bottomBrightness = 0.45 + (intensity * 0.45) // 45% to 90% brightness at bottom
      
      // Calculate RGB values for smooth light gray gradient
      const topR = Math.floor(107 + (108 * topBrightness))
      const topG = Math.floor(122 + (93 * topBrightness))
      const topB = Math.floor(146 + (69 * topBrightness))
      
      const midR = Math.floor(139 + (76 * bottomBrightness))
      const midG = Math.floor(157 + (58 * bottomBrightness))
      const midB = Math.floor(195 + (20 * bottomBrightness))
      
      const bottomR = Math.floor(175 + (40 * intensity))
      const bottomG = Math.floor(190 + (25 * intensity))
      const bottomB = Math.floor(215 + (10 * intensity))
      
      gradient.addColorStop(0, `rgba(${topR}, ${topG}, ${topB}, 0.9)`)
      gradient.addColorStop(0.5, `rgba(${midR}, ${midG}, ${midB}, 0.92)`)
      gradient.addColorStop(1, `rgba(${bottomR}, ${bottomG}, ${bottomB}, 0.95)`)
      
      this.canvasCtx.fillStyle = gradient
      this.canvasCtx.fillRect(x, y, barWidth, barHeight)
      
      // Add subtle glow for high intensity
      if (intensity > 0.65) {
        this.canvasCtx.shadowBlur = 8 + (intensity * 6)
        this.canvasCtx.shadowColor = `rgba(184, 197, 214, ${0.4 + intensity * 0.4})`
        this.canvasCtx.fillRect(x, y, barWidth, barHeight)
        this.canvasCtx.shadowBlur = 0
      }
      
      // Draw peak hold indicator in lime green
      if (this.peakValues[i] > 0) {
        const peakHeight = Math.min((this.peakValues[i] / 255) * this.canvas.height * 0.9, this.canvas.height * 0.95)
        const peakY = this.canvas.height - peakHeight
        
        this.canvasCtx.fillStyle = '#a0ff50'
        this.canvasCtx.fillRect(x, peakY - 2, barWidth, 3)
        
        // Glow on peak
        this.canvasCtx.shadowBlur = 6
        this.canvasCtx.shadowColor = 'rgba(160, 255, 80, 0.8)'
        this.canvasCtx.fillRect(x, peakY - 2, barWidth, 3)
        this.canvasCtx.shadowBlur = 0
      }
    }
  }
  
  // Start visualization
  start() {
    this.isPlaying = true
    this.drawSpectrum()
  }
  
  // Stop visualization
  stop() {
    this.isPlaying = false
    if (this.animationId) {
      cancelAnimationFrame(this.animationId)
      this.animationId = null
    }
    // Draw idle state
    this.drawSpectrum()
  }
  
  // Resize canvas
  resize() {
    this.canvas.width = this.canvas.offsetWidth || 600
    this.canvas.height = this.canvas.offsetHeight || 120
  }
}

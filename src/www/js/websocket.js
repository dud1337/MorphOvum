// WebSocket connection management

export function connectWebSocket(callbacks) {
  var loc = window.location, new_uri;
  if (loc.protocol === "https:") {
    new_uri = "wss:";
  } else {
    new_uri = "ws:";
  }
  new_uri += "//" + loc.host + loc.pathname + 'notify';

  const ws = new WebSocket(new_uri)

  ws.addEventListener('message', (event) => {
    switch (event.data) {
      case 'music_changed':
      case 'music_paused':
        if (callbacks.onMusicChanged) callbacks.onMusicChanged()
        if (callbacks.onUpdateToggleStates) callbacks.onUpdateToggleStates()
        return
      case 'ambience_changed':
      case 'ambience_paused':
        if (callbacks.onAmbienceChanged) callbacks.onAmbienceChanged()
        if (callbacks.onUpdateToggleStates) callbacks.onUpdateToggleStates()
        return
    }
  })
  
  ws.addEventListener("close", () => {
    connectWebSocket(callbacks); // Attempt to reconnect after connection closure
  });

  ws.addEventListener("error", (error) => {
    connectWebSocket(callbacks); // Attempt to reconnect on error
  });
}

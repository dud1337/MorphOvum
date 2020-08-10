var api_funcs = [{"name": "ambience_current_playlist", "resource": "ambience/current/playlist", "description": "Return the currently playing ambience playlist", "argument": null}, {"name": "ambience_current_track", "resource": "ambience/current/track", "description": "Return the currently playing ambience track", "argument": null}, {"name": "ambience_history", "resource": "ambience/history", "description": "Returns up to 100 of the last played tracks for a player", "argument": null}, {"name": "ambience_ls", "resource": "ambience/ls", "description": "List the contents of a subdirectory in the ambience directory", "argument": "directory"}, {"name": "ambience_lsc", "resource": "ambience/lsc", "description": "Enqueue a file or the contents of a subdirectory in the music directory", "argument": "directory"}, {"name": "ambience_lsp", "resource": "ambience/lsp", "description": "Play a file or the contents of a subdirectory in the ambience directory", "argument": "directory"}, {"name": "ambience_skip", "resource": "ambience/skip", "description": "Skip the current ambience track", "argument": null}, {"name": "ambience_toggle", "resource": "ambience/toggle", "description": "Toggle the playing of the ambience player", "argument": null}, {"name": "ambience_wp", "resource": "ambience/wp", "description": "Play the web resource in the ambience player", "argument": "url"}, {"name": "clips_now", "resource": "clips/now", "description": "Schedule a clip to be played now", "argument": null}, {"name": "clips_toggle", "resource": "clips/toggle", "description": "Toggle the playing of clips", "argument": null}, {"name": "music_current_playlist", "resource": "music/current/playlist", "description": "Return the currently playing music playlist", "argument": null}, {"name": "music_current_track", "resource": "music/current/track", "description": "Return the currently playing music track", "argument": null}, {"name": "music_history", "resource": "music/history", "description": "Returns the last music tracks played (max 100)", "argument": null}, {"name": "music_ls", "resource": "music/ls", "description": "List the contents of a subdirectory in the music directory", "argument": "directory"}, {"name": "music_lsc", "resource": "music/lsc", "description": "Enqueue a file or the contents of a subdirectory in the music directory", "argument": "directory"}, {"name": "music_lsp", "resource": "music/lsp", "description": "Play a file or the contents of a subdirectory in the music directory", "argument": "directory"}, {"name": "music_playlist", "resource": "music/playlist", "description": "Plays a playlist from available playlists. An int n input will play the nth playlist", "argument": "playlist"}, {"name": "music_playlists", "resource": "music/playlists", "description": "Lists available playlists", "argument": "playlist"}, {"name": "music_skip", "resource": "music/skip", "description": "Skip the currently playing music track", "argument": null}, {"name": "music_toggle", "resource": "music/toggle", "description": "Toggle the playing of the music player", "argument": null}, {"name": "music_wp", "resource": "music/wp", "description": "Play the web resource in the music player", "argument": "url"}];

function getter_n_setter(resource, results_id) {
  // sets a GET function for each api function
  function unique_getter() {
		var xhttp = new XMLHttpRequest();
  	xhttp.onreadystatechange = function() {
   	  if (this.readyState == 4 && this.status == 200) {
    		document.getElementById(results_id).innerHTML = this.responseText;
    	}
  	}
  	xhttp.open("GET", resource, true);
  	xhttp.send();
  };
  return unique_getter
};
  
function create_api_frontend_button(api_metadata, container) {
  // Create div with interaction for API function
  var api_func_div = document.createElement("div");
  api_func_div.id = api_metadata.name;
  
  var descr_div = document.createElement("div");
  descr_div.id = api_metadata.name + "_description";
  descr_div.innerHTML = api_metadata["description"];
  descr_div.class = "api_entry_description";
  api_func_div.appendChild(descr_div);
  
  if (api_metadata.argument) {
    var arg_input = document.createElement("input");
    arg_input.id = api_metadata.name + "id";
    arg_input.type = "text";
    arg_input.placeholder = api_metadata.argument;
    arg_input.classList.add("api_entry_arg_input");
    api_func_div.appendChild(arg_input);
  };
  
  var resp_box = document.createElement("div");
  resp_box.id = api_metadata.name + "_resp";
  resp_box.classList.add("resp_box_class");
  api_func_div.appendChild(resp_box);
  
  var req_button = document.createElement("input");
  req_button.id = api_metadata.name + "_call";
  req_button.type = "button";
  req_button.value = "Request";
  req_button.classList.add("api_entry_req_button");
  req_button.onclick = getter_n_setter("" + api_metadata.resource, resp_box.id);
  
  api_func_div.appendChild(req_button);
  
  container.appendChild(api_func_div);
};

window.onload = function() {
	var container = document.getElementById("api_interface_container");
	for (i = 0; i < api_funcs.length; i++) {
		create_api_frontend_button(api_funcs[i], container);
	}
}



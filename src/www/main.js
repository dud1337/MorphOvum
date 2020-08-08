var api_funcs = {
  music_ls: {
    name:       "music_ls",
    resource:   "music/ls/",
    description:"List the music files available in a subdirectory of the music or ambience directory",
    argument:   "Directory"
  },
  music_current_track: {
    name:       "music_current_track",
    resource:   "music/current/track",
    description:"Get the currently playing music or ambience track",
    argument:   false
  }
};

var container = document.getElementById("api_interface_container");

function getter_n_setter(resource, results_id) {
  // sets a GET function for each api function
  function butt() {
		var xhttp = new XMLHttpRequest();
  	xhttp.onreadystatechange = function() {
   	  if (this.readyState == 4 && this.status == 200) {
    		document.getElementById(results_id).innerHTML = this.responseText;
    	}
  	}
  	xhttp.open("GET", resource, true);
  	xhttp.send();
  };
  return butt
};
  
function create_api_frontend_button(api_metadata) {
  // Create div with interaction for API function
  var api_func_div = document.createElement("div");
  api_func_div.id = api_metadata.name;
  
  var descr_div = document.createElement("div");
  descr_div.id = api_metadata.name + "_description";
  descr_div.innerHTML = api_metadata.description;
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
  req_button.onclick = getter_n_setter(api_metadata.resource, resp_box.id);
  
	api_func_div.appendChild(req_button);
  
  container.appendChild(api_func_div);
};

for (api_func in api_funcs) {
	create_api_frontend_button(api_funcs[api_func]);
}

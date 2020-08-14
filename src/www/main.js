fetch('./api_data.json')
	.then(response => response.json())
	.then(json => {
		var container = document.getElementById("api_interface_container");
		for (i = 0; i < json.length; i++) {
			create_api_frontend_button(json[i], container);
		}
		create_admin_api_module();
})

function request_function_generator(api_metadata) {
    // sets a GET or POST function for each api function
	var resource = api_metadata.resource;
	if ( api_metadata.argument ) {
		function request_function() {
			var xhttp = new XMLHttpRequest();
			xhttp.onreadystatechange = function() {
				if (this.readyState == 4 && this.status == 200) {
					document.getElementById(api_metadata.name + '_resp').innerHTML = this.responseText;
				}
			}
			xhttp.open("POST", resource, true);
			xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
			xhttp.send(api_metadata.argument + '=' + document.getElementById(api_metadata.name + '_arg').value);
		}
	} else {
		function request_function() {
			var xhttp = new XMLHttpRequest();
			xhttp.onreadystatechange = function() {
				if (this.readyState == 4 && this.status == 200) {
					document.getElementById(api_metadata.name + '_resp').innerHTML = this.responseText;
				}
			}
			xhttp.open("GET", resource, true);
			xhttp.send();
		}
	}
	return request_function;
}
    
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
        arg_input.id = api_metadata.name + "_arg";
        arg_input.type = "text";
        arg_input.placeholder = api_metadata.argument;
		arg_input.classList.add("api_entry_arg_input");
        api_func_div.appendChild(arg_input);
    };
    
    var resp_box = document.createElement("div");
    resp_box.id = api_metadata.name + "_resp";
    resp_box.classList.add("resp_box_class");
    
    var req_button = document.createElement("input");
    req_button.id = api_metadata.name + "_call";
    req_button.type = "button";
    req_button.value = "Request";
    req_button.classList.add("api_entry_req_button");
    req_button.onclick = request_function_generator(api_metadata);
    
    api_func_div.appendChild(req_button);
    api_func_div.appendChild(resp_box);

    container.appendChild(api_func_div);
};

function create_admin_api_module() {
	var admin_container = document.getElementById("admin_login_container");
	var api_metadata = {"name":"admin", "resource":"admin", "description":"Enter admin password to use admin-only functions", "argument":"password_hash"};

    // Create div with interaction for API function
    var api_func_div = document.createElement("div");
    api_func_div.id = api_metadata.name;
    
    var descr_div = document.createElement("div");
    descr_div.id = api_metadata.name + "_description";
    descr_div.innerHTML = api_metadata["description"];
    descr_div.class = "api_entry_description";
    api_func_div.appendChild(descr_div);
    
    var arg_input = document.createElement("input");
    arg_input.id = api_metadata.name + "_arg";
    arg_input.type = "text";
    arg_input.placeholder = "password";
	arg_input.classList.add("api_entry_arg_input");
    api_func_div.appendChild(arg_input);
    
	var resp_box = document.createElement("div");
    resp_box.id = api_metadata.name + "_resp";
    resp_box.classList.add("resp_box_class");
    
    var req_button = document.createElement("input");
    req_button.id = api_metadata.name + "_call";
    req_button.type = "button";
    req_button.value = "Request";
    req_button.classList.add("api_entry_req_button");

	function request_function() {
		var xhttp = new XMLHttpRequest();
		xhttp.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				document.getElementById(api_metadata.name + '_resp').innerHTML = this.responseText;
			}
		}
		xhttp.open("POST", api_metadata.resource, true);
		xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
		xhttp.send(api_metadata.argument + '=' + document.getElementById(api_metadata.name + '_arg').value);
	}

    req_button.onclick = request_function;

    api_func_div.appendChild(req_button);
    api_func_div.appendChild(resp_box);

    admin_container.appendChild(api_func_div);
};

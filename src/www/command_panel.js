fetch('./api_data.json')
	.then(response => response.json())
	.then(json => {
		var container = document.getElementById("api_interface_container");
		create_api_table_row(
			{"name":"admin", "resource":"admin", "description":"Enter admin password to use admin-only functions", "argument":"password_hash"},
			container,
			true
		);
		for (i = 0; i < json.length; i++) {
			create_api_table_row(
				json[i],
				container,
				false
			);
		}
})

function sha256_digest(message) {
    const msgUint8 = new TextEncoder().encode(message);
    return crypto.subtle.digest('SHA-256', msgUint8)
      .then(hashBuffer => {
        const hashArray = Array.from(new Uint8Array(hashBuffer)); 
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        return hashHex;
      })
}

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
    
function create_api_table_row(api_metadata, container, admin) {
	//Create a table row for an api function
    var api_func_tr = document.createElement("tr");
    api_func_tr.id = api_metadata.name;
	api_func_tr.classList.add("tr_api");
    
    var descr_td = document.createElement("td");
    descr_td.id = api_metadata.name + "_description";
    descr_td.innerHTML = api_metadata["description"];
    descr_td.classList.add("td_description");
    api_func_tr.appendChild(descr_td);
    
	var arg_td = document.createElement("td");
	arg_td.classList.add("td_arg");
	if (api_metadata.argument) {
        var arg_input = document.createElement("input");
        arg_input.id = api_metadata.name + "_arg";
		if (admin) {
	        arg_input.type = "password";
	        arg_input.placeholder = "password";
		} else {
		    arg_input.type = "text";
	        arg_input.placeholder = api_metadata.argument;
		}
		arg_input.classList.add("api_entry_arg_input");
        arg_td.appendChild(arg_input);
    };
	api_func_tr.appendChild(arg_td);
    
    var resp_td = document.createElement("td");
    resp_td.id = api_metadata.name + "_resp";
	resp_td.innerHTML = ' ';
    resp_td.classList.add("td_resp");
   
	var req_td = document.createElement("td");
	req_td.classList.add("td_req");
    var req_button = document.createElement("input");
    req_button.id = api_metadata.name + "_call";
    req_button.type = "button";
    req_button.value = "Request";
    req_button.classList.add("api_entry_req_button");
	if (admin) {
		function request_function() {
			var xhttp = new XMLHttpRequest();
			xhttp.onreadystatechange = function() {
				if (this.readyState == 4 && this.status == 200) {
					document.getElementById(api_metadata.name + '_resp').innerHTML = this.responseText;
				}
			}
			xhttp.open("POST", api_metadata.resource, true);
			xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
			sha256_digest(document.getElementById(api_metadata.name + '_arg').value).then(hashed_message => {
				xhttp.send(api_metadata.argument + '=' + hashed_message);
			})
		}
    	req_button.onclick = request_function;
	} else {
	    req_button.onclick = request_function_generator(api_metadata);
	}
	req_td.appendChild(req_button);
    
    api_func_tr.appendChild(req_td);
    api_func_tr.appendChild(resp_td);

    container.appendChild(api_func_tr);
};

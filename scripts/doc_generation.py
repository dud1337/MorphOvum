#####################################################################
#
#   Generate API documentation in README.md and doc.json file
#
#####################################################################
import sys
import json
from inspect import getfullargspec
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(0, '../src')
import io_functions

api_flags = ['admin', 'busy', 'patience']

api_list = []
readme_table_post = '**POST requests**\n\n'
readme_table_post += '| Resource | Argument | Flags | Function |\n| ------ | ------ | ------ | ------ |\n'
readme_table_post += '| `/admin` | `password_hash` | | Sent a SHA256 hash of the admin password to obtain an admin session |\n'

readme_table_get = '**GET requests**\n\n'
readme_table_get += '| Resource | Flags | Function |\n| ------ | ------ | ------ |\n'

for attr_name in dir(io_functions.InputHandler):
    attr = getattr(io_functions.InputHandler, attr_name)
    if hasattr(attr, 'is_api_method'):
        method_data_for_json = {
            'name'          :attr_name,
            'resource'      :attr_name.replace('_', '/'),
            'description'   :attr.__doc__
        }
        is_post = len(getfullargspec(attr)[0]) > 1

        readme_tmp = '| `/' + attr_name.replace('_', '/') + '` '

        if len(getfullargspec(attr)[0]) > 1:
            method_arg = getfullargspec(attr)[0][1]
            readme_tmp += '| `' + method_arg + '` |'
            method_data_for_json['argument'] = method_arg
        else:
            method_arg = None
            method_data_for_json['argument'] = None
            
        api_list.append(method_data_for_json)

        for api_flag in api_flags:
            if hasattr(attr, 'is_' + api_flag + '_method'):
                readme_tmp += ' `' + api_flag + '`'
        readme_tmp += ' | '

        readme_tmp += attr.__doc__ + ' |\n'

        if is_post:
            readme_table_post += readme_tmp
        else:
            readme_table_get += readme_tmp

print(readme_table_post)
print(readme_table_get)
with open('../src/www/api_data.json', 'w') as f:
    f.write(json.dumps(api_list))

#####################################################################
#
#   Generate API documentation in README.md and doc.json file
#
#####################################################################
import sys
import json
from inspect import getfullargspec
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(0, '../src/core')
import io_functions

api_flags = ['admin', 'busy', 'patience']

api_list = []
readme_table = '| Resource | Flags | Function |\n| ------ | ------ | ------ |\n'

for attr_name in dir(io_functions.InputHandler):
    attr = getattr(io_functions.InputHandler, attr_name)
    if hasattr(attr, 'is_api_method'):
        method_data_for_json = {
            'name'          :attr_name,
            'resource'      :attr_name.replace('_', '/'),
            'description'   :attr.__doc__
        }
        if len(getfullargspec(attr)[0]) > 1:
            method_arg = getfullargspec(attr)[0][1]
            readme_table += '| `/' + attr_name.replace('_', '/') + '/<' + method_arg + '> `|'
            method_data_for_json['argument'] = method_arg
        else:
            method_arg = None
            readme_table += '| `/' + attr_name.replace('_', '/') + ' `|'
            method_data_for_json['argument'] = None
        api_list.append(method_data_for_json)

        for api_flag in api_flags:
            if hasattr(attr, 'is_' + api_flag + '_method'):
                readme_table += ' `' + api_flag + '`'
        readme_table += ' | '

        readme_table += attr.__doc__ + ' |\n'

print(readme_table)
print(json.dumps(api_list))
with open('../src/www/api_data.json', 'w') as f:
    f.write(json.dumps(api_list))

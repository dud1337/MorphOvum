import requests
import hashlib

password = 'changeme'

port = 8139
base_url = 'http://127.0.0.1:' + str(port)

data = {
    'password_hash':hashlib.sha256(password).hexdigest()
}

with requests.Session() as s:
    print('Try admin-only command:')
    test = s.get(base_url + '/music/lsp')
    print(test.content)
    
    print('Try to login:')
    login = s.post(base_url + '/admin', data=data)
    print(login.content)

    print('Try admin-only command:')
    test = s.get(base_url + '/clips/now')

    print(test.content)

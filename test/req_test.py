import requests

port = 8139
base_url = 'http://127.0.0.1:' + str(port)

data = {
    'password_hash':'057ba03d6c44104863dc7361fe4578965d1887360f90a0895882e58a6248fc86'
}

with requests.Session() as s:
    print('Try admin-only command:')
    test = s.get(base_url + '/music/lsp')
    print(test.content)
    
    print('Try to login:')
    login = s.post(base_url + '/admin', data=data)
    print(login.content)

#    print('Try admin-only command:')
#    test = s.get(base_url + '/music/lsp')

    print('Try admin-only command:')
    test = s.get(base_url + '/clips/now')

    print(test.content)


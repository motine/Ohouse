import xmlrpclib

server = xmlrpclib.Server('https://127.0.0.1:9000')

print server.ListResources('me', 'you')

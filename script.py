import ESL

conn = ESL.ESLconnection('192.168.10.93', 38021, 'ClueCon')
if conn.connected():
    print('ESL connected')
    e = conn.api('callcenter_config tier list')
    print(e.getBody())
else:
    print('ESL Error')

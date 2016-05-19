import requests
import msgpack
payload = []
rows = 0
for row in open('events.csv'):
    payload.append(row.strip().split(','))
    rows += 1
    if rows == 1000:
        print "sending 1000 adet"
        r = requests.post("http://127.0.0.1:5000/submit",
                  data = msgpack.packb(payload))
        payload = []
        rows = 0
        next

print "sending son posta adet : " + str(len(payload))
r = requests.post("http://127.0.0.1:5000/submit",
                data = msgpack.packb(payload))

import json, urllib.request, urllib.error

url = 'http://127.0.0.1:8000/users/signup'
payload = {
    'name': 'HTTPUser',
    'email': 'httpuser@example.com',
    'password': 'pass123',
    'org_name': 'Org',
    'role': 'buyer',
}
req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
try:
    res = urllib.request.urlopen(req)
    print('STATUS', res.status)
    print(res.read().decode())
except urllib.error.HTTPError as e:
    print('HTTP ERROR', e.code)
    try:
        print(e.read().decode())
    except Exception:
        pass
except Exception as exc:
    import traceback
    traceback.print_exc()

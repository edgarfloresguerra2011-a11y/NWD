import http.client, json

def api(method, path, data=None, token=None):
    conn = http.client.HTTPConnection('localhost', 9876)
    body = json.dumps(data) if data else None
    headers = {'Content-Type':'application/json'} if data else {}
    if token:
        headers['Authorization'] = 'Bearer '+token
    conn.request(method, path, body, headers)
    resp = conn.getresponse()
    return resp.status, json.loads(resp.read().decode())

# Register
st, body = api('POST', '/api/v1/auth/register', {'email':'freshx@demo.com','password':'Test123!','full_name':'FreshX'})
token = body['access_token']
print('1. Register:', st)

# Create account
st, body = api('POST', '/api/v1/accounts/', {'email':'warmscore@sender.com','provider':'smtp','warmup_max_per_day':30}, token)
print('2. Create account:', st, 'id=', body.get('id'))

# Warmup scores
st, body = api('GET', '/api/v1/analytics/warmup-scores', token=token)
print('3. Warmup scores status:', st)
if st == 200:
    for s in body:
        label = s['warmup_label'].replace('\U0001f525','HOT').replace('\U0001f31e','WARM').replace('\U0001f31c','WARMING').replace('\u2744','COLD')
        print('   {}: Score={} Label={} Inbox={}%'.format(s['email'], s['warmup_score'], label, s['inbox_placement_est']))

# Seed test
if st == 200 and body:
    st, seed = api('POST', '/api/v1/analytics/seed-test', {'account_id': body[0]['account_id'], 'test_email': 'test@mail-tester.com'}, token)
    print('4. Seed test:', st)
    if st == 200:
        for rec in seed['recommendations']:
            print(f"   → {rec}")

print('\nDONE')

import http.client, json

def do(path, method='GET', data=None, token=None):
    conn = http.client.HTTPConnection('localhost', 9876)
    body = json.dumps(data) if data else None
    headers = {'Content-Type':'application/json'} if data else {}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    conn.request(method, path, body, headers)
    resp = conn.getresponse()
    raw = resp.read().decode()
    try:
        return resp.status, json.loads(raw)
    except:
        return resp.status, {'raw': raw}

# Register fresh + create account
st, body = do('/api/v1/auth/register', 'POST', {'email':'hot@test.com','password':'Test123!','full_name':'Hot Test'})
token = body['access_token']
print('1. Register:', st)

st, body = do('/api/v1/accounts/', 'POST', {'email':'warm@sender.com','provider':'smtp','warmup_max_per_day':30}, token)
print('2. Create account:', st, 'id=', body.get('id'))

st, body = do('/api/v1/analytics/warmup-scores', token=token)
print('3. Warmup scores:', st)
if body:
    for acct in body:
        print(f"   {acct['email']}: Score={acct['warmup_score']} Label={acct['warmup_label']} Inbox={acct['inbox_placement_est']}%")

    st, seed = do('/api/v1/analytics/seed-test', 'POST', {'account_id': body[0]['account_id'], 'test_email': 'test@mail-tester.com'}, token)
    print('4. Seed test:', st)
    if st == 200:
        for rec in seed.get('recommendations', []):
            print(f"   → {rec}")
    else:
        print('   Body:', str(seed)[:300])

# Analytics overview
st, body = do('/api/v1/analytics/overview', token=token)
print('5. Analytics overview:', st)
if st == 200:
    print(f"   Accounts: {body['overview']['total_accounts']}")
    print(f"   Warmups: {body['overview']['active_warmups']}")

print('\nALL DONE')

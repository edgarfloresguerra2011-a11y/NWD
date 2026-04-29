"""Full end-to-end API audit"""
import http.client, json

BASE = 'localhost', 9876
passed = 0
failed = 0

def api(method, path, data=None, token=None):
    conn = http.client.HTTPConnection(*BASE)
    body = json.dumps(data) if data else None
    headers = {}
    if data: headers['Content-Type'] = 'application/json'
    if token: headers['Authorization'] = 'Bearer ' + token
    conn.request(method, path, body, headers)
    resp = conn.getresponse()
    raw = resp.read().decode()
    try:
        return resp.status, json.loads(raw)
    except:
        return resp.status, raw

def test(name, method, path, data=None, expected_status=200, token=None):
    global passed, failed
    try:
        st, body = api(method, path, data, token)
        if st == expected_status:
            passed += 1
            print('  PASS: {} -> {}'.format(name, st))
        else:
            failed += 1
            detail = body.get('detail', str(body)[:100]) if isinstance(body, dict) else str(body)[:100]
            print('  FAIL: {} -> expected {} got {}: {}'.format(name, expected_status, st, detail))
    except Exception as e:
        failed += 1
        print('  ERROR: {} -> {}'.format(name, str(e)[:100]))

# ====== 1. HEALTH ======
print('\n===== HEALTH =====')
test('Health check', 'GET', '/api/v1/health')

# ====== 2. AUTH ======
print('\n===== AUTH =====')
# Register fresh user
st, body = api('POST', '/api/v1/auth/register', {'email':'test@test.com','password':'Test123!','full_name':'Test User'})
if st == 201:
    passed += 1
    print('  PASS: Register -> 201')
else:
    failed += 1
    print('  FAIL: Register -> {} {}'.format(st, str(body)[:100]))

TOKEN = body.get('access_token', '')

# Try registering same user (should fail 400)
st, body = api('POST', '/api/v1/auth/register', {'email':'test@test.com','password':'Test123!','full_name':'Test User'})
if st == 400:
    passed += 1
    print('  PASS: Duplicate register -> 400')
else:
    failed += 1
    print('  FAIL: Duplicate register -> {}'.format(st))

# Login
test('Login', 'POST', '/api/v1/auth/login', {'email':'test@test.com','password':'Test123!'}, token=TOKEN)
test('Login wrong password', 'POST', '/api/v1/auth/login', {'email':'test@test.com','password':'WRONG'}, expected_status=401, token=TOKEN)

# Me
test('Get me', 'GET', '/api/v1/auth/me', token=TOKEN)

# Unauthenticated access
test('No auth me', 'GET', '/api/v1/auth/me', expected_status=401)

# ====== 3. ACCOUNTS ======
print('\n===== ACCOUNTS =====')
# Create account
test('Create account SMTP', 'POST', '/api/v1/accounts/', {'email':'sender@mydomain.com','provider':'smtp','warmup_max_per_day':30}, expected_status=201, token=TOKEN)
test('Create account Gmail', 'POST', '/api/v1/accounts/', {'email':'my@gmail.com','provider':'gmail','access_token':'mock_token'}, expected_status=201, token=TOKEN)

# List accounts
test('List accounts', 'GET', '/api/v1/accounts/', token=TOKEN)
st, accts = api('GET', '/api/v1/accounts/', token=TOKEN)
if st == 200 and len(accts) >= 2:
    passed += 1
    print('  PASS: At least 2 accounts created')
else:
    failed += 1
    print('  FAIL: Expected 2+ accounts, got {}'.format(len(accts) if isinstance(accts, list) else accts))

if st == 200 and accts:
    acct_id = accts[0]['id']
    # Get account by id
    test('Get account by ID', 'GET', '/api/v1/accounts/{}'.format(acct_id), token=TOKEN)
    # Update account
    test('Update account', 'PUT', '/api/v1/accounts/{}'.format(acct_id), {'warmup_max_per_day':50}, token=TOKEN)
    # Start warmup
    test('Start warmup', 'POST', '/api/v1/accounts/{}/start-warmup'.format(acct_id), token=TOKEN)
    # Pause warmup
    test('Pause warmup', 'POST', '/api/v1/accounts/{}/pause-warmup'.format(acct_id), token=TOKEN)
    # Delete account
    test('Delete account', 'DELETE', '/api/v1/accounts/{}'.format(acct_id), token=TOKEN)
    test('Delete non-existent', 'DELETE', '/api/v1/accounts/99999', expected_status=404, token=TOKEN)

# ====== 4. CAMPAIGNS ======
print('\n===== CAMPAIGNS =====')
# Create campaign
test('Create campaign', 'POST', '/api/v1/campaigns/', {'name':'Test Campaign','steps':[{'step_order':1,'subject':'Hello','body_text':'Hi','delay_hours':24}]}, expected_status=201, token=TOKEN)

st, camps = api('GET', '/api/v1/campaigns/', token=TOKEN)
if st == 200 and camps:
    camp_id = camps[0]['id']
    test('List campaigns', 'GET', '/api/v1/campaigns/', token=TOKEN)
    test('Get campaign', 'GET', '/api/v1/campaigns/{}'.format(camp_id), token=TOKEN)
    test('Update campaign', 'PUT', '/api/v1/campaigns/{}'.format(camp_id), {'name':'Updated'}, token=TOKEN)
    test('Launch campaign', 'POST', '/api/v1/campaigns/{}/launch'.format(camp_id), token=TOKEN)
    test('Pause campaign', 'POST', '/api/v1/campaigns/{}/pause'.format(camp_id), token=TOKEN)
    test('Delete campaign', 'DELETE', '/api/v1/campaigns/{}'.format(camp_id), token=TOKEN)
else:
    failed += 1
    print('  FAIL: Could not get campaign list')

# ====== 5. ANALYTICS ======
print('\n===== ANALYTICS =====')
test('Analytics overview', 'GET', '/api/v1/analytics/overview', token=TOKEN)
test('Warmup scores', 'GET', '/api/v1/analytics/warmup-scores', token=TOKEN)

st, scores = api('GET', '/api/v1/analytics/warmup-scores', token=TOKEN)
if st == 200 and scores:
    test('Seed test', 'POST', '/api/v1/analytics/seed-test', {'account_id':scores[0]['account_id'],'test_email':'test@mail-tester.com'}, token=TOKEN)
else:
    # Create an account first
    st, _ = api('POST', '/api/v1/accounts/', {'email':'seedtest@sender.com','provider':'smtp','warmup_max_per_day':30}, token=TOKEN)
    st, scores = api('GET', '/api/v1/analytics/warmup-scores', token=TOKEN)
    if st == 200 and scores:
        test('Seed test', 'POST', '/api/v1/analytics/seed-test', {'account_id':scores[0]['account_id'],'test_email':'test@mail-tester.com'}, token=TOKEN)

# ====== 6. DOMAINS ======
print('\n===== DOMAINS =====')
test('Create domain', 'POST', '/api/v1/domains/', {'domain_name':'example.com'}, token=TOKEN)
st, doms = api('GET', '/api/v1/domains/', token=TOKEN)
if st == 200 and doms:
    dom_id = doms[0]['id']
    test('List domains', 'GET', '/api/v1/domains/', token=TOKEN)
    test('DNS check', 'POST', '/api/v1/domains/{}/dns-check'.format(dom_id), token=TOKEN)
    test('Delete domain', 'DELETE', '/api/v1/domains/{}'.format(dom_id), token=TOKEN)

# ====== 7. WARMUP ======
print('\n===== WARMUP =====')
test('Warmup status', 'GET', '/api/v1/warmup/status', token=TOKEN)
st, accts = api('GET', '/api/v1/accounts/', token=TOKEN)
if st == 200 and accts:
    test('Warmup schedule', 'POST', '/api/v1/warmup/{}/schedule'.format(accts[0]['id']), token=TOKEN)

# ====== SUMMARY ======
print('\n' + '='*60)
print('RESULTS: {} PASSED / {} FAILED / {} TOTAL'.format(passed, failed, passed+failed))
if failed == 0:
    print('ALL TESTS PASSED')
else:
    print('SOME TESTS FAILED')
print('='*60)

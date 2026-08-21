import os, base64, urllib.request, urllib.parse, json, time

ROOT = os.path.dirname(os.path.abspath(__file__))

# --- 默认值（请修改，或在同目录创建 githubAPI.txt：第1行用户名、第2行Token） ---
USER  = 'YOUR_GITHUB_USERNAME'
TOKEN = 'YOUR_GITHUB_TOKEN'
REPO  = 'huoke-system-gilos'
BRANCH = 'main'

# --- 自动从同级 githubAPI.txt 读取（优先） ---
txt = os.path.join(ROOT, 'githubAPI.txt')
if os.path.isfile(txt):
    try:
        lines = [ln.strip() for ln in open(txt, 'r', encoding='utf-8') if ln.strip()]
        if len(lines) >= 2:
            u = lines[0]
            if '：' in u:
                u = u.split('：', 1)[1]
            USER  = u.strip()
            TOKEN = lines[1].strip()
    except Exception:
        pass

API = 'https://api.github.com/repos/{}/{}'.format(USER, REPO)

HEADERS = {
    'Authorization': 'Bearer ' + TOKEN,
    'Accept': 'application/vnd.github+json',
    'Content-Type': 'application/json',
    'X-GitHub-Api-Version': '2022-11-28',
}

IGNORE_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.vite',
               '.idea', '.pytest_cache', '.mypy_cache', '.ruff_cache',
               'dist', 'build', 'eggs', 'tmp', 'temp', 'logs', 'data'}
IGNORE_FILES = {'.env', '.env.local', 'gilos.db', 'githubAPI.txt',
                '.DS_Store', 'Thumbs.db', 'Desktop.ini'}
IGNORE_EXTS = {'.pyc', '.pyo', '.whl', '.egg', '.log', '.cache',
               '.tmp', '.bak', '.swp', '.swo', '.sqlite', '.sqlite3'}

def should_skip(dirpath, name):
    rel = os.path.relpath(dirpath, ROOT).replace(os.sep, '/')
    if any(seg in IGNORE_DIRS for seg in rel.split('/')):
        return True
    if name in IGNORE_FILES:
        return True
    ext = os.path.splitext(name)[1].lower()
    if ext in IGNORE_EXTS:
        return True
    return False

all_files = []
for dp, dns, fns in os.walk(ROOT):
    dns[:] = [d for d in dns if d not in IGNORE_DIRS]
    for fn in fns:
        fp = os.path.join(dp, fn)
        rel = os.path.relpath(fp, ROOT).replace(os.sep, '/')
        if (rel.startswith('frontend/node_modules')
                or rel.startswith('backend/.venv')
                or rel.startswith('backend/data')):
            continue
        if should_skip(dp, fn):
            continue
        if fn.startswith('.') and fn not in ('.gitignore', '.env.example'):
            continue
        try:
            sz = os.path.getsize(fp)
        except:
            continue
        if sz > 20 * 1024 * 1024:
            print('[SKIP >20MB] ' + rel)
            continue
        all_files.append((rel, fp))

PRIORITY_ROOT = {'.gitignore', 'README.md', 'HANDOVER.md',
                 'push_to_github.bat', '白皮书.docx'}
all_files.sort(key=lambda t: (0 if t[0] in PRIORITY_ROOT else 1, t[0]))

print('准备上传 {} 个文件...'.format(len(all_files)))
print('前 5 个优先: ' + str([f[0] for f in all_files[:5]]))
print()

def gh(method, url, data=None):
    body = json.dumps(data).encode('utf-8') if data is not None else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            text = r.read().decode('utf-8') or '{}'
            return r.status, json.loads(text)
    except urllib.error.HTTPError as e:
        try:
            info = json.loads(e.read().decode('utf-8') or '{}')
        except:
            info = {}
        return e.code, info

success = 0
failed = []
skipped = 0
for idx, (rel, fp) in enumerate(all_files, 1):
    enc_rel = urllib.parse.quote(rel, safe='/')
    url = API + '/contents/' + enc_rel
    try:
        with open(fp, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('ascii')
    except Exception as e:
        print('  [{}/{}] FAIL read {}: {}'.format(idx, len(all_files), rel, e))
        failed.append((rel, str(e)))
        continue

    payload = {
        'message': 'feat: init ' + rel,
        'content': b64,
        'branch': BRANCH,
    }

    code, info = gh('PUT', url, payload)

    if code in (200, 201):
        success += 1
        if idx % 10 == 0 or idx <= 8 or idx == len(all_files):
            print('  [{}/{}] OK   {}'.format(idx, len(all_files), rel))
    else:
        msg = info.get('message', '')
        # 已存在 -> 先 GET sha 再 update
        if code == 422 and 'sha' in msg.lower():
            gcode, ginfo = gh('GET', url + '?ref=' + BRANCH)
            if gcode == 200 and 'sha' in ginfo:
                payload['sha'] = ginfo['sha']
                code2, info2 = gh('PUT', url, payload)
                if code2 in (200, 201):
                    success += 1
                    print('  [{}/{}] OK (update) {}'.format(idx, len(all_files), rel))
                    time.sleep(0.3)
                    continue
                else:
                    m2 = info2.get('message', '')
                    print('  [{}/{}] FAIL update {}: {} {}'.format(
                        idx, len(all_files), rel, code2, m2))
                    failed.append((rel, '{} {}'.format(code2, m2)))
                    continue
            else:
                # 404 不存在但报 422？跳过
                pass
        if code == 403 and 'rate limit' in msg.lower():
            print('  [RATE LIMIT] {}，等待 60 秒...'.format(msg))
            time.sleep(60)
            # 重试当前
            idx -= 1
            continue
        if code == 404:
            print('  [{}/{}] SKIP {} (404 路径不合法): {}'.format(
                idx, len(all_files), rel, msg))
            skipped += 1
            continue
        print('  [{}/{}] FAIL {}: {} {}'.format(
            idx, len(all_files), rel, code, msg))
        failed.append((rel, '{} {}'.format(code, msg)))
    time.sleep(0.25)

print()
print('=' * 60)
print('FINISH: 成功 {} / 总 {}，失败 {}，跳过 {}'.format(
    success, len(all_files), len(failed), skipped))
if failed:
    print('失败项 (前 15):')
    for r, m in failed[:15]:
        print('   - {}: {}'.format(r, m))
print()
print('仓库地址：https://github.com/{}/{}'.format(USER, REPO))
print()

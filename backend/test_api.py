import time
import json
import urllib.request

API = "http://127.0.0.1:8000/api/v1"

def req(method, path, body=None):
    data = json.dumps(body).encode("utf-8") if body else None
    r = urllib.request.Request(API + path, data=data, method=method,
                                headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

body = {"query": "日本跨境电商卖家", "search_mode": "family_bucket"}
task = req("POST", "/tasks", body)
print("=== CREATED ===")
print(json.dumps({k: task[k] for k in ["id","query","status","progress","current_step","created_at"]}, ensure_ascii=False, indent=2))
tid = task["id"]

for i in range(1, 20):
    time.sleep(4)
    g = req("GET", f"/tasks/{tid}")
    st = g["task"]["status"]
    p = round(g["task"]["progress"], 1)
    step = g["task"].get("current_step", "")
    print(f"poll #{i:02d}  status={st:<9}  progress={p:>5}%  step={step}")
    if st in ("completed", "failed", "partial"):
        break

t = g["task"]
print("\n=== FINAL STATS ===")
for k in ["status","progress","total_contents","total_high_intent_leads","total_companies","total_demands","total_company_opportunities","total_trends","total_competitions"]:
    print(f"  {k}: {t[k]}")

leads = req("GET", f"/tasks/{tid}/leads?high_intent_only=true&limit=5")
print("\n=== HIGH INTENT LEADS ===")
print(f"total={leads['total']}  high_intent={leads['high_intent_total']}")
for l in leads["items"][:5]:
    title = (l.get("title") or "").replace("\r"," ").replace("\n"," ")[:55]
    print(f"  - [{l['category']}] score={l['overall_score']:>5.1f} (intent={l['intent_score']:.0f}) platform={l['source_platform']:<13} company={l.get('company_name') or '':<16} title={title}")

print("\n=== COST SUMMARY ===")
print(json.dumps(g.get("cost_summary", {}), ensure_ascii=False, indent=2))

print("\n=== EXPANDED KEYWORDS (top 15) ===")
for kw in (g.get("expanded_keywords") or [])[:15]:
    print(f"  - {kw}")

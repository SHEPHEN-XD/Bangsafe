import re, json, os, time, uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

APP_DIR = os.path.dirname(__file__)
REPORTS_FILE = os.path.join(APP_DIR, "reports.json")

if not os.path.exists(REPORTS_FILE):
    with open(REPORTS_FILE, "w", encoding="utf-8") as f:
        json.dump({"reports": []}, f, ensure_ascii=False, indent=2)

app = FastAPI(title="BANGSAFE — The National CyberShield")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUSPICIOUS_KEYWORDS = [
    "login", "secure", "verify", "confirm", "account", "update", "bank", "payment",
    "reset", "support", "service", "auth", "signin", "password", "verify-account"
]
SUSPICIOUS_TLDS = ["tk","ml","ga","cf","gq"]
COMMON_BRAND_KEYWORDS = ["facebook","google","gmail","bkash","nagad","dbbl","rocket","bank"]

def is_ip_host(host: str) -> bool:
    return bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host))

def domain_from_url(url: str) -> str:
    try:
        without_proto = re.sub(r"^https?://", "", url, flags=re.I)
        parts = without_proto.split("/")[0].split(":")[0]
        return parts.lower()
    except Exception:
        return url.lower()

def tld_of(domain: str) -> str:
    parts = domain.rsplit(".",1)
    return parts[1].lower() if len(parts)>1 else ""

def score_url(url: str):
    reasons=[]
    score=0
    d = domain_from_url(url)
    if "@" in url or " " in url:
        score+=25; reasons.append("URL contains '@' or spaces (possible trick).")
    if is_ip_host(d):
        score+=18; reasons.append("Host is an IP address.")
    if "xn--" in d:
        score+=20; reasons.append("Punycode / IDN (homograph) risk.")
    low=url.lower()
    kw_hits=[k for k in SUSPICIOUS_KEYWORDS if k in low]
    if kw_hits:
        add=min(30, 6*len(kw_hits))
        score+=add; reasons.append("Suspicious keywords: "+", ".join(kw_hits))
    if len(url)>120:
        score+=6; reasons.append("Very long URL.")
    if url.count("?")+url.count("&")>4:
        score+=6; reasons.append("Many query parameters.")
    if d.count("-")>=3:
        score+=6; reasons.append("Multiple hyphens in domain.")
    tld=tld_of(d)
    if tld in SUSPICIOUS_TLDS:
        score+=8; reasons.append(f"TLD .{tld} often abused (heuristic).")
    brand_hits=[b for b in COMMON_BRAND_KEYWORDS if b in d and not d.startswith(b)]
    if brand_hits:
        score+=18; reasons.append("Impersonation-like keywords: "+", ".join(brand_hits))
    score=min(100,score)
    verdict="safe"
    if score>=60: verdict="danger"
    elif score>=25: verdict="suspicious"
    return {"score":score,"reasons":reasons,"verdict":verdict,"domain":d}

class ScanRequest(BaseModel):
    url: str

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/scan")
async def scan(req: ScanRequest):
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="Empty URL")
    if not re.match(r"^https?://", url, flags=re.I):
        url = "http://"+url
    result = score_url(url)
    result.update({"url":url, "requested_at": time.time()})
    return result

@app.post("/report")
async def report(request: Request):
    data = await request.json()
    url = data.get("url")
    note = data.get("note","")
    if not url:
        raise HTTPException(status_code=400, detail="Missing url")
    entry = {"id": str(uuid.uuid4()), "url": url, "note": note, "ts": time.time()}
    with open(REPORTS_FILE,"r+",encoding="utf-8") as f:
        try:
            doc=json.load(f)
        except:
            doc={"reports":[]}
        doc.setdefault("reports",[]).append(entry)
        f.seek(0); json.dump(doc,f,ensure_ascii=False,indent=2); f.truncate()
    return {"status":"ok","entry":entry}

@app.get("/reports")
async def reports(limit: int=100):
    with open(REPORTS_FILE,"r",encoding="utf-8") as f:
        doc=json.load(f)
    items=list(reversed(doc.get("reports",[])))
    return items[:limit]

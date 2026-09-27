from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from curl_cffi import requests
import uvicorn

app = FastAPI(title="SofaScore Proxy")

# الترويسات الضرورية لتجاوز Cloudflare
HEADERS = {
    "X-Requested-With": "XMLHttpRequest",  # إلزامي لمنع 403
    "Referer": "https://www.sofascore.com/",
    "Accept": "application/json",
}

@app.get("/")
async def root():
    return {"status": "ok", "message": "SofaScore Proxy is running"}

@app.get("/api/v1/event/{event_id}/lineups")
async def get_lineups(event_id: int):
    """
    جلب بيانات التشكيلة لمباراة معينة من SofaScore.
    """
    url = f"https://www.sofascore.com/api/v1/event/{event_id}/lineups"

    try:
        # استخدام curl_cffi لمحاكاة بصمة Chrome بالكامل
        # هذا هو المفتاح لتجاوز Cloudflare WAF / TLS Fingerprinting
        response = requests.get(
            url,
            headers=HEADERS,
            impersonate="chrome120",  # محاكاة متصفح Chrome الإصدار 120
            timeout=20
        )

        if response.status_code == 200:
            return JSONResponse(content=response.json())
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Match lineups not found. The lineups may not be published yet.")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"SofaScore API returned error: {response.text[:200]}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
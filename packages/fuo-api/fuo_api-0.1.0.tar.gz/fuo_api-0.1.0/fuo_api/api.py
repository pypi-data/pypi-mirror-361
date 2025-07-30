from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests
import re
from io import BytesIO

app = FastAPI(title="FUOverflow API")

# CORS cho frontend (mở rộng tùy mục đích)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/image-ids/")
def get_image_ids(thread_url: str):
    try:
        response = requests.get(thread_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

    soup = BeautifulSoup(response.text, 'html.parser')
    tags = soup.find_all('a', class_="file-preview")
    ids = []

    for tag in tags:
        href = tag.get("data-lb-sidebar-href")
        if href:
            match = re.search(r'webp\.([0-9]+)\/\?', href)
            if match:
                ids.append(match.group(1))

    if not ids:
        raise HTTPException(status_code=404, detail="Không tìm thấy ảnh.")

    return {"count": len(ids), "ids": ids}


@app.get("/api/image/{image_id}")
def get_image(image_id: str):
    img_url = f"https://fuoverflow.com/media/{image_id}/full"
    try:
        img_resp = requests.get(img_url, timeout=10)
        img_resp.raise_for_status()
    except requests.RequestException:
        raise HTTPException(status_code=404, detail="Không thể tải ảnh.")

    return StreamingResponse(BytesIO(img_resp.content), media_type="image/jpeg")

from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from analyze_video import analyze_video

app = FastAPI(title="Traffic Intelligence Backend")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):

    file_path = UPLOAD_DIR / Path(file.filename).name

    with open(file_path, "wb") as output_file:
        output_file.write(await file.read())

    print(f"Analyzing: {file_path}")

    result = analyze_video(file_path)

    video_filename = Path(result["annotated_video"]).name
    result["annotated_video"] = f"/videos/{video_filename}"

    return {
        "filename": file.filename,
        "analysis": result
    }


app.mount("/videos", StaticFiles(directory="uploads"), name="videos")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
from analyze_video import analyze_video
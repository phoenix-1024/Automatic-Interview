from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


router = APIRouter()


# Mount the directory containing your static files
router.mount("/static", StaticFiles(directory="frontend"), name="static")


@router.get("/")
async def read_root():
    # Serve your index.html file
    return FileResponse("frontend/index.html")


@router.get("/generate_questions")
async def read_page1():
    return FileResponse("frontend/generate_questions.html")


@router.get("/select_jobs")
async def read_page2():
    return FileResponse("frontend/select_jobs.html")

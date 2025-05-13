from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from wd14_tagger_api.wd14_tagger import ImageTagger # Make sure the path to your module is correct
import os

# Getting environment variables for configuration
DEVICE = os.getenv("DEVICE", "cuda")
WD14_MODEL = os.getenv("WD14_MODEL", "wd14-convnextv2.v1")
WD14_THRESHOLD = float(os.getenv("WD14_THRESHOLD", 0.35))
WD14_REPLACE_UNDERSCORE = os.getenv("WD14_REPLACE_UNDERSCORE", "true") == "true"

print(WD14_REPLACE_UNDERSCORE)
app = FastAPI()

# CORS middleware для кросс-оригин запросов
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initializing the tagger with default values or from the environment
tagger = ImageTagger(model_name=WD14_MODEL, threshold=WD14_THRESHOLD, device=DEVICE)

class ModelSettings(BaseModel):
    wd14_model: str 
    threshold: float 

@app.post("/update-settings/")
async def update_settings(settings: ModelSettings):
    if settings.model_name:
        tagger.change_model(settings.model_name)

    if settings.threshold is not None:
        tagger.threshold = settings.threshold

    return {"message": "Settings updated successfully"}

@app.post("/tag-image/")
async def tag_image(file: UploadFile = File(...)):
    try:
        temp_file_path = f"temp_{file.filename}"

        with open(temp_file_path, 'wb') as buffer:
            buffer.write(file.file.read())

        tags_result = tagger.image_interrogate(temp_file_path)

        os.remove(temp_file_path)  # Clearing a temporary file after use

        tags_str = ", ".join(tags_result.keys())
        
        if(WD14_REPLACE_UNDERSCORE):
            tags_str = tags_str.replace("_", " ")
            
        return tags_str  

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8002)

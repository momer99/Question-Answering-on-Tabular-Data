from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from io import StringIO
import pandas as pd
from sklearn.preprocessing import LabelEncoder

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to specify trusted origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class DatasetDescription(BaseModel):
    columns: list
    shape: tuple
    description: str

# Helper function to process CSV file and generate a description
def process_csv(file_content: str):
    try:
        # Read the file into a pandas DataFrame
        df = pd.read_csv(StringIO(file_content))
    except Exception as e:
        raise ValueError(f"Error processing CSV: {e}")

    # Data preprocessing (basic)
    for column in df.select_dtypes(include=['object']).columns:
        encoder = LabelEncoder()
        df[column] = encoder.fit_transform(df[column])

    description = f"Dataset contains {df.shape[0]} rows and {df.shape[1]} columns.\n"
    description += f"Columns: {', '.join(df.columns)}.\n"
    description += "First few rows of the dataset:\n"
    description += df.head().to_string()

    return df, description

# Endpoint to accept CSV file upload
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    print(f"File content received: {content[:200]}...")  # Debug: Print the first 200 characters of the file

    df, description = process_csv(content.decode("utf-8"))
    return DatasetDescription(columns=df.columns.tolist(), shape=df.shape, description=description)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
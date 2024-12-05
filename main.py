# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import TapasTokenizer, TapasForQuestionAnswering
import pandas as pd
import torch
from datasets import load_dataset
import os

app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the pre-trained TAPAS model (we'll fine-tune it later)
tokenizer = TapasTokenizer.from_pretrained('google/tapas-base-finetuned-wtq')
model = TapasForQuestionAnswering.from_pretrained('google/tapas-base-finetuned-wtq')

# Load the DataBench QA dataset
print("Loading DataBench QA dataset...")
databench_qa = load_dataset("cardiffnlp/databench", "qa")
print("DataBench QA dataset loaded.")

# Extract the list of dataset names from the QA dataset
dataset_names = set(databench_qa['train']['dataset'])
print(f"Datasets found in DataBench QA: {dataset_names}")

# Function to load the actual datasets
def load_databench_datasets(dataset_names):
    datasets = {}
    data_dir = "databench_datasets"  # Directory where datasets are stored
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory {data_dir}. Please place your datasets here.")

    for name in dataset_names:
        dataset_path = os.path.join(data_dir, f"{name}.csv")
        if os.path.isfile(dataset_path):
            print(f"Loading dataset: {name}")
            try:
                datasets[name] = pd.read_csv(dataset_path)
            except Exception as e:
                print(f"Error loading dataset {name}: {e}")
        else:
            print(f"Dataset file {dataset_path} not found.")
            datasets[name] = pd.DataFrame()  # Empty DataFrame as placeholder

    return datasets

# Load the datasets into a dictionary
datasets = load_databench_datasets(dataset_names)

# Endpoint to list available datasets
@app.get("/datasets/")
async def get_datasets():
    available_datasets = [name for name in datasets.keys() if not datasets[name].empty]
    return {"datasets": available_datasets}

# Endpoint to process question and return an answer
@app.post("/ask/")
async def answer_question(dataset_name: str, question: str):
    if dataset_name not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    table = datasets[dataset_name]

    if table.empty:
        return {"question": question, "answer": "Dataset is not available or empty."}

    # Preprocess the table (e.g., fill missing values)
    table = table.fillna(value="Unknown")

    # Prepare inputs for the model
    inputs = tokenizer(
        table=table,
        queries=question,
        padding='max_length',
        truncation=True,
        return_tensors="pt"
    )

    # Get model outputs
    with torch.no_grad():
        outputs = model(**inputs)

    # Get the predicted answer coordinates
    predicted_answer_coordinates, predicted_aggregation_indices = tokenizer.convert_logits_to_predictions(
        inputs,
        outputs.logits,
        outputs.logits_aggregation
    )

    # Extract the answers from the table
    answers = []
    for coordinates in predicted_answer_coordinates:
        cell_values = []
        for coord in coordinates:
            cell_value = table.iat[coord]
            cell_values.append(str(cell_value))
        answers.append(", ".join(cell_values))

    # Handle aggregation (if any)
    aggregation_ops = ['NONE', 'SUM', 'AVERAGE', 'COUNT']
    agg_op_idx = predicted_aggregation_indices[0]
    agg_op = aggregation_ops[agg_op_idx]

    if agg_op == 'NONE':
        answer = ", ".join(answers)
    elif agg_op == 'SUM':
        # Sum numerical answers
        nums = [float(a) for a in answers if a.replace('.', '', 1).isdigit()]
        answer = str(sum(nums)) if nums else "0"
    elif agg_op == 'AVERAGE':
        # Average numerical answers
        nums = [float(a) for a in answers if a.replace('.', '', 1).isdigit()]
        answer = str(sum(nums) / len(nums)) if nums else "0"
    elif agg_op == 'COUNT':
        # Count the number of answers
        answer = str(len(answers))
    else:
        answer = ", ".join(answers)

    return {"question": question, "answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

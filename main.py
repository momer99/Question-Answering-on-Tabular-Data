from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import TapasTokenizer, TapasForQuestionAnswering
import pandas as pd
import torch

app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the fine-tuned TAPAS model (replace with your model if fine-tuned)
tokenizer = TapasTokenizer.from_pretrained('google/tapas-base-finetuned-wtq')
model = TapasForQuestionAnswering.from_pretrained('google/tapas-base-finetuned-wtq')

# Preload datasets
# Replace these paths with the actual paths to your datasets
datasets = {
    "sales_data": pd.read_csv("datasets/sales_data.csv"),
    "inventory_data": pd.read_csv("datasets/inventory_data.csv"),
    # Add more datasets as needed
}

# Endpoint to list available datasets
@app.get("/datasets/")
async def get_datasets():
    return {"datasets": list(datasets.keys())}

# Endpoint to process question and return an answer
@app.post("/ask/")
async def answer_question(dataset_name: str, question: str):
    if dataset_name not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    table = datasets[dataset_name]

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
        answer = str(sum(float(a) for a in answers if a.replace('.', '', 1).isdigit()))
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

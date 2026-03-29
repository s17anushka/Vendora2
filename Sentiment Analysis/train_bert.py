import os
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

# MODEL
MODEL_NAME = "distilbert-base-uncased"

# LABEL MAP
LABEL2ID = {"negative": 0, "neutral": 1, "positive": 2}
ID2LABEL = {0: "negative", 1: "neutral", 2: "positive"}

# CONFIG
MAX_LEN = 64
BATCH_SIZE = 8
EPOCHS = 1
LR = 2e-5
SAVE_DIR = "./sentiment_model"

print("🚀 TRAINING STARTED")

# ─────────────────────────────
# LOAD YOUR DATASET
# ─────────────────────────────
def load_data():
    df = pd.read_csv("final_merged_data.csv")

    print("✅ Dataset Loaded")
    print("Columns:", df.columns)
    print("Total rows:", len(df))

    # 🔥 FIX
    df = df.rename(columns={"sentiment": "label"})

    df = df.dropna()
    df = df[df["label"].isin(["positive", "neutral", "negative"])]

    df["label_id"] = df["label"].map(LABEL2ID)

    print("After cleaning:", len(df))
    print(df["label"].value_counts())

    return df


# ─────────────────────────────
# DATASET CLASS
# ─────────────────────────────
class ReviewDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.encodings = tokenizer(
            texts.tolist(),
            truncation=True,
            padding=True,
            max_length=MAX_LEN,
            return_tensors="pt"
        )
        self.labels = torch.tensor(labels.tolist(), dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            "input_ids": self.encodings["input_ids"][idx],
            "attention_mask": self.encodings["attention_mask"][idx],
            "labels": self.labels[idx]
        }


# ─────────────────────────────
# TRAIN FUNCTION
# ─────────────────────────────
def train():
    device = torch.device("cpu")
    print("🖥 Using device:", device)

    df = load_data()

    train_df, val_df = train_test_split(
        df,
        test_size=0.2,
        stratify=df["label_id"],
        random_state=42
    )

    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)
    model = DistilBertForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=3
    )
    model.to(device)

    train_ds = ReviewDataset(train_df["text"], train_df["label_id"], tokenizer)
    val_ds = ReviewDataset(val_df["text"], val_df["label_id"], tokenizer)

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)

    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)

    # TRAIN LOOP
    for epoch in range(EPOCHS):
        print(f"\n🔥 Epoch {epoch+1}")

        model.train()
        total_loss = 0

        for i, batch in enumerate(train_loader):
            optimizer.zero_grad()

            outputs = model(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device),
                labels=batch["labels"].to(device)
            )

            loss = outputs.loss
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

            if i % 20 == 0:
                print(f"Step {i}, Loss: {loss.item():.4f}")

        print("Avg Loss:", total_loss / len(train_loader))

        # VALIDATION
        model.eval()
        preds, true = [], []

        with torch.no_grad():
            for batch in val_loader:
                outputs = model(
                    input_ids=batch["input_ids"].to(device),
                    attention_mask=batch["attention_mask"].to(device)
                )
                preds.extend(torch.argmax(outputs.logits, dim=1).cpu().numpy())
                true.extend(batch["labels"].cpu().numpy())

        print(classification_report(true, preds, labels=[0,1,2], target_names=["negative","neutral","positive"]))

    # SAVE MODEL
    os.makedirs(SAVE_DIR, exist_ok=True)
    model.save_pretrained(SAVE_DIR)
    tokenizer.save_pretrained(SAVE_DIR)

    print("\n🎯 MODEL TRAINED & SAVED SUCCESSFULLY!")


if __name__ == "__main__":
    train()
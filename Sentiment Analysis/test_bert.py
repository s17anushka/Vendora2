from transformers import pipeline

classifier = pipeline("text-classification", model="./sentiment_model")

label_map = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive"
}

def smart_predict(text):
    result = classifier(text)[0]

    label = label_map[result["label"]]
    score = result["score"]

    text_lower = text.lower()

    # 🔥 STRONG NEUTRAL KEYWORDS
    neutral_keywords = [
        "okay", "average", "fine", "not bad", "not good",
        "nothing special", "decent", "so so"
    ]

    # 🔥 RULE 1: keyword based neutral
    if any(word in text_lower for word in neutral_keywords):
        return "neutral"

    # 🔥 RULE 2: medium confidence
    if score < 0.85:
        return "neutral"

    return label


# TEST
while True:
    text = input("Enter review: ")
    if text == "exit":
        break
    print("Prediction:", smart_predict(text))
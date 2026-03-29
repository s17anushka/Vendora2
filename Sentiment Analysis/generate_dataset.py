import random
import pandas as pd

# domains
services = [
    "plumber", "electrician", "salon", "mechanic",
    "doctor", "delivery", "cleaning service", "AC repair",
    "car service", "internet technician"
]

# positive templates
positive_templates = [
    "The {service} was very professional and on time",
    "{service} did an excellent job",
    "Very satisfied with the {service}",
    "{service} was quick and efficient",
    "Highly recommend this {service}",
    "Great experience with the {service}"
]

# negative templates
negative_templates = [
    "{service} came late and was rude",
    "Very bad experience with the {service}",
    "{service} did not complete the work properly",
    "Unprofessional behavior from the {service}",
    "Waste of money, very disappointed",
    "{service} was slow and inefficient"
]

data = []

# generate 30000 rows
for _ in range(30000):
    service = random.choice(services)
    
    if random.random() > 0.5:
        text = random.choice(positive_templates).format(service=service)
        sentiment = "positive"
    else:
        text = random.choice(negative_templates).format(service=service)
        sentiment = "negative"
    
    data.append([text, sentiment])

# create dataframe
df = pd.DataFrame(data, columns=["text", "sentiment"])

# save
df.to_csv("synthetic_reviews.csv", index=False)

print("Dataset generated!")
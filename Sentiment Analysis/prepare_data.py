import pandas as pd

df = pd.read_csv("cleaned_reviews.csv")

# check columns first
print(df.columns)

# keep only needed columns (adjust if needed)
df = df[['cleaned_review', 'sentiments']]

# remove neutral
df = df[df['sentiments'] != 'neutral']

# rename columns
df = df.rename(columns={
    'cleaned_review': 'text',
    'sentiments': 'sentiment'
})

# save final dataset
df.to_csv("final_data.csv", index=False)

print("Final dataset ready!")
print(df['sentiment'].value_counts())
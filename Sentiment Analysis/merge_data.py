import pandas as pd

# load datasets
df1 = pd.read_csv("final_data.csv")          # cleaned amazon
df2 = pd.read_csv("synthetic_reviews.csv")  # generated

# combine
df = pd.concat([df1, df2], ignore_index=True)

# shuffle data
df = df.sample(frac=1).reset_index(drop=True)

# save final merged dataset
df.to_csv("final_merged_data.csv", index=False)

print("Merged dataset ready!")
print(df['sentiment'].value_counts())
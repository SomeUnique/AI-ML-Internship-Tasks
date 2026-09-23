import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

CSV_PATH = "spam.csv"      
TEXT_COLUMN = "v2"          
LABEL_COLUMN = "v1"          
ENCODING = "latin-1"        

# 1. Load dataset
df = pd.read_csv("D:\\New downloads\\Internship\\task 2 Minhal Shaaz\\spam.csv", encoding=ENCODING)
df = df[[LABEL_COLUMN, TEXT_COLUMN]].dropna()
df.columns = ["label", "message"]

print("Dataset shape:", df.shape)
print(df["label"].value_counts())

# 2. Clean labels -> binary (spam=1, ham/not-spam=0)
df["label_num"] = df["label"].str.lower().map({"ham": 0, "spam": 1, "not spam": 0})
df = df.dropna(subset=["label_num"]) 

# 3. Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    df["message"], df["label_num"],
    test_size=0.2, random_state=42, stratify=df["label_num"]
)

# 4. TF-IDF Vectorization
vectorizer = TfidfVectorizer(stop_words="english", lowercase=True, max_features=5000)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# 5. Train Naive Bayes classifier
model = MultinomialNB()
model.fit(X_train_tfidf, y_train)

# 6. Predict & Evaluate
y_pred = model.predict(X_test_tfidf)

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("\n=== METRICS ===")
print(f"Accuracy:  {acc:.4f}")
print(f"Precision: {prec:.4f}")
print(f"Recall:    {rec:.4f}")
print(f"F1 Score:  {f1:.4f}")
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n",
      classification_report(y_test, y_pred, target_names=["ham", "spam"]))

# 7. Test on custom examples
samples = [
    "Congratulations! You've won a free iPhone. Click here to claim now!!!",
    "Hey, are we still meeting for lunch tomorrow?",
    "URGENT: Your account has been suspended. Verify immediately at this link."
]
sample_tfidf = vectorizer.transform(samples)
preds = model.predict(sample_tfidf)
print("\n=== Sample Predictions ===")
for s, p in zip(samples, preds):
    print(f"[{'SPAM' if p == 1 else 'HAM'}] {s}")
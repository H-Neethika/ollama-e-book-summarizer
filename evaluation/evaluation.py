import pandas as pd
from rouge import Rouge
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from bert_score import score as bert_score
import numpy as np

# Load files
model_df = pd.read_csv("book_gemma_2b.csv")
baseline_df = pd.read_csv("baseline_chapter_summaries.csv")

# Clean and align based on titles
model_df["title"] = model_df["title"].str.strip()
baseline_df["title"] = baseline_df["title"].str.strip()

# Merge on chapter titles
merged_df = pd.merge(baseline_df, model_df, on="title", suffixes=("_ref", "_gen"))

# Initialize metrics
rouge = Rouge()
bleu_scores = []
rouge_l_scores = []
bert_p, bert_r, bert_f1 = [], [], []

# Evaluate each summary
for _, row in merged_df.iterrows():
    reference = row["summary_ref"]
    generated = row["summary_gen"]

    # BLEU
    bleu = sentence_bleu([reference.split()], generated.split(), smoothing_function=SmoothingFunction().method1)
    bleu_scores.append(bleu)

    # ROUGE
    scores = rouge.get_scores(generated, reference)[0]
    rouge_l_scores.append(scores["rouge-l"]["f"])

# BERTScore (vectorized)
P, R, F1 = bert_score(
    merged_df["summary_gen"].tolist(),
    merged_df["summary_ref"].tolist(),
    lang="en",
    verbose=True
)
bert_p = P.tolist()
bert_r = R.tolist()
bert_f1 = F1.tolist()

# Add results to DataFrame
merged_df["BLEU"] = bleu_scores
merged_df["ROUGE-L"] = rouge_l_scores
merged_df["BERT-P"] = bert_p
merged_df["BERT-R"] = bert_r
merged_df["BERT-F1"] = bert_f1

# Save detailed results
merged_df.to_csv("summary_evaluation_detailed.csv", index=False)

# Print overall averages
print("\n=== AVERAGE SCORES ===")
print(f"BLEU      : {np.mean(bleu_scores):.4f}")
print(f"ROUGE-L   : {np.mean(rouge_l_scores):.4f}")
print(f"BERTScore-F1 : {np.mean(bert_f1):.4f}")

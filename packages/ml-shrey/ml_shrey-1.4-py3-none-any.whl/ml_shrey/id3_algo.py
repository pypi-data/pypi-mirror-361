import pandas as pd
import math
from collections import Counter

# Calculate entropy of a dataset
def entropy(data):
    label_column = data.iloc[:, -1]
    counts = Counter(label_column)
    total = len(label_column)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())

# Information gain of splitting on an attribute
def info_gain(data, attr):
    total_entropy = entropy(data)
    values = data[attr].unique()
    weighted_entropy = 0
    for val in values:
        subset = data[data[attr] == val]
        weighted_entropy += (len(subset) / len(data)) * entropy(subset)
    return total_entropy - weighted_entropy

# ID3 algorithm
def id3(data, features):
    labels = data.iloc[:, -1]
    
    # If all labels are same
    if len(labels.unique()) == 1:
        return labels.iloc[0]

    # If no more features left
    if not features:
        return labels.mode()[0]

    # Choose best attribute
    gains = [info_gain(data, attr) for attr in features]
    best_attr = features[gains.index(max(gains))]

    tree = {best_attr: {}}
    for val in data[best_attr].unique():
        subset = data[data[best_attr] == val]
        subtree = id3(subset.drop(columns=[best_attr]), [f for f in features if f != best_attr])
        tree[best_attr][val] = subtree

    return tree

# Classify a test sample
def classify(tree, sample):
    if not isinstance(tree, dict):
        return tree
    root = next(iter(tree))
    value = sample.get(root)
    if value in tree[root]:
        return classify(tree[root][value], sample)
    else:
        return "Unknown"

# Main function to run ID3 and classify a sample
def decision_tree_from_csv(file_path):
    data = pd.read_csv(file_path)
    features = list(data.columns[:-1])
    tree = id3(data, features)

    print("\nGenerated Decision Tree:")
    print(tree)

    # Classify one sample (hardcoded, as required)
    test_sample = {
        features[i]: data.iloc[0][i] for i in range(len(features))
    }
    print("\nClassifying sample:", test_sample)
    result = classify(tree, test_sample)
    print("Predicted label:", result)

def id3(*args, **kwargs):
    return decision_tree_from_csv(*args, **kwargs)

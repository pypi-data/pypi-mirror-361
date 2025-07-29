import csv

def candidate_elimination(file_path):
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)[1:]  # skip header

    concepts = [row[:-1] for row in data]
    targets = [row[-1] for row in data]

    n = len(concepts[0])
    S = concepts[0].copy()
    G = [['?' for _ in range(n)]]

    for i, example in enumerate(concepts):
        if targets[i] == "Yes":
            for j in range(n):
                if S[j] != example[j]:
                    S[j] = '?'
            G = [g for g in G if all(g[k] == '?' or g[k] == S[k] for k in range(n))]
        else:
            new_G = []
            for g in G:
                for j in range(n):
                    if g[j] == '?':
                        if S[j] != '?':
                            g_new = g.copy()
                            g_new[j] = S[j]
                            new_G.append(g_new)
            G = new_G

    print("Final Specific Hypothesis (S):", S)
    print("Final General Hypotheses (G):", G)

def candidate(*args, **kwargs):
    return candidate_elimination(*args, **kwargs)

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans

def run_clustering(file_path, k=3, gmm_components=3):
    data = pd.read_csv(file_path)
    print("Input Data Shape:", data.shape)
    print(data.head())

    f1 = data['V1'].values
    f2 = data['V2'].values
    X = np.array(list(zip(f1, f2)))

    print("\nOriginal Data Points (X):\n", X)

    # Plot original dataset
    print('\nGraph for Whole Dataset')
    plt.scatter(f1, f2, c='black', s=7)
    plt.title("Original Dataset")
    plt.xlabel("V1")
    plt.ylabel("V2")
    plt.show()

    # KMeans Clustering
    kmeans = KMeans(n_clusters=k, random_state=0)
    kmeans_labels = kmeans.fit_predict(X)
    centroids = kmeans.cluster_centers_

    print("\nKMeans Cluster Labels:\n", kmeans_labels)
    print("KMeans Centroids:\n", centroids)

    print('\nGraph using KMeans Algorithm')
    plt.scatter(X[:, 0], X[:, 1], c=kmeans_labels, s=40, cmap='viridis')
    plt.scatter(centroids[:, 0], centroids[:, 1], marker='*', s=200, c='red')
    plt.title("KMeans Clustering")
    plt.xlabel("V1")
    plt.ylabel("V2")
    plt.show()

    # EM using GMM
    gmm = GaussianMixture(n_components=gmm_components, random_state=0).fit(X)
    gmm_labels = gmm.predict(X)
    probs = gmm.predict_proba(X)
    size = 10 * probs.max(1) ** 3

    print('\nGraph using EM Algorithm (GMM)')
    plt.scatter(X[:, 0], X[:, 1], c=gmm_labels, s=size, cmap='viridis')
    plt.title("EM Clustering using GMM")
    plt.xlabel("V1")
    plt.ylabel("V2")
    plt.show()

def kmeans(*args, **kwargs):
    return run_clustering(*args, **kwargs)

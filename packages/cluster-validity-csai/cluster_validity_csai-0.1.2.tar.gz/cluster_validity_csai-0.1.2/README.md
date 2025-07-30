# CSAIEvaluator: Clustering Stability Assessment Index (CSAI)

CSAIEvaluator is a Python library for evaluating the stability and validity of clustering algorithms across multiple data splits.
It uses a newly proposed Clustering Stability Assessment Index (CSAI) that compares the feature structure of clusters over different partitions.

## Installation

```bash
pip install cluster-validity-csai

```

## Example Usage

```python
from csai import CSAIEvaluator
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

# Sample data: assume 'key_umap' column contains embedding vectors (e.g., from UMAP)
df = pd.DataFrame({
    "key_umap": [np.random.rand(10) for _ in range(100)]
})

# Split data into training and test sets
X_train, X_test = train_test_split(df, test_size=0.3, random_state=42)

# Define a clustering function
def kmeans_label_func(embeddings, n_clusters=5):
    model = KMeans(n_clusters=n_clusters, random_state=42)
    labels = model.fit_predict(embeddings)
    return labels, model

# Initialize and run CSAI evaluator
csai = CSAIEvaluator()
csai_score = csai.run_csai_evaluation(
    X_train,
    X_test,
    key_col="key_umap",
    label_func=kmeans_label_func,
    n_splits=5
)

print("CSAIEvaluator Score:", csai_score)
```
## 📄 Citation
If you use this package in your work, please cite:

Tarekegn, A. N., Tessem, B., & Rabbi, F. (2025).  
*A New Cluster Validation Index Based on Stability Analysis*.  
In Proceedings of the 14th International Conference on Pattern Recognition Applications and Methods (ICPRAM),  
SciTePress, pp. 377–384.  
DOI: [10.5220/0013309100003905](https://doi.org/10.5220/0013309100003905)

## License

This software is provided under a custom academic, non-commercial license.  
See [LICENSE.txt](https://github.com/AdaneNT/cluster-validity-csai/blob/main/LICENSE) for full terms.

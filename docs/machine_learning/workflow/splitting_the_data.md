---
author: Knowledge Base Automation System
created_at: '2025-07-04'
description: Documentation on Splitting The Data for machine_learning/workflow
title: Splitting The Data
updated_at: '2025-07-04'
version: 1.0.0
---

# Splitting the Data

## Overview
Splitting the data is a crucial step in the machine learning workflow where the preprocessed dataset is divided into separate subsets for training, validation, and sometimes testing. This separation allows for unbiased model evaluation and helps prevent overfitting.

## Key Components

### Basic Split Types
- **Training Set**: Used to train the model, typically 60-80% of the data.
- **Validation Set**: Used for hyperparameter tuning and model selection, typically 10-20% of the data.
- **Test Set**: Used for final model evaluation, typically 10-20% of the data.

### Splitting Strategies
- **Random Split**: Simple random division of data (suitable for large, homogeneous datasets).
- **Stratified Split**: Maintains the same class distribution in each subset (important for imbalanced datasets).
- **Time-Based Split**: Uses time as a separator (crucial for time series data).
- **Group-Based Split**: Ensures related samples stay in the same subset (e.g., all images from one patient).
- **K-Fold Cross-Validation**: Divides data into k subsets, using each as a validation set in turn.

### Handling Class Imbalance
- **Random Oversampling**: Duplicating minority class samples.
- **Random Undersampling**: Removing majority class samples.
- **Synthetic Data Generation**: Creating synthetic samples (e.g., SMOTE, ADASYN).
- **Class Weights**: Adjusting model weights inversely proportional to class frequencies.
- **Stratification**: Ensuring class distributions are maintained in all splits.

## Best Practices
1. **Randomize Before Splitting**: Shuffle data to avoid any ordering biases.
2. **Set Random Seeds**: Ensure reproducibility of splits.
3. **Stratify When Needed**: Use stratified sampling for imbalanced datasets.
4. **Preserve Time Order**: For time series data, maintain chronological ordering.
5. **Avoid Data Leakage**: Ensure test set remains completely separate from model development.
6. **Consider Cross-Validation**: Use k-fold when dataset size is limited.
7. **Validate Split Quality**: Check for representative distributions in all subsets.

## Tools & Libraries
- **Scikit-learn**: `train_test_split`, `StratifiedKFold`, etc.
- **Imbalanced-learn**: Specialized tools for handling imbalanced datasets.
- **TensorFlow/PyTorch**: Built-in data splitting functionalities.
- **Pandas**: Data manipulation to support custom splitting requirements.

## Implementation Example
```python
# Example: Different data splitting approaches
import numpy as np
from sklearn.model_selection import train_test_split, KFold, StratifiedKFold, TimeSeriesSplit
from imblearn.over_sampling import SMOTE
import pandas as pd

# Sample data
X = np.random.rand(1000, 10)  # 1000 samples, 10 features
y = np.random.choice([0, 1], size=1000, p=[0.8, 0.2])  # Imbalanced binary target (80/20)
groups = np.random.choice([0, 1, 2, 3], size=1000)  # Group identifiers

# 1. Basic random split
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

print(f"Train set: {X_train.shape[0]} samples")
print(f"Validation set: {X_val.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")

# 2. Stratified split (preserves class distribution)
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42)

print(f"\nClass distribution in original data: {np.bincount(y) / len(y)}")
print(f"Class distribution in training data: {np.bincount(y_train) / len(y_train)}")
print(f"Class distribution in validation data: {np.bincount(y_val) / len(y_val)}")
print(f"Class distribution in test data: {np.bincount(y_test) / len(y_test)}")

# 3. K-fold cross-validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)
for i, (train_idx, val_idx) in enumerate(kf.split(X)):
    print(f"\nFold {i+1}:")
    print(f"  Training: {len(train_idx)} samples")
    print(f"  Validation: {len(val_idx)} samples")

# 4. Stratified K-fold cross-validation
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for i, (train_idx, val_idx) in enumerate(skf.split(X, y)):
    print(f"\nStratified Fold {i+1}:")
    print(f"  Training class distribution: {np.bincount(y[train_idx]) / len(train_idx)}")
    print(f"  Validation class distribution: {np.bincount(y[val_idx]) / len(val_idx)}")

# 5. Time series split
# Assuming data is time-ordered
tscv = TimeSeriesSplit(n_splits=3)
for i, (train_idx, val_idx) in enumerate(tscv.split(X)):
    print(f"\nTime Series Split {i+1}:")
    print(f"  Training: {len(train_idx)} samples (indices {min(train_idx)}-{max(train_idx)})")
    print(f"  Validation: {len(val_idx)} samples (indices {min(val_idx)}-{max(val_idx)})")

# 6. Handling imbalanced data with SMOTE
X_train_resampled, y_train_resampled = SMOTE(random_state=42).fit_resample(X_train, y_train)
print(f"\nOriginal training class distribution: {np.bincount(y_train)}")
print(f"Resampled training class distribution: {np.bincount(y_train_resampled)}")
```

## References
- [Data Acquisition](data_acquisition.md) - First step in ML workflow
- [Preprocessing](preprocessing.md) - Step before data splitting
- [Build + Train Model](build_train_model.md) - Next step after splitting
- [Scikit-learn Cross-Validation Guide](https://scikit-learn.org/stable/modules/cross_validation.html) - External resource
- [Imbalanced-learn Documentation](https://imbalanced-learn.org/stable/) - External resource for imbalanced datasets

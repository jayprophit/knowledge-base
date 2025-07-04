---
author: Knowledge Base Automation System
created_at: '2025-07-04'
description: Documentation on Hyperparameter Tuning for machine_learning/workflow
title: Hyperparameter Tuning
updated_at: '2025-07-04'
version: 1.0.0
---

# Hyperparameter Tuning

## Overview
Hyperparameter tuning is the process of optimizing a model's hyperparameters to improve performance. Unlike model parameters that are learned from data during training, hyperparameters are set before training begins and control the learning process itself. Effective tuning can significantly enhance model performance, generalization, and convergence speed.

## Key Components

### Common Hyperparameters

#### General Hyperparameters
- **Learning Rate**: Controls the step size during optimization.
- **Regularization Strength**: L1/L2 penalty coefficients to prevent overfitting.
- **Batch Size**: Number of samples processed before model update.
- **Number of Epochs/Iterations**: How many times the model sees the entire dataset.

#### Algorithm-Specific Hyperparameters
- **Tree-Based Models**: Max depth, min samples per leaf, number of trees, split criteria.
- **Neural Networks**: Number of layers, units per layer, activation functions, dropout rates.
- **Support Vector Machines**: Kernel type, C parameter, gamma.
- **Clustering**: Number of clusters, distance metrics, convergence thresholds.
- **Dimensionality Reduction**: Number of components, perplexity.

### Search Strategies
- **Grid Search**: Exhaustive search over specified parameter values.
- **Random Search**: Randomly sampling from parameter distributions.
- **Bayesian Optimization**: Sequential model-based optimization using surrogate models.
- **Genetic Algorithms**: Evolutionary approach inspired by natural selection.
- **Population-Based Training**: Concurrent optimization with population of models.
- **Gradient-Based Optimization**: For differentiable hyperparameters.

### Architecture Tweaking
- **Network Architecture**: Adjusting the number, type, and arrangement of layers.
- **Feature Engineering**: Selecting or transforming input features.
- **Ensemble Construction**: Combining multiple models with different architectures.
- **Transfer Learning**: Adapting pre-trained models to new tasks.

### Regularization Techniques
- **L1/L2 Regularization**: Adding penalty terms to the loss function.
- **Dropout**: Randomly deactivating neurons during training.
- **Batch Normalization**: Normalizing layer inputs to stabilize training.
- **Data Augmentation**: Artificially increasing dataset size with transformations.
- **Early Stopping**: Halting training when validation performance plateaus.

### Diagnostics and Analysis
- **Study Why Model is Struggling**: Analyzing bias vs. variance trade-off.
- **Learning Curves**: Plotting training vs. validation performance over time.
- **Validation Curves**: Plotting performance vs. hyperparameter values.
- **Feature Importance**: Identifying which features contribute most to predictions.

## Best Practices
1. **Define Search Space Carefully**: Balance breadth and computational cost.
2. **Start Broad, Then Refine**: Begin with coarse search, then zoom in on promising regions.
3. **Use Cross-Validation**: Ensure tuning results generalize across different data subsets.
4. **Monitor Multiple Metrics**: Don't optimize for just one performance measure.
5. **Consider Computational Budget**: Choose search strategy based on available resources.
6. **Avoid Data Leakage**: Keep test data completely separate from tuning process.
7. **Document Everything**: Record all experiments, parameters, and results.
8. **Balance Complexity and Performance**: Consider model size, speed, and interpretability.

## Tools & Libraries
- **Scikit-learn**: `GridSearchCV`, `RandomizedSearchCV`.
- **Optuna**: Framework for hyperparameter optimization.
- **Hyperopt**: Distributed asynchronous hyperparameter optimization.
- **Ray Tune**: Scalable hyperparameter tuning library.
- **Keras Tuner**: Hyperparameter tuning for Keras models.
- **Weights & Biases**: Experiment tracking and visualization.
- **MLflow**: Managing the end-to-end machine learning lifecycle.

## Implementation Example
```python
# Example: Various hyperparameter tuning approaches
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from scipy.stats import randint, uniform

import optuna
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
import tensorflow as tf
from tensorflow import keras

# Assuming X_train, y_train, X_val, y_val are already defined from data splitting

# 1. Grid Search with Scikit-learn
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'bootstrap': [True, False]
}

grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid=param_grid,
    cv=5,
    scoring='f1',
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train, y_train)

print(f"Best parameters: {grid_search.best_params_}")
print(f"Best cross-validation score: {grid_search.best_score_:.4f}")
print(f"Validation score: {grid_search.score(X_val, y_val):.4f}")

# 2. Random Search with Scikit-learn
param_distributions = {
    'n_estimators': randint(50, 500),
    'max_depth': randint(10, 50),
    'min_samples_split': randint(2, 20),
    'min_samples_leaf': randint(1, 10),
    'bootstrap': [True, False]
}

random_search = RandomizedSearchCV(
    RandomForestClassifier(random_state=42),
    param_distributions=param_distributions,
    n_iter=100,
    cv=5,
    scoring='f1',
    n_jobs=-1,
    random_state=42,
    verbose=1
)

random_search.fit(X_train, y_train)

print(f"Best parameters: {random_search.best_params_}")
print(f"Best cross-validation score: {random_search.best_score_:.4f}")
print(f"Validation score: {random_search.score(X_val, y_val):.4f}")

# 3. Bayesian Optimization with Optuna
def objective(trial):
    # Define hyperparameters to search
    n_estimators = trial.suggest_int('n_estimators', 50, 500)
    max_depth = trial.suggest_int('max_depth', 10, 50)
    min_samples_split = trial.suggest_int('min_samples_split', 2, 20)
    min_samples_leaf = trial.suggest_int('min_samples_leaf', 1, 10)
    bootstrap = trial.suggest_categorical('bootstrap', [True, False])
    
    # Create and evaluate model
    rf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        bootstrap=bootstrap,
        random_state=42
    )
    
    # Use cross-validation score as objective
    score = cross_val_score(rf, X_train, y_train, cv=5, scoring='f1').mean()
    
    return score  # Optuna maximizes by default

# Create a study
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=100)

print(f"Best parameters: {study.best_params}")
print(f"Best value: {study.best_value:.4f}")

# Train final model with best parameters
best_rf = RandomForestClassifier(
    **study.best_params,
    random_state=42
)
best_rf.fit(X_train, y_train)
print(f"Validation score: {best_rf.score(X_val, y_val):.4f}")

# 4. Hyperparameter Tuning for Neural Networks (Keras)
def build_model(hp):
    model = keras.Sequential()
    
    # Number of units in first layer
    model.add(keras.layers.Dense(
        units=hp.Int('units', min_value=32, max_value=512, step=32),
        activation='relu',
        input_shape=(X_train.shape[1],)
    ))
    
    # Optional dropout
    if hp.Boolean('dropout'):
        model.add(keras.layers.Dropout(hp.Float('dropout_rate', min_value=0.1, max_value=0.5, step=0.1)))
    
    # Number of hidden layers
    for i in range(hp.Int('num_hidden_layers', 0, 3)):
        model.add(keras.layers.Dense(
            units=hp.Int(f'units_{i}', min_value=32, max_value=256, step=32),
            activation='relu'
        ))
        
        if hp.Boolean(f'dropout_{i}'):
            model.add(keras.layers.Dropout(hp.Float(f'dropout_rate_{i}', min_value=0.1, max_value=0.5, step=0.1)))
    
    # Output layer
    model.add(keras.layers.Dense(1, activation='sigmoid'))
    
    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(
            learning_rate=hp.Float('learning_rate', min_value=1e-4, max_value=1e-2, sampling='log')
        ),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model

# Initialize Keras Tuner
tuner = keras.tuner.Hyperband(
    build_model,
    objective='val_accuracy',
    max_epochs=50,
    factor=3,
    directory='keras_tuning',
    project_name='hyperparameter_optimization'
)

# Early stopping callback
early_stopping = keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)

# Search for best hyperparameters
tuner.search(
    X_train, y_train,
    epochs=50,
    validation_data=(X_val, y_val),
    callbacks=[early_stopping]
)

# Get best hyperparameters
best_hyperparameters = tuner.get_best_hyperparameters(1)[0]
print(f"Best hyperparameters: {best_hyperparameters.values}")

# Build and train final model
best_model = tuner.hypermodel.build(best_hyperparameters)
history = best_model.fit(
    X_train, y_train,
    epochs=50,
    validation_data=(X_val, y_val),
    callbacks=[early_stopping]
)

# 5. Visualization: Learning Curves
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 4))

# Plot training & validation accuracy
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')

# Plot training & validation loss
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')

plt.tight_layout()
plt.show()
```

## References
- [Build + Train Model](build_train_model.md) - Related step in ML workflow
- [Evaluate Performance](evaluate_performance.md) - Previous step before tuning
- [Deployment](temp_reorg/docs/machine_learning/workflow/deployment.md) - Next step after successful tuning
- [Scikit-learn Hyperparameter Tuning](https://scikit-learn.org/stable/modules/grid_search.html) - External resource
- [Optuna Documentation](https://optuna.readthedocs.io/) - External resource
- [Ray Tune Documentation](https://docs.ray.io/en/latest/tune/index.html) - External resource
- [Neural Network Architecture Search](https://en.wikipedia.org/wiki/Neural_architecture_search) - External resource

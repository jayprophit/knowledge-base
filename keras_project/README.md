# Keras Deep Learning Project

This project provides a template for deep learning projects using Keras and TensorFlow. It includes setup instructions, example code, and best practices for building and training neural networks.

## Getting Started

### Prerequisites

- Python 3.8 or later
- pip (Python package manager)
- (Optional) CUDA-compatible GPU for accelerated training

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd keras_project
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
keras_project/
├── data/                    # Directory for datasets
├── models/                  # Saved models
├── notebooks/               # Jupyter notebooks
├── src/                     # Source code
│   ├── data/                # Data loading and preprocessing
│   ├── models/              # Model definitions
│   ├── training/            # Training scripts
│   └── utils/               # Utility functions
├── tests/                   # Unit tests
├── requirements.txt         # Project dependencies
└── README.md               # This file
```

## Quick Start

1. **Run the MNIST CNN example**:
   ```bash
   python src/examples/mnist_cnn.py
   ```

2. **Start Jupyter Notebook**:
   ```bash
   jupyter notebook
   ```
   Then open `notebooks/exploratory_analysis.ipynb`

## Example: Training a CNN on MNIST

```python
# Import required libraries
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# Load and preprocess the data
(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()
x_train = x_train.reshape(-1, 28, 28, 1).astype("float32") / 255.0
x_test = x_test.reshape(-1, 28, 28, 1).astype("float32") / 255.0

# Build the model
model = keras.Sequential([
    layers.Conv2D(32, 3, activation="relu", input_shape=(28, 28, 1)),
    layers.MaxPooling2D(),
    layers.Conv2D(64, 3, activation="relu"),
    layers.MaxPooling2D(),
    layers.Flatten(),
    layers.Dropout(0.5),
    layers.Dense(10, activation="softmax"),
])

# Compile and train
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.fit(x_train, y_train, batch_size=128, epochs=5, validation_split=0.1)

# Evaluate
model.evaluate(x_test, y_test, verbose=2)
```

## Best Practices

1. **Use version control**
   - Track your code, notebooks, and model definitions
   - Use `.gitignore` to exclude large data files and model checkpoints

2. **Organize your code**
   - Separate data loading, model definition, and training logic
   - Use configuration files for hyperparameters
   - Document your code and experiments

3. **Manage experiments**
   - Track hyperparameters and metrics
   - Save model checkpoints
   - Log training progress

4. **Optimize performance**
   - Use data pipelines for efficient loading
   - Enable GPU acceleration
   - Profile your code to identify bottlenecks

## Contributing

1. Fork the repository
2. Create a new branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Resources

- [Keras Documentation](https://keras.io/)
- [TensorFlow Tutorials](https://www.tensorflow.org/tutorials)
- [Deep Learning with Python Book](https://www.manning.com/books/deep-learning-with-python-second-edition)

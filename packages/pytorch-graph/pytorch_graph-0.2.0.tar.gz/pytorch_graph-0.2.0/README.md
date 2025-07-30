# Torch Vis

**Enhanced PyTorch neural network architecture visualization with professional flowchart diagrams**. Transform your PyTorch models into beautiful, informative flowchart visualizations with comprehensive layer analysis.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-1.8+-red.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Enhanced Flowchart Diagrams**: Professional vertical flowchart visualization (default)
- **Comprehensive Layer Analysis**: Parameter counts, memory usage, and tensor shapes
- **Activation Function Indicators**: Visual highlights for activation layers
- **Data Flow Visualization**: Tensor sizes displayed on connection arrows
- **Multiple Styles**: Flowchart (default), standard, and research paper styles
- **Memory Analysis**: Per-layer and total memory usage estimates
- **Model Complexity Assessment**: Color-coded size indicators (Small/Medium/Large)
- **High-Quality Exports**: PNG diagrams with customizable DPI
- **Pure Python**: No external dependencies beyond standard ML stack

## Installation

```bash
pip install torch-vis
```

### Optional Dependencies
```bash
# For enhanced features
pip install torch-vis[full]

# For development
pip install torch-vis[dev]
```

## Quick Start

### Basic Usage (Enhanced Flowchart - Default)

```python
import torch
import torch.nn as nn
import torch_vis

# Define your PyTorch model
model = nn.Sequential(
    nn.Linear(784, 128),
    nn.ReLU(),
    nn.Linear(128, 64),
    nn.ReLU(),
    nn.Linear(64, 10)
)

# Generate enhanced flowchart diagram (default style)
torch_vis.generate_architecture_diagram(
    model=model,
    input_shape=(1, 784),
    output_path="my_model.png",
    title="My Neural Network"
)
```

### One-Line Visualization

```python
# Minimal code - outputs enhanced flowchart by default
torch_vis.generate_architecture_diagram(model, (1, 784), "model.png")
```

## Diagram Styles

### Enhanced Flowchart (Default)
```python
# Default - no style parameter needed
torch_vis.generate_architecture_diagram(model, input_shape, "flowchart.png")
```

**Features:**
- Lightning bolt icons for activation functions
- Memory usage per layer (e.g., "~1.2MB")
- Data flow indicators on arrows (e.g., "128K elements")
- Summary panel with total parameters, memory, layer counts
- Color-coded model complexity (Small/Medium/Large)

### Other Styles
```python
# Standard style
torch_vis.generate_architecture_diagram(model, input_shape, "standard.png", style="standard")

# Research paper style
torch_vis.generate_architecture_diagram(model, input_shape, "paper.png", style="research_paper")
```

## Model Analysis

```python
# Analyze model statistics
analysis = torch_vis.analyze_model(model, input_shape=(1, 784))
print(f"Parameters: {analysis.get('total_params', 'N/A')}")

# Multiple convenient functions
torch_vis.generate_flowchart_diagram(model, input_shape, "flowchart.png")
torch_vis.generate_research_paper_diagram(model, input_shape, "paper.png")
```

## Advanced Features

### Custom Titles and Paths
```python
torch_vis.generate_architecture_diagram(
    model=model,
    input_shape=(3, 224, 224),
    output_path="models/resnet_architecture.png",
    title="ResNet-18 Architecture",
    style="flowchart"  # or "standard", "research_paper"
)
```

### Model Analysis
```python
# Get detailed model information
analysis = torch_vis.analyze_model(model, input_shape=(1, 784), detailed=True)
```

## What Makes Torch Vis Special

### Enhanced Information Display
- **Parameter Counts**: Exact count per layer
- **Memory Usage**: Estimated memory consumption (float32)
- **Tensor Shapes**: Input → Output shape transformations  
- **Layer Types**: Color-coded layer categories
- **Model Size**: Automatic complexity assessment

### Professional Quality
- **Clean Layout**: Minimal, focused design
- **High DPI**: Publication-ready image quality
- **Consistent Styling**: Professional appearance
- **Compact Output**: Efficient use of space

### Developer Friendly
- **Simple API**: Sensible defaults, minimal configuration
- **PyTorch Native**: Built specifically for PyTorch models
- **Fast Generation**: Optimized rendering pipeline
- **No External Services**: Fully offline operation

## Requirements

- Python ≥ 3.8
- PyTorch ≥ 1.8.0
- matplotlib ≥ 3.3.0
- numpy ≥ 1.19.0

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## More Examples

```python
# CNN Example
cnn_model = nn.Sequential(
    nn.Conv2d(3, 32, 3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Conv2d(32, 64, 3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Flatten(),
    nn.Linear(64 * 8 * 8, 128),
    nn.ReLU(),
    nn.Linear(128, 10)
)

torch_vis.generate_architecture_diagram(
    cnn_model, 
    input_shape=(1, 3, 32, 32),
    output_path="cnn_architecture.png",
    title="CNN for CIFAR-10"
)
```

**Torch Vis** - Making PyTorch model visualization simple, beautiful, and informative! 
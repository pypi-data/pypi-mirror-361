# image-dataset-converter-paddle
[image-dataset-converter](https://github.com/waikato-datamining/image-dataset-converter) 
plugins for [Paddle (PArallel Distributed Deep LEarning)](https://github.com/PaddlePaddle).


## Installation

Via PyPI:

```bash
pip install image_dataset_converter_paddle
```

The latest code straight from the repository:

```bash
pip install git+https://github.com/waikato-datamining/image-dataset-converter-paddle.git
```

## Dataset formats

The following dataset formats are supported:

| Domain               | Format                                   | Read                           | Write                        | 
|:---------------------|:-----------------------------------------|:-------------------------------|:-----------------------------| 
| Image classification | [Paddle](formats/imageclassification.md) | [Y](plugins/from-paddle-ic.md) | [Y](plugins/to-paddle-ic.md) | 
| Image segmentation   | [Paddle](formats/imagesegmentation.md)   | [Y](plugins/from-paddle-is.md) | [Y](plugins/to-paddle-is.md) | 


## Plugins

See [here](plugins/README.md) for an overview of all plugins.


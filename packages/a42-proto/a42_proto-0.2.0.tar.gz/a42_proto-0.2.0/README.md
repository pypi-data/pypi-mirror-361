# a42_proto

Python Protobuf bindings for A42 sensor messages.

## Installation

```bash
pip install a42_proto
```

## Data

Sample frames are available from [BWSyncAndShare](https://bwsyncandshare.kit.edu/s/MtNZEctamGd2pTf).

## Example Usage

- **Load data**  
  See [scripts/read_data.py](https://github.com/HSE-VSV/DataReaderA42/blob/main/scripts/read_data.py) for a minimal example that loads a `.pb` frame and prints the `object_list`.

- **Visualize point cloud & grid**  
  See [scripts/visualize.py](https://github.com/HSE-VSV/DataReaderA42/blob/main/scripts/visualize.py) for a minimal example that transforms all laser points into the global frame and renders them in Open3D. For the visualization in this script you need some additional dependencys:
  
```bash
pip install numpy open3d
```

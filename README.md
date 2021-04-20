# DeepPoseRobot, an implementation of DeepPoseKit

To see rendering examples, open [Render_Examples.md](https://github.com/AdamExley/DeepPoseRobot/blob/main/Render_Examples.md)

This is an adaptation of both [DeepPoseKit](https://deepposekit.org) and [PixelLib](https://github.com/ayoolaolafenwa/PixelLib) to predict robot joint angles.

The robot is isolated from the background using PixelLib and then the keypoint locations of the robot are predicted using a DeepPoseKit model.

Visualization uses the [Turbo Colormap](https://ai.googleblog.com/2019/08/turbo-improved-rainbow-colormap-for.html).

3D Rendering is done via [Pyrender](https://github.com/mmatl/pyrender), which facilitates automatic keypoint and segmentation annotation

# Usage

The following are the main steps that must be taken to train a new model:
1. Configure meshes
2. Create and configure a skeleton
3. Create a dataset
4. Align the dataset
5. Perform automatic annotation
6. Train the model

## Meshes

Meshes are loaded from a robot's URDF.

The URDF can be changed via the wizard: ```python wizard.py```

The mesh for each joint, as well as that mesh's specific name, is specified in ```mesh_config.json``` in the ```data``` directory.

More details about mesh configuration can be found in that directory's README.

## Skeletons

Skeletons contain the basic information for keypoint rendering, detection, and usage.

They consist of a ```.csv``` and ```.json``` file.

A skeleton is created by first creating a CSV per DeepPoseKit's standards, which then is used to produce a JSON template. The JSON then allows you to configure the relative position of each keypoint to each joint, as well as how each keypoint is used to predict joint angles.

To create a skeleton, follow the instructions in the wizard: ```python wizard.py```

## Datasets

Datasets are expected to contain RGB images in a ```.png``` format with accopanying depthmaps in a ```.npy``` array file, and a ```.json``` information file.

To build, or recompile a dataset, simply run the wizard with arguments:
```bash
python wizard.py dataset_name [-rebuild] [-recompile]
```
With ```-rebuild``` recreating the dataset from the raw data directly, and with ```-recompile``` reprocessing the dataset from the raw data stored in the dataset itself.

## Automatic Annotation

### Alignment

Before running any automatic annotation, first align the dataset with the render using the Aligner found in the wizard: ```python wizard.py```

1. Select Dataset
2. Click "Align"

### Annotation

Then, use the automatic annotation script:

```bash
python annotate_auto.py dataset_name skeleton_name [-no_preview] [-no_seg] [-no_key]
```

## Training




# Installation

This requires [Tensorflow](https://github.com/tensorflow/tensorflow) for both segmentation and pose estimation. [Tensorflow](https://github.com/tensorflow/tensorflow) should be manually installed, along with CUDA and cuDNN according to the [Tensorflow Installation Instructions](https://www.tensorflow.org/install).

It is reccommended to **not** install CUDA with Visual Studio integration.

The reccommended versions are:

[CUDA 11.0](https://developer.nvidia.com/cuda-11.0-download-archive)

[cuDNN 8.0.4](https://developer.nvidia.com/rdp/cudnn-archive)

(Tensorflow-gpu 2.0.0 is verified to work with CUDA 10.0 on Windows if the above do not work)

## Installing with Anaconda on Windows

To use DeepPoseKit on Windows, you must first manually install `Shapely`, one of the dependencies for the [imgaug package](https://github.com/aleju/imgaug):
```bash
conda install -c conda-forge shapely
```

Install requirements with pip:
```bash
pip install --upgrade --r requirements.txt
```


# License

Released under a Apache 2.0 License. See [LICENSE](https://github.com/jgraving/deepposekit/blob/master/LICENSE) for details.

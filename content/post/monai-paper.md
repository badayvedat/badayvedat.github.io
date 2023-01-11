---
author: Vedat Baday

title: My notes on the MONAI paper

date: 2022-01-11

description: A brief guide to Turkish sentiment analysis with Hugging Face

tags: ["MONAI", "senior-project", "paper", "summary"]

---



* MONAI is opt-in and incremental over PyTorch

* Core components
  
  * Foundational components: Independent domain-specialized APIs compatible with PyTorch
    
    * Data
      
      * MetaTensor, MONAI's tensor class
        
        * Inherits and extends from the PyTorch's tensor.Tensor for compatibility and interoperability
        
        * Stores image metadata (e.g. DICOM, NIfTI image metadata)
        
        * Stores additional metadata such as transformations applied on the tensor
          
          * Helpful for inspecting the applied augmentations
          
          * Needed for actions such as inverse transforms
      
      * Cach-based datasets
      
      * Patch-based datasets
      
      * Enhanced data loader
    
    * Dataset
      
      * Due to the relative lack of high-quality labeling, data augmentation techniques are very important for effective learning
        
        * Pre-processing can be a significant overhead
      
      * MONAI provides extensions to the PyTorch Dataset class
        
        * Aims on caching and persistence to reduce the computational expense and overhead of the pre-processing
        
        * CacheDataset
          
          * Caches the results of deterministic operations of pre-processing pipelines in the *memory* for future training steps
          
          * Examples are pixel/voxel resampling, rescaling 
        
        * PersistentDataset
          
          * Analogous functionality to CacheDataset
          
          * Outputs of deterministic stages stored in an intermediary file system representation rather than memory
          
          * Use of this dataset is recommended for 3D datasets or where the overall dataset size is much larger than RAM
    
    * Reference Datasets
      
      * [MedMNIST](https://medmnist.com/), medical domain analogue of the MNIST
      
      * [Medical Segmentation Decathlon](https://arxiv.org/abs/2106.05735)
      
      * MONAI provides Dataset extension classes that simplify the downloading, storage, partitioning of these datasets.
        
        * As an extension of CacheDataset
      
      * MONAI consortium also manages a *msd-for-monai* S3 bucket in US and EU regions, via AWS Open Data for cloud-based model training and data distribution.
      
      * TciaDataset
        
        * Automatically downloads and extracts publicly-accessible datasets from the [The Cancer Imaging Archive](https://www.cancerimagingarchive.net/) with accompying DICOM segmentations, and acts as PyTorch datasets to generate training, validatino, and test data.
    
    * Readers & Writers
      
      * Support for various formats including NIfTI, DICOM
    
    * Transforms
      
      - Provides both domain-specific transforms and common transforms used in used in the volumetric medical-imaging deep learning pipelines
      
      - Majority of transforms are compatible with both PyTorch and Numpy input, not requiring the explicit conversion between the two formats
      
      - Physics-specific transforms
        
        - > Data acquired from magnetic resonance imaging is recorded in *k*-space, and therefore it is desirable to be able to augment MR images in the *k*-space domain.
          
          - I believe number of channels is referred as *k*-spaces.
      
      - Invertible transforms
        
        - Useful in some scenarios
          
          - TTA (Test Time Augmentation) Paper: [Aleatoric uncertainty estimation with test-time augmentation for medical image segmentation with convolutional neural
            networks](https://arxiv.org/abs/1807.07356)
          
          - Save inferred segmented image preserving the original geometry
    
    * Loss functions
      
      * Adhere to PyTorch API conventions and compatible with PyTorch
      
      * Provides specialized losses such as Dice, Tversky loss that are not present in the PyTorch.
      
      * Segmentation, regression, classification
    
    * Metrics
      
      - MONAI is among the initiatives of the *[Metrics Reloaded consortium](https://arxiv.org/abs/2206.01653)*
        
        - Mission of consortium is to "foster reliable algorithm validation through problem-aware choice of metrics with the long-term goal of enabling the treliable tracking of scientific progress and bridging the current chasm between AI research and translation into biomedical imaging practice"
      
      - DICE, ROCAUC, FROC, Hausdorff
    
    * Network Architectures
      
      * Network definitions provided by MONAI are divided into two categories
      
      *  Reference implementation of a published architecture
        
        * Such as ResNet, BasicUNet, EfficientNet and transformer based networks
        
        * 1/2/3D inputs and outputs based on the constructor parameters are defined where possible
      
      * Generaul purpose architectures
        
        * Defines sensible defaults
        
        * Inherits structures and components from other similar networks with customization without major rewrite
        
        * Compatible with [Torchscript](https://pytorch.org/tutorials/beginner/Intro_to_TorchScript_tutorial.html)
          
          * Allows trained networks to be loaded with not Python dependency (and thus no MONAI dependency)
    
    * Inference modules
      
      * For inference on large. volumes, the sliding window approach is used to achieve high performance with flexible memory requirements.
        
        * Typical processs
          
          Iteratively running batched window inferences untill all windows are analyzed
          
          Inference outputs are aggregated into a single segmentation map, and the results are saved to file
          
          Metrics computed
        
        * Selection of the continuous windows on the original image
      
      * *overlap* and *blending_mode* configurations are available to handle window overlap
      
      * Sliding windows, saliency Infer
    
    * Visualisations
      
      * Tensorboard integration
        
        * MONAI provides wrapper functions to enables several functionalities for visualization
        
        * The presentation of 3D images as GIFs on the Tensorboard
        
        * Set of 2D slices
        
        * Interactive 3D rendering 
      
      * Jupyter Notebook integration
      
      * Interpretability
        
        * "Which parts of the image were important in t arriving to a given decision of classification?"
        
        * MONAI supports [occlusion sensitivity](https://arxiv.org/abs/1311.2901), [Grad-CAM](https://arxiv.org/abs/1610.02391), [Smoothgrad](https://arxiv.org/abs/1706.03825) and TTA (Test Time Augmentation)
      
      * Utilities
        
        * *blend_image* to create RGB images from the superposition of images and labels
        
        * *matshow3d* to create 3D volume figure as a grid of images
    
    * Registration
      
      *  Registration is an image processing method for aligning multiple scenes into a single integrated image
      
      * Components from [DeepReg](https://arxiv.org/abs/2011.02580) are imported into MONAI
    
    * CSRC
      
      - C++/CUDA extensions for core MONAI Python APIs
  
  * MONAI workflows: For ease of robust training & evaluation of research experiments
    
    * MONAI training and inference workflows extend the Engine class of the [Ignite](https://pytorch.org/ignite/index.html)
      
      * Encapsulates the training loop while supporting online metric calculation, visualization, and saving network state
      
      * Simplified, quicker, easier workflows
      
      * SupervisedTrainer, SuperVisedEvaluator
    
    * Workflow event handler
      
      * Model checkpoint saving/loading, validation pipelines, LR scheduling, metrics report generation, network output saving, transform inverter
    
    * Provides utility *set_determinism* for reproducible results
      
      * Sets the random seed for PyTorch, Numpy, native Python random library, and backend flags



### Appendix

Typical PyTorch Training Loop

```python
for epoch in range(max_epochs):
    network.train()
    for inputs, labels in train_loader:
        optimizer.zero_grad()
        outputs = network(inputs)
        loss = loss_function(outputs, labels)
        labels.backward()
        optimizer.step()

    network.eval()
    with torch.no_grad():
        for val_inputs, val_labels in val_loader:
            val_outputs = network(val_inputs)
            metric(y_pred=val_outputs, y=val_labels)
            
        metric = metric.aggregate().item()
        print("Validation result:", metric)
```

MONAI Training Loop

```python
evaluator = SupervisedEvaluator(
    val_data_loader=val_loader,
    network=network,
    key_val_metric={ "metric": metric },
    ...
)

trainer = SupervisedTrainer(
    max_epochs=num_epochs,
    train_data_loader=train_loader,
    network=network,
    optimizer=optimizer,
    loss_function=loss_function,
    train_handlers=[ValidationHandler(1, evaluator)],
    ...
)

trainer.run()
```

Utility for reproducible workflows

```python
random_seed = 42
monai.utils.set_determinism(
    seed=random_seed,
    use_deterministic_algorithms=True
)

# perform computation

monai.utils.set_determinism(
    seed=None,
    use_deterministic_algorithms=False
)
```

### References

[1] MONAI: An open-source framework for deep learning in healthcare



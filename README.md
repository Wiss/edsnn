# Energy-dependent SNN

Code used for simulations in [Unveiling the role of local metabolic constraints on the structure and activity of spiking neural networks](https://www.biorxiv.org/content/10.1101/2023.10.25.563409v1) article


## Installation

### The easy way

Following this approach all the results in the article could be replicated. I will assume that you have miniconda3 installed. If not, you can follow the instructions [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install).

1. clone the repo
``` shell
git clone git@github.com:Wiss/edsnn.git
```
and go to the new folder: `cd edsnn`

2. create a conda environment

``` shell
edsnn $ conda env create -f environment.yml
```
This would create an environment with all the required packages. To activate the environment do: `conda activate nest_33_ehp`, which activate the environment with the default name given in the environment.yaml file

3. There is a folder (`edsnn/network/models/built_models`) containing all the necessary built models that nest requires to run the code and experiments. The nest installation associated with the conda environment needs to be able to find and use this files. So they need to exist in `~/miniconda3/envs/nest_33_ehp/lib_nest`. To automatically copy the built models into nest library run:

```shell
edsnn $ bash copy_built_models_to_nest_lib.sh
```

4. If everything works well, now you can run a test experiment. First go to the network folder:

``` shell
edsnn $ cd network
edsnn/network $ python -m src.experiment -f config/test.yaml
```

The results should appear in the `edsnn/network/results/test` folder.

**OBS:** Using this approach, you will not be able to generate new models (its not possible to run `network/neu-syn_cogeneration.py`). 

### for developing new models (more flexible but a harder way)

If you want to create your own energy-dependent models, then specific version of nest and nestml are required, In particular:

#### NEST
The code works with NEST v3.3. Specifically, under commit:
```
master@61f08e0ea
```
You can find that commit [here](https://github.com/nest/nest-simulator/commit/61f08e0ea4abb2d02c6019d409114b289c4dd3f3).

#### NESTML
The code works with NESTML Version [5.0.0-post-deb](https://zenodo.org/records/5784175). Particularly, under commit:
```
master@160253c61cad8b3facd2f3cdcd410015dc524c53
```
you can install that specific version by running:

``` shell
pip install https://github.com/nest/nestml/archive/160253c61cad8b3facd2f3cdcd410015dc524c53.zip
```

## Citation
```
@article {Jaras2023,
	author = {Jaras, Ismael and Orchard, Marcos E. and Maldonado, Pedro E. and Vergara, Rodrigo C.},
	title = {Unveiling the role of local metabolic constraints on the structure and activity of spiking neural networks},
	elocation-id = {2023.10.25.563409},
	year = {2023},
	doi = {10.1101/2023.10.25.563409},
	publisher = {Cold Spring Harbor Laboratory},
	URL = {https://www.biorxiv.org/content/early/2023/10/27/2023.10.25.563409},
	eprint = {https://www.biorxiv.org/content/early/2023/10/27/2023.10.25.563409.full.pdf},
	journal = {bioRxiv}
}
```

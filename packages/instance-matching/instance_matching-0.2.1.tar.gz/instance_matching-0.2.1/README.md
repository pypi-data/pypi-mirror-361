
# Instance-Matching

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/1017841272.svg)](https://doi.org/10.5281/zenodo.15861414)

**Instance-Matching** is a lightweight Python toolkit for extracting, matching, evaluating and visualizing correspondences between high-definition map lane-level instances (center-lines and lane-dividers) and per-frame local inference results.


## 📦 Installation

```bash
# 0) (Optional) create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 1) Install system dependencies (required for cyipopt)
conda install -c conda-forge pkg-config ipopt

# 2a) Install from PyPI
pip install instance-matching

# 2b) For development, clone and install in editable mode
git clone git@github.com:wjswlsghks98/instance-matching.git
cd instance-matching
pip install --editable .
````

---

## 📂 Data Preparation

For performing evaluation of instance matching module, first download data files from the [Zenodo repository](https://doi.org/10.5281/zenodo.15860891).

Running evaluation of this package expects `.osm` and preprocessed `.pkl` files under a `data/` directory at the project root:

```
instance-matching/
├── data/
│   ├── boston-seaport.osm
│   ├── boston-seaport.pkl
│   ├── singapore-hollandvillage.osm
│   ├── singapore-hollandvillage.pkl
│   └── …
```


---

## 🚀 Quick Start

### 1) Create `config.yaml`

```yaml
mode: matching

map_names:
  - boston-seaport

map_origins:
  boston-seaport: [42.336849169438615, -71.05785369873047]
  singapore-hollandvillage: [1.2993652317780957, 103.78217697143555]
  singapore-onenorth: [1.2882100868743724, 103.78475189208984]
  singapore-queenstown: [1.2782562240223188, 103.76741409301758]

match:
  mode: ablation            # ablation, geom, topo, geom-topo, fusion-base, fusion, gromov-wasserstein
  eval_mode: comparison     # comparison or forward
  params:
    padding_cost: 10
    weights: [1.0, 1.0, 1.0, 1.0, 1.0]
  verbose: iter-detailed
  precompute: false
```

### 2) Run via CLI

```bash
instance-matching run --config config.yaml
```

### 3) Run via Python API

```python
import yaml
from instance_matching import run_evaluation

cfg = yaml.safe_load(open("config.yaml"))
run_evaluation(cfg)
```

---

## 🔧 Core Modules

* **`cli.py`**       – command-line entry point (`run --config …`)
* **`evaluator.py`** – orchestration of extract, match, evaluate (`run_evaluation`)
* **`extractor.py`** – GT & local instance extraction (`extract_local_instances`, etc.)
* **`reporter.py`**  – aggregation & terminal reporting (`Reporter` class)
* **`visualizer.py`**– plotting utilities (`plot`)
* **`matcher/`**     – matching algorithms:

  * `InstanceMatcher` for optimization-based matching
  * `GromovWasserstein` for GW-based matching
* **`utils.py`**     – sampling, distance, adjacency helper functions

---

## 📖 Usage Example

```python
from shapely.geometry import Polygon
from instance_matching import (
    extract_local_instances,
    Reporter,
    InstanceMatcher,
)

# 1) Load full GT instances (e.g. from pickle)
# user defined loading function is needed (for examples, look src/evaluator.py)
full = load_full_instances("data/boston-seaport.pkl")

# 2) Sample per-frame local instances
perception_box = Polygon([...])
local = extract_local_instances(full, perception_box, noise_std=0.3, offset_std=0.3)

# 3) Match
matcher = InstanceMatcher(full, local, config["match"])
report = matcher.match()

# 4) Aggregate & print
rep = Reporter(mode="matching")
rep.update("boston-seaport", [report])
rep.print("boston-seaport", trip_iter=1, tripN=1, frame_iter=1, frameN=1)
```

## 📄 License

This project is licensed under the **MIT License** – see [LICENSE](LICENSE).

## Cite

If you are using our work in your study, please cite our paper
```
@ARTICLE{Jeon2025InstanceMatching,
author={Jeon, Jinhwan and Choi, Seibum B.},
journal={IEEE Transactions on Intelligent Transportation Systems}, 
title={Efficient Arc Spline Approximation of Large Sized Complex Lane-Level Road Maps}, 
year={2025},
volume={},
number={},
pages={**},
keywords={**},
doi={**}
}
```

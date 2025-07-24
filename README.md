# NYC Restaurant Inspections

This repository contains an analysis of the NYC Restaurant Inspections database.

## Local Setup

1. Ensure uv is installed. If not, install it by running in a powershell: 
    ```
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

2. Ensure you have python installed. Run in a terminal `uv python install` to install the most recent stable python version

3. Add python to your PATH  by running: `uv python update-shell`

4. Run `uv sync` to create the virtual environment based on the dependencies identified in `pyproject.toml`



When setting up a project from zero/first time: `uv init` to generate the `pyproject.toml`

To add new python packages: `uv add <package_name>` (this installs and adds the packages to the dependencies section of the pyproject.toml file)

To run python scripts on the terminal, use `uv run python <script_name>.py` instead of traditional  `python <script_name>.py` 

## Getting a Mistral API Key to run the GenAI section

1.  Create a Mistral account and select the free plan https://auth.mistral.ai/ui/registration

2. Once you have an account go to https://console.mistral.ai/home
3. Go to API keys on the left panel and generate a new API key
4. Open the .yaml file `notebooks/secrets.yaml` and add your newly created key. Save the file.


## Repo Structure

The core of the code developed is available in `notebooks/nyc_inspections_part_II.ipynb`.

```
nyc_inspections/
├── data/*
├── documentation/*
├── figures/*
├── models/*
└── notebooks/
    └── nyc_inspections_I.ipynb
    └── nyc_inspections_II.ipynb
    └── secrets.yaml
└── src/
    └── preprocess.py
```


* `data/`: folder that contains the .csv with the data for this project
* `documentation/`: folder that contains documentation related to the dataset
* `figures/`: folder to store generated figures
* `models/`: folder to store ML models and parameters
* `notebooks/`: folder that contains notebooks and the `secrets.yaml`file
    * `nyc_inspections_I.ipynb`: this notebook contains initial analysis. This analysis resulted in the `Preprocess` available in `src/preprocess.py` that is responsible for cleaning up and aggregating the data.
    * `nyc_inspections_II.ipynb`: this notebook contains the core of the tasks: 
        * data preprocessing for ML Models
        * ML model training and results
        * Insights
        * GenAI
* `src/`: folder that contains python functions and classes




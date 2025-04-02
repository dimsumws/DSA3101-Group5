# Guest Journey Patterns
## Overview

## Data and Methodology
**File:** `data_preparation.py` 
* Python script used to filter relevant responses from survey data
* Create list of sequences based on path matrix from survey data and concatenated to original survey data   
**File** `guest_journey_analysis.ipynb`
* Jupyter notebook for data visualisation and analysis   
**File:** `guest_path_plot.py`
* Python script used to generate plots on guests movement in the order of navigation of USS     
**File:** `sequence_mining.py`
* Python script for sequence mining using SPMF's TNS algorithm for sequence analysis

## Analysis

### Sequence Analysis using TNS Algorithm
The algorithm used for this project is the TNS algorithm, used to discovering the **top-k non-redundant sequential rules** appearing in a sequence database.
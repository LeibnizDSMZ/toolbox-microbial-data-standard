[![release: 0.1.0](https://img.shields.io/badge/rel-0.1.0-blue.svg?style=flat-square)](https://github.com/LeibnizDSMZ/toolbox-microbial-data-standard)
[![MIT LICENSE](https://img.shields.io/badge/License-MIT-brightgreen.svg?style=flat-square)](https://choosealicense.com/licenses/mit/)

# Toolbox to work with microbial strain data standard


A collection of helpful tools to improve the work with files formatted in the new microbial
data standard. At the moment his toolbox includes:

## IO functions
Simplifying the input and output of files formatted in the new data standard:

### Read a file with strain data
```python
from toolbox_microbial_strain_data.io_functions import (
    load_microbial_strain_data,
)

strain_data_object = load_microbial_strain_data("PATH/TO/INPUT-FILE.json")
```

### Write a file of strain data
```python
from toolbox_microbial_strain_data.io_functions import (
    write_microbial_strain_to,
)

write_microbial_strain_to(strain_data_object, "PATH/TO/OUTPUT-FILE.json")
```


## Merge function

Merging two datasets of microbial strain data formatted in the new standard is a typical
task. This function is handling the technical aspects of merging the datasets. The decision
if two datasets should be merged has to be handled extra.

### Merge
```python
from toolbox_microbial_strain_data import merge, io_functions

# Read two datasets from json files:
dataset_1 = io_functions.load_microbial_strain_data("PATH/TO/INPUT-FILE-1.json")
dataset_2 = io_functions.load_microbial_strain_data("PATH/TO/INPUT-FILE-2.json")

# if dataset_1 and dataset_2 are about the same strain you can merge them with:

merged_dataset = merge.merge_strains(dataset_1, dataset_2)
```
The merged dataset will automatically join the lists of sources, skipping source duplicates.
Every datapoint with a source information in the datasets will be merged if it is an exact
duplicate.

## Split functions

### Split by source object
```python
from toolbox_microbial_strain_data import split, io_functions

# Read a dataset from json files:
dataset = io_functions.load_microbial_strain_data("PATH/TO/INPUT-FILE.json")

# define source whose data should be split from the original file
source_to_split = "ANY_TYPE_OF_SOURCE_OBJECT"

data_without_this_source, data_of_split_source = split.split_data_by_source(dataset, source_to_split)
```
Splitting a dataset by providing the data set and the source whose data should be split
from the original file. Returns two datasets, both of type `Strain`.

### Split by source index
```python
from toolbox_microbial_strain_data import split, io_functions

# Read a dataset from json files:
dataset = io_functions.load_microbial_strain_data("PATH/TO/INPUT-FILE.json")

# define source whose data should be split from the original file by index
source_index_to_split = 1 # splits of the data from sources index 1

data_without_this_source, data_of_split_source = split.split_data_by_source_index(dataset, source_index_to_split)
```
Splitting a dataset by providing the index of the source whose data should be split
from the original file. Returns two datasets, both of type `Strain`.

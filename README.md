# Assassin's Query
> Building a simple index and implementing querying against it.

## Installation instructions
Before running the project you will have to install the following dependencies.

```
pip install nltk
```

In order to run the program you will also have to download `punkt`.
```
nltk.download('punkt')
```

## Running
For the ease of use both python scripts `RetrieveSequential.py` and `RetrieveInvertedIndex.py` provide explanation about the optional parameters when using the argument `--help`.

The script requires one compulsory argument: #query. Example:
```python
python RetrieveSequential.py "spletna storitev"
```
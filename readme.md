## usage


```bash
python bib2csv.py -h
python csv2bib.py -h
```
```bash
# read initial bib (collected from web) to csv
python bib2csv.py -b ./examples/web_refs.bib -c refs.csv

# create refs.bib bibtex file from previously-generated csv
python csv2bib.py -c refs.csv -b refs.bib
```

```bash
python bib2csv.py -b ./examples/web_refs.bib -c refs.csv && python csv2bib.py -c refs.csv -b refs.bib
```


## installation

dependencies: pybtex, pandas, argparse

I use `conda` but you can just as easily install with `pip` or other.

```bash
conda install -c conda-forge pybtex
conda install -c conda-forge pandas
conda install -c conda-forge argparse
```

## links

https://docs.pybtex.org/api/index.html
http://www.paolomonella.it/pybtex/index.html
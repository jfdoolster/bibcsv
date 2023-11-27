import pandas as pd
import pybtex.database
import pybtex.utils

from bibtypes import bib_entry_types

# pylint: disable=redefined-outer-name

class ConvertCsv2Bib:
    def __init__(self, csv_path: str, bib_path = 'refs.bib', tex_path='refs.tex', display_citations=False):
        print(f"\nReading csv file '{csv_path}' ...")
        self.dfin = pd.read_csv(csv_path, quotechar='"', sep='\t', dtype=str)
        self.dfin = self.dfin.fillna('')
        print(f"File Read! Found {self.number_of_entries()} reference(s)")

        print("Converting .csv to .bib ...")
        self.bib_data = self.initialize_entries()
        self.populate_entries()
        print("Conversion completed!")


        self.cite_str = self.create_cite_list()
        if display_citations:
            print(self.cite_str)

        self.create_refs_tex(tex_path,bib_path)

        self.bib_data.to_file(bib_path, 'bibtex')
        print(f"Output bib file '{bib_path}'", end="\n\n")

    def number_of_entries(self) -> int:
        return len(self.dfin)

    def initialize_entries(self) -> pybtex.database.BibliographyData:
        tmp_dict = {}
        for _, row in self.dfin.iterrows():
            entry_key = row['entry_key']
            entry_type = row['entry_type']
            if entry_type not in bib_entry_types:
                print(f"WARN ({entry_key}): '{entry_type}' is not a recognized bibtex entry type (ignored)")
                continue
            tmp_dict[entry_key] = pybtex.database.Entry(entry_type, [])
        return pybtex.database.BibliographyData(tmp_dict)

    def populate_entries(self):
        for _, row in self.dfin.iterrows():
            entry_key = row['entry_key']
            entry_type = row['entry_type']
            if entry_key not in list(self.bib_data.entries):
                continue

            for required_field in bib_entry_types[entry_type]['required']:
                if row[required_field] == "":
                    print(f"WARN ({entry_key}): required field '{required_field}' is empty")
                self.bib_data.entries[entry_key].fields[required_field] = row[required_field]

            for optional_field in bib_entry_types[entry_type]['optional']:
                if optional_field in self.dfin.columns:
                    self.bib_data.entries[entry_key].fields[optional_field] = row[optional_field]

            entry_specific_fields = bib_entry_types[entry_type]['required'] + \
                                    bib_entry_types[entry_type]['optional'] + \
                                    ['entry_key', 'entry_type']

            for remaining_field in self.dfin.columns:
                if (remaining_field not in entry_specific_fields) and (row[remaining_field] != ""):
                    self.bib_data.entries[entry_key].fields[remaining_field] = row[remaining_field]

    def create_cite_list(self) -> str:
        entry_list = list(self.bib_data.entries)
        cites=""
        for i,e in enumerate(entry_list):
            if i == (len(entry_list)-1):
                cites += e+""
                continue
            cites += e+","
        cite_str=r"All Citations~\cite{"+cites+r"}%"
        return cite_str

    def create_refs_tex(self, tex_path: str, bib_path: str):
        bib = bib_path.split('/')[-1]
        refs = bib[:bib.index('.bib')]
        with open(tex_path, "w", encoding="utf_8") as tex_file:
            tex_file.writelines([
                r"\documentclass[email=false]{achemso}", "\n",
                r"\title{Full List of References}", "\n",
                r"\begin{document}", "\n",
                self.cite_str, "\n",
                r"\bibliography{"+f"{refs:s}"+"}", "\n",
                r"\end{document}"])




if __name__ =="__main__":

    import os
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--csv_path', required=True, type=str,
        help='path to IINPUT csv file')
    parser.add_argument('-b', '--bib_path', default='refs.bib', type=str,
        help='path to OUTPUT bibtex file')
    parser.add_argument('-t', '--tex_path', default='refs.tex', type=str,
        help='path to OUTPUT tex file with bibliography only')
    args = parser.parse_args()
    argdict = vars(args)

    csv_path=os.path.abspath(argdict['csv_path'])
    bib_path=os.path.abspath(argdict['bib_path'])
    tex_path=os.path.abspath(argdict['tex_path'])
    if not os.path.isfile(csv_path):
        print(f"ERROR: file '{csv_path}' does not exist")
        sys.exit()

    ConvertCsv2Bib(csv_path, bib_path, tex_path, display_citations=True)

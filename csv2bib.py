import pybtex.database
import pandas as pd
from utils import bib_entry_types

class csv2bib:
    def __init__(self, csvname: str, bibname = 'refs.bib'):
        print(f"Reading csv file '{csvname}' ...")
        self.dfin = pd.read_csv(csvname, quotechar="'", sep='\t', dtype=str)
        self.dfin = self.dfin.fillna('')
        print(f"File Read! Found {self.number_of_entries()} reference(s)", end="\n\n")

        self.bib_data = self.initialize_entries()
        self.populate_entries()
        self.bib_data.to_file(bibname, 'bibtex')

    def number_of_entries(self) -> int:
        return len(self.dfin)

    def initialize_entries(self):
        tmp_dict = {}
        for _, row in self.dfin.iterrows():
            tmp_dict[row['entry_key']] = pybtex.database.Entry(row['entry_type'], [])
        return pybtex.database.BibliographyData(tmp_dict)

    def populate_entries(self):
        for _, row in self.dfin.iterrows():
            entry_key = row['entry_key']
            entry_type = self.bib_data.entries[entry_key].type
            if entry_type not in bib_entry_types:
                print(f"WARN ({entry_key}): '{entry_type}' is not a recognized bibtex entry type (ignored)")
                continue

            for required_field in bib_entry_types[entry_type]['required']:
                if row[required_field] == "":
                    print(f"WARN ({entry_key}): required field '{required_field}' is empty")
                self.bib_data.entries[entry_key].fields[required_field] = row[required_field]

            for optional_field in bib_entry_types[entry_type]['optional']:
                if row[optional_field] != "":
                    self.bib_data.entries[entry_key].fields[optional_field] = row[optional_field]

            entry_specific_fields = bib_entry_types[entry_type]['required'] + \
                                    bib_entry_types[entry_type]['optional'] + \
                                    ['entry_key', 'entry_type']

            for remaining_field in self.dfin.columns:
                if (remaining_field not in entry_specific_fields) and (row[remaining_field] != ""):
                    self.bib_data.entries[entry_key].fields[remaining_field] = row[remaining_field]









if __name__ =="__main__":

    csv2bib("refs.csv")
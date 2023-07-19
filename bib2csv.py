#import argparse
import pybtex.database
import pybtex.utils
import pandas as pd
from utils import bib_entry_types

class bib2csv:
    def __init__(self, bibname: str, csvname='refs.csv', custom_keys=True):
        print(f"Parsing bibtex file '{bibname}' ...")
        self.bib_data = pybtex.database.parse_file(bibname)
        print(f"File Parsed! Found {self.number_of_entries()} reference(s)", end="\n\n")

        self.dfout = pd.DataFrame()
        self.populate_df(custom_keys)
        self.validate_df()
        self.reorder_df()

        self.dfout.to_csv(csvname, index=False, quotechar="'", sep='\t')
        print(f"\nbibtex file '{bibname}' converted to csv '{csvname}'!", end="\n\n")

    def reorder_df(self):
        self.dfout = self.dfout[[
            'entry_key', 'entry_type','keywords',
            'title','author','journal','booktitle',
            'url','doi',
            'year','month',
            'publisher','organization','school','institution',
            'volume','number','pages','chapter','edition','series',
            'editor',
            'address',
            'annote',
            'crossref',
            'howpublished',
            'key',
            'note',
            'eprint',
            'biburl',
            'isbn',
            'abstract']]

    def validate_df(self) -> None:
        for _, row in self.dfout.iterrows():
            entry_key  = row['entry_key']
            entry_type = row['entry_type']
            if entry_type not in bib_entry_types:
                print(f"WARN ({entry_key}): '{entry_type}' is not a recognized bibtex entry type")
                continue
            for required_field in bib_entry_types[entry_type]['required']:
                if row[required_field] == "":
                    print(f"WARN ({entry_key}): required field '{required_field}' is empty")

    def populate_df(self, custom_keys: bool) -> None:
        for e in self.list_of_entries():
            entry_key = e
            if custom_keys:
                entry_key = self.custom_entry_key(e, display=True)
            tmp_dict = {
                "entry_key": entry_key,
                "entry_type": self.get_entry_type(e),

                "address": self.get_field(e, 'address'),
                "annote": self.get_field(e, 'annote'),
                "author": self.create_author_str(e),
                "booktitle": self.get_field(e, 'booktitle'),
                "chapter": self.get_field(e, 'chapter'),
                "crossref": self.get_field(e, 'crossref'),
                "edition": self.get_field(e, 'edition'),
                "editor": self.get_field(e, 'editor'),
                "howpublished": self.get_field(e, 'howpublished'),
                "institution": self.get_field(e, 'institution'),
                "journal": self.get_field(e, 'journal'),
                "key": e,
                "month": self.get_field(e, 'month'),
                "note": self.get_field(e, 'note'),
                "number": self.get_field(e, 'number'),
                "organization": self.get_field(e, 'organization'),
                "pages": self.get_field(e, 'pages'),
                "publisher": self.get_field(e, 'publisher'),
                "school": self.get_field(e, 'school'),
                "series": self.get_field(e, 'series'),
                "title": self.get_field(e, 'title'),
                "volume": self.get_field(e, 'volume'),
                "year": self.get_field(e, 'year'),

                "keywords": self.get_field(e, 'keywords'),
                "url": self.get_field(e, 'url'),
                "doi": self.get_field(e, 'doi'),
                "eprint": self.get_field(e, 'eprint'),
                "biburl": self.get_field(e, 'biburl'),
                "isbn": self.get_field(e, 'isbn'),
                "abstract": self.get_abstract(e),
            }
            tmp_df = pd.DataFrame([tmp_dict])
            #print(json.dumps(tmp_dict,sort_keys=True, indent=4))
            self.dfout = pd.concat([self.dfout, tmp_df], ignore_index=True)

    def list_of_entries(self) -> list:
        return list(self.bib_data.entries)

    def number_of_entries(self) -> int:
        return len(self.bib_data.entries)

    def get_entry_type(self, entry_key: str) -> str:
        return self.bib_data.entries[entry_key].type

    def list_fields(self, entry_key: str) -> pybtex.utils.OrderedCaseInsensitiveDict:
        return self.bib_data.entries[entry_key].fields

    def get_abstract(self, entry_key: str) -> str:
        abstract = ""
        if "abstract" in self.list_fields(entry_key):
            abstract = self.get_field(entry_key, 'abstract')
        elif "abstractNote" in self.list_fields(entry_key):
            abstract = self.get_field(entry_key, 'abstractNote')
        return abstract

    def get_field(self, entry_key: str, field_name: str) -> str:
        value = ""
        try:
            value = self.bib_data.entries[entry_key].fields[field_name.lower()]
        except KeyError:
            value = ""
        #if ',' in value:
        #    print(f"WARN: comma (',') found in '{field_name}' ({entry_key})")
        return value

    def get_first_author(self, entry_key: str) -> pybtex.database.Person:
        return self.bib_data.entries[entry_key].persons['author'][0]

    def custom_entry_key(self, entry_key, display=False) -> str:
        lastname = ''.join(self.get_first_author(entry_key).last_names)
        year = self.get_field(entry_key, 'year')

        custom_key = entry_key
        if len(year) != 0:
            custom_key = f"{lastname}{year}"
            if display:
                print(f"Re-Keying '{entry_key}' -> '{custom_key}'")

        return custom_key


    def create_author_str(self, entry_key: str) -> str:
        author_list = self.bib_data.entries[entry_key].persons['author']
        author_str = ""
        for i,p in enumerate(author_list):
            first_name = ''.join(p.first_names)
            middle_name = ''.join(p.middle_names)
            last_name = ''.join(p.last_names)
            #print(type(first_name), type(middle_name), type(last_name))
            author_str += f"{first_name:s} {middle_name:s} {last_name:s}"
            if i != (len(author_list) - 1):
                author_str += "  and  "
        return author_str



if __name__ =="__main__":

    #parser = argparse.ArgumentParser()
    #parser.add_argument('-b', '--bib', required=True, type=str,
    #    help='path to INPUT bibtex file')
    #parser.add_argument('-c', '--csv', required=True, type=str,
    #    help='path to OUTPUT csv file')
    #args = parser.parse_args()
    #argdict = vars(args)

    bib2csv("~/Downloads/csp_6_.bib")

    df0 = pd.read_csv('refs.csv', quotechar="'", sep='\t')

    print(df0.columns)

    #print(df0.loc[0,'abstract'])

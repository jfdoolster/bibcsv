import argparse
import pybtex.database
import pybtex.utils
import pandas as pd

class bib2tsv:
    def __init__(self, fname: str, csvname='refs.tsv', custom_keys=True):
        print(f"Parsing bibtex file '{fname}' ...")
        self.bib_data = pybtex.database.parse_file(fname)
        print(f"File Parsed! Found {self.number_of_entries()} reference(s)", end="\n\n")

        self.dfout = pd.DataFrame()
        self.populate_df(custom_keys)

        self.dfout.to_csv(csvname, index=False, sep='\t')
        print(f"\nbibtex file '{fname}' converted to tsv '{csvname}'!", end="\n\n")

    def reorder_df(self):
        pass

    def populate_df(self, custom_keys: bool):
        for e in self.list_of_entries():
            key = e
            if custom_keys:
                key = self.create_custom_key(e)
            tmp_dict = {
                "key": key,
                "content-type": self.get_content_type(e),
                "note": self.get_field(e, 'note'),
                "keywords": self.get_field(e, 'keywords'),

                "journal": self.get_field(e, 'journal'),
                "title": self.get_field(e, 'title'),
                "author": self.create_author_str(e),

                "url": self.get_field(e, 'url'),

                "year": self.get_field(e, 'year'),
                "month": self.get_field(e, 'month'),

                "pages": self.get_field(e, 'pages'),
                "volume": self.get_field(e, 'volume'),
                "number": self.get_field(e, 'number'),
                "chapter": self.get_field(e, 'chapter'),
                "series": self.get_field(e, 'series'),
                "publisher": self.get_field(e, 'publisher'),

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

    def get_content_type(self, entry_key: str) -> str:
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
        if '\t' in value:
            print(f"WARN: semicolon (';') found in '{field_name}' ({entry_key})")
        return value

    def get_first_author(self, entry_key: str) -> pybtex.database.Person:
        return self.bib_data.entries[entry_key].persons['author'][0]

    def create_custom_key(self, entry_key) -> str:
        lastname = ''.join(self.get_first_author(entry_key).last_names)
        year = self.get_field(entry_key, 'year')

        custom_key = entry_key
        if len(year) != 0:
            custom_key = f"{lastname}{year}"
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

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bibtex', required=True, type=str,
        help='path to bibtex file')
    args = parser.parse_args()
    argdict = vars(args)

    bib2tsv("~/Downloads/csp_6_.bib")

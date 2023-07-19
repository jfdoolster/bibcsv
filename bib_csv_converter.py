import pybtex.database
import pybtex.utils
import pandas as pd
import json

class ConvertBib2Csv:
    def __init__(self, bib_path: str, csv_path='refs.csv', custom_keys=True, display_keywords=False):
        print(f"\nParsing bibtex file '{bib_path}' ...",)
        self.bib_data = pybtex.database.parse_file(bib_path)
        print(f"File parsed! Found {self.number_of_entries()} reference(s)")

        print("Converting .bib to .csv ...")
        self.dfout = pd.DataFrame()
        self.populate_df(custom_keys)
        self.validate_df()
        self.reorder_df()
        print("Conversion completed!")

        if display_keywords:
            self.check_keywords()

        self.dfout.to_csv(csv_path, index=False, quotechar="'", sep='\t')
        print(f"Output csv file '{csv_path}'", end="\n\n")

    def check_keywords(self):
        keywords = self.dfout['keywords']
        keywords_all = []
        for kw in keywords:
            kw_list = [x.strip() for x in kw.split(',')]
            for k in kw_list:
                keywords_all.append(k)
        keywords_all = [i for i in keywords_all if i != ""]

        kw_dict = {}
        keywords_del = keywords_all
        for kw in keywords_all:
            if kw in keywords_del:
                kw_dict[kw] = keywords_all.count(kw)
                keywords_del = [i for i in keywords_del if i != kw]

        print(json.dumps(kw_dict, sort_keys=True, indent=4))
        print(keywords_del)


    def reorder_df(self):
        self.dfout = self.dfout[[
            'entry_key', 'keywords',
            'howpublished','journal','publisher',
            'title','booktitle',
            'link','url','doi','entry_type',
            'author','editor',
            'organization','school','institution',
            'year','month',
            'volume','number','pages','chapter','edition','series',
            'address',
            'annote',
            'crossref',
            'key',
            'note',
            'eprint',
            'biburl',
            'isbn',
            'abstract']]
        self.dfout = self.dfout.sort_values(by=['entry_key'])

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
                "author": self.create_person_str(e, ptype='author'),
                "booktitle": self.get_field(e, 'booktitle'),
                "chapter": self.get_field(e, 'chapter'),
                "crossref": self.get_field(e, 'crossref'),
                "edition": self.get_field(e, 'edition'),
                "editor": self.create_person_str(e, ptype='editor'),
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

                "keywords": self.get_keywords(e),
                "link":  self.get_field(e, 'link'),
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
            self.dfout = self.dfout.fillna('')

    def list_of_entries(self) -> list:
        return list(self.bib_data.entries)

    def number_of_entries(self) -> int:
        return len(self.bib_data.entries)

    def get_entry_type(self, entry_key: str) -> str:
        return self.bib_data.entries[entry_key].type

    def list_fields(self, entry_key: str) -> pybtex.utils.OrderedCaseInsensitiveDict:
        return self.bib_data.entries[entry_key].fields

    def get_keywords(self, entry_key: str) -> str:
        keywords = ""
        kw_str = self.get_field(entry_key, 'keywords')
        kw_list = [x.strip().lower() for x in kw_str.split(',')]
        kw_list.sort()
        if len(kw_list) > 0:
            keywords = ', '.join(kw_list)
        return keywords


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

    def get_main_name(self, entry_key: str) -> str: #pybtex.database.Person:
        main_name = "Misc"
        persons = self.bib_data.entries[entry_key].persons
        for ptype in ['author', 'editor']:
            if ptype in persons.keys():
                tmp = (persons[ptype])[0]
                main_name = ''.join(tmp.last_names)
                for rep in ['.', ',', '-', r'\`', r'\~']:
                    main_name = main_name.replace(rep, "")
                return main_name

        for field in ['orgainization','institution']:
            tmp_str = self.get_field(entry_key, field)
            if tmp_str != "":
                main_name = "".join(tmp_str.split())
                for rep in ['.', ',', '-', r'\`', r'\~']:
                    main_name = main_name.replace(rep, "")
                return main_name

        return main_name



    def custom_entry_key(self, entry_key, display=False) -> str:
        main_name = self.get_main_name(entry_key)
        year = self.get_field(entry_key, 'year')

        custom_key = entry_key
        if len(year) != 0 and main_name != 'Misc':
            custom_key = f"{main_name}{year}"
            if display:
                print(f"Re-Keying '{entry_key}' -> '{custom_key}'")

        return custom_key

    def create_person_str(self, entry_key: str, ptype: 'author') -> str:
        person_str = ""
        persons = self.bib_data.entries[entry_key].persons
        if ptype not in persons.keys():
            return ""
        person_list = persons[ptype]
        for i,p in enumerate(person_list):
            first_name = ''.join(p.first_names)
            middle_name = ''.join(p.middle_names)
            last_name = ''.join(p.last_names)
            #print(type(first_name), type(middle_name), type(last_name))
            person_str += f"{first_name:s} {middle_name:s} {last_name:s}"
            if i != (len(person_list) - 1):
                person_str += "  and  "
        return person_str

class ConvertCsv2Bib:
    def __init__(self, csv_path: str, bib_path = 'refs.bib', display_citations=False):
        print(f"\nReading csv file '{csv_path}' ...")
        self.dfin = pd.read_csv(csv_path, quotechar="'", sep='\t', dtype=str)
        self.dfin = self.dfin.fillna('')
        print(f"File Read! Found {self.number_of_entries()} reference(s)")

        print("Converting .csv to .bib ...")
        self.bib_data = self.initialize_entries()
        self.populate_entries()
        print("Conversion completed!")

        if display_citations:
            self.create_cite_list()

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

    def create_cite_list(self):
        print("\n\\cite{", end="")
        entry_list = list(self.bib_data.entries)
        for i,e in enumerate(entry_list):
            if i == (len(entry_list)-1):
                print(e, end="}\n\n")
                continue
            print(e, end=", ")

# https://www.openoffice.org/bibliographic/bibtex-defs.html
bib_entry_types = {
    'article': {
        'required': ['author', 'title', 'journal', 'year'],
        'optional': ['volume', 'number', 'pages', 'month', 'note'],
    },
    'book': {
        'required': ['author', 'editor', 'title', 'publisher', 'year'],
        'optional': ['volume', 'number', 'series', 'address', 'edition', 'month', 'note'],
    },
    'booklet': {
        'required': ['title'],
        'optional': ['author', 'howpublished', 'address', 'month', 'year', 'note'],
    },
    'conference': {
        'required': ['author', 'title', 'booktitle', 'year'],
        'optional': ['editor', 'volume', 'number', 'series', 'pages', 'address', 'month', 'organization', 'publisher', 'note'],
    },
    'inbook': {
        'required': ['author', 'editor', 'title', 'chapter', 'pages', 'publisher', 'year'],
        'optional': ['volume', 'number', 'series', 'type', 'address', 'edition', 'month', 'note'],
    },
    'incollection': {
        'required': ['author', 'title', 'booktitle', 'publisher', 'year'],
        'optional': ['editor', 'volume', 'number', 'series', 'type', 'chapter', 'pages', 'address', 'edition', 'month', 'note'],
    },
    'inproceedings': {
        'required': ['author', 'title', 'booktitle', 'year'],
        'optional': ['editor', 'volume', 'number', 'series', 'pages', 'address', 'month', 'organization', 'publisher', 'note'],
    },
    'manual': {
        'required': ['title'],
        'optional': ['author', 'organization', 'address', 'edition', 'month', 'year', 'note'],
    },
    'mastersthesis': {
        'required': ['author', 'title', 'school', 'year'],
        'optional': ['type', 'address', 'month', 'note'],
    },
    'misc': {
        'required': [],
        'optional': ['author', 'title', 'howpublished', 'month', 'year', 'note'],
    },
    'phdthesis': {
        'required': ['author', 'title', 'school', 'year'],
        'optional': ['type', 'address', 'month', 'note'],
    },
    'proceedings': {
        'required': ['title', 'year'],
        'optional': ['editor', 'volume', 'number', 'series', 'address', 'month', 'organization', 'publisher', 'note'],
    },
    'techreport': {
        'required': ['author', 'title', 'institution', 'year'],
        'optional': ['type', 'number', 'address', 'month', 'note'],
    },
    'unpublished': {
        'required': ['author', 'title', 'note'],
        'optional': ['month', 'year'],
    },
}


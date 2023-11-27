import os
import sys
from bibcsv import ConvertCsv2Bib, ConvertBib2Csv

if __name__ == "__main__":

    # create formatted csv from bib
    bib_path=os.path.abspath('./examples/web_refs.bib')
    if not os.path.isfile(bib_path):
        print(f"ERROR: file '{bib_path}' does not exist")
        sys.exit()
    csv_path=os.path.abspath('./examples/web_refs.csv')
    tex_path=os.path.abspath("./examples/web_refs.tex")
    ConvertBib2Csv(bib_path, csv_path, custom_keys=True)
    c2b = ConvertCsv2Bib(csv_path, None, display_citations=True)
    c2b.create_refs_tex(tex_path, bib_path)

    # from formatted csv
    csv_path=os.path.abspath("./examples/refs.csv")
    if not os.path.isfile(csv_path):
        print(f"ERROR: file '{csv_path}' does not exist")
        sys.exit()
    bib_path=os.path.abspath("./examples/refs.bib")
    tex_path=os.path.abspath("./examples/refs.tex")
    c2b = ConvertCsv2Bib(csv_path, bib_path, display_citations=True)
    c2b.create_refs_tex(tex_path, bib_path)

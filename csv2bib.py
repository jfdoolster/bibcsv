
if __name__ =="__main__":

    import os
    import sys
    import argparse
    from bib_csv_converter import ConvertCsv2Bib

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--csv_path', required=True, type=str,
        help='path to IINPUT csv file')
    parser.add_argument('-b', '--bib_path', default='refs.bib', type=str,
        help='path to OUTPUT bibtex file')
    args = parser.parse_args()
    argdict = vars(args)

    csv_path=os.path.abspath(argdict['csv_path'])
    bib_path=os.path.abspath(argdict['bib_path'])
    if not os.path.isfile(csv_path):
        print(f"ERROR: file '{csv_path}' does not exist")
        sys.exit()

    ConvertCsv2Bib(csv_path, bib_path, display_citations=True)


if __name__ =="__main__":
    import os
    import sys
    import argparse
    from bib_csv_converter import ConvertBib2Csv

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bib_path', required=True, type=str,
        help='path to INPUT bibtex file')
    parser.add_argument('-c', '--csv_path', default='refs.csv', type=str,
        help='path to OUTPUT csv file')
    parser.add_argument('-r', '--rename_keys', default=True, type=bool,
        help='rename bibtex keys using author name and year')
    args = parser.parse_args()
    argdict = vars(args)

    bib_path=os.path.abspath(argdict['bib_path'])
    csv_path=os.path.abspath(argdict['csv_path'])
    if not os.path.isfile(bib_path):
        print(f"ERROR: file '{bib_path}' does not exist")
        sys.exit()

    ConvertBib2Csv(bib_path, csv_path, custom_keys=argdict['rename_keys'])


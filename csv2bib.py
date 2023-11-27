from csv2bib import ConvertCsv2Bib

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

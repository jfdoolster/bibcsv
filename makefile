mkfile_dir  := $(strip $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))

.PHONY: all info build clean

all: info build

info:
	$(info mkfile_dir:   $(mkfile_dir))
	@:

build:
	@(python bib2csv.py -b ./examples/web_refs.bib -c refs.csv)
	@(python csv2bib.py -c  refs.csv -b refs.bib -t refs.tex)
	cp ./refs.bib ../acs_paper/refs.bib

clean:
	$(info 'clean' process not specified ($(mkfile_dir)makefile))
	@:

rsync_recdir:= $(strip $(dir $(HOME)/Documents/))
rsync_opts   = -aAXH --delete --inplace

.PHONY: check_lsync lsync

check_lsync:
	@rsync $(rsync_opts) --out-format="%o %n" -v --dry-run $(realpath $(mkfile_dir)) $(rsync_recdir)
	$(info tx:     $(realpath $(mkfile_dir)))
	$(info rx_dir: $(rsync_recdir))
	@( echo && read -ep "Are you sure?!? [Y/n]: " sure && \
		case "$$sure" in [yY]) true;; *) false;; esac )

lsync: check_lsync
	@rsync $(rsync_opts) --stats $(realpath $(mkfile_dir)) $(rsync_recdir)


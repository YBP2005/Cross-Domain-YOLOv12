# Build the IJCV submission (article + electronic supplementary material).
#
#   make            # both documents, full pdflatex/bibtex cycle
#   make article    # main text only
#   make supplement # supplementary material only
#   make clean
#
# The real work is in build.sh, which runs
#   pdflatex -> pdflatex -> bibtex -> pdflatex -> pdflatex
# for each document and falls back to Tectonic if pdflatex is unavailable.

SHELL := /usr/bin/env bash

.PHONY: all article supplement clean

all:
	./build.sh all

article:
	./build.sh article

supplement:
	./build.sh supplement

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.pdf *.xdv *.pass1.out *.pass2.out \
	      *.pass3.out *.pass4.out *.bibtex.out

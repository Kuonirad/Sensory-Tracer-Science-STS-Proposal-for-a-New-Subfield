# Build the STS manuscript and an arXiv-ready source tarball.
#
#   make          -> main.pdf (requires a TeX distribution)
#   make arxiv    -> arxiv-submission.tar.gz (source upload for arXiv)
#   make clean    -> remove build artifacts

MAIN = main

.PHONY: all arxiv clean

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex references.bib
	pdflatex -interaction=nonstopmode $(MAIN).tex
	bibtex $(MAIN)
	pdflatex -interaction=nonstopmode $(MAIN).tex
	pdflatex -interaction=nonstopmode $(MAIN).tex

# arXiv prefers a source tarball; it compiles server-side.
arxiv: $(MAIN).tex references.bib
	tar -czf arxiv-submission.tar.gz $(MAIN).tex references.bib
	@echo "Created arxiv-submission.tar.gz — upload this at https://arxiv.org/submit"

clean:
	rm -f $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).log $(MAIN).out \
	      $(MAIN).pdf arxiv-submission.tar.gz

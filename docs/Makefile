# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXAPI     = sphinx-apidoc
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = _build

SOURCEDIR     = ../sciit
EXCLUDEDIRS    =  $(SOURCEDIR)/man/* $(SOURCEDIR)/hooks/*
APIDIR = ./api

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files"
	@echo "  latex      to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  latexpdf   to make LaTeX files and run them through pdflatex"
	@echo "  man        to make manual pages"
	@echo "  coverage   to run coverage check of the documentation (if enabled)"
	@echo "  clean      refresh the docs"

.PHONY: clean
clean:
	rm -rf $(APIDIR)
	rm -rf $(BUILDDIR)/

.PHONY: html
html:
	rm -rf $(BUILDDIR)/html/
	$(SPHINXAPI) -o $(APIDIR) $(SOURCEDIR) $(EXCLUDEDIRS) --separate
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

.PHONY: latex
latex:
	rm -rf $(BUILDDIR)/latex/
	$(SPHINXAPI) -o $(APIDIR) $(SOURCEDIR) $(EXCLUDEDIRS)
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex
	@echo
	@echo "Build finished; the LaTeX files are in $(BUILDDIR)/latex."
	@echo "Run \`make' in that directory to run these through (pdf)latex" \
	      "(use \`make latexpdf' here to do that automatically)."

.PHONY: latexpdf
latexpdf:
	rm -rf $(BUILDDIR)/latex/
	$(SPHINXAPI) -o $(APIDIR) $(SOURCEDIR) $(EXCLUDEDIRS)
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex
	@echo "Running LaTeX files through pdflatex..."
	$(MAKE) -C $(BUILDDIR)/latex all-pdf
	@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/latex."

.PHONY: man
man:
	rm -rf $(BUILDDIR)/man/
	$(SPHINXAPI) -o $(APIDIR) $(SOURCEDIR) $(EXCLUDEDIRS)
	$(SPHINXBUILD) -b man $(ALLSPHINXOPTS) $(BUILDDIR)/man
	@echo
	@echo "Build finished. The manual pages are in $(BUILDDIR)/man."

.PHONY: coverage
coverage:
	rm -rf $(BUILDDIR)/coverage/
	$(SPHINXAPI) -o $(APIDIR) $(SOURCEDIR) $(EXCLUDEDIRS)
	$(SPHINXBUILD) -b coverage $(ALLSPHINXOPTS) $(BUILDDIR)/coverage
	@echo "Testing of coverage in the sources finished, look at the " \
	      "results in $(BUILDDIR)/coverage/python.txt."

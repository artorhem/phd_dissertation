BUILDDIR = build
MAIN     = main

# Subdirectories that \include writes .aux files into
AUX_SUBDIRS = admin_chapters/committee_page \
              admin_chapters/lay_summary \
              admin_chapters/preface \
              admin_chapters/acknowledgements \
              admin_chapters/dedication \
              body_chapters

LATEXMK_OPTS = \
	-pdf \
	-interaction=nonstopmode \
	-output-directory=$(BUILDDIR) \
	-synctex=1 \
	-f

.PHONY: all clean view diff

all: $(BUILDDIR)/$(MAIN).pdf

$(BUILDDIR)/$(MAIN).pdf: $(MAIN).tex | $(BUILDDIR)
	@mkdir -p $(addprefix $(BUILDDIR)/,$(AUX_SUBDIRS))
	latexmk $(LATEXMK_OPTS) $(MAIN)

$(BUILDDIR):
	mkdir -p $(BUILDDIR)

view: $(BUILDDIR)/$(MAIN).pdf
	open $(BUILDDIR)/$(MAIN).pdf

DIFF_REV ?= HEAD

diff:
	git-latexdiff $(DIFF_REV) -- --main $(MAIN).tex \
		--no-view --latexmk -b -o $(BUILDDIR)/$(MAIN)-diff.pdf
	@echo ""
	@echo "Diff PDF: $(BUILDDIR)/$(MAIN)-diff.pdf"

clean:
	rm -rf $(BUILDDIR)

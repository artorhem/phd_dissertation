BUILDDIR = build
MAIN     = main
TEX      = pdflatex
TEXFLAGS = -interaction=nonstopmode -output-directory=$(BUILDDIR)
BIBTEX   = bibtex

# Subdirectories that \include writes .aux files into
AUX_SUBDIRS = admin_chapters/committee_page \
              admin_chapters/lay_summary \
              admin_chapters/preface \
              admin_chapters/acknowledgements \
              admin_chapters/dedication \
              body_chapters

.PHONY: all clean view

all: $(BUILDDIR)/$(MAIN).pdf

$(BUILDDIR)/$(MAIN).pdf: $(MAIN).tex | $(BUILDDIR)
	@mkdir -p $(addprefix $(BUILDDIR)/,$(AUX_SUBDIRS))
	$(TEX) $(TEXFLAGS) $(MAIN)
	cd $(BUILDDIR) && BIBINPUTS=../:$(BIBINPUTS) BSTINPUTS=../:$(BSTINPUTS) $(BIBTEX) $(MAIN)
	$(TEX) $(TEXFLAGS) $(MAIN)
	$(TEX) $(TEXFLAGS) $(MAIN)

$(BUILDDIR):
	mkdir -p $(BUILDDIR)

view: $(BUILDDIR)/$(MAIN).pdf
	open $(BUILDDIR)/$(MAIN).pdf

clean:
	rm -rf $(BUILDDIR)

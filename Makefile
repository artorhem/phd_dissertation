###############################################################################
# Configuration
###############################################################################

# The paper name without pdf extension
PAPER=diss

# Build directory for the paper
BUILD_DIR=build

# the plots used in the apper
PLOTS=

# the figures that are used in the paper
FIGURES=

# optional build dependencies
DEPS_OPT=

# LATEXMK Options
LATEXMK_OPTS=\
	-latexoption=-interaction=nonstopmode \
	-output-directory=$(BUILD_DIR) \
	-e '$$max_repeat=10' \

###############################################################################
# The paper targets
###############################################################################
PAPER_DRAFT=$(PAPER)-draft
PAPER_DRAFT_MAIN=diss.tex
PAPER_DRAFT_PDF=$(BUILD_DIR)/$(PAPER_DRAFT).pdf

DEFAULT_MODE=$(PAPER_DRAFT_PDF)

###############################################################################
# Latexmk command definition
###############################################################################

# the latexmk command
LATEXMK=latexmk -pdf -logfilewarnings -f $(LATEXMK_OPTS)


###############################################################################
# Dependencies
###############################################################################

DEPS_TEX=$(wildcard content/*.tex)
DEPS_BIB=$(wildcard content/*.bib)
DEPS_FIG=$(wildcard figures/**)
DEPS_PLOT=$(wildcard plots/**)

DEPS=Makefile $(DEPS_TEX) $(DEPS_BIB) $(DEPS_FIG) $(DEPS_PLOT) $(DEPS_OPT)


###############################################################################
# Make Targets (Building)
###############################################################################


default: $(DEFAULT_MODE)

all:  $(PAPER_DRAFT_PDF) $(PAPER_SUBMISSION_PDF)

clean:
	rm -rf $(BUILD_DIR)/* ; rm -rf content/*.aux

distclean: clean

$(PAPER_DRAFT_PDF) : $(DEPS) $(PAPER_DRAFT_MAIN)
	$(LATEXMK) -jobname="$(PAPER_DRAFT)" $(PAPER_DRAFT_MAIN)
	cp $(PAPER_DRAFT_PDF) $(BUILD_DIR)/$(PAPER)-latest.pdf
	@echo ""
	@echo "Built paper:    $(PAPER_DRAFT_PDF)"
	@echo "Updated latest: $(BUILD_DIR)/$(PAPER)-latest.pdf"

draft: $(PAPER_DRAFT_PDF)

.PHONY: all clean rebuild-figures $(PAPER_DRAFT_PDF)


figures/%.pdf: figures/%.svg
	inkscape $< --export-area-drawing --export-pdf=$@

###############################################################################
# Make Targets (Open)
###############################################################################

view-draft: $(PAPER_DRAFT_PDF)
	xdg-open $(PAPER_DRAFT_PDF)

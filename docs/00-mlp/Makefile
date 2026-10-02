LATEXMK ?= latexmk
FLAGS = -pdf -silent -interaction=nonstopmode -halt-on-error -file-line-error
SOURCE = mlp-slides.tex
DATA = $(wildcard data/*.dat) data/readouts.tex

.PHONY: all slides data
all: slides
slides: mlp-slides.pdf
data: data/readouts.tex

data/readouts.tex: build_mlp_checks.py
	. ../../env/bin/activate && python build_mlp_checks.py

mlp-slides.pdf: $(SOURCE) $(DATA)
	$(LATEXMK) $(FLAGS) $(SOURCE)

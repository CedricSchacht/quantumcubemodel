.PHONY: ctan build generate-diagrams doc examples clean

EXAMPLES_TEX := $(wildcard examples/*.tex)
EXAMPLES_PDF := $(patsubst examples/%.tex,examples/out/%.pdf,$(EXAMPLES_TEX))

ctan: build generate-diagrams doc examples
	zip quantumcubemodel.zip \
		LICENSE.md \
		README.md \
		quantumcubemodel.sty \
		examples/*.tex \
		examples/out/*.pdf \
		quantumcubemodel-doc.pdf \
		quantumcubemodel-bib.bib

build:
	./build.py

generate-diagrams:
	./generate-diagrams.py

doc:
	mkdir -p out
	latexmk -lualatex -shell-escape -outdir=out quantumcubemodel-doc.tex
	cp out/quantumcubemodel-doc.pdf ./quantumcubemodel-doc.pdf

examples: $(EXAMPLES_PDF)

examples/out/%.pdf: examples/%.tex
	mkdir -p examples/out
	latexmk -cd -lualatex -shell-escape -outdir=out $<

clean:
	latexmk -C -outdir=out
	latexmk -C -outdir=examples/out
	rm -f quantumcubemodel.zip
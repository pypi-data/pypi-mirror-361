# bibiso4 📒

Convert bibtex journal and series names to [ISO4](https://en.wikipedia.org/wiki/ISO_4). E.g., `Physical Review D` becomes `Phys. Rev. D`.

## Install 💥

     pipx install bibiso4

## Usage 💥

### Convert strings

    iso4 The Journal of Whatever Science
    # J.  Whatever Sci.

### Convert bibtex files

 The original bibtex file isn't modified; instead, you should direct output to a new bibtex file. 

    bibiso4 references.bib > references_iso4.bib

If you wish to see the changes, you can do e.g.,

    diff references.bib references_iso4.bib

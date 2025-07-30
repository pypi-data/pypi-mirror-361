# MAD Backend coordinates manipulation toolkit

## Installation
`pip install mad_services`

## Polyply pipeline utilities

### GRO files
When user submits GRO files which features negative atom coordinates they must be translated to positive values for polyply gen_coor to work.
`mad-boxer -i ./data/coord.gro -o ../wrapped.gro`


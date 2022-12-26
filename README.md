# rdf-star-presidents

[RDF-star][rdf-star] dataset on U.S. presidents, mined from Wikidata.

## Usage

Navigate to the [releases page][releases] to download the data in N-Triples-
star format.

## Build

The build requires Python and Rust.

```sh
pip install -r requirements.txt
python3 query.py
cargo run -q > rdf-star-presidents.nt
```

[releases]: https://github.com/langston-barrett/rdf-star-presidents/releases
[rdf-star]: https://www.w3.org/2021/12/rdf-star.html
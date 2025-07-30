# AxiusMEM

A W3C-compliant temporal knowledge graph library for AI agents.

[![PyPI version](https://badge.fury.io/py/axiusmem.svg)](https://badge.fury.io/py/axiusmem)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docs](https://readthedocs.org/projects/axiusmem/badge/?version=latest)](https://axiusmem.readthedocs.io/en/latest/)

## Features
- **Bi-temporal data model** (valid & transaction time)
- **Incremental and batch data ingestion**
- **Advanced querying** (SPARQL, temporal, semantic, full-text)
- **GraphDB integration** (connection pooling, repository management)
- **AI agent utilities** (context retrieval, memory management)
- **ORM/Mapper** (Python objects <-> RDF)
- **Extensive tests and Sphinx documentation**

## Installation

### Using pip
```bash
pip install axiusmem
```

### Using conda
```bash
conda install -c conda-forge axiusmem
```

## Quick Start
```python
from axiusmem import AxiusMEM

mem = AxiusMEM()
mem.load_ontology('src/axiusmem/axiusmem_ontology.ttl')
mem.connect_graphdb()
# Add triples, query, manage agent memory, etc.
```

## Documentation
- [Sphinx Docs (HTML)](https://axiusmem.readthedocs.io/en/latest/)
- [Product Requirements (PRD)](docs/PRD_%20AxiusMEM.md)
- [Ontology (Turtle)](src/axiusmem/axiusmem_ontology.ttl)
- [Developer Guide](docs/docs_dev_guide.md)

## Contributing
See [CONTRIBUTORS.md](CONTRIBUTORS.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).

## License
See [LICENSE](LICENSE).

## Community & Support
- Feedback, issues, and feature requests: [GitHub Issues](https://github.com/your-org/axiusmem/issues)
- Roadmap and discussions: [GitHub Discussions](https://github.com/your-org/axiusmem/discussions) 

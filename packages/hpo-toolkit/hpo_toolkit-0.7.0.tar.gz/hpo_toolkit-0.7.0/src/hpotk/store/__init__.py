"""
The `hpotk.store` package provides :class:`OntologyStore` - a class for local caching of ontology data.

The ontology store should be configured using :func:`hpotk.configure_ontology_store` function:

>>> import hpotk
>>> store = hpotk.configure_ontology_store()

The store can then be used to fetch an ontology with a given release, e.g. `v2023-10-09`:

>>> hpo = store.load_minimal_hpo(release='v2023-10-09')
>>> hpo.version
'2023-10-09'

or fetch the *latest* release by omitting the `release` argument:

>>> latest_hpo = store.load_minimal_hpo()  # doctest: +SKIP
>>> latest_hpo.version  # doctest: +SKIP
'2024-04-26'

.. note::

  The release `2024-04-26` is the latest release as of June 2024 when this documentation was written.
"""

from ._api import (
    OntologyType,
    OntologyStore,
    RemoteOntologyService,
    OntologyReleaseService,
)
from ._github import GitHubRemoteOntologyService, GitHubOntologyReleaseService
from ._config import configure_ontology_store

__all__ = [
    "configure_ontology_store",
    "OntologyType",
    "OntologyStore",
    "RemoteOntologyService",
    "OntologyReleaseService",
    "GitHubRemoteOntologyService",
    "GitHubOntologyReleaseService",
]

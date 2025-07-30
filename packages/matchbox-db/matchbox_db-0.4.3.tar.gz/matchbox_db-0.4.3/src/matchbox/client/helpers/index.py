"""Functions to index data sources to the Matchbox server."""

from matchbox.client import _handler
from matchbox.common.sources import SourceConfig


def index(
    source_config: SourceConfig,
    batch_size: int | None = None,
) -> None:
    """Indexes data in Matchbox.

    Args:
        source_config: A SourceConfig with credentials set
        batch_size: the size of each batch when fetching data from the warehouse,
            which helps reduce the load on the database. Default is None.
    """
    if not source_config.location.credentials:
        raise ValueError("Source credentials are not set")

    data_hashes = source_config.hash_data(batch_size=batch_size)
    _handler.index(source_config=source_config, data_hashes=data_hashes)

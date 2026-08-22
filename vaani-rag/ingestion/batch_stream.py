from typing import Iterator, List, TypeVar

T = TypeVar("T")


def stream_batches(
    items: Iterator[T],
    batch_size: int,
) -> Iterator[List[T]]:
    """
    Converts an item stream into bounded-size batches.

    Example:

        items = 1, 2, 3, 4, 5
        batch_size = 2

        yields:
            [1, 2]
            [3, 4]
            [5]
    """

    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0")

    batch: List[T] = []

    for item in items:
        batch.append(item)

        if len(batch) >= batch_size:
            yield batch
            batch = []

    if batch:
        yield batch
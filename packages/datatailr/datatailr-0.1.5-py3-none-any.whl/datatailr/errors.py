class DatatailrError(Exception):
    """Base class for all DataTailr exceptions."""

    pass


class BatchJobError(DatatailrError):
    """Exception raised for errors related to batch jobs."""

    pass

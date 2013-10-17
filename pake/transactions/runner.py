#!/sur/bin/env python3

"""This file contains PAKE transactions runner.
"""


class Runner():
    """This object implements logic needed to run PAKE
    requests - request is a middle-form of a single line of
    transaction file.
    """
    def __init__(self, reqs):
        self._reqs = reqs

    def finalize(self):
        """Finalize data in the transaction e.g. fill missing data.
        """
        return self

    def run(self):
        """Call this method to run the transaction.
        """
        pass

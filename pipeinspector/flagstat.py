class Flagstat(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self._parse()

    def _parse(self):
        with open(self.file_path) as flagstat:
            self._values = [int(x.split(' ')[0]) for x in flagstat]

    @property
    def read1(self):
        """Number of read1 reads. Primary only."""
        return self._values[6]

    @property
    def read2(self):
        """Number of read2 reads. Primary only."""
        return self._values[7]


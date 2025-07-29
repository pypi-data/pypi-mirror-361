class ScanRef:
    """Identify a scan reference from blissdata

    Argument:
        key: blissdata scan identifier
    """

    def __init__(self, key: str):
        self.key = key

    def __repr__(self):
        return f"<ScanRef key={self.key}>"


class Scan:
    def __init__(self, scan):
        """Small wrapper around a loaded bliss scan"""
        self._scan = scan

    def __str__(self):
        s = self._scan
        return f"""Scan(number={s.number}, name={s.name}, path={s.path}, state={s.state})"""

    @property
    def detail(self):
        """Some details about the scan"""
        s = self._scan
        info = self._scan.info
        print(
            f"""Scan number={s.number} key={s.key}

    name:\t{s.name}
    title:\t{info.get('title')}
    filename:\t{s.path}
    save:\t{info['save']}

    start_time:\t{info['start_time']}
    end_time:\t{info['end_time']}
    end_reason:\t{info['end_reason']}

    npoints:\t{info.get('npoints')}
"""
        )

    @property
    def key(self):
        """The blissdata key"""
        return self._scan.key

    @property
    def scan(self):
        """This blissdata scan object"""
        return self._scan

    @property
    def info(self):
        """The scans scan_info"""
        return self._scan.info

    def stream(self, key: str | None = None):
        """A stream of data"""
        if key is None:
            print(
                f"Return a stream of data, available streams: {list(self._scan.streams.keys())}"
            )
            return

        return self._scan.streams[key]

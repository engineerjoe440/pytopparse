################################################################################
"""
PyTopParse - Parse results of `/usr/bin/top -b -n 1`.
"""
################################################################################

import re
from typing import Union, Generator
from pathlib import Path

#pylint: disable=no-name-in-module
from pydantic import BaseModel

__version__ = "0.0.1"

RE_TOP_PROCESS = re.compile(
    r' *(?P<pid>\d{1,7}) +(?P<ppid>\d{1,7}) +(?P<user>\w{1,30})'
    r' +(?P<stat>.{1,3}) +(?P<vsz>\w{1,7}) +(?P<percent_vsz>\d{1,7})\%'
    r' +(?P<percent_cpu>\d{1,2})\%'
    r' +(?P<command>[a-zA-Z0-9.\/_\\\ \:\-\=\;\[\]\{\}]{4,})'
)

#pylint: disable=too-many-instance-attributes
class TopProcess(BaseModel):
    """Single Process Record within Top."""
    pid: int
    ppid: int
    user: str
    stat: str
    vsz: int
    percent_vsz: int
    percent_cpu: int
    command: str

    @staticmethod
    def from_row(row_contents: str) -> Union["TopProcess", None]:
        """Parse the Row into Respective Data."""
        results = RE_TOP_PROCESS.search(row_contents)
        if results:
            group_data = results.groupdict()
            if str(group_data['vsz']).endswith('m'):
                used = int(str(group_data['vsz']).split('m', maxsplit=1)[0])
                group_data['vsz'] = used * 10e6
            return TopProcess(**group_data)
        return None

class TopProcessList:
    """Processes from Top."""
    file_path: str
    processes: dict[TopProcess]

    def __init__(self, file_path: str) -> None:
        """Read and Parse the File to Interpret all Process Records."""
        self.file_path = file_path
        self.processes = {}
        with open(file_path, 'r', encoding='utf-8') as src:
            contents = src.readlines()[4:] # Skip first 4 Heading Lines
        for row in contents:
            if (proc := TopProcess.from_row(row)):
                self.processes[proc.pid] = proc

    @property
    def name(self):
        """Root Name of the File Path."""
        return Path(self.file_path).name

    def walk(self, reverse=False) -> Generator[TopProcess, None, None]:
        """Walk Over Processes."""
        for proc in sorted(
            self.processes.values(),
            key=lambda v: v.vsz,
            reverse=reverse
        ):
            yield proc

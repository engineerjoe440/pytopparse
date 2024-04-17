################################################################################
"""
PyTopParse - Parse results of `/usr/bin/top -b -n 1`.
"""
################################################################################

from typing import Union
import re

#pylint: disable=no-name-in-module
from pydantic import BaseModel

RE_TOP_PROCESS = re.compile(
    r' *(?P<pid>\d{1,7}) +(?P<ppid>\d{1,7}) +(?P<user>\w{1,30})'
    r' +(?P<stat>.{1,3}) +(?P<vsz>\w{1,7}) +(?P<percent_vsz>\d{1,7})\%'
    r' +(?P<percent_cpu>\d{1,2})\% +(?P<command>\w+)'
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
    def from_row(row_contents: str) -> Union["TopProcess" | None]:
        """Parse the Row into Respective Data."""
        results = RE_TOP_PROCESS.search(row_contents)
        if results:
            group_data = results.groupdict()
            if str(group_data['vsz']).endswith('m'):
                used = int(str(group_data['vsz']).split('m', maxsplit=1)[0])
                group_data['vsz'] = used * 10e6
            return TopProcess(**group_data)
        return None

def parse_processes_from_file(file_name: str) -> dict[int, TopProcess]:
    """Read and Parse the File to Interpret all Process Records."""
    records = {}
    with open(file_name, 'r', encoding='utf-8') as src:
        contents = src.readlines()[4:] # Skip first 4 Heading Lines
    for row in contents:
        proc = TopProcess.from_row(row)
        records[proc.pid] = proc

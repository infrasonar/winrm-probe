from libprobe.probe import Probe
from lib.check.software import check_software
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = {
        'software': check_software
    }

    probe = Probe("winrm", version, checks)

    probe.start()

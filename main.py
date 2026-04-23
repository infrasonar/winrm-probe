from libprobe.probe import Probe
from lib.check.scheduled_tasks import CheckScheduledTasks
from lib.check.software import CheckSoftware
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = (
        CheckScheduledTasks,
        CheckSoftware,
    )
    probe = Probe("winrm", version, checks)

    probe.start()

from libprobe.probe import Probe
from lib.check.software import check_software
from lib.check.scheduled_tasks import check_scheduled_tasks
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = {
        'scheduledTasks': check_scheduled_tasks,
        'software': check_software,
    }

    probe = Probe("winrm", version, checks)

    probe.start()

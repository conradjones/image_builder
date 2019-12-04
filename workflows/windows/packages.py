from util import util
import uuid


def install_packages(*, remote, packages):
        print('buildImage:waiting for winrs connection')
        if not remote.remoteWaitDeviceIsAwake():
            print('buildImage:failed to wait for device')
            return False

        print('buildImage:installing Winstall')
        remote.remoteInstallWinstall()

        print('buildImage:installing packages')
        for package in packages:
            result = remote.remoteInstallPackage(package)
            if "Reboot" not in result:
                continue

            print('buildImage:reboot required, rebooting....')
            remote.remoteReboot()

        input("buildImage:Press Enter to continue...")

        return True


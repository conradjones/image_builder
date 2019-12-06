

def install_packages(*, remote, packages):
        print('buildImage:waiting for winrs connection')
        if not remote.remoteWaitDeviceIsAwake():
            print('buildImage:failed to wait for device')
            return False

        print('buildImage:installing Winstall')
        remote.remoteInstallWinstall()

        print('buildImage:installing packages')
        for package_name in packages.keys():
            result = remote.remoteInstallPackage(package_name, packages[package_name])
            if "Reboot" not in result:
                continue

            print('buildImage:reboot required, rebooting....')
            remote.remoteReboot()

        return True


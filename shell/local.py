import subprocess
import shutil
import os
import fnmatch


class LocalShell:
    def execute_process(self, args, ignore_exit=False):
        process = subprocess.Popen(args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode is not 0 and not ignore_exit:
            raise Exception(
                "%s returned exit code :%s\n%s\n%s" % (" ".join(args), process.returncode, stderr.decode("utf-8"),
                                                       stdout.decode("utf-8")))
        return process.returncode, stdout.decode("utf-8"), stderr.decode("utf-8")

    def put(self, source, dest):
        shutil.copy(source, dest)

    def mkdir(self, folder):
        if not os.path.isdir(folder):
            os.mkdir(folder)

    def rmdir(self, folder, recurse=False):
        if recurse:
            shutil.rmtree(folder)
        else:
            os.rmdir(folder)

    def _file_match(self, filename, excludes):
        for exclude in excludes:
            if fnmatch.fnmatch(filename, exclude):
                return True
        return False

    def rmdir_contents(self, folder, excludes=[]):
        for filename in os.listdir(folder):
            if self._file_match(filename, excludes):
                continue

            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

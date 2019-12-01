import fabric


class SSH:

    def __init__(self, conn_string):
        self._conn = fabric.Connection(conn_string)
        if self._conn is None:
            raise Exception('Failed to connect to :%s' % conn_string)

    def execute_process(self, args, ignore_exit=False):
        command = " ".join(args)
        result = self._conn.run(command, hide=False)
        if result.exited is not 0 and not ignore_exit:
            raise Exception(
                "%s returned exit code :%s\n%s" % (" ".join(args), result.exited, result.stderr))
        return result.exited, result.stdout, result.stderr

    def put(self, source, dest):
        self._conn.put(source, dest)

    def mkdir(self, folder):
        self.execute_process(["mkdir", folder])

    def rmdir(self, folder, recurse=False):
        if recurse:
            self.execute_process(['rmdir', '-rf', folder])
        else:
            self.execute_process(['rmdir', folder])

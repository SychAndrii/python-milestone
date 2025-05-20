import os
import pwd
import grp
import time
import fcntl
import psutil
import resource
import signal
import sys
import atexit

class Daemon(object):
    """
    Usage: create a Daemon() subclass
    - override the run() method
    @param object
    @param username - unpriviledged username for daemon
    @param groupname - unpriviledged group name for daemon
    @param pidFile - the runtime PID file with path
    """
    def __init__(self, username, groupname, pidFile, STDIN='/dev/null', STDOUT='/dev/null', STDERR='/dev/null'):
        self.ver = 0.4
        self.pauseRunLoop = 0
        self.pauseReExec = 1
        self.pauseDeath = 3
        self.signalReload = False
        self._daemonRunning = True
        self.processName = os.path.basename(sys.argv[0])
        self.STDIN = STDIN
        self.STDOUT = STDOUT
        self.STDERR = STDERR
        self.pidFile = pidFile
        self.newUID, self.newGID = self.__getUserAndGroupIDs(username, groupname)

    def _lock_pid_file(self):
        self.pidfile_fd = open(self.pidFile, 'w+')

        try:
            fcntl.flock(self.pidfile_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("Another instance of the daemon is already running.")
        
        self.pidfile_fd.seek(0)
        self.pidfile_fd.truncate()
        self.pidfile_fd.write(str(os.getpid()))
        self.pidfile_fd.flush()

    def _release_pid_file(self):
        if self.pidfile_fd:
            try:
                fcntl.flock(self.pidfile_fd.fileno(), fcntl.LOCK_UN)
                self.pidfile_fd.close()
                os.remove(self.pidFile)
            except Exception as e:
                print(f"Error releasing PID file: {e}")

    def _handlerSIGTERM(self, signum, frame):
        self._daemonRunning = False
        if hasattr(self, "sock"):
            try:
                self.sock.close()
            except Exception:
                pass

    def _handlerReExec(self, signum, frame):
        print("Received SIGHUP — ignoring, nothing to reload.")

    def __getUserAndGroupIDs(self, username, groupname):
        uid = pwd.getpwnam(username).pw_uid
        gid = grp.getgrnam(groupname).gr_gid
        return uid, gid 

    def _daemonize(self):
        """
        double-fork et al
        """
        if os.path.exists(self.pidFile):
            raise RuntimeError('Already running')

        try:
            pid = os.fork()
            if pid > 0:
                raise SystemExit(0)  # Parent death
        except OSError as e:
            raise RuntimeError('fork #1 failed.')

        os.chdir("/tmp")
        os.setsid()
        os.umask(0)

        if os.getuid() == 0:
            os.setgid(self.newGID)
            os.setuid(self.newUID)
        else:
            print("⚠️ Not running as root — skipping privilege drop to nobody/nogroup.")

        # Second fork (relinquish session leadership)
        try:
            pid = os.fork()
            if pid > 0:
                raise SystemExit(0)
        except OSError as e:
            raise RuntimeError('fork #2 failed.')
        
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        self._lock_pid_file()

        # Replace file descriptors for stdin, stdout, and stderr
        sys.stdout.flush()
        sys.stdin.flush()

        with open(self.STDIN, 'rb', 0) as file:
            os.dup2(file.fileno(), sys.stdin.fileno())
        with open(self.STDOUT, 'ab', 0) as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
        with open(self.STDERR, 'ab', 0) as f:
            os.dup2(f.fileno(), sys.stderr.fileno())

        # Arrange to have the PID file removed on exit/signal
        atexit.register(self._release_pid_file)

    def _getProces(self):
        procs = []
        for p in psutil.process_iter():
            if self.processName in [part.split('/')[-1] for part in p.cmdline()]:
                # Skip the current process
                if p.pid != os.getpid():
                    procs.append(p)
        return procs

    def start(self):
        """
        Start daemon.
        """
        # signal handlers
        signal.signal(signal.SIGINT, self._handlerSIGTERM)
        signal.signal(signal.SIGTERM, self._handlerSIGTERM)
        signal.signal(signal.SIGHUP, self._handlerReExec)

        # Check if the daemon is already running.
        procs = self._getProces()
        if procs:
            pids = ",".join([str(p.pid) for p in procs])
            errorMessage = f"Find a previous daemon processes with PIDs {pids}. Is not already the daemon running?"
            print(errorMessage)
            sys.exit(1)
        else:
            message = f"Start the daemon version {self.ver}"
            print(message)
            self._daemonize()
            self._infiniteLoop()

    def _infiniteLoop(self):
        try:
            if self.pauseRunLoop:
                time.sleep(self.pauseRunLoop)
            while self._daemonRunning:
                self.run()
                time.sleep(self.pauseRunLoop)
        except Exception as e:
            sys.stderr.write(f"Run method failed: {e}")
            sys.exit(1)

    def run(self):
        pass

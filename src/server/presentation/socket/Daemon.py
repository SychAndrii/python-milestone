import os
import sys
import pwd
import grp
import atexit
import fcntl
import signal
import resource
import logzero
from logzero import logger


class Daemon(object):
    def __init__(self, username, groupname, pidFile, STDIN='/dev/null', STDOUT='/dev/null', STDERR='/dev/null'):
        self._daemonRunning = True
        self.processName = os.path.basename(sys.argv[0])
        self.STDIN = STDIN
        self.STDOUT = STDOUT
        self.STDERR = STDERR
        self.pidFile = pidFile

        logzero.logfile("/tmp/socket-daemon-logfile.log", maxBytes=1e6, backupCount=3, disableStderrLogger=True)
        logger.info("Initializing daemon process...")
        self.newUID, self.newGID = self.__getUserAndGroupIDs(username, groupname)

    def _lock_pid_file(self):
        logger.debug(f"Attempting to lock PID file at: {self.pidFile}")
        self.pidfile_fd = open(self.pidFile, 'w+')

        try:
            fcntl.flock(self.pidfile_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            logger.info("Successfully locked PID file.")
        except BlockingIOError:
            logger.error("Another instance of the daemon is already running.")
            raise RuntimeError("Another instance of the daemon is already running.")
        
        self.pidfile_fd.seek(0)
        self.pidfile_fd.truncate()
        self.pidfile_fd.write(str(os.getpid()))
        self.pidfile_fd.flush()
        logger.debug(f"Wrote PID {os.getpid()} to file.")

    def _release_pid_file(self):
        if self.pidfile_fd:
            try:
                fcntl.flock(self.pidfile_fd.fileno(), fcntl.LOCK_UN)
                self.pidfile_fd.close()
                os.remove(self.pidFile)
                logger.info("Released PID file and removed it.")
            except Exception as e:
                logger.error(f"Error releasing PID file: {e}")

    def _handlerSIGTERM(self, signum, frame):
        logger.info("Received SIGTERM or SIGINT. Shutting down daemon.")
        self._daemonRunning = False
        if hasattr(self, "sock"):
            try:
                self.sock.close()
                logger.debug("Closed socket cleanly.")
            except Exception:
                pass

    def _handlerReExec(self, signum, frame):
        logger.info("Received SIGHUP — ignoring, nothing to reload.")

    def __getUserAndGroupIDs(self, username, groupname):
        logger.debug(f"Fetching UID and GID for {username}:{groupname}")
        uid = pwd.getpwnam(username).pw_uid
        gid = grp.getgrnam(groupname).gr_gid
        return uid, gid

    def _daemonize(self):
        logger.info("Starting daemonization sequence.")

        if os.path.exists(self.pidFile):
            logger.error("PID file already exists. Daemon already running?")
            raise RuntimeError('Already running')

        try:
            pid = os.fork()
            if pid > 0:
                logger.debug(f"First fork succeeded. Parent exiting (PID: {pid}).")
                raise SystemExit(0)
        except OSError as e:
            logger.error(f"First fork failed: {e}")
            raise RuntimeError('fork #1 failed.')

        os.chdir("/")
        os.setsid()
        os.umask(0)
        logger.debug("Daemon detached from terminal, new session created.")

        if os.getuid() == 0:
            try:
                os.setgid(self.newGID)
                os.setuid(self.newUID)
                logger.info(f"Dropped privileges to UID:{self.newUID} GID:{self.newGID}")
            except Exception as e:
                logger.warning(f"Privilege drop failed: {e}")
        else:
            logger.info("⚠️ Not running as root — skipping privilege drop.")

        try:
            pid = os.fork()
            if pid > 0:
                logger.debug(f"Second fork succeeded. Parent exiting (PID: {pid}).")
                raise SystemExit(0)
        except OSError as e:
            logger.error(f"Second fork failed: {e}")
            raise RuntimeError('fork #2 failed.')

        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        logger.debug("Core dump disabled.")

        self._lock_pid_file()

        sys.stdout.flush()
        sys.stdin.flush()

        with open(self.STDIN, 'rb', 0) as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        with open(self.STDOUT, 'ab', 0) as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
        with open(self.STDERR, 'ab', 0) as f:
            os.dup2(f.fileno(), sys.stderr.fileno())

        logger.debug("File descriptors redirected to null.")

        atexit.register(self._release_pid_file)
        logger.info("Daemonization complete. Running main loop...")

    def start(self):
        signal.signal(signal.SIGINT, self._handlerSIGTERM)
        signal.signal(signal.SIGTERM, self._handlerSIGTERM)
        signal.signal(signal.SIGHUP, self._handlerReExec)

        logger.info("Starting daemon service...")
        self._daemonize()
        self._infiniteLoop()

    def _infiniteLoop(self):
        try:
            while self._daemonRunning:
                self.run()
        except Exception as e:
            logger.error(f"Run method failed: {e}")
            sys.exit(1)

    def run(self):
        pass

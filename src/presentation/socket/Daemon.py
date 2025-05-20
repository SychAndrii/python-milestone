import os
import time
import psutil
import signal

class Daemon(object):
    """
    Usage: create a Daemon() subclass
    - override the run() method
    - start, stop, restart
    @param object
    @param newUID - unpriviledged UID for daemon
    @param newGID - unpriviledged GID for daemon
    @param pidFile - the runtime PID file with path
    """
    def __init__(self, newUID, newGID, pidFile, STDIN='/dev/null', STDOUT='/dev/null', STDERR='/dev/null'):
        self.ver = 0.4  # version
        self.pauseRunLoop = 0  # pause between run() calls
        self.pauseReExec = 1  # pause between death and exec
        self.pauseDeath = 3  # pause before SIGTERM
        self.signalReload = False
        self._daemonRunning = True
        self.processName = os.path.basename(sys.argv[0])
        self.STDIN = STDIN
        self.STDOUT = STDOUT
        self.STDERR = STDERR
        self.pidFile = pidFile

    def _handlerSIGTERM(self, signum, frame):
        self._daemonRunning = False

    def _handlerReExec(self, signum, frame):
        self.signalReload = True

    def _daemonize(self):
        """
        double-fork et al
        """
        if os.path.exists(pidFile):
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
        os.setuid(newUID)
        os.setgid(newGID)

        # Second fork (relinquish session leadership)
        try:
            pid = os.fork()
            if pid > 0:
                raise SystemExit(0)
        except OSError as e:
            raise RuntimeError('fork #2 failed.')

        # Replace file descriptors for stdin, stdout, and stderr
        sys.stdout.flush()
        sys.stdin.flush()

        with open(self.STDIN, 'rb', 0) as file:
            os.dup2(file.fileno(), sys.stdin.fileno())
        with open(self.STDOUT, 'ab', 0) as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
        with open(self.STDERR, 'ab', 0) as f:
            os.dup2(f.fileno(), sys.stderr.fileno())

        # Write the PID file
        with open(self.pidFile, 'w') as writePID:
            print(os.getpid(), file=writePID)

        # Arrange to have the PID file removed on exit/signal
        atexit.register(lambda: os.remove(self.pidFile))

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
            # Daemonize the main process
            self._daemonize()
            # Start a infinitive loop that periodically runs run() method
            self._infiniteLoop()

    def version(self):
        message = f"The daemon version {self.ver}"
        print(message)

    def status(self):
        """
        Get status of the daemon.
        """
        procs = self._getProces()
        if procs:
            pids = ",".join([str(p.pid) for p in procs])
            message = f"The daemon is running with PID {pids}."
            print(message)
        else:
            message = "The daemon is not running!"
            print(message)

    def reload(self):
        """
        Reload the daemon.
        """
        procs = self._getProces()
        if procs:
            for p in procs:
                os.kill(p.pid, signal.SIGHUP)
                message = f"Send SIGHUP signal into the daemon process with PID {p.pid}."
                print(message)
        else:
            errorMessage = "The daemon is not running!"
            print(errorMessage)

    def stop(self):
        """
        Stop the daemon.
        """
        procs = self._getProces()

        def on_terminate(process):
            message = f"The daemon process with PID {process.pid} has ended correctly."
            print(message)

        if procs:
            for p in procs:
                p.terminate()
            gone, alive = psutil.wait_procs(procs, timeout=self.pauseDeath, callback=on_terminate)
            for p in alive:
                message = f"The daemon process with PID {p.pid} was killed with SIGTERM!"
                print(message)
                p.kill()
        else:
            errorMessage = "Cannot find some daemon process, I will do nothing."
            print(errorMessage)

    def restart(self):
        """
        Restart the daemon.
        """
        self.stop()
        if self.pauseReExec:
            time.sleep(self.pauseReExec)
        self.start()

    def _infiniteLoop(self):
        try:
            if self.pauseRunLoop:
                time.sleep(self.pauseRunLoop)
            while self._daemonRunning:
                self.run()
                time.sleep(self.pauseRunLoop)
        except Exception as e:
            errorMessage = f"Run method failed: {e}"
            sys.stderr.write(errorMessage)
            sys.exit(1)

    # this method you have to override
    def run(self):
        pass
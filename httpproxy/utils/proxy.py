import os
import time
import signal
import logging
from threading import Thread
from http.server import HTTPServer
from socketserver import BaseServer
from multiprocessing import cpu_count
from easy_daemon.daemon import Daemon
from httpproxy.utils.handler import MyTestHandler
from pooledProcessMixin import PooledProcessMixIn
from httpproxy.config import translate as _, logger, cmd_args

default = signal.getsignal(signal.SIGTERM)


class ExecDaemon(Daemon):
    def run(self):
        def sig_handler(signum, frame):
            """

            Signal SIGTERM handler
            :param signum: signal
            :type signum: int
            :param frame: frame
            :type frame: FrameType

            """
            if not (proxy.kill and proxy.closed):
                signal.signal(signal.SIGTERM, default)
                proxy.shutdown()
            time.sleep(1)
            if proxy.kill:
                Thread(target=BaseServer.shutdown, args=(proxy,)).start()

        signal.signal(signal.SIGTERM, sig_handler)
        HTTPProxy.allow_reuse_address = True
        proxy = HTTPProxy(processes=int(cmd_args.processes), threads=int(cmd_args.threads), log=logger)
        try:
            proxy.serve_forever()
        finally:
            proxy.shutdown()
        logger.info(_('terminal terminated'))
        signal.signal(signal.SIGTERM, default)
        os.kill(os.getpid(), signal.SIGTERM)
        self.logger.info('daemon terminated')


class HTTPProxy(PooledProcessMixIn, HTTPServer):
    """

    Simple http-proxy

    """
    def __init__(self, processes=max(2, cpu_count()), threads=64, daemon=False, kill=True, debug=False, log=None):
        """
        Constructor
        :param processes: processes pool length
        :type processes: int
        :param threads: threads pool length for process
        :type threads: int
        :param daemon: True if daemon threads
        :type daemon: bool
        :param kill: True if kill main process when shutdown
        :type kill: bool
        :param debug: True if debug mode
        :type debug: bool
        :param log: logger
        :type log: logging.Logger
        """
        HTTPServer.__init__(self, (cmd_args.host, cmd_args.port), MyTestHandler)
        self._process_n = processes
        self._thread_n = threads
        self._daemon = daemon
        self._kill = kill
        self._debug = debug
        self._logger = log
        self._init_pool()
        logger.info('listening on %s:%s' % (cmd_args.host, cmd_args.port))

    @property
    def kill(self):
        """
        Kill property
        :return: kill property
        """
        return self._kill

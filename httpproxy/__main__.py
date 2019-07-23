#!/usr/bin/python3

import sys

########################################################################################################################
#                                                 Main function                                                        #
########################################################################################################################


def main():
    sys.path.append('../')
    sys.path.append('/app')
    from httpproxy.config import logger, cmd_args, parser, home
    from httpproxy.utils.proxy import ExecDaemon
    cmd_args.pid = cmd_args.pid.replace('~', home)
    daemon = ExecDaemon(cmd_args.pid, logger)
    if cmd_args.debug:
        daemon.run()
    elif 'start' == cmd_args.action:
        daemon.start()
    elif 'stop' == cmd_args.action:
        daemon.stop()
    elif 'restart' == cmd_args.action:
        daemon.restart()
    else:
        parser.print_help()
    sys.exit(0)

########################################################################################################################
#                                                  Entry point                                                         #
########################################################################################################################


if __name__ == '__main__':
    main()

import os
import logging
import argparse
import builtins
from multiprocessing import cpu_count
from httpproxy.utils.helpers import set_config, activate_virtual_environment, set_localization, get_logger

########################################################################################################################
#                                                 Configuration                                                        #
########################################################################################################################

parser = argparse.ArgumentParser(prog='http_proxy')
home = os.getenv("HOME")
parser.add_argument('action', help='start | stop | restart', default='start')
parser.add_argument('-c', '--config', help='config file', default='~/.http_proxy/config.json')
parser.add_argument('-s', '--host', help='binding host', default='127.0.0.1')
parser.add_argument('-p', '--port', help='binding port', default=8888)
parser.add_argument('-r', '--processes', help='processes count', default=cpu_count())
parser.add_argument('-t', '--threads', help='threads count', default=64)
parser.add_argument('-i', '--pid', help='pid file', default='~/.http_proxy/http_proxy.pid')
parser.add_argument('-l', '--log_level', help='logging level: CRITICAL, ERROR, WARNING, INFO, DEBUG or NOTSET',
                    default='INFO')
parser.add_argument('-d', '--debug', help='debugging', action="store_true")

cmd_args = parser.parse_args()
config_args = set_config(cmd_args.config.replace('~', home))

########################################################################################################################
#                                                  Localization                                                        #
########################################################################################################################

set_localization(**config_args)
translate = _ = builtins.__dict__.get('_', lambda x: x)


########################################################################################################################
#                                                    Logging                                                           #
########################################################################################################################

try:
    log_level, level_error = logging._nameToLevel[cmd_args.log_level], False
except KeyError:
    level_error = True
    log_level = logging._nameToLevel['INFO']
logger = get_logger('http_proxy', config_args.get("log_format", "%(levelname)-10s|%(asctime)s|"
                                                               "%(process)d|%(thread)d| %(name)s --- "
                                                               "%(message)s (%(filename)s:%(lineno)d)"),
                    config_args.get('log_file', '~/.http_proxy/http_proxy.log').replace('~', home), log_level)
if level_error:
    logger.warning('%s \'%s\', %s \'INFO\' %s' % (_('incorrect logging level'), cmd_args.log_level, _('used'),
                                                  _('by default')))
    cmd_args.log_level = 'INFO'


########################################################################################################################
#                                               Virtual environment                                                    #
########################################################################################################################

if config_args.get('environment') != "":
    activate_virtual_environment(**config_args)
    logger.info('%s \'%s\'' % (_('activated virtual environment'), config_args.get('environment')))

import os
import sys
import site
import json
import pycurl
import gettext
import logging
import builtins
import traceback
from io import BytesIO, StringIO
from urllib.parse import urlencode

_ = builtins.__dict__.get('_', lambda x: x)

########################################################################################################################
#                                                    Some helpers                                                      #
########################################################################################################################


def set_config(config_name):
    """

    Config parse

    :param config_name: config file name
    :type config_name: str
    :return: parsed config
    :rtype: dict

    """
    import json
    try:
        return json.load(open(config_name, 'r'))
    except FileNotFoundError:
        print('%s %s' % (config_name, 'not found'))
        exit(1)
    except json.JSONDecodeError as error:
        print('%s %s: %s' % (config_name, 'format error', str(error)))
        exit(1)


def activate_virtual_environment(**kwargs):
    """

    Activate virtual environment

    :param kwargs: key parameters

    Allowed following parameters:

    - environment (virtual environment directory, default: 'venv')
    - packages (path to packages in environment, default: 'lib/python{VERSION}/site-packages')

    """
    env = kwargs.get('environment', 'venv').replace('~', os.getenv('HOME'))
    env_path = env if env[0:1] == "/" else os.getcwd() + "/" + env
    env_activation = env_path + '/' + 'bin/activate_this.py'
    site.addsitedir(env_path + '/' + kwargs.get('packages', 'lib/python%s.%s/site-packages' % (
        sys.version_info.major, sys.version_info.minor)).replace(
        '{VERSION}', '%s.%s' % (sys.version_info.major, sys.version_info.minor)))
    sys.path.append('/'.join(env_path.split('/')[:-1]))
    try:
        exec(open(env_activation).read())
    except Exception as e:
        print('%s: (%s)' % ('virtual environment activation error', str(e)))
        exit(1)


def set_localization(**kwargs):
    """

    Install localization

    :param kwargs: key parameters

    Allowed following parameters:

    - locale_domain (default: sys.argv[0])
    - locale path (default: '/usr/share/locale')
    - language (default: 'en')
    - quiet (default: False)

    """
    locale_domain = kwargs.get('locale_domain', sys.argv[0])
    locale_dir = kwargs.get('locale_dir', '/usr/share/locale').replace('~', os.getenv('HOME'))
    language = kwargs.get('language', 'en')
    gettext.install(locale_domain, locale_dir)
    try:
        gettext.translation(locale_domain, localedir=locale_dir, languages=[language]).install()
    except FileNotFoundError:
        if not kwargs.get('quiet', False):
            print('%s %s \'%s\' %s, %s' % ('translation', 'for', language, 'not found', 'use default'))


def get_logger(logger_name, logging_format, file_name, level=logging.INFO):
    """

    Get logger with path 'file name'. If permission error, create log in /tmp

    :param logger_name: logger name
    :type logger_name: str
    :param logging_format: log format
    :type logging_format: str
    :param file_name: log file name
    :type file_name: str
    :param level: logging level
    :type level: int
    :return: logger
    :rtype: logging.Logger

    """
    path, prepared = '', True
    for cat in file_name.split('/')[1:-1]:
        path += '/%s' % cat
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except PermissionError:
                prepared = False
                break
    if not prepared:
        file_name = '/tmp/%s' % file_name.split('/')[-1]
    logging.basicConfig(level=level, format=logging_format)
    log = logging.getLogger(logger_name)
    handler = logging.FileHandler(file_name, encoding='utf8')
    handler.setFormatter(logging.Formatter(logging_format))
    log.addHandler(handler)
    log.setLevel(level=level)
    return log


def error_handler(logger, error, message, sys_exit=False, debug_info=False):
    """

    Error handler

    :param logger: logger
    :type logger: logging.Logger
    :param error: current exception
    :type error: Exception or None
    :param message: custom message
    :type message: str
    :param sys_exit: if True, sys.exit(1)
    :type sys_exit: bool
    :param debug_info: if True, output traceback
    :type debug_info: bool

    """
    _ = builtins.__dict__.get('_', lambda x: x)
    if debug_info:
        et, ev, tb = sys.exc_info()
        logger.error(
            '%s %s: %s\n%s\n--->\n--->\n' % (message, _('error'), error,
                                             ''.join(traceback.format_exception(et, ev, tb))))
    else:
        logger.error('%s%s: %s' % (message, _('error'), error))
    if sys_exit:
        logger.error(_('error termination'))
        exit(1)


def curl_request(url, raw=False, head=None, post_data=None, post_file=None, post_upload=None, credentials=None,
                 raw_data=False, patch=False):
    post_fields = None
    if post_file is not None:
        try:
            post_data = {parm.split('=')[0]: urlencode(parm.split('=')[1]) for parm in
                         open(post_file, 'r').read().split('&')}
        except FileNotFoundError:
            print('File %s not found' % post_file)
            return None
    c = pycurl.Curl()
    buf = BytesIO()
    headers = BytesIO()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.WRITEFUNCTION, buf.write)
    c.setopt(c.HEADERFUNCTION, headers.write)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    if head is not None:
        c.setopt(pycurl.HTTPHEADER, head)
    if post_data is not None:
        if not raw_data:
            post_fields = urlencode(post_data)
        else:
            post_fields = post_data
        if not patch:
            c.setopt(c.POSTFIELDS, post_fields.encode())
    if post_upload is not None:
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.HTTPPOST, post_upload)
    if credentials is not None:
        c.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
        c.setopt(pycurl.USERPWD, credentials)
    if patch:
        c.setopt(pycurl.UPLOAD, 1)
        c.setopt(pycurl.CUSTOMREQUEST, 'PATCH')
        c.setopt(pycurl.READFUNCTION, BytesIO(post_fields.encode()).read)
        c.setopt(pycurl.INFILESIZE, len(post_fields.encode()))
    c.perform()
    code = c.getinfo(c.RESPONSE_CODE)
    c.close()
    try:
        response = json.loads(buf.getvalue().decode('UTF-8')) if not raw else buf.getvalue()
    except json.JSONDecodeError:
        response = {}
    return code, headers.getvalue(), response

from dns import resolver
from http.server import BaseHTTPRequestHandler
from httpproxy.utils.helpers import curl_request, error_handler
from httpproxy.config import translate as _, logger, config_args


class MyTestHandler (BaseHTTPRequestHandler):
    """

    Request handler

    """
    def do_GET(self):
        for host in config_args.get('enabled', []):
            try:
                for s in resolver.query(host['domain'], 'A'):
                    if s.address == self.client_address[0]:
                        for u in host.get('url', []):
                            if self.path.startswith(u):
                                code, url, response = None, '%s%s' % (host.get('redirect', ''), self.path), None
                                for x in range(host.get('attempts', 3)):
                                    code, headers, response = curl_request(url, raw=True)
                                    logger.info('%s [%s] GET %s --> %s' % (
                                        self.client_address[0], code, self.path, host.get('redirect', '')))
                                    if code == 302 and host.get('follow_redirect', False):
                                        redirect = None
                                        for header in headers.decode().split('\r\n'):
                                            if header.startswith('Location:'):
                                                redirect = ''.join(header.split(' ')[1:]).strip()
                                                break
                                        if redirect:
                                            code, headers, response = curl_request(redirect, raw=True)
                                            logger.info('%s [%s] GET %s --> %s' % (
                                                self.client_address[0], code, self.path, redirect))
                                    if code == host.get('code_expected', 201):
                                        break
                                self.send_response(code)
                                for header in self.headers:
                                    self.send_header(header, self.headers[header])
                                self.end_headers()
                                self.wfile.write(response)
                                return
            except resolver.NXDOMAIN:
                logger.info('%s \'%s\' %s' % (_('domain'), host['domain'], _('not exists')))
            except resolver.NoAnswer:
                logger.info('%s \'%s\'' % (_('no answer for domain'), host['domain']))
            except Exception as e:
                error_handler(logger, e, _('get handler'), debug_info=True)
        self.send_response(403)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        logger.info('%s [403] GET %s' % (self.client_address[0], self.path))
        self.wfile.write(bytes('403 Forbidden'.encode()))

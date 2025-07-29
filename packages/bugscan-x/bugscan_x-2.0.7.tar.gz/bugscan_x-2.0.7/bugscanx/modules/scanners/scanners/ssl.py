import ssl
import socket

from .base import BaseScanner


class SSLScannerBase(BaseScanner):
    def __init__(
        self,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.tls_version = ssl.PROTOCOL_TLS

    def resolve_ip(self, host):
        try:
            return socket.gethostbyname(host)
        except Exception:
            return "Unknown"

    def task(self, payload):
        sni = payload['host']

        if not sni:
            return

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_client:
                socket_client.settimeout(2)
                socket_client.connect((sni, 443))
                context = ssl.SSLContext(self.tls_version)
                with context.wrap_socket(
                    socket_client,
                    server_hostname=sni,
                    do_handshake_on_connect=True,
                ) as ssl_socket:
                    
                    data = {
                        'sni': sni,
                        'tls_version': ssl_socket.version()
                    }
                    
                    self._handle_success(data)
        except Exception:
            pass

        self.progress(sni)

    def complete(self):
        self.progress(self.logger.colorize("Scan completed", "GREEN"))


class HostSSLScanner(SSLScannerBase):
    def __init__(
        self,
        input_file=None,
        threads=50,
        output_file=None,
        **kwargs
    ):
        super().__init__(threads=threads, is_cidr_input=False, output_file=output_file, **kwargs)
        self.input_file = input_file

        if self.input_file:
            self.set_host_total(self.input_file)

    def log_info(self, **kwargs):
        messages = [
            self.logger.colorize('{tls_version:<8}', 'CYAN'),
            self.logger.colorize('{ip:<15}', 'YELLOW'),
            self.logger.colorize('{sni}', 'LGRAY'),
        ]
        formatted_message = '  '.join(messages).format(**kwargs)
        self.logger.log(formatted_message)
        
        if self.output_file and 'tls_version' in kwargs and kwargs['tls_version']:
            plain_message = f"{kwargs['tls_version']:<8}  {kwargs['ip']:<15}  {kwargs['sni']}"
            self.write_to_file(plain_message)

    def generate_tasks(self):
        for host in self.generate_hosts_from_file(self.input_file):
            yield {
                'host': host,
            }

    def init(self):
        self.write_scan_metadata(self.input_file)
        self.log_info(tls_version='TLS', ip='IP', sni='SNI')
        self.log_info(tls_version='---', ip='--', sni='---')

    def _handle_success(self, data):
        data['ip'] = self.resolve_ip(data['sni'])
        self.success(data)
        self.log_info(**data)


class CIDRSSLScanner(SSLScannerBase):
    def __init__(
        self,
        cidr_ranges=None,
        threads=50,
        output_file=None,
        **kwargs
    ):
        super().__init__(threads=threads, is_cidr_input=True, cidr_ranges=cidr_ranges, output_file=output_file, **kwargs)
        self.cidr_ranges = cidr_ranges or []
        
        if self.cidr_ranges:
            self.set_cidr_total(self.cidr_ranges)

    def log_info(self, **kwargs):
        messages = [
            self.logger.colorize('{tls_version:<8}', 'CYAN'),
            self.logger.colorize('{sni}', 'LGRAY'),
        ]
        formatted_message = '  '.join(messages).format(**kwargs)
        self.logger.log(formatted_message)
        
        if self.output_file and 'tls_version' in kwargs and kwargs['tls_version']:
            plain_message = f"{kwargs['tls_version']:<8}  {kwargs['sni']}"
            self.write_to_file(plain_message)

    def generate_tasks(self):
        for host in self.generate_cidr_hosts(self.cidr_ranges):
            yield {
                'host': host,
            }

    def init(self):
        self.write_scan_metadata()
        self.log_info(tls_version='TLS', sni='SNI')
        self.log_info(tls_version='---', sni='---')

    def _handle_success(self, data):
        self.success(data)
        self.log_info(**data)

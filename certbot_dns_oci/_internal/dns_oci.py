"""DNS Authenticator for Oracle Cloud Infrastructure DNS."""
import logging

import zope.interface

from oci import config
from oci.dns import DnsClient
from oci.dns.models import RecordDetails, UpdateRRSetDetails
from oci.exceptions import ServiceError
from os import path, environ

from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Oracle Cloud Infrastructure (OCI)
    This Authenticator uses the OCI API to fulfill a dns-01 challenge.
    """

    description = 'Obtain certificates using a DNS TXT record (if you are using OCI for DNS).'
    ttl = 60

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    def more_info(self):  # pylint: disable=missing-function-docstring
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' + \
               'the OCI API.'

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=60)
        add('credentials', help='Path to OCI credentials file', default=None)
        add('profile', help='Profile name in OCI credentials file', default=None)

    def _setup_credentials(self):
        if self.conf('credentials') is None:
            oci_config_file = path.join(path.expanduser("~"), ".oci", "config")
        else:
            oci_config_file = self.conf('credentials')

        oci_config_profile = 'DEFAULT'

        if self.conf('profile') is not None:
            oci_config_profile = self.conf('profile')
        elif 'OCI_CONFIG_PROFILE' in environ:
            oci_config_profile = environ.get('OCI_CONFIG_PROFILE')

        self.credentials = config.from_file(file_location=oci_config_file, profile_name=oci_config_profile)

    def _perform(self, domain, validation_name, validation):
        self._get_oci_client().add_txt_record(domain, validation_name, validation, self.ttl)

    def _cleanup(self, domain, validation_name, validation):
        self._get_oci_client().del_txt_record(domain, validation_name)

    def _get_oci_client(self):
        return _OciClient(self.credentials)


class _OciClient:
    """
    Encapsulates all communication with the OCI API.
    """
    def __init__(self, oci_config):
        self.client = DnsClient(oci_config)

    def add_txt_record(self, domain_name, record_name, record_content, ttl):
        zone_name = self._find_zone_name(domain_name)
        try:
            logger.debug('Update TXT record with data: %s', record_content)
            update_rr_set_details = UpdateRRSetDetails(
                items=[
                    RecordDetails(
                        domain=record_name,
                        rdata=record_content,
                        rtype='TXT',
                        ttl=ttl
                    )
                ]
            )
            self.client.update_rr_set(zone_name_or_id=zone_name,
                                      domain=record_name, rtype='TXT',
                                      update_rr_set_details=update_rr_set_details)
        except Exception as e:
            logger.warning('Error updating TXT record %s using the OCI API: %s', record_name, e)

    def del_txt_record(self, domain_name, record_name):
        zone_name = self._find_zone_name(domain_name)
        rr_set = self.client.get_rr_set(zone_name_or_id=zone_name, domain=record_name, rtype='TXT')

        try:
            if rr_set.data.items:
                logger.debug('Removing TXT record with data: %s', rr_set.data.items)
                self.client.delete_rr_set(zone_name_or_id=domain_name, domain=record_name, rtype='TXT')
        except Exception as e:
            logger.warning('Error deleting TXT record %s using the OCI API: %s', rr_set.data.items, e)

    def _find_zone_name(self, domain_name):
        domain_name_guesses = dns_common.base_domain_name_guesses(domain_name)
        for domain in domain_name_guesses:
            try:
                self.client.get_zone(zone_name_or_id=domain)
                return domain
            except ServiceError as e:
                if e.status == 404:
                    pass

        raise errors.PluginError('Cannot find zone for domain name {}'.format(domain_name))

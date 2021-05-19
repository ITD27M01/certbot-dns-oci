"""Tests for certbot_dns_oci._internal.dns_oci."""

import unittest

import oci
try:
    import mock
except ImportError: # pragma: no cover
    from unittest import mock # type: ignore

from certbot import errors
from certbot.plugins import dns_test_common
from certbot.plugins.dns_test_common import DOMAIN
from certbot.tests import util as test_util

API_ERROR = oci.exceptions.ServiceError(
    status="Fake Exception",
    code=404,
    headers={},
    message="Just fake exception"
)
OCI_CREDENTIALS = {
    "user": "ocid1.user.oc1..fake_user",
    "tenancy": "ocid1.tenancy.oc1..fake_tenancy",
    "region": "eu-frankfurt-1",
    "fingerprint": "1a:a2:36:85:e6:9e:ea:2d:ce:0b:0e:5c:bc:e3:cd:88",
    "key_file": "tests/fake.pem"
}


class AuthenticatorTest(test_util.TempDirTestCase, dns_test_common.BaseAuthenticatorTest):

    def setUp(self):
        from certbot_dns_oci._internal.dns_oci import Authenticator

        super().setUp()

        path = "tests/test_oci_config.ini"
        self.config = mock.MagicMock(oci_credentials=path,
                                     oci_profile='DEFAULT',
                                     oci_propagation_seconds=0)  # don't wait during tests

        self.auth = Authenticator(self.config, "oci")

        self.mock_client = mock.MagicMock()
        # _get_oci_client | pylint: disable=protected-access
        self.auth._get_oci_client = mock.MagicMock(return_value=self.mock_client)

    def test_perform(self):
        self.auth.perform([self.achall])

        expected = [mock.call.add_txt_record(DOMAIN, '_acme-challenge.' + DOMAIN, mock.ANY, 60)]
        self.assertEqual(expected, self.mock_client.mock_calls)

    def test_cleanup(self):
        # _attempt_cleanup | pylint: disable=protected-access
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])

        expected = [mock.call.del_txt_record(DOMAIN, '_acme-challenge.' + DOMAIN)]
        self.assertEqual(expected, self.mock_client.mock_calls)


class OciClientTest(unittest.TestCase):

    id_num = 1
    record_prefix = "_acme-challenge"
    record_name = record_prefix + "." + DOMAIN
    record_content = "bar"
    record_ttl = 60

    def setUp(self):
        from certbot_dns_oci._internal.dns_oci import _OciClient

        self.oci_client = _OciClient(OCI_CREDENTIALS)

        self.client = mock.MagicMock()
        self.oci_client.client = self.client

    def test_add_txt_record(self):
        self.client.get_zone.return_value = DOMAIN

        self.oci_client.add_txt_record(DOMAIN, self.record_name, self.record_content,
                                       self.record_ttl)

        call_count = self.client.update_rr_set.call_count
        self.assertEqual(call_count, 1)

    def test_add_txt_record_fail_to_find_domain(self):
        self.client.get_zone.side_effect = API_ERROR

        self.assertRaises(errors.PluginError,
                          self.oci_client.add_txt_record,
                          DOMAIN, self.record_name, self.record_content, self.record_ttl)

    def test_add_txt_record_error_finding_domain(self):
        self.client.get_zone.side_effect = API_ERROR

        self.assertRaises(errors.PluginError,
                          self.oci_client.add_txt_record,
                          DOMAIN, self.record_name, self.record_content, self.record_ttl)

    def test_add_txt_record_error_creating_record(self):
        self.client.update_rr_set.side_effect = API_ERROR

        self.client.get_zone.return_value = DOMAIN

        self.assertRaises(errors.PluginError,
                          self.oci_client.add_txt_record,
                          DOMAIN, self.record_name, self.record_content, self.record_ttl)

    def test_del_txt_record(self):
        self.client.get_zone.return_value = DOMAIN

        self.oci_client.del_txt_record(DOMAIN, self.record_name)

        self.assertTrue(self.client.delete_rr_set.called)

    def test_del_txt_record_fail_to_find_domain(self):
        self.client.get_zone.side_effect = API_ERROR
        self.assertRaises(errors.PluginError,
                          self.oci_client.del_txt_record,
                          DOMAIN, self.record_name)

    def test_del_txt_record_error_finding_domain(self):
        self.client.get_zone.side_effect = API_ERROR
        self.assertRaises(errors.PluginError,
                          self.oci_client.del_txt_record,
                          DOMAIN, self.record_name)

    def test_del_txt_record_error_deleting_record(self):
        self.client.delete_rr_set.side_effect = API_ERROR

        self.client.get_zone.return_value = DOMAIN

        self.assertRaises(errors.PluginError,
                          self.oci_client.del_txt_record,
                          DOMAIN, self.record_name)

    def test_del_txt_record_error_finding_record(self):
        self.client.get_rr_set.side_effect = API_ERROR

        self.client.get_zone.return_value = DOMAIN

        self.assertRaises(errors.PluginError,
                          self.oci_client.del_txt_record,
                          DOMAIN, self.record_name)


if __name__ == "__main__":
    unittest.main()  # pragma: no cover

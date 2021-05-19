# Oracle Cloud Infrastructure DNS Authenticator plugin for Certbot

Plugin automates the process of `dns-01` challenge by managing TXT records
using the Oracle Cloud Infrastructure DNS service.

## Installation

```shell
pip3 install certbot-dns-oci
```

## Arguments

| Name        | Description | Default |
| ------------- |:-------------:| :-------------: |
| **--authenticator dns-oci** | Select the plugin |Required|
| **--dns-oci-credentials** | OCI credentials config file location |`~/.oci/config`|
| **--dns-oci-profile** | Profile name in OCI credentials config file |`DEFAULT`|
| **--dns-oci-propagation-seconds** | DNS record propagation timeout |60|

## Credentials
Plugin requires the
[OCI credentials configuration file](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm)
which location is `~/.oci/config` by default. You can specify which profile
to load in the case of multiple profiles with different values. By default
the `DEFAULT` profile is loaded.

**--dns-oci-credentials** accepts `instance_principal` value which
switches certbot to use instance principal for OCI authentication,
[please read the documentation about it.](https://docs.oracle.com/en-us/iaas/Content/Identity/Tasks/callingservicesfrominstances.htm)
At least your dynamic group must be able to read `dns-zones` in
compartment and manage `dns-records`.
## Example

```shell
certbot certonly --email user@example.com \
                 --authenticator dns-oci -d www.example.com --dry-run
```

## Requirements
```
oci
certbot
```
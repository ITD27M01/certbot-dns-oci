# Oracle Cloud Infrastructure DNS Authenticator plugin for Certbot

Plugin automates the process of dns-01 challenge by managing TXT records in
the Oracle Cloud Infrastructure DNS service.

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
**--dns-oci-credentials** has special value `instance_principal` that switches
certbot to use the instance principal for OCI authentication
([please, read the documentation about the feature.](https://docs.oracle.com/en-us/iaas/Content/Identity/Tasks/callingservicesfrominstances.htm))
Corresponding dynamic group must be able to read `dns-zones` in compartment
and manage `dns-records`.

In other cases, plugin requires the
[OCI credentials configuration file](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm),
which is `~/.oci/config` by default.
The profile can be specified by **--dns-oci-profile** (usually `DEFAULT`).
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
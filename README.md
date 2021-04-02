# Oracle Cloud Infrastructure DNS Authenticator plugin for Certbot

Plugin automates the process of `dns-01` challenge by managing TXT records using the Oracle Cloud Infrastructure
DNS service.

## Installation

```shell
pip3 install certbot-dns-oci
```

## Arguments

| Name        | Description | Default |
| ------------- |:-------------:| :-------------: |
| `--authenticator dns-oci` | Select the plugin |Required|
| `--dns-oci-credentials` | OCI credentials config file location |`~/.oci/config`|
| `--dns-oci-profile` | Profile name in OCI credentials config file |`DEFAULT`|
| `--dns-oci-propagation-seconds` | DNS record propagation timeout |60|

## Usage

```shell
certbot certonly --email user@example.com \
                 --authenticator dns-oci -d 'www.example.com' --dry-run
```

## Requirements
```
oci
certbot
```
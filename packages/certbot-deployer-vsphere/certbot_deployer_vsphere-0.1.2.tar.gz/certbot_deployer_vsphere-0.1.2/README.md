certbot_deployer_vsphere
===========

[Certbot Deployer] plugin for deploying web certificates for the vSphere web UI via [Certbot] "deploy hook".

# Requires

* Python 3.9+
* vSphere 7 or 8

# Installation

You can install with [pip]:

```sh
python3 -m pip install certbot_deployer_vsphere
```

Or install from source:

```sh
git clone <url>
pip install certbot_deployer_vsphere
```

# Usage

## Examples

Examples assume the tool is being run as a Certbot deploy hook, and the environment variable `RENEWED_LINEAGE` points to the live certificate directory just updated by Certbot.

To deploy the certificate bundle indicated by `$RENEWED_LINEAGE` to `$VSPHEREHOST`:

```sh
certbot-deployer-vsphere --user $VSPHEREUSER --password $VSPHEREPASSWORD --host $VSPHEREHOST
```

## Config

It is recommended that you store the password in the Certbot Deployer configuration file (`/etc/certbot_deployer/certbot_deployer.conf`) with appropriate permissions rather than providing it as an argument and leaving it visible in the process list

```json
{
  [...],
  "vsphere": {
    "user": "vsphereuser",
    "password": "vspherepassword",
    "host": "vspherehost",
  }
}
```

## Reference

```
usage: certbot-deployer vsphere [-h] --user USER --password PASSWORD --host
                                HOST [--tls-no-verify]

Certbot Deployer plugin for deploying web certificates to VSphere

options:
  -h, --help            show this help message and exit
  --user USER, -u USER  vSphere API user
  --password PASSWORD, -p PASSWORD
                        vSphere API password
  --host HOST, -H HOST  vsphere host to target
  --tls-no-verify       Skip TLS verification of the API endpoints e.g. if
                        deploying Certbot certificates over self-signed
                        certificates currently in-place
```

# Contributing

Merge requests are welcome. You should probably open an issue first to discuss what you would like to change.

To run the test suite:

```bash
# Dependent targets create venv and install dependencies
make
```

Please make sure to add/update tests along with any changes.

# License

License :: OSI Approved :: MIT License


[Certbot Deployer]: https://github.com/theias/certbot_deployer
[Certbot]: https://certbot.eff.org/
[pip]: https://pip.pypa.io/en/stable/

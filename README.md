# ASSHer
Asynchronous SSH/SFTP runner.

## Installation

```sh
python3 -m pip install assher
```

## Usage as command-line utility
You can see help by running
```sh
python3 -m assher --help
```
Example of running on a couple of networks (using bash sequence expression)
```sh
python3 -m assher -L 50 --hosts 192.168.22{5..6}.{10..254} -c "hostname -s" -U root -i ~/.ssh/very_secret_privkey
```
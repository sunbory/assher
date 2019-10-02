# ASSHer
Asynchronous SSH/SFTP runner.

## Installation

```sh
python3 -m pip install assher
```

## Some examples of usage as command-line utility
You can see help by running
```sh
python3 -m assher --help
```
Example of running on a couple of networks (using bash sequence expression)
```sh
python3 -m assher -L 50 --hosts 192.168.22{5..6}.{10..254} -c "hostname -s" \
-U root -i ~/.ssh/very_secret_privkey
```
The same with overriding global connection parametes for second subnet
```sh
python -m assher -L 10 \
--hosts {192.168.225.{10..254},user:password@192.168.226.{10.254}:2222} \
-c "uptime" -U root -P anotherpass
```

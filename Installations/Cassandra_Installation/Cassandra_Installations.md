# Apache Cassandra Installation Guide

## Installing Java

```bash
sudo apt install openjdk-8-jdk
```

## Downloading Apache Cassandra
```bash
cd /usr/local
sudo wget https://dlcdn.apache.org/cassandra/4.0.11/apache-cassandra-4.0.11-bin.tar.gz
sudo tar -xzf apache-cassandra-4.0.11-bin.tar.gz
sudo mv apache-cassandra-4.0.11 /usr/local/cassandra 
sudo chown -R hadoop:hadoop cassandra
```

## Installing Apache Ant
```bash
cd /usr/local/cassandra 
wget https://ant.apache.org/bindownload.cgi
```

## Cassandra Configuration
### cassandra.yaml (Single node configuration)
```bash
cd /usr/local/cassandra/conf
sudo gedit cassandra.yaml
Set listen_address and rpc_address to the IP address of your machine.
```

## Create a systemctl service for Cassandra
```bash
sudo gedit /etc/systemd/system/cassandra.service
```

- Paste the following configuration:

```bash
[Unit]
Description=Apache Cassandra Database
After=network.target

[Service]
User=hadoop
Group=hadoop
WorkingDirectory=/usr/local/cassandra/bin
ExecStart=/usr/local/cassandra/bin/cassandra -f
ExecStop=/usr/local/cassandra/bin/nodetool stopdaemon
Restart=always

[Install]
WantedBy=multi-user.target
```

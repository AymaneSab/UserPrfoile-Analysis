
# Apache ZooKeeper Installation Guide

## Requirements

- Verify Java installation:
  ```bash
  java -version
  ```
## Download and Install ZooKeeper 

- Download binary version
    ```bash
    sudo wget https://dlcdn.apache.org/zookeeper/zookeeper-3.8.3/apache-zookeeper-3.8.3-bin.tar.gz
    ```

- Extract the downloaded file
    ```bash
    sudo tar -xvf apache-zookeeper-3.8.3-bin.tar.gz
    ```
- Rename the extracted directory
    ```bash
    sudo mv apache-zookeeper-3.8.3-bin zookeeper
    ```

- Change the directory owner to hadoop
    ```bash
    sudo chown -R hadoop:hadoop /usr/local/zookeeper
    ```

- Navigate to the zookeeper directory
    ```bash
    cd /usr/local/zookeeper
    ```

## Configure ZooKeeper
### zoo.cfg

- Navigate to the ZooKeeper configuration directory:
    ```bash
    cd /usr/local/zookeeper/conf
    ```

- Edit the zoo.cfg file:
    ```bash
    sudo gedit zoo.cfg
    ```
- Add the following configuration for standalone mode:
    ```bash
    tickTime = 2000
    dataDir = /usr/local/zookeeper/data
    clientPort = 2181
    initLimit = 5
    syncLimit = 2
    ```

## Create System Service

- Create a ZooKeeper systemd service file:
    ```bash
    sudo gedit /etc/systemd/system/zookeeper.service
    ```

- Paste the following content into the file:
    ```bash
    [Unit]
    Description=Zookeeper Daemon
    Documentation=http://zookeeper.apache.org
    Requires=network.target
    After=network.target
    
    [Service]    
    Type=forking
    WorkingDirectory=/usr/local/zookeeper
    User=hadoop
    Group=hadoop
    ExecStart=/usr/local/zookeeper/bin/zkServer.sh start /usr/local/zookeeper/conf/zoo.cfg
    ExecStop=/usr/local/zookeeper/bin/zkServer.sh stop /usr/local/zookeeper/conf/zoo.cfg
    ExecReload=/usr/local/zookeeper/bin/zkServer.sh restart /usr/local/zookeeper/conf/zoo.cfg
    TimeoutSec=30
    Restart=on-failure
    
    [Install]
    WantedBy=default.target
    ```
- Reload systemd and enable ZooKeeper service to start on boot:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable zookeeper
    ```



















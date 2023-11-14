# Apache Spark Installation on Ubuntu

## Requirements

```bash
sudo apt update                          
sudo apt install default-jdk
```
         
## Download and install spark 
- change to local directorie
```bash
cd /usr/local
```
- Install binary Version
```bash
sudo wget https://archive.apache.org/dist/spark/spark-3.4.0/spark-3.4.0-bin-hadoop3.tgz
sudo tar -xvf spark-3.4.0-bin-hadoop3.tgz # Extract the file 
sudo mv spark-3.4.0-bin-hadoop3 spark    
sudo chown -R hadoop:hadoop /usr/local/spark
```

## Apache Spark Configuration
- Configure Environment Variables

```bash
sudo gedit ~/.bashrc

export SPARK_HOME=/usr/local/spark
export PATH=$PATH:$SPARK_HOME/bin

source ~/.bashrc
```

## Starting Apache Spark
```bash
cd /usr/local/spark/sbin

./start-all.sh       # Start Spark services
spark-shell          # Start Spark shell
```

## Stop Spark
```bash
./stop-all.sh
```

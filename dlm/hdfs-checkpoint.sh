#!/bin/bash

FSIMAGE_DIR=/data/cdh/dfs/snn/current
OIV_OUT_DIR=/tmp

# Save name space on primary Namenode. We save latest metadata to the fsimage file.
echo "Save name space on primary Namenode."
hdfs dfsadmin -safemode enter
hdfs dfsadmin -saveNamespace
hdfs dfsadmin -safemode leave

# Check point name space on secondary Namenode.
echo "Stop Secondary NameNode service and check point."
hdfs secondarynamenode stop
hdfs secondarynamenode -checkpoint force

# Convert binary Namenode fsiamge file to text format using the OIV tool.
echo "Convert binary Namenode fsiamge file to text format."
LATEST_FSIMAGE=`ls -tr $FSIMAGE_DIR/fsimage_* | grep -v 'md5' | tail -1`
hdfs oiv -i $LATEST_FSIMAGE -o $OIV_OUT_DIR/fsimage.xml -p XML

echo "Done."

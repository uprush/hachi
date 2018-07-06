# End to End Data Analytics and Deep Learning Pipeline Demo

This is to demonstrate an end-to-end pipeline for data analytics and deep learning.

## Environment Setup
In this demo, we use Apache Nifi, Apache Solr, Apache Spark, TensorFlow. The easiest way to get everything up is to use Hortonworks Data Platform and its Nifi and Solr management pack.


Setup the Banana dashboard by copying default.json to dashboard dir
```
cd /opt/lucidworks-hdpsearch/solr/server/solr-webapp/webapp/banana/app/dashboards/
mv default.json default.json.orig
wget https://raw.githubusercontent.com/abajwa-hw/ambari-nifi-service/master/demofiles/default.json
```

Allow Solr to recognize the timestamp format of tweets. Make the following change and restart Solr.
```
vi /opt/lucidworks-hdpsearch/solr/server/solr/configsets/data_driven_schema_configs/conf/solrconfig.xml

<processor>
    <arr name="format">
      <str>EEE MMM d HH:mm:ss Z yyyy</str>
```

Create tweets collection in Solr.
```
/opt/lucidworks-hdpsearch/solr/bin/solr create -c tweets \
   -d data_driven_schema_configs \
   -s 1 \
   -rf 1
```

## Demo Setup
Import `nifi-template.xml` into Nifi template.

Import `zeppelin-notebook.json` into Zeppelin notebook.

Configure a S3 Viewer to point to your S3 bucket. In Ambari File View config:
```
fs.defaultFS=s3a://your-bucket/;fs.s3a.access.key=<your-access-key>;fs.s3a.secret.key=<your-secret-key>
```

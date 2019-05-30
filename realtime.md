# Realtime Dashboard

## TODO
* unixtime in ES should be date type

## Kafka Integration
Start KSQL CLI
```
./bin/ksql http://localhost:8087
```

Create KSQL doglovers Stream.
```
ksql> CREATE STREAM doglovers (tweet_id varchar, unixtime bigint,time varchar, user varchar, screen_name varchar, language varchar, hashtags varchar, location varchar, media_url varchar, msg varchar) with (kafka_topic = 'doglovers', value_format = 'json');
```

Run an example query.
```
ksql> select screen_name, language, location from doglovers limit 3;
```

## Integration with Elasticsearch

Install Kafka Connect Elasticsearch connector.
```
./bin/confluent-hub install confluentinc/kafka-connect-elasticsearch:latest
```

Start Kafka Connect
```
./bin/connect-standalone -daemon etc/schema-registry/connect-json-standalone.properties etc/kafka-connect-elasticsearch/doglovers.properties
```

Show Connect Config
```
./bin/confluent config elasticsearch-sink-doglovers

Current configuration of 'elasticsearch-sink-doglovers' connector:
{
  "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
  "type.name": "doglovers",
  "topics": "doglovers",
  "tasks.max": "1",
  "topic.index.map": "doglovers:doglovers",
  "name": "elasticsearch-sink-doglovers",
  "connection.url": "http://localhost:9200",
  "key.ignore": "true",
  "schema.ignore": "true"
}
```

Check Kibaba Dashboard
http://fb-ubuntu01.purestorage.int:5601/app/kibana#/dashboards?_g=()

Create index with field mapping.
```
PUT /doglovers
{
    "mappings" : {
      "properties" : {
        "hashtags" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "language" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "location" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "media_url" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "msg" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "screen_name" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "time" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "tweet_id" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "unixtime" : {
          "type" : "date",
          "format": "epoch_millis",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "user" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        }
      }
    }
}

```


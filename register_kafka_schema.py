import argparse
import os
import sys

import requests

parser = argparse.ArgumentParser(description='Register schema in Kafka Schema Registry.')
# general
parser.add_argument('--registry-url', default='http://localhost:8081', help='Kafka schema registry URL.')
parser.add_argument('--topic', default='doglovers', help='Kafka topic to associate with the schema.')
parser.add_argument('--schema-file', default='doglovers.avsc', help='Avro schema file.')

args = parser.parse_args()

url = args.registry_url
topic = args.topic
schema_file = args.schema_file

print("Schema Registry URL: " + url)
print("Topic: " + topic)
print("Schema file: " + schema_file)
print

aboslute_path_to_schema = os.path.join(os.getcwd(), schema_file)
with open(aboslute_path_to_schema, 'r') as content_file:
    schema = content_file.read()

payload = "{ \"schema\": \"" \
          + schema.replace("\"", "\\\"").replace("\t", "").replace("\n", "") \
          + "\" }"

url = url + "/subjects/" + topic + "-value/versions"
headers = {"Content-Type": "application/vnd.schemaregistry.v1+json"}

r = requests.post(url, headers=headers, data=payload)
if r.status_code == requests.codes.ok:
    print("Success")
else:
    r.raise_for_status()

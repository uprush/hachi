# Twitter Analytics Notebook – S3A Demo
S3A connector is a Hadoop DFS protocol implementation for S3 compitable storage. S3A connector enables the Hadoop ecosystem to store and process data in S3 compitable storages. S3A has been used in production for years, especially heavily used on the cloud environment. In this notebook, we demonstrate to use S3A supported tool, including hdfs command line, Apache Spark and Apache Hive, to access data in S3.

## Use Case
Ingest Twitter data in real-time, send the data to Solr for near real-time indexing and dashboarding. Raw tweets data is also sent to S3. Further processing and analytics are performed using open source big data tools such as Apache Spark and Apache Hive.

Demo environment is built on top of Cloudera CDH 6.0.0.

## Process Data in Spark
Let's take a look at the tweets data stored in S3.
With S3A connector, we can use the hdfs command line to access S3 just like accessing HDFS.

```sh
$ su hdfs
$ hdfs dfs -ls s3a://deephub/tweets/ | head -n 5

$ hdfs dfs -cat s3a://deephub/tweets/755825773249087 | head -n 1

Found 40 items
-rw-rw-rw-   1 zeppelin zeppelin     819360 2018-07-06 16:23 s3a://deephub/tweets/755825773249087
-rw-rw-rw-   1 zeppelin zeppelin     640045 2018-07-06 16:23 s3a://deephub/tweets/755847797668277
-rw-rw-rw-   1 zeppelin zeppelin     750379 2018-07-06 16:23 s3a://deephub/tweets/755874821579546
-rw-rw-rw-   1 zeppelin zeppelin     778645 2018-07-06 16:23 s3a://deephub/tweets/755898847037685
{"created_at":"Fri Jul 06 07:58:39 +0000 2018","id":1015142971845431296,"id_str":"1015142971845431296","text":"RT @Namastaywoke: The fact that the dog could be either one of them is SENDING MEEE https:\/\/t.co\/mFfEafRljS","source":"\u003ca href=\"http:\/\/twitter.com\/download\/iphone\" rel=\"nofollow\...
```

Read JSON data using Spark.
```scala
$ spark-shell

scala> val flatJSON = sc.textFile("s3a://deephub/tweets/")

// Count total number of rows in all JSON files.
scala> flatJSON.count()

flatJSON: org.apache.spark.rdd.RDD[String] = s3a://deephub/tweets/ MapPartitionsRDD[69] at textFile at <console>:59
res80: Long = 4082
```

Convert to DataFrame. Take a look at its JSON schema.
```scala
scala> import org.apache.spark.sql.SparkSession
scala> import spark.implicits._
scala> import org.apache.spark.sql.functions._

scala> val sqlContext = SparkSession.builder().getOrCreate()
scala> val tweetsDF = sqlContext.read.json(sqlContext.createDataset(flatJSON))
scala> tweetsDF.printSchema()

tweetsDF: org.apache.spark.sql.DataFrame = [contributors: string, coordinates: struct<coordinates: array<double>, type: string> ... 34 more fields]
root
 |-- contributors: string (nullable = true)
 |-- coordinates: struct (nullable = true)
 |    |-- coordinates: array (nullable = true)
 |    |    |-- element: double (containsNull = true)
 |    |-- type: string (nullable = true)
 |-- created_at: string (nullable = true)
 |-- display_text_range: array (nullable = true)
 |    |-- element: long (containsNull = true)
 |-- entities: struct (nullable = true)
 |    |-- hashtags: array (nullable = true)
 |    |    |-- element: struct (containsNull = true)
 |    |    |    |-- indices: array (nullable = true)
 |    |    |    |    |-- element: long (containsNull = true)
 |    |    |    |-- text: string (nullable = true)
 |    |-- media: array (nullable = true)
```

Who are the most influential users and what did they tweet?
```scala
scala> tweetsDF.select($"user.id", $"user.screen_name", $"user.followers_count", $"text").orderBy($"user.followers_count".desc).show(10)

+----------+---------------+---------------+--------------------+
|        id|    screen_name|followers_count|                text|
+----------+---------------+---------------+--------------------+
| 835083097|       PupsPorn|        1885147|this dog knows ex...|
|  15632759|         ELLEUK|        1219160|Kylie Jenner Buil...|
|   9609632|     australian|         661614|Media Watch Dog: ...|
| 195516975|  Joselyn_Dumas|         631885|RT @nii_sarpei: A...|
|  15484198| georgegalloway|         291320|@lisalazuli @DecA...|
|2909804893|    DalmatianHd|         149545|RT @DalmatianHd: ...|
|2909804893|    DalmatianHd|         149545|Meet Wiley: a swe...|
|1347947466|Berti_and_Ernie|         147057|'The world would ...|
|  54856746| jonfitchdotnet|         136636|My buddy’s new do...|
| 244368081|   TheMarkTwain|         130228|It's not the size...|
+----------+---------------+---------------+--------------------+
only showing top 10 rows


// We are interested in the user information. Let's create a dataframe just for the user data.
scala> val users = tweetsDF.select($"user.*", $"text")

scala> users.printSchema()

root
 |-- contributors_enabled: boolean (nullable = true)
 |-- created_at: string (nullable = true)
 |-- default_profile: boolean (nullable = true)
 |-- default_profile_image: boolean (nullable = true)
 |-- description: string (nullable = true)
 |-- favourites_count: long (nullable = true)
 |-- follow_request_sent: string (nullable = true)
 |-- followers_count: long (nullable = true)
 |-- following: string (nullable = true)
 |-- friends_count: long (nullable = true)
 |-- geo_enabled: boolean (nullable = true)
 |-- id: long (nullable = true)
 |-- id_str: string (nullable = true)
 |-- is_translator: boolean (nullable = true)
 |-- lang: string (nullable = true)
 |-- listed_count: long (nullable = true)

// Create a temporary view
scala> users.createOrReplaceTempView("users")

```

Top 10 influential English language users by SQL.
```scala
scala> val sqlDF = sqlContext.sql("select screen_name, followers_count from users where lang = 'en' order by followers_count desc limit 10")

scala> sqlDF.show()

+---------------+---------------+
|    screen_name|followers_count|
+---------------+---------------+
|       PupsPorn|        1885147|
|         ELLEUK|        1219160|
|     australian|         661614|
|  Joselyn_Dumas|         631885|
| georgegalloway|         291320|
|    DalmatianHd|         149545|
|    DalmatianHd|         149545|
|Berti_and_Ernie|         147057|
| jonfitchdotnet|         136636|
|   TheMarkTwain|         130228|
+---------------+---------------+
```

Make a S3 directory for persisting the data frame.
```
$ hdfs dfs -mkdir s3a://deephub/twitter-users-par/
```

Persistent to S3 as Parquet file.
```scala
scala> users.write.format("parquet").mode("overwrite").save("s3a://deephub/twitter-users-par/")

```

Confirm parquet file in S3.
```
$ hdfs dfs -ls s3a://deephub/twitter-users-par

Found 41 items
-rw-rw-rw-   1 root root          0 2018-11-07 14:37 s3a://deephub/twitter-users-par/_SUCCESS
-rw-rw-rw-   1 root root      46822 2018-11-07 14:37 s3a://deephub/twitter-users-par/part-00000-add657ad-d05e-4df8-b561-5763caee5845-c000.snappy.parquet
-rw-rw-rw-   1 root root      47159 2018-11-07 14:37 s3a://deephub/twitter-users-par/part-00001-add657ad-d05e-4df8-b561-5763caee5845-c000.snappy.parquet
...
```

### Query Data in Apache Hive
We can also use Apache Hive to access data stored in S3 via S3A. This is open used for reporting use cases.

Open a Hive client, create a external table in Hive, point its location to the bucket on S3 via S3A.

```sql
$ beeline
beeline> !connect jdbc:hive2://hadoop02.purestorage.int:10000


beeline> create external table if not exists twitter_users(
    contributors_enabled boolean,
    created_at string,
    default_profile boolean,
    default_profile_image boolean,
    description string,
    favourites_count bigint,
    follow_request_sent string,
    followers_count bigint,
    `following` string,
    friends_count bigint,
    geo_enabled boolean,
    id bigint,
    id_str string,
    is_translator boolean,
    lang string,
    listed_count bigint,
    location string,
    name string,
    notifications string,
    profile_background_color string,
    profile_background_image_url string,
    profile_background_image_url_https string,
    profile_background_tile boolean,
    profile_banner_url string,
    profile_image_url string,
    profile_image_url_https string,
    profile_link_color string,
    profile_sidebar_border_color string,
    profile_sidebar_fill_color string,
    profile_text_color string,
    profile_use_background_image boolean,
    protected boolean,
    screen_name string,
    statuses_count bigint,
    time_zone string,
    translator_type string,
    url string,
    utc_offset string,
    verified boolean,
    text string
) stored as parquet
location "s3a://deephub/twitter-users-par/";

beeline> show tables;
+----------------+
|    tab_name    |
+----------------+
| twitter_users  |
+----------------+
```

Run a sample query.
```sql
beeline> select screen_name, followers_count, text from twitter_users  limit 2;
+---------------+------------------+----------------------------------------------------+
|  screen_name  | followers_count  |                        text                        |
+---------------+------------------+----------------------------------------------------+
| ttamiaaa      | 188              | RT @Namastaywoke: The fact that the dog could be.. |
| Marxrawr      | 819              | RT @jessarakelyan: ‼️‼️‼️‼️ https://t.co/seeLQyuF6 |
+---------------+------------------+----------------------------------------------------+
```

Apache Impala also supports querying data in S3.
```sql
default> select screen_name, followers_count, text from twitter_users  limit 2;
+-------------+-----------------+-------------------------------------------------------+
| screen_name | followers_count | text                                                  |
+-------------+-----------------+-------------------------------------------------------+
| ttamiaaa    | 188             | RT @Namastaywoke: The fact that the dog could be...   |
| Marxrawr    | 819             | RT @jessarakelyan: ‼️‼️‼️‼️ https://t.co/seeLQyuF68   |
+-------------+-----------------+-------------------------------------------------------+
Fetched 2 row(s) in 0.04s
```

## Summary
We demonstrated big data analytics use cases on S3. S3A protocol support enables easy integration with big data and data analytics tool like Apache Spark, Apache Hive and Apache Impala.

Key Take Aways:

- Simple. Zero effort management.
- Flexible. Separate compute and storage, scale independently.
- Integrate with big data and data analytics tool.

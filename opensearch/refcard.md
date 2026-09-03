---
title: refcard
description: Opensearch, Elastic Reference Card
published: true
date: 2026-02-20T14:24:25.635Z
tags: helpers, elastic, opensearch
editor: markdown
dateCreated: 2026-02-20T14:24:25.635Z
---

# OVERVIEW
* get version and details
```bash
curl -XGET 'http://localhost:9200'
```

# CLUSTER
```bash
 curl 'http://localhost:9200/_cluster/health?pretty'
 curl 'http://localhost:9200/_cluster/health?wait_for_status=yellow&timeout=50s&pretty'
 curl 'http://localhost:9200/_cluster/state?pretty'
 curl 'http://localhost:9200/_cluster/stats?human&pretty'
 curl 'http://localhost:9200/_cluster/pending_tasks?pretty'
```

* full settings
```bash
curl 'http://localhost:9200/_cluster/settings?include_defaults=true&flat_settings=true&pretty'
```

## Disk filling
Add or modify the following lines in `elasticsearch.yml` to set the desired disk watermark levels and their corresponding percentages:
```bash
cluster.routing.allocation.disk.watermark.low: 85%
cluster.routing.allocation.disk.watermark.high: 90%
cluster.routing.allocation.disk.watermark.flood_stage: 95%
```

* low
  Elasticsearch starts allocating new shards to nodes with disk usage below this level.
* high
  Elasticsearch starts throttling shard allocations to nodes with disk usage above this level.
* flood_stage
  Elasticsearch prevents shard allocations on nodes with disk usage above this level.

* check current settings with:
```bash
 curl -s 'http://localhost:9200/_cluster/settings?include_defaults=true&flat_settings=true&pretty' | grep watermark
```


# ADMIN
* force a synced flush
```bash
 curl -XPOST 'localhost:9200/_flush/synced'
```

* Change the number of shards being recovered simultaneously per node
```bash
curl -XPUT localhost:9200/_cluster/settings -d '{
"transient" :{
"cluster.routing.allocation.exclude._ip" : "1.2.3.4"
}
}';echo
```

* Change the recovery speed
```bash
curl -XPUT localhost:9200/_cluster/settings -d '{
"transient" :{
"indices.recovery.max_bytes_per_sec" : "80mb"
}
}';echo
```

* Change the number of concurrent streams for a recovery on a single node
```bash
curl -XPUT localhost:9200/_cluster/settings -d '{
"transient" :{
"indices.recovery.concurrent_streams" : 6
}
}';echo
```

# NODE

* get infos
```bash
curl 'http://localhost:9200/_nodes?pretty'
 curl 'http://localhost:9200/_nodes/stats?pretty'
 curl 'http://localhost:9200/_nodes/nodeId1,nodeId2/stats?pretty'
 curl 'http://localhost:9200/_cat/nodes?v=true'
```

* remove nodes from clusters gracefully
```bash
curl -XPUT localhost:9200/_cluster/settings -d '{
"transient" :{
"cluster.routing.allocation.exclude._ip" : "1.2.3.4"
}
}';echo
```

# INDICES
* list
```bash
curl -X GET 'http://localhost:9200/_cat/indices?v'
```

* delete
```bash
curl -X DELETE 'http://localhost:9200/examples'
```

* back up
```bash
curl -XPOST --header 'Content-Type: application/json' http://localhost:9200/_reindex -d '{
  "source": {
    "index1": "someexamples"
  },
  "dest": {
    "index2": "someexamples_copy"
  }
}'
```

* change replica count of an Indice
```bash
curl -XPUT --header 'Content-Type: application/json' 'http://localhost:9200/_index_name_/_settings' -d '{
  "index" : {
    "number_of_replicas" : 1
  }
}'
```

* change replica count of all indices
```bash
curl -X PUT "127.0.0.1:9200/.*/_settings" -H 'Content-Type: application/json' -d'{ "index" : { "number_of_replicas" : 0 } }'
```


* list all docs in an index
```bash
curl -X GET 'http://localhost:9200/elasticsearch_query_examples/_search'
```

## Debug Single Node Replica issues
```bash
rpm -q opensearch
   opensearch-2.19.0-1.x86_64
```

```bash
curl -s -XGET localhost:9200/_cat/indices | grep  yell
   yellow open top_queries-2025.02.22-91903 8dXcpNv9QTyciYQCVzKmkQ 1 1      4433 1522  11.8mb  11.8mb
   yellow open top_queries-2025.02.23-91904 CFNMBEGBSnieQ5oYsM3Q8g 1 1      7127 1513  16.1mb  16.1mb
```

```bash
curl -s -X GET "localhost:9200/_cluster/settings?include_defaults=true&flat_settings=true" | jq '.defaults."cluster.default_number_of_replicas"'
   "1"
```

* `vim /etc/opensearch/opensearch.yml`
  ```
  cluster.default_number_of_replicas: 0
  ```

```bash
systemctl restart opensearch
```

```bash
curl -s -X GET "localhost:9200/_cluster/settings?include_defaults=true&flat_settings=true" | jq '.defaults."cluster.default_number_of_replicas"'
  "0"
```

```bash
curl https://raw.githubusercontent.com/joe-speedboat/linux.scripts/refs/heads/master/shell/opensearch_template_replica_debug.sh | bash
```

```bash
curl -X PUT "127.0.0.1:9200/top_queries-*/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "number_of_replicas": 0
  }
}'
```

```bash
curl -s -XGET localhost:9200/_cat/indices | grep  top_quer
   green open top_queries-2025.02.22-91903 8dXcpNv9QTyciYQCVzKmkQ 1 0      4433 1522  11.8mb  11.8mb
   green open top_queries-2025.02.23-91904 CFNMBEGBSnieQ5oYsM3Q8g 1 0      7127 1513  16.1mb  16.1mb
```



# SHARDS
* list shards
```bash
 curl -XGET localhost:9200/_cat/shards?v
```

* show details of a shard
```bash
curl -X GET 'http://localhost:9200/_cat/shards/graylog_39?v'
```

* move shards from one node to another
```bash
curl -XPOST 'http://localhost:9200/_cluster/reroute' -d '{
"commands" : [
{
"move" :
{
"index" : "indexname", "shard" : 1,
"from_node" : "nodename", "to_node" : "nodename"
}
}
]
}';echo
```

* force the allocation of an unassigned shard with a reason
```bash
curl -XPOST 'http://localhost:9200/_cluster/reroute?explain' -d '{
"commands" : [ {
"allocate" : {
"index" : "indexname", "shard" : 0, "node" : "nodename"
}
} ]
}';echo
```

## Delete Unassigned Shards
```bash
curl http://localhost:9200/_cluster/health?pretty
curl -XGET localhost:9200/_cat/shards?h=index,shard,prirep,state,unassigned.reason
curl -XGET http://localhost:9200/_cat/shards | grep UNASSIGNED | awk {'print $1'} | xargs -i curl -XDELETE "http://localhost:9200/{}"
curl -XGET localhost:9200/_cat/shards?h=index,shard,prirep,state,unassigned.reason
curl http://localhost:9200/_cluster/health?pretty
```

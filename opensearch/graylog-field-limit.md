---
title: Graylog - Admin Access Notes
description: Graylog Data Node: Increase OpenSearch Field Limit to 5000
published: true
date: 2026-10-26T14:13:39.501Z
tags: opensearch, graylog
editor: markdown
dateCreated: 2026-06-30T10:38:51.218Z
---

# Graylog Data Node: Increase OpenSearch Field Limit to 5000

## Purpose

This runbook describes how to increase the OpenSearch index field limit used by Graylog Data Node from the default value to `5000`.

This procedure is useful when Graylog logs contain errors similar to:

```text
java.lang.IllegalArgumentException: Limit of total fields [1000] has been exceeded
```

OpenSearch defaults `index.mapping.total_fields.limit` to `1000`. This limit controls the maximum number of fields allowed in an index mapping. Increasing it is supported, but it should be treated carefully because excessive fields can increase memory usage and query cost.

## Scope

This procedure covers:

* Generating a Graylog Data Node client certificate in the Graylog UI
* Copying the certificate files to the Graylog node
* Running an OpenSearch health check
* Checking the current Graylog write indices
* Creating a default OpenSearch index template with `index.mapping.total_fields.limit = 5000`
* Rotating the affected Graylog index sets in the Web UI
* Verifying that the new active indices use the new limit

## Prerequisites

You need:

* SSH access to the Graylog node
* Graylog administrator access to the Web UI
* Access to the Graylog Data Node OpenSearch API, normally on port `9200`
* A generated Data Node client certificate with sufficient OpenSearch permissions, normally role `all_access`

Graylog supports generating a client certificate for Data Node access and using it with tools such as `curl` against the OpenSearch API.

## 1. Generate the client certificate in the Graylog UI

In the Graylog Web UI, go to:

```text
System -> Cluster Configuration -> Configuration -> Generate Client Certificate
```

Generate a client certificate with the following values:

```text
Principal: FQDN or hostname of the client/node used for curl
Role: all_access
Unencrypted private key: recommended for short-term emergency CLI use
```

Save the generated certificate data as three files:

```text
client-cert.crt
client-cert.key
ca.crt
```

## 2. Copy the certificate files to the Graylog target node

On the Graylog node:

```bash
mkdir -p /root/graylog-opensearch-client
chmod 700 /root/graylog-opensearch-client
cd /root/graylog-opensearch-client
```

Create the certificate file:

```bash
cat > client-cert.crt <<'EOF'
PASTE_CLIENT_CERTIFICATE_HERE
EOF
```

Create the private key file:

```bash
cat > client-cert.key <<'EOF'
PASTE_CLIENT_PRIVATE_KEY_HERE
EOF
```

Create the CA certificate file:

```bash
cat > ca.crt <<'EOF'
PASTE_CA_CERTIFICATE_HERE
EOF
```

Set restrictive permissions:

```bash
chmod 600 client-cert.crt client-cert.key ca.crt
```

## 3. Define shell variables

Adjust `OS_URL` if the Data Node hostname is different.

```bash
cd /root/graylog-opensearch-client

OS_URL="https://graylog1:9200"
CERT="client-cert.crt"
KEY="client-cert.key"
CACERT="ca.crt"

CURL="curl --cacert $CACERT --cert $CERT --key $KEY"
```

If certificate validation fails during incident handling, use this temporary variant:

```bash
CURL="curl -k --cert $CERT --key $KEY"
```

Do not keep `-k` as the long-term default because it disables TLS certificate verification.

## 4. Run OpenSearch health check

Run:

```bash
$CURL "$OS_URL/_cluster/health?pretty"
```

Expected result:

```json
{
  "cluster_name" : "datanode-cluster",
  "status" : "green",
  "timed_out" : false
}
```

A `green` status means the cluster is healthy from an allocation perspective. If the cluster is `yellow` or `red`, investigate OpenSearch/Data Node health before continuing.

## 5. Check current Graylog write indices

List the active Graylog write aliases:

```bash
$CURL "$OS_URL/_cat/aliases?v" | grep deflector
```

Example output:

```text
short_deflector                             short_170
long_deflector                              long_0
graylog_deflector                           graylog_7
gl-system-events_deflector                  gl-system-events_3
gl-events_deflector                         gl-events_0
```

In this example, the active write indices are:

```text
short_170
long_0
graylog_7
gl-system-events_3
gl-events_0
```

## 6. Verify the current field limit setting

Check all current deflector targets:

```bash
for index in $($CURL "$OS_URL/_cat/aliases?h=alias,index" | awk '/_deflector/ {print $2}' | sort -u); do
  echo "### $index"
  $CURL "$OS_URL/$index/_settings?pretty" | grep -A6 -B6 total_fields || echo "No explicit total_fields setting found"
done
```

If no explicit setting is shown, the index is using the OpenSearch default, normally `1000`.

## 7. Create an OpenSearch index template with field limit 5000

Create a template that applies to the known Graylog index prefixes:

```bash
cat > graylog-total-fields-limit.json <<'EOF'
{
  "index_patterns": [
    "short_*",
    "long_*",
    "graylog_*",
    "gl-system-events_*",
    "gl-events_*"
  ],
  "order": 1000,
  "settings": {
    "index.mapping.total_fields.limit": 5000
  }
}
EOF
```

Upload the template:

```bash
$CURL -X PUT "$OS_URL/_template/graylog-total-fields-limit" \
  -H 'Content-Type: application/json' \
  -d @graylog-total-fields-limit.json
```

Expected response:

```json
{"acknowledged":true}
```

Graylog supports adding custom OpenSearch mappings and settings through OpenSearch index templates. These custom templates are merged with Graylog’s own default template when new indices are created.

## 8. Verify the template

Run:

```bash
$CURL "$OS_URL/_template/graylog-total-fields-limit?pretty"
```

Expected content:

```json
{
  "graylog-total-fields-limit" : {
    "order" : 1000,
    "index_patterns" : [
      "short_*",
      "long_*",
      "graylog_*",
      "gl-system-events_*",
      "gl-events_*"
    ],
    "settings" : {
      "index" : {
        "mapping" : {
          "total_fields" : {
            "limit" : "5000"
          }
        }
      }
    }
  }
}
```

## 9. Rotate the affected Graylog index sets in the Web UI

The template applies only to newly created indices. Existing active indices are not changed automatically.

In the Graylog Web UI, go to:

```text
System -> Indices
```

For each affected index set:

```text
Open the index set -> Maintenance -> Rotate active write index
```

Rotate the relevant index sets, for example:

```text
short
long
graylog
gl-system-events
gl-events
```

Graylog documents manual index rotation through the index set detail page and the maintenance menu.

## 10. Verify the new active indices

After rotation, list the deflector aliases again:

```bash
$CURL "$OS_URL/_cat/aliases?v" | grep deflector
```

Example after rotation:

```text
short_deflector                             short_171
long_deflector                              long_1
graylog_deflector                           graylog_8
gl-system-events_deflector                  gl-system-events_4
gl-events_deflector                         gl-events_1
```

Now verify that the new active write indices have the field limit:

```bash
for index in $($CURL "$OS_URL/_cat/aliases?h=alias,index" | awk '/_deflector/ {print $2}' | sort -u); do
  echo "### $index"
  $CURL "$OS_URL/$index/_settings?pretty" | grep -A6 -B6 total_fields || echo "No total_fields setting found"
done
```

Expected result for each new active index:

```json
"total_fields" : {
  "limit" : "5000"
}
```

## 11. Monitor Graylog after rotation

Check whether the Graylog journal starts draining:

```bash
watch -n 10 'du -sh /var/lib/graylog-server/journal 2>/dev/null || du -sh /var/lib/graylog/journal 2>/dev/null'
```

Check Graylog server logs:

```bash
journalctl -u graylog-server -f
```

The previous error should disappear:

```text
Limit of total fields [1000] has been exceeded
```

If the error changes to:

```text
Limit of total fields [5000] has been exceeded
```

then the field explosion is still ongoing and the affected log source, extractor, or pipeline rule must be fixed.

## Notes

Increasing the field limit is an operational workaround. The better long-term fix is to reduce dynamic field creation, split unrelated log sources into separate index sets, and avoid parsing arbitrary nested JSON structures into indexed fields.

Common causes of excessive fields include:

```text
Kubernetes labels and annotations
Application JSON payloads with dynamic keys
HTTP headers parsed into individual fields
Firewall logs with highly variable field names
Pipeline rules creating dynamic field names
Extractors parsing too much nested data
```

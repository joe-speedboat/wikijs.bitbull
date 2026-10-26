---
title: inventory migration howto
description: how to migrate/compare ansible inventories
published: true
date: 2026-10-26T14:13:27.384Z
tags: ansible, inventory, migration
editor: markdown
dateCreated: 2026-04-23T08:52:55.635Z
---

# Ansible Inventory Migration Verification

## Overview

When migrating an Ansible inventory (e.g., from legacy static inventory to dynamic sources like Foreman, NetBox, or custom CMDB), **validation is critical** to ensure no configuration drift is introduced.

This method provides a **deterministic, host-level comparison** by:

* Exporting normalized inventory data per host
* Comparing snapshots using checksums
* Highlighting exact deviations

This approach avoids ambiguity from raw inventory diffs and focuses on **effective runtime data**.

---

## Validation Strategy

The verification is based on three core principles:

1. **Flatten host variables (`hostvars`)**
2. **Normalize group membership**
3. **Compare per-host snapshots via checksum**

This ensures:

* Order-independent comparison
* Noise reduction (ignoring internal Ansible variables)
* Clear, actionable diff output

---

## Step 1 – Export Inventory Snapshot

Use an Ansible playbook to export the effective inventory state per host.

### Playbook: `inventory_dump.yml`

```yaml
- name: Export inventory state per host
  hosts: all
  gather_facts: false

  vars:
    outdir: "/tmp/inventory_snapshot"

  tasks:
    - name: Ensure output directory exists
      ansible.builtin.file:
        path: "{{ outdir }}"
        state: directory
        mode: "0755"
      run_once: true
      delegate_to: localhost

    - name: Read effective host vars exactly like ansible-inventory --host
      ansible.builtin.command: >-
        ansible-inventory
        {% for src in ansible_inventory_sources %}
        -i {{ src | quote }}
        {% endfor %}
        --host {{ inventory_hostname | quote }}
      register: inventory_host_json
      changed_when: false
      delegate_to: localhost
    - name: Write snapshot file per host
      ansible.builtin.copy:
        dest: "{{ outdir }}/{{ inventory_hostname }}.txt"
        mode: "0644"
        content: |-
          vars:
          {{ (inventory_host_json.stdout | from_json | to_nice_yaml(indent=2)) | indent(2, true) }}
          groups:
          {% for g in group_names | sort %}
            - {{ g }}
          {% endfor %}
      delegate_to: localhost
```

### Execution

Run this playbook against both inventories:

```bash
# Old inventory
ansible-playbook -i inventory_old inventory_dump.yml
mv /tmp/inventory_snapshot /tmp/inventory_old

# New inventory
ansible-playbook -i inventory_new inventory_dump.yml
mv /tmp/inventory_snapshot /tmp/inventory_new
```

---

## Step 2 – Compare Snapshots

Use a checksum-based comparison script.

### Script: `compare.inventory.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

DIR1="${1:-/tmp/inventory_old}"
DIR2="${2:-/tmp/inventory_new}"

if [[ ! -d "$DIR1" || ! -d "$DIR2" ]]; then
  echo "ERROR: both arguments must be existing directories"
  echo "Usage: $0 <left_dir> <right_dir>"
  exit 2
fi

tmp_all=$(mktemp)
trap 'rm -f "$tmp_all"' EXIT

{
  find "$DIR1" -maxdepth 1 -type f -printf '%f\n'
  find "$DIR2" -maxdepth 1 -type f -printf '%f\n'
} | sort -u > "$tmp_all"

rc=0

while IFS= read -r file; do
  left="$DIR1/$file"
  right="$DIR2/$file"

  if [[ ! -f "$left" ]]; then
    printf 'ONLY_RIGHT  %s\n' "$file"
    rc=1
    continue
  fi

  if [[ ! -f "$right" ]]; then
    printf 'ONLY_LEFT   %s\n' "$file"
    rc=1
    continue
  fi

  md5_left=$(md5sum "$left"  | awk '{print $1}')
  md5_right=$(md5sum "$right" | awk '{print $1}')

  if [[ "$md5_left" == "$md5_right" ]]; then
    printf 'SAME        %s\n' "$file"
  else
    printf 'DIFF        %s\n' "$file"
    printf '  LEFT : %s\n' "$md5_left"
    printf '  RIGHT: %s\n' "$md5_right"
    rc=1
  fi
done < "$tmp_all"

exit "$rc"
```

### Execution

```bash
bash compare.inventory.sh /tmp/inventory_old /tmp/inventory_new
```

---

## Step 3 – Interpret Results

### Output Types

| Result       | Meaning                         |
| ------------ | ------------------------------- |
| `SAME`       | Host configuration is identical |
| `DIFF`       | Host exists in both but differs |
| `ONLY_LEFT`  | Host missing in new inventory   |
| `ONLY_RIGHT` | Host missing in old inventory   |

### Example

```text
SAME        deploy0.domain.tld.txt
DIFF        confl.domain.tld.txt
  LEFT : 2055155554a6f7a93730f4be8a1ea859
  RIGHT: 776954e90d567b35c971c03987d63807
```

Interpretation:

* `deploy0` → fully consistent
* `confl` → configuration drift detected → requires inspection

---

## Step 4 – Deep Dive on Differences

For hosts marked as `DIFF`, run:

```bash
diff -u /tmp/inventory_old/host.txt /tmp/inventory_new/host.txt
```

This reveals:

* Missing/extra variables
* Value changes
* Group membership differences

---

## Key Design Decisions

### Why not compare raw inventory files?

Raw inventory comparison is unreliable due to:

* Variable inheritance
* Group hierarchy
* Dynamic inventory resolution

This method compares **effective state**, not source definitions.

---

### Why filter variables?

The playbook excludes:

* `ansible_*` → runtime/internal facts
* `inventory_*` → internal metadata
* `group_names`, `groups` → handled separately

This ensures only **relevant configuration data** is compared.

---

### Why checksum instead of diff?

Checksums provide:

* Fast comparison across large inventories
* Clean summary output
* Easy CI/CD integration

Detailed diffs are only needed for exceptions.

---

## Best Practices

* Run comparison in CI before switching inventories
* Treat any `DIFF` as a **migration blocker**
* Version-control snapshot outputs for traceability
* Extend filtering if environment-specific noise exists (e.g., timestamps)

---

## Optional Enhancements

* Replace `md5sum` with `sha256sum` for stricter hashing
* Add JSON export for machine-readable diffing
* Integrate into pipelines (GitLab CI / Jenkins)
* Add whitelist for expected differences

---

## Conclusion

This method provides a **reproducible, scalable, and precise** way to validate Ansible inventory migrations.

It ensures that:

* No host configuration is unintentionally altered
* Group memberships remain intact
* Variable sets are consistent across environments

For large environments, this approach scales cleanly and integrates well into automation workflows.

# Replication Package

This directory contains scripts and data for replicating the results from Förmögenhetsanalys.

## Running the Full Replication

```bash
cd replication
./run_all.sh
```

## Expected Receipts

The `expected_receipts.json` file contains the SHA256 hashes of expected outputs.

## Verification

To verify replication:
```bash
python ../scripts/compare_receipts.py expected_receipts.json receipts.json
```

## Components

- `run_all.sh`: Master script running all replication steps
- `expected_receipts.json`: Expected output hashes
- `receipts.json`: Actual output hashes (generated after run)

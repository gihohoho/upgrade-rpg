# Master Data Nullable Fields

## v087 nullable skill proc rate fix

`skills.baseProcRate` from the generated seed can be missing/null for skills that do not use a base activation probability.

Previously the local seed importer converted a missing `baseProcRate` into `0`, so the API returned:

```json
{ "code": "lightsabre", "procRate": 0 }
```

The seed parity checker correctly reported this as different from the seed source:

```json
{ "code": "lightsabre", "baseProcRate": null }
```

From v087 onward, `skills.proc_rate` is nullable and the seed importer preserves `null` values. This keeps the DB/API master data aligned with the extracted JS seed data.

Run after applying this version:

```bash
# Location: backend folder with the virtual environment activated
python scripts/setup_dev_db.py --reset --seed --verify
python scripts/check_master_data_parity.py
```

# Database Backups Directory

This directory stores PostgreSQL database backups.

## Backup Files

All `.sql` and `.sql.gz` files are automatically ignored by Git for security and size reasons.

## Usage

```bash
# Create backup
make backup

# List backups
make backup-list

# Restore from backup
make restore FILE=backups/fleet_management_20250930_120000.sql.gz
```

## Retention Policy

By default, the system keeps the last 10 backups. Older backups are automatically pruned.

Configure via environment variable:
```bash
export MAX_BACKUPS=20
```

## Manual Backup/Restore

See `scripts/backup.sh` and `scripts/restore.sh` for direct script usage.

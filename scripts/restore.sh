#!/bin/bash
set -e

BACKUP_DIR="backups"

source_env() {
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    fi
}

show_help() {
    cat << EOF
Fleet Management Database Restore Script

Usage: $0 [OPTIONS] BACKUP_FILE

ARGUMENTS:
    BACKUP_FILE         Path to backup file (required)

OPTIONS:
    -h, --help          Show this help message
    -d, --docker        Restore to Docker container
    -l, --local         Restore to local PostgreSQL (default)
    -y, --yes           Skip confirmation prompt
    -v, --verbose       Verbose output
    --dry-run           Show what would be done without executing

ENVIRONMENT VARIABLES:
    DATABASE_URL        PostgreSQL connection string (required for local)
    POSTGRES_USER       PostgreSQL username (default: fleetuser)
    POSTGRES_DB         PostgreSQL database name (default: fleet_management)

EXAMPLES:
    # Restore to Docker container
    $0 --docker backups/fleet_management_20250930_120000.sql.gz

    # Restore to local PostgreSQL
    $0 --local backups/fleet_management_20250930_120000.sql.gz

    # Skip confirmation
    $0 --yes --docker backups/latest.sql.gz

    # Dry run
    $0 --dry-run backups/fleet_management_20250930_120000.sql.gz

NOTES:
    ⚠️  WARNING: This will REPLACE ALL DATA in the target database!
    ⚠️  Make sure to backup current data before restoring!

EOF
}

parse_database_url() {
    if [ -z "$DATABASE_URL" ]; then
        echo "ERROR: DATABASE_URL not set"
        exit 1
    fi
    
    DB_USER=$(echo "$DATABASE_URL" | sed -n 's|.*://\([^:]*\):.*|\1|p')
    DB_PASS=$(echo "$DATABASE_URL" | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')
    DB_HOST=$(echo "$DATABASE_URL" | sed -n 's|.*@\([^:]*\):.*|\1|p')
    DB_PORT=$(echo "$DATABASE_URL" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
    DB_NAME=$(echo "$DATABASE_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')
}

check_backup_file() {
    if [ ! -f "$BACKUP_FILE" ]; then
        echo "ERROR: Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "Backup file: $BACKUP_FILE ($BACKUP_SIZE)"
    
    if [[ "$BACKUP_FILE" == *.gz ]]; then
        IS_COMPRESSED=true
        echo "Format: Compressed (gzip)"
    else
        IS_COMPRESSED=false
        echo "Format: Uncompressed"
    fi
}

confirm_restore() {
    if [ "$SKIP_CONFIRM" = true ]; then
        return 0
    fi
    
    echo ""
    echo "⚠️  WARNING: This will REPLACE ALL DATA in the database!"
    echo "⚠️  Current database: $DB_NAME"
    echo "⚠️  All existing data will be lost!"
    echo ""
    read -p "Are you sure you want to continue? [y/N] " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Restore cancelled"
        exit 0
    fi
}

restore_docker() {
    echo "📥 Restoring database to Docker container..."
    
    CONTAINER_NAME="fleet_management_db"
    POSTGRES_USER=${POSTGRES_USER:-fleetuser}
    POSTGRES_DB=${POSTGRES_DB:-fleet_management}
    
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        echo "ERROR: Container $CONTAINER_NAME is not running"
        echo "Start it with: docker compose up -d"
        exit 1
    fi
    
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would restore to Docker container: $CONTAINER_NAME"
        echo "[DRY RUN] Database: $POSTGRES_DB"
        echo "[DRY RUN] User: $POSTGRES_USER"
        return 0
    fi
    
    DB_NAME="$POSTGRES_DB"
    confirm_restore
    
    echo "Dropping existing database..."
    docker exec "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -c "DROP DATABASE IF EXISTS $POSTGRES_DB;" postgres
    
    echo "Creating fresh database..."
    docker exec "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -c "CREATE DATABASE $POSTGRES_DB;" postgres
    
    if [ "$IS_COMPRESSED" = true ]; then
        echo "Restoring from compressed backup..."
        gunzip -c "$BACKUP_FILE" | docker exec -i "$CONTAINER_NAME" psql -U "$POSTGRES_USER" "$POSTGRES_DB"
    else
        echo "Restoring from uncompressed backup..."
        cat "$BACKUP_FILE" | docker exec -i "$CONTAINER_NAME" psql -U "$POSTGRES_USER" "$POSTGRES_DB"
    fi
    
    echo "✅ Database restored successfully"
}

restore_local() {
    echo "📥 Restoring database to local PostgreSQL..."
    
    source_env
    parse_database_url
    
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would restore to local PostgreSQL"
        echo "[DRY RUN] Host: $DB_HOST:$DB_PORT"
        echo "[DRY RUN] Database: $DB_NAME"
        echo "[DRY RUN] User: $DB_USER"
        return 0
    fi
    
    confirm_restore
    
    export PGPASSWORD="$DB_PASS"
    
    echo "Dropping existing database..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "DROP DATABASE IF EXISTS $DB_NAME;" postgres
    
    echo "Creating fresh database..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;" postgres
    
    if [ "$IS_COMPRESSED" = true ]; then
        echo "Restoring from compressed backup..."
        gunzip -c "$BACKUP_FILE" | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME"
    else
        echo "Restoring from uncompressed backup..."
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" < "$BACKUP_FILE"
    fi
    
    unset PGPASSWORD
    
    echo "✅ Database restored successfully"
}

MODE="docker"
SKIP_CONFIRM=false
DRY_RUN=false
VERBOSE=false
BACKUP_FILE=""
IS_COMPRESSED=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--docker)
            MODE="docker"
            shift
            ;;
        -l|--local)
            MODE="local"
            shift
            ;;
        -y|--yes)
            SKIP_CONFIRM=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            set -x
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
        *)
            BACKUP_FILE="$1"
            shift
            ;;
    esac
done

if [ -z "$BACKUP_FILE" ]; then
    echo "ERROR: No backup file specified"
    echo ""
    show_help
    exit 1
fi

echo "======================================"
echo "Fleet Management Database Restore"
echo "======================================"
echo "Mode: $MODE"
echo "Dry run: $DRY_RUN"
echo "======================================"
echo ""

check_backup_file

case $MODE in
    docker)
        restore_docker
        ;;
    local)
        restore_local
        ;;
esac

if [ "$DRY_RUN" = false ]; then
    echo ""
    echo "======================================"
    echo "✅ Restore completed successfully!"
    echo "======================================"
fi

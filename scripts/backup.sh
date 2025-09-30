#!/bin/bash
set -e

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DEFAULT_BACKUP_FILE="${BACKUP_DIR}/fleet_management_${TIMESTAMP}.sql.gz"
MAX_BACKUPS=${MAX_BACKUPS:-10}

source_env() {
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    fi
}

show_help() {
    cat << EOF
Fleet Management Database Backup Script

Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help          Show this help message
    -f, --file FILE     Custom backup filename (default: fleet_management_TIMESTAMP.sql.gz)
    -d, --docker        Backup from Docker container
    -l, --local         Backup from local PostgreSQL (default)
    -n, --no-compress   Don't compress the backup
    -v, --verbose       Verbose output

ENVIRONMENT VARIABLES:
    DATABASE_URL        PostgreSQL connection string (required for local)
    POSTGRES_USER       PostgreSQL username (default: fleetuser)
    POSTGRES_DB         PostgreSQL database name (default: fleet_management)
    MAX_BACKUPS         Maximum number of backups to keep (default: 10)

EXAMPLES:
    # Backup from Docker container
    $0 --docker

    # Backup from local PostgreSQL
    $0 --local

    # Custom filename
    $0 --file my_backup.sql.gz

    # Without compression
    $0 --no-compress

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

backup_docker() {
    echo "📦 Backing up database from Docker container..."
    
    CONTAINER_NAME="fleet_management_db"
    POSTGRES_USER=${POSTGRES_USER:-fleetuser}
    POSTGRES_DB=${POSTGRES_DB:-fleet_management}
    
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        echo "ERROR: Container $CONTAINER_NAME is not running"
        echo "Start it with: docker compose up -d"
        exit 1
    fi
    
    if [ "$COMPRESS" = true ]; then
        echo "Creating compressed backup: $BACKUP_FILE"
        docker exec "$CONTAINER_NAME" pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$BACKUP_FILE"
    else
        BACKUP_FILE="${BACKUP_FILE%.gz}"
        echo "Creating uncompressed backup: $BACKUP_FILE"
        docker exec "$CONTAINER_NAME" pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_FILE"
    fi
    
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "✅ Backup created successfully: $BACKUP_FILE ($BACKUP_SIZE)"
}

backup_local() {
    echo "📦 Backing up database from local PostgreSQL..."
    
    source_env
    parse_database_url
    
    export PGPASSWORD="$DB_PASS"
    
    if [ "$COMPRESS" = true ]; then
        echo "Creating compressed backup: $BACKUP_FILE"
        pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"
    else
        BACKUP_FILE="${BACKUP_FILE%.gz}"
        echo "Creating uncompressed backup: $BACKUP_FILE"
        pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"
    fi
    
    unset PGPASSWORD
    
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "✅ Backup created successfully: $BACKUP_FILE ($BACKUP_SIZE)"
}

prune_old_backups() {
    echo "🗑️  Checking for old backups (keeping last $MAX_BACKUPS)..."
    
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.sql* 2>/dev/null | wc -l)
    
    if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
        DELETE_COUNT=$((BACKUP_COUNT - MAX_BACKUPS))
        echo "Removing $DELETE_COUNT old backup(s)..."
        ls -1t "$BACKUP_DIR"/*.sql* | tail -n "$DELETE_COUNT" | xargs rm -f
        echo "✅ Cleanup complete"
    else
        echo "No cleanup needed ($BACKUP_COUNT backups found)"
    fi
}

MODE="docker"
COMPRESS=true
VERBOSE=false
BACKUP_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--file)
            BACKUP_FILE="$2"
            shift 2
            ;;
        -d|--docker)
            MODE="docker"
            shift
            ;;
        -l|--local)
            MODE="local"
            shift
            ;;
        -n|--no-compress)
            COMPRESS=false
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            set -x
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

mkdir -p "$BACKUP_DIR"

if [ -z "$BACKUP_FILE" ]; then
    BACKUP_FILE="$DEFAULT_BACKUP_FILE"
fi

if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
fi

echo "======================================"
echo "Fleet Management Database Backup"
echo "======================================"
echo "Mode: $MODE"
echo "Compression: $COMPRESS"
echo "Backup file: $BACKUP_FILE"
echo "======================================"
echo ""

case $MODE in
    docker)
        backup_docker
        ;;
    local)
        backup_local
        ;;
esac

prune_old_backups

echo ""
echo "======================================"
echo "📊 Backup Summary"
echo "======================================"
ls -lh "$BACKUP_DIR" | tail -n +2 | awk '{print $9, "("$5")"}'
echo "======================================"
echo "✅ Backup completed successfully!"

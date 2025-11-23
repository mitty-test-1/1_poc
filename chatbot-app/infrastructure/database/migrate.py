#!/usr/bin/env python3
"""
Database Migration Runner for Chatbot Application

This script manages database schema migrations for the chatbot application.
It supports running migrations up (apply changes) and down (rollback changes).

Usage:
    python migrate.py up [version]     # Run all migrations or specific version
    python migrate.py down [version]   # Rollback all migrations or specific version
    python migrate.py status           # Show migration status
    python migrate.py create <name>    # Create new migration files

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (default: postgresql://postgres:password@localhost:5432/chatbot)
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
import argparse
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MigrationRunner:
    def __init__(self, database_url=None):
        self.database_url = database_url or os.getenv(
            'DATABASE_URL',
            'postgresql://postgres:password@localhost:5432/chatbot'
        )
        self.migrations_dir = Path(__file__).parent / 'migrations'

    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.database_url)

    def ensure_migration_table(self):
        """Ensure migration tracking table exists"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(10) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    checksum VARCHAR(64)
                )
                """)
                conn.commit()

    def get_applied_migrations(self):
        """Get list of applied migrations"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT version, name, applied_at FROM schema_migrations ORDER BY version")
                return cursor.fetchall()

    def get_available_migrations(self):
        """Get list of available migration files"""
        migrations = []
        if self.migrations_dir.exists():
            for file in sorted(self.migrations_dir.glob('*.sql')):
                if not file.name.endswith('_down.sql'):
                    version = file.name.split('_')[0]
                    name = '_'.join(file.name.split('_')[1:]).replace('.sql', '')
                    migrations.append({
                        'version': version,
                        'name': name,
                        'up_file': file,
                        'down_file': self.migrations_dir / f"{version}_{name}_down.sql"
                    })
        return migrations

    def calculate_checksum(self, file_path):
        """Calculate checksum of migration file"""
        import hashlib
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def run_migration_up(self, migration):
        """Run a migration up"""
        up_file = migration['up_file']
        if not up_file.exists():
            raise FileNotFoundError(f"Migration file {up_file} not found")

        logger.info(f"Running migration {migration['version']}: {migration['name']}")

        # Read migration SQL
        with open(up_file, 'r') as f:
            sql = f.read()

        # Execute migration
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)

                # Record migration as applied
                checksum = self.calculate_checksum(up_file)
                cursor.execute("""
                INSERT INTO schema_migrations (version, name, checksum)
                VALUES (%s, %s, %s)
                """, (migration['version'], migration['name'], checksum))

                conn.commit()

        logger.info(f"Migration {migration['version']} applied successfully")

    def run_migration_down(self, migration):
        """Run a migration down"""
        down_file = migration['down_file']
        if not down_file.exists():
            raise FileNotFoundError(f"Down migration file {down_file} not found")

        logger.info(f"Rolling back migration {migration['version']}: {migration['name']}")

        # Read down migration SQL
        with open(down_file, 'r') as f:
            sql = f.read()

        # Execute rollback
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)

                # Remove migration record
                cursor.execute("DELETE FROM schema_migrations WHERE version = %s", (migration['version'],))

                conn.commit()

        logger.info(f"Migration {migration['version']} rolled back successfully")

    def migrate_up(self, target_version=None):
        """Run migrations up to target version"""
        self.ensure_migration_table()

        applied = {m['version'] for m in self.get_applied_migrations()}
        available = self.get_available_migrations()

        to_apply = []
        for migration in available:
            if migration['version'] not in applied:
                to_apply.append(migration)
                if target_version and migration['version'] == target_version:
                    break

        if not to_apply:
            logger.info("No migrations to apply")
            return

        for migration in to_apply:
            self.run_migration_up(migration)

        logger.info(f"Applied {len(to_apply)} migration(s)")

    def migrate_down(self, target_version=None):
        """Rollback migrations down to target version"""
        applied = self.get_applied_migrations()
        if not applied:
            logger.info("No migrations to rollback")
            return

        available = {m['version']: m for m in self.get_available_migrations()}

        to_rollback = []
        for migration in reversed(applied):
            if migration['version'] in available:
                to_rollback.append({
                    'version': migration['version'],
                    'name': migration['name'],
                    'up_file': available[migration['version']]['up_file'],
                    'down_file': available[migration['version']]['down_file']
                })
                if target_version and migration['version'] == target_version:
                    break

        if not to_rollback:
            logger.info("No migrations to rollback")
            return

        for migration in to_rollback:
            self.run_migration_down(migration)

        logger.info(f"Rolled back {len(to_rollback)} migration(s)")

    def show_status(self):
        """Show migration status"""
        self.ensure_migration_table()

        applied = {m['version']: m for m in self.get_applied_migrations()}
        available = self.get_available_migrations()

        print("Migration Status:")
        print("=" * 50)

        for migration in available:
            version = migration['version']
            status = "APPLIED" if version in applied else "PENDING"
            applied_at = applied[version]['applied_at'] if version in applied else ""
            print("12")

    def create_migration(self, name):
        """Create new migration files"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        version = f"{timestamp}"

        up_file = self.migrations_dir / f"{version}_{name}.sql"
        down_file = self.migrations_dir / f"{version}_{name}_down.sql"

        # Create up migration template
        up_content = f"""-- Migration: {name}
-- Version: {version}
-- Date: {datetime.now().strftime('%Y-%m-%d')}
-- Description: {name}

-- Add your migration SQL here

-- Migration completed successfully
"""

        # Create down migration template
        down_content = f"""-- Rollback Migration: {name}
-- Version: {version} (down)
-- Date: {datetime.now().strftime('%Y-%m-%d')}
-- Description: Rollback {name}

-- Add your rollback SQL here

-- Migration rollback completed successfully
"""

        with open(up_file, 'w') as f:
            f.write(up_content)

        with open(down_file, 'w') as f:
            f.write(down_content)

        logger.info(f"Created migration files:")
        logger.info(f"  {up_file}")
        logger.info(f"  {down_file}")

def main():
    parser = argparse.ArgumentParser(description='Database Migration Runner')
    parser.add_argument('command', choices=['up', 'down', 'status', 'create'],
                       help='Migration command')
    parser.add_argument('argument', nargs='?', help='Version for up/down or name for create')
    parser.add_argument('--database-url', help='Database connection URL')

    args = parser.parse_args()

    runner = MigrationRunner(args.database_url)

    try:
        if args.command == 'up':
            runner.migrate_up(args.argument)
        elif args.command == 'down':
            runner.migrate_down(args.argument)
        elif args.command == 'status':
            runner.show_status()
        elif args.command == 'create':
            if not args.argument:
                parser.error("Migration name is required for 'create' command")
            runner.create_migration(args.argument)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
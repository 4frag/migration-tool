'''
Database Migration Tool - Минимально рабочий вариант.

Синхронизирует целевую БД по образцу источника.
'''

import sys

from src.database_syncer import DatabaseSyncer
from src.utils import format_dsn


AVAILABLE_ARGS = 3

def main() -> None:
    '''Точка входа - можно вызвать вручную или через CLI.'''

    if len(sys.argv) < AVAILABLE_ARGS:
        print('Usage: python main.py <source_dsn> <target_dsn> [--apply]')
        print('\nExamples:')
        print("  python main.py 'postgresql://user:pass@localhost/test' 'postgresql://user:pass@localhost/prod'")
        print("  python main.py 'postgresql://user:pass@localhost/test' 'postgresql://user:pass@localhost/prod' --apply")
        sys.exit(1)

    source_dsn = sys.argv[1]
    target_dsn = sys.argv[2]
    apply_changes = '--apply' in sys.argv

    source_dsn = format_dsn(source_dsn)
    target_dsn = format_dsn(target_dsn)

    success = DatabaseSyncer.sync_databases(source_dsn, target_dsn, dry_run=not apply_changes)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

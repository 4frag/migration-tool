import logging

from alembic.autogenerate import api
from alembic.migration import MigrationContext
from alembic.operations import MigrateOperation, Operations
from alembic.operations.ops import DropColumnOp, DropTableOp
from sqlalchemy import Connection, MetaData, create_engine, inspect, text
from sqlalchemy.schema import SchemaItem


# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def include_object(
    _obj: SchemaItem,
    name: str,
    type_: str,
    _reflected: bool,
    _compare_to: SchemaItem | None
) -> bool:
    """
    Типизированный фильтр объектов для Alembic.

    Игнорирует любые таблицы, начинающиеся с 'bak_'.
    """
    return not (type_ == 'table' and name.startswith('bak_'))

class DatabaseSyncer:
    @classmethod
    def sync_databases(cls, source_dsn: str, target_dsn: str, dry_run: bool = True) -> bool:
        logger.info('=' * 60)
        logger.info('DATABASE MIGRATION TOOL')
        logger.info('=' * 60)

        try:
            source_engine = create_engine(source_dsn, connect_args={'connect_timeout': 1})
            target_engine = create_engine(target_dsn, connect_args={'connect_timeout': 1})

            # Шаг 1: Отражение эталона
            source_metadata = MetaData()
            source_metadata.reflect(bind=source_engine)
            logger.info('✓ Source reflected (%d tables)', len(source_metadata.tables))

            # Шаг 2: Генерация плана изменений
            with target_engine.connect() as conn:
                ctx = MigrationContext.configure(
                    conn,
                    opts={'include_object': include_object}
                )
                migration_script = api.produce_migrations(ctx, source_metadata)

            if not migration_script.upgrade_ops or not migration_script.upgrade_ops.ops:
                logger.info('✓ Databases are already in sync.')
                return True

            # Шаг 3: Показ операций
            cls._print_ops(migration_script.upgrade_ops.ops)

            if dry_run:
                logger.info('✓ Dry run mode: no changes applied.')
                return True

            # Шаг 4: Применение с транзакцией  # noqa: RUF003
            with target_engine.begin() as conn:
                # Настраиваем контекст для выполнения
                ctx = MigrationContext.configure(
                    conn,
                    opts={'include_object': include_object}
                )
                op = Operations(ctx)
                cls._apply_operations(migration_script.upgrade_ops.ops, conn, op)
        except Exception:
            logger.exception('✗ Migration failed')
            return False
        else:
            logger.info('✓ Migration finished successfully!')
            return True

    @classmethod
    def _apply_operations(
        cls,
        ops_list: list[MigrateOperation],
        conn: Connection,
        op: Operations
    ) -> None:
        for operation in ops_list:
            if hasattr(operation, 'ops'):
                cls._apply_operations(operation.ops, conn, op)
                continue

            # Безопасный бэкап
            if isinstance(operation, DropColumnOp):
                confirm = input(f'⚠️ Confirm dropping column {operation.column_name} from table {operation.table_name}? (y/n): ')
                if confirm.lower() != 'y':
                    raise ValueError('Operation cancelled by user.')  # noqa: TRY003
                cls._backup_column(conn, operation)
            elif isinstance(operation, DropTableOp):
                confirm = input(f'⚠️ Confirm dropping table {operation.table_name}? (y/n): ')
                if confirm.lower() != 'y':
                    raise ValueError('Operation cancelled by user.')  # noqa: TRY003
                cls._backup_table(conn, operation)
            try:
                op.invoke(operation)
                logger.info('✓ Applied: %s', operation)
            except Exception:
                logger.exception('✗ Failed on operation: %s', operation)
                raise

    @classmethod
    def _backup_column(cls, conn: Connection, operation: DropColumnOp) -> None:
        '''Динамически определяет PK и делает бэкап колонки.'''
        table_name = operation.table_name
        col_name = operation.column_name

        # Используем инспектор для поиска Primary Key
        inspector = inspect(conn)
        pk_info = inspector.get_pk_constraint(table_name)
        pk_cols = pk_info.get('constrained_columns', [])

        # Формируем список колонок для сохранения (PK + удаляемая колонка)
        pk_str = ', '.join([f'"{c}"' for c in pk_cols])
        select_cols = f'{pk_str}, "{col_name}"' if pk_cols else '*'

        backup_name = f'bak_{table_name}_{col_name}'
        logger.info('⚠️  Backing up column %s to %s (PK: %s)...', col_name, backup_name, pk_cols or 'None')

        conn.execute(text(f'DROP TABLE IF EXISTS "{backup_name}"'))
        conn.execute(text(f'CREATE TABLE "{backup_name}" AS SELECT {select_cols} FROM "{table_name}"'))  # noqa: S608

    @classmethod
    def _backup_table(cls, conn: Connection, operation: DropTableOp) -> None:
        backup_name = f'bak_{operation.table_name}'
        logger.info('⚠️  Backing up entire table to %s...', backup_name)
        conn.execute(text(f'DROP TABLE IF EXISTS "{backup_name}"'))
        conn.execute(text(f'CREATE TABLE "{backup_name}" AS SELECT * FROM "{operation.table_name}"'))  # noqa: S608

    @classmethod
    def _print_ops(cls, ops: list[MigrateOperation], indent: int = 0) -> None:
        for op in ops:
            if hasattr(op, 'ops'):
                logger.info('%s%s:', '  ' * indent, type(op).__name__)
                cls._print_ops(op.ops, indent + 1)
            else:
                logger.info('%s- %s', '  ' * indent, op)

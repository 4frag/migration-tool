def format_dsn(dsn: str) -> str:
    '''Форматирует DSN для вывода, скрывая пароль.'''
    return dsn.replace('postgresql://', 'postgresql+psycopg2://')

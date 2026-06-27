import os
import time
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from grid.database import Database
from grid.data.exceptions import DataException
from grid.data import generation, emissions, pricing, demand

ERROR_REPORTING_THRESHOLD = int(os.environ.get('ERROR_REPORTING_THRESHOLD', '0'))


def run_action(label: str, callback, database: Database) -> None:
    print(label, end='', flush=True)
    start = time.monotonic()

    try:
        callback(database)
        print('OK', end='')
        database.clear_errors(label)
    except DataException as e:
        error = str(e)
        print(f'ERROR: {error}', end='')

        count = database.get_error_count(label, error)
        if count >= ERROR_REPORTING_THRESHOLD and ERROR_REPORTING_THRESHOLD > 0:
            database.clear_errors(label)
            print(f'\n{label.strip()} {error}', file=sys.stderr)

    elapsed = time.monotonic() - start
    print(f' ({elapsed:.3f} seconds)')


def main():
    database = Database()

    run_action('Updating generation… ', lambda db: generation.update(db), database)
    run_action('Updating emissions…  ', lambda db: emissions.update(db), database)
    run_action('Updating pricing…    ', lambda db: pricing.update(db), database)
    run_action('Updating demand…     ', lambda db: demand.update(db), database)
    run_action('Finishing update…    ', lambda db: db.finish_update(), database)


if __name__ == '__main__':
    main()

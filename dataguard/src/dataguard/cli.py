import click
from pathlib import Path
from dataguard.pipeline import run_pipeline

@click.command()
@click.option('--input-file', required=True, type=click.Path(exists=True), help='Path to the dataset CSV file.')
@click.option('--run-name', required=True, type=str, help='Name of the quality run.')
def main(input_file, run_name):
    click.echo(f"Starting DataGuard for {input_file} as run '{run_name}'")
    schema = {'order_id': 'int64', 'customer_id': 'int64', 'unit_price': 'float64', 'quantity': 'int64'}
    rules = {'unit_price': (0.01, 1000.0), 'quantity': (1, 100)}
    run_pipeline(str(input_file), run_name, schema=schema, rules=rules)
    click.echo("DataGuard finished processing.")

if __name__ == '__main__':
    main()
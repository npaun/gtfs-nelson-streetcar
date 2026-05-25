#!/usr/bin/env python3
import csv
import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import Any


Context = dict[str, str]
GTFS = dict[str, list[Any]]


def load_gtfs(src: Path) -> GTFS:
    gtfs = {}
    for file in Path(src).glob('*.txt'):
        table = gtfs[file.stem] = []
        with file.open() as fp:
            rd = csv.DictReader(file.open())
            for row in rd:
                table.append(row)

    return gtfs


def expand_vars(gtfs: GTFS, ctx: Context) -> None:
    for name, table in gtfs.items():
        for row in table:
            for k, v in row.items():
                row[k] = v.format(**ctx)


def serialize_gtfs(gtfs: GTFS, dest: Path) -> None:
    for name, table in gtfs.items():
        with Path(dest / f"{name}.txt").open('w') as fp:
            field_names = table[0].keys()
            wr = csv.DictWriter(fp, field_names)
            wr.writeheader()
            for row in table:
                wr.writerow(row)


def get_ctx(gtfs: GTFS) -> Context:
    return dict(
            start_date=min(row['start_date'] for row in gtfs['calendar']),
            end_date=max(row['end_date'] for row in gtfs['calendar']),
            now=datetime.now().strftime('%Y%m%d00')
    )


def transform(src: Path, dest: Path) -> None: 
    gtfs = load_gtfs(src)
    ctx = get_ctx(gtfs)
    print(ctx)
    expand_vars(gtfs, ctx)
    shutil.rmtree(dest)
    dest.mkdir()
    serialize_gtfs(gtfs, dest)



def main():
    cmd = argparse.ArgumentParser()
    cmd.add_argument('src', type=Path)
    cmd.add_argument('dest', type=Path)
    args = cmd.parse_args()
    transform(args.src, args.dest)


if __name__ == '__main__':
    main()





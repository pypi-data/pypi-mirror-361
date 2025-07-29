# -*- coding: utf-8 -*-
# readdata.py

import os

import pandas as pd


def readdata(fn, q_range=None, read_csv_args=None, print_filename=True):
    """Read a datafile pandas Dataframe
    extract a file_name
    select q-range: q_min <= q <= q_max
    """
    if print_filename:
        print(f"Reading file '{fn}'")
    if read_csv_args is None:
        read_csv_args = dict()
    if "sep" not in read_csv_args:
        read_csv_args.update(sep=r"\s+")
    if "names" not in read_csv_args:
        read_csv_args.update(names=("q", "I", "e"))
    if "index_col" not in read_csv_args:
        read_csv_args.update(index_col=False)
    # print("f_read_data, read_csv_args:", read_csv_args) # for debugging

    _, file_ext = os.path.splitext(fn)
    if file_ext.lower() == ".pdh":  # for PDH files
        nrows = pd.read_csv(
            fn,
            skiprows=2,
            nrows=1,
            usecols=[
                0,
            ],
            sep=r"\s+",
            header=None,
        ).values[0, 0]
        read_csv_args.update(skiprows=5, nrows=nrows)
    df_data = pd.read_csv(fn, **read_csv_args)

    # select q-range
    if q_range is not None:
        q_min, q_max = q_range
        df_data = df_data[(df_data.q > q_min) & (df_data.q < q_max)]

    file_name = os.path.basename(fn).split("[")[0]
    return df_data, file_name

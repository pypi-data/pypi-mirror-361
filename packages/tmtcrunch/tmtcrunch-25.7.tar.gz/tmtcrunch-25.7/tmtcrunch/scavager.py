"""Scavager helpers."""

__all__ = [
    "read_fraction",
]


from ast import literal_eval

import pandas as pd

from .utils import mod_mass_repr


def read_fraction(fpath: str) -> pd.DataFrame:
    """
    Read and reformat Scavager PSMs_full.tsv file.

    :param fpath: path to the Scavager file.
    :return: DataFrame
    """
    eval_cols = ["protein", "modifications"]
    df_psm = pd.read_table(fpath, converters={key: literal_eval for key in eval_cols})

    mapping = {
        "ML score": "PSM_score",
        "RT exp": "retention_time",
        "decoy1": "decoy_training",
        "decoy2": "decoy_testing",
        "q": "PSM_q",
    }
    df_psm.rename(columns=mapping, inplace=True)

    df_psm["file"] = fpath
    df_psm["modifications"] = df_psm["modifications"].apply(mods_from_scavager)

    return df_psm


def mods_from_scavager(scavager_modifications: list) -> dict:
    """
    Convert list of modifications from the Scavager format ["location@total_mass"] to
    the dict {location: "total_mass"}.

    :param scavager_modifications: list of modifications.
    :return: dict of modifications.
    """
    mods = [mod.split("@") for mod in scavager_modifications]
    return {int(loc): mod_mass_repr(mass) for mass, loc in mods}

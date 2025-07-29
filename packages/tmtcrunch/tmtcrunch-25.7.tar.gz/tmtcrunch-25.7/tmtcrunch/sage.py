"""Sage helpers."""

__all__ = [
    "read_fraction",
]


import os.path
import re

import pandas as pd

from .utils import mod_mass_repr, standard_residue_mass


def read_fraction(fpath: str) -> pd.DataFrame:
    """
    Read and reformat Sage output files.

    :param fpath: path to the Sage output directory.
    :return: DataFrame
    """
    search_file = os.path.join(fpath, "results.sage.tsv")
    tmt_file = os.path.join(fpath, "tmt.tsv")
    df_search = pd.read_table(search_file, index_col=["filename", "scannr"])
    df_tmt = pd.read_table(tmt_file, index_col=["filename", "scannr"])
    df_psm = pd.concat([df_search, df_tmt], axis=1, join="inner")
    df_psm.reset_index(inplace=True)

    mapping = {
        "proteins": "protein",
        "rt": "retention_time",
        "sage_discriminant_score": "PSM_score",
        "scannr": "spectrum",
        "spectrum_q": "PSM_q",
    }
    df_psm.rename(columns=mapping, inplace=True)

    df_psm["decoy"] = df_psm["label"].apply(lambda x: True if x == -1 else False)
    df_psm["decoy_training"] = False
    df_psm["decoy_testing"] = df_psm["decoy"]
    df_psm["file"] = fpath
    df_psm["peptide_mod_delta"] = df_psm["peptide"]  # peptide with modifications
    df_psm["peptide"] = df_psm["peptide"].apply(strip_modifications)
    df_psm["mod_delta"] = df_psm["peptide_mod_delta"].apply(extract_modifications)
    df_psm["modifications"] = df_psm[["peptide", "mod_delta"]].apply(
        lambda df: mods_total_mass(df.iloc[0], df.iloc[1]), axis=1
    )
    df_psm["protein"] = df_psm["protein"].apply(lambda x: x.split(";"))
    df_psm["PSM_score"] = -df_psm["PSM_score"]  # less is better

    return df_psm


def strip_modifications(sequence: str) -> str:
    """
    Strip modifications from peptide sequence.

    :param sequence: peptide sequence with modifications.
    :return: peptide sequence.
    """
    res = re.findall(r"[A-Z]+", sequence)
    peptide = "".join(res)
    return peptide


def extract_modifications(sequence: str) -> dict:
    """
    Extract modifications from peptide sequence to dict
    {position: "mass"}.

    :param sequence: peptide sequence with modifications.
    :return: dict of modifications.
    """
    pattern = r"\[(\+\d+\.\d+)\]\-?"
    remainder = sequence
    modifications = {}
    position = 0
    while True:
        match = re.search(pattern, remainder)
        if match:
            position += match.start()
            modifications[position] = match.group(1)
            remainder = remainder[match.end() :]
        else:
            break
    return modifications


def mods_total_mass(peptide: str, modifications: dict, residue_mass: dict = None):
    """
    Replace delta mass of modification with the total mass of the site and modification.

    :param peptide: unmodified peptide sequence.
    :param modifications: dict of modifications {position: "delta mass"}.
    :param residue_mass: animo acid residue masses. Default is `standard_residue_mass`.
    :return: dict of modifications {position: "total mass"}.
    """
    if residue_mass is None:
        residue_mass = standard_residue_mass
    peptide = "-" + peptide
    return {
        pos: mod_mass_repr(residue_mass[peptide[pos]] + float(mass_delta))
        for pos, mass_delta in modifications.items()
    }

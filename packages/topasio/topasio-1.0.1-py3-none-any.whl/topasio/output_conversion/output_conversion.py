from pathlib import Path
import re
from dataclasses import dataclass
import quantities as q
import numpy as np
import pyarrow.csv as csv
import pyarrow as pa
import polars as pl
import pyarrow.parquet as pq
import logging
import json

logger = logging.getLogger("topasio")

regexes = {
    "float": r"\d+(?:\.\d+)?(?:[eE][+-]?\d+)?",
    "about_energy": r"#.+?bin.+?energ.+?",
    "reports": r"(\w+) in (\d+) bin[ s] of ([\d.]+) (.+)",
}



def get_header_from_csv(filepath: str | Path):
    filepath = Path(filepath)

    header = ""
    with open(filepath, "r") as f:
        for line in f:
            if line.startswith("#"):
                header += line
            else:
                break
    return header


def get_header_from_bin(filepath: str | Path):
    filepath = Path(filepath)

    if filepath.suffix == ".bin":
        filepath = filepath.with_suffix(".binheader")

    with open(filepath, "r") as f:
        header = f.read()
    if not header:
        raise ValueError(f"Header file {filepath} is empty.")
    return header


def get_header(filepath: str | Path):
    filepath = Path(filepath)

    if filepath.suffix == ".csv":
        return get_header_from_csv(filepath)
    elif filepath.suffix in [".bin", ".binheader"]:
        return get_header_from_bin(filepath)
    else:
        raise ValueError(
            f"Unsupported file type: {filepath.suffix}. Expected .csv, .bin, or .binheader."
        )

@dataclass
class EnergyBinning:
    nbins: int = None
    binwidth: q.Quantity = None
    startE: q.Quantity = None
    endE: q.Quantity = None

@dataclass
class SpaceBinning:
    num: int = None
    width: q.Quantity = None
    name: str = None

def get_binning_info(filepath: str | Path):
    header = get_header(filepath)

    energy_bins = EnergyBinning()
    space_bins = []

    for line in header.splitlines():
        about_energy = about_energy = re.search(regexes["about_energy"], line, re.IGNORECASE)
        if about_energy:
            matches = re.findall(regexes["float"], line, re.IGNORECASE)
            matches = [float(match) for match in matches]
            assert len(matches) == 4, (
                "Header line does not contain the expected number of matches which is 4."
            )
            assert round((matches[3] - matches[2]) / matches[1]) == round(matches[0]), (
                "Header line about energy cannot be interpreted."
                f"Expected floats in line '{line}' to be in the form of [Nbins, bin width, min energy, max energy]"
            )
            energy_bins.nbins, energy_bins.binwidth, energy_bins.startE, energy_bins.endE = matches
            energy_bins.nbins = int(energy_bins.nbins)
            energy_units = re.findall(f"{regexes['float']} (\\w+) ?", line)
            assert energy_units[0] == "bins", (
                "Energy binning header line does not contain the expected word 'bins'."
            )
            energy_units = energy_units[1:]
            if len(set(energy_units)) > 1:
                logger.warning(
                    "Energy binning header line contains multiple units. "
                    "By default, the first unit will be used."
                )
                energy_unit = energy_units[0]
            else:
                energy_unit = energy_units[0]
            energy_bins.startE = q.Quantity(energy_bins.startE, energy_unit)
            energy_bins.endE = q.Quantity(energy_bins.endE, energy_unit)
            energy_bins.binwidth = q.Quantity(energy_bins.binwidth, energy_unit)
            

        if not about_energy:
            matches = re.findall(regexes["reports"], line)
            if len(matches)>0:
                matches = matches[0]
                space_bins.append(SpaceBinning(width=q.Quantity(matches[2], matches[3]), num=int(matches[1]), name=matches[0]))
    # print(energy_bins, space_bins)
    # print(energy_bins.__dict__)
    return energy_bins, space_bins

def get_space_part(space_bins: list[SpaceBinning]):
    bin1, bin2, bin3 = np.meshgrid(
        *[range(space_bin.num) for space_bin in space_bins],
        indexing='ij'
    )
    bin1 = bin1.squeeze().flatten()
    bin2 = bin2.squeeze().flatten()
    bin3 = bin3.squeeze().flatten()

    space_part = np.stack([bin1, bin2, bin3], axis=1)
    bin_widths = np.array([space_bin.width.magnitude for space_bin in space_bins])
    bin_widths = np.matlib.repmat(bin_widths, space_part.shape[0], 1)
    # print(f"Space part shape before multiplication: {space_part.shape}")
    # print(f"Bin widths shape: {bin_widths.shape}")
    # print(f"Bin widths: {bin_widths}")
    space_part = space_part.astype(float) * bin_widths.astype(float)

    return space_part

def get_energy_col_names(energy_bins: EnergyBinning):
    names = list(np.arange(energy_bins.startE,
                    energy_bins.endE,
                    energy_bins.binwidth))
    names = [float(name) for name in names]
    assert len(names) == energy_bins.nbins, (
        "Number of names does not match the number of bins."
        f"Expected {energy_bins.nbins} names, got {len(names)}"
    )
    energy_names = ["underflow"] + names + ["overflow"]
    return energy_names

def get_qnty_info(filename: str | Path):
    header = get_header(filename)

    matches = re.findall(r"# (\w+) \( (.+) \) :(.+)", header)
    assert len(matches) == 1, f"Header does not contain the expected number of matches for QUANTITY. Expected 1 match, found {len(matches)}"
    matches = matches[0]

    quantity_name = matches[0]
    quantity_unit = matches[1]
    reports = re.sub(r"\s+", " ", matches[2]).strip().split(" ")
    return quantity_name, quantity_unit, reports

def write_to_parquet(filename: str | Path):
    logger.info(f"Converting {filename} to Parquet format...")
    filename = Path(filename)
    if not filename.exists():
        raise FileNotFoundError(f"File {filename} does not exist.")
    header = get_header(filename)
    logger.debug(f"Header: {header}")
    
    energy_bins, space_bins = get_binning_info(filename)
    logger.debug(f"Energy Binning: {energy_bins}")
    logger.debug(f"Space Binning: {space_bins}\n")

    if energy_bins.nbins is not None:
        specific_names = get_energy_col_names(energy_bins)
        if "primary track" not in header.lower() and "pre-step" not in header.lower(): # TODO: this only accounts for primary track and incident track
            specific_names += ["no_incident_track"]

        qnty_name, qnty_unit, reports = get_qnty_info(filename)
    else:
        qnty_name, qnty_unit, reports = get_qnty_info(filename)
        specific_names = reports

    logger.info(f"Quantity Name: {qnty_name}, Quantity Unit: {qnty_unit}, Reports: {reports}")

    if filename.suffix == ".csv":
        if energy_bins.nbins is None:
            csv_colnames = ["bin1", "bin2", "bin3"] + specific_names
        else:
            csv_colnames = specific_names
        csv_colnames = [str(colname) for colname in csv_colnames]
        measurements = csv.read_csv(filename, read_options=csv.ReadOptions(skip_rows=len(header.splitlines()),
                                                                             column_names=csv_colnames))
        measurements = measurements.to_pandas()
        measurements = measurements[[colname for colname in csv_colnames if colname not in ["bin1", "bin2", "bin3"]]].values
    elif filename.suffix in [".bin", ".binheader"]:
        measurements = np.fromfile(filename.with_suffix(".bin"), dtype=float)
        measurements = measurements.reshape((len(specific_names), -1), order="F").T

    space_part = get_space_part(space_bins)

    logger.info(f"The part of the df dedicated to space binning info has shape: {space_part.shape}")
    logger.info(f"The part of the df dedicated to measurements has shape: {measurements.shape}")

    space_arrays = [pa.array(space_part[:, i], type=pa.float64()) for i in range(space_part.shape[1])]
    space_colnames = [str(space_bin.name) for space_bin in space_bins]

    measurement_arrays = [pa.array(measurements[:, i], type=pa.float64()) for i in range(measurements.shape[1])]
    measurements_colnames = [str(name) for name in specific_names]

    table = pa.Table.from_arrays(space_arrays + measurement_arrays, names=space_colnames + measurements_colnames)

    metadata = {
        "E": {"n_bins": str(energy_bins.nbins) if energy_bins.nbins is not None else "None",
              "bin_width": str(energy_bins.binwidth) if energy_bins.binwidth is not None else "None",
              "start_E": str(energy_bins.startE) if energy_bins.startE is not None else "None",
              "end_E": str(energy_bins.endE) if energy_bins.endE is not None else "None"},
    }
    for space_bin in space_bins:
        metadata[space_bin.name] = {
            "num": str(space_bin.num) if space_bin.num is not None else "None",
            "width": str(space_bin.width.magnitude) if space_bin.width is not None else "None",
            "unit": str(space_bin.width.units) if space_bin.width is not None else "None",
        }
    metadata["quantity"] = {
        "name": qnty_name,
        "unit": qnty_unit,
        "reports": "["+ ", ".join(reports) + "]",
    }
    metadata["original_filename"] = str(filename)
    metadata["original_header"] = header.strip()

    metadata = {"topasio": json.dumps(metadata, indent=4)}

    schema = pa.schema(table.schema, metadata=metadata)
    table = table.cast(schema)

    if energy_bins.nbins is not None:
        energy_values = []
        valid_colnames = []
        for colname in table.column_names:
            try:
                energy_value = float(colname)
                energy_values.append(energy_value)
                valid_colnames.append(colname)
            except ValueError:
                continue

        
        df = pl.from_arrow(table)
        df_valid = df.select(valid_colnames)
        
        # start = time.time()
        df = df.with_columns(
            pl.sum_horizontal(df_valid).alias("total_fluence"),
        )
        df = df.with_columns([
            pl.sum_horizontal([
                pl.col(colname) * E for colname, E in zip(valid_colnames, energy_values)
            ]).alias("weighted_sum"),
        ])
        df = df.with_columns(
            (pl.col("weighted_sum") / pl.col("total_fluence")).alias("weighted_average")
        ).drop(["weighted_sum"])
        # print(f"Time POLARS: {time.time() - start:.2f} seconds")


        table = df.to_arrow()
        table = table.cast(pa.schema(table.schema, metadata=metadata))

        # print(df.head(10))
        # def get_mean_energy(df):
        #     # df.cols = ["X", "Y", "0", "0.1", "0.2", ...]
        #     energy_cols = valid_colnames
        #     weights = [float(col) for col in energy_cols]

        #     def get_avg_energy(row):
        #         if row[energy_cols].sum() == 0:
        #             return 0
        #         return np.average(weights, weights=row[energy_cols])

        #     mean_energy = df.apply(get_avg_energy, axis=1)

        #     return mean_energy
        
        # start = time.time()
        # df_pd = df.to_pandas()
        # df_pd["weighted_average"] = get_mean_energy(df_pd)
        # print(f"Time Pandas: {time.time() - start:.2f} seconds")
        # print(df_pd.head(10))

        # print(np.average(table.column("weighted_average").to_numpy()))
    pq.write_table(table, filename.with_suffix(".parquet"), compression="snappy")


def read_topasio_metadata(filename: str | Path):
    filename = Path(filename)
    if not filename.exists():
        raise FileNotFoundError(f"File {filename} does not exist.")
    if filename.suffix != ".parquet":
        raise ValueError(f"File {filename} is not a Parquet file.")
    
    metadata = pq.read_metadata(filename).metadata
    metadata = {k.decode(): v.decode() for k, v in metadata.items()}
    metadata = {k: v for k, v in metadata.items() if k != "ARROW:schema"}
    return json.loads(metadata["topasio"])


if __name__ == "__main__":

    filenames = [
        "full_linac_head_sim/PrimaryTrackScorer.csv"
    ]

    for filename in filenames:
        filename = Path(filename)

        write_to_parquet(filename)
        # pprint(read_topasio_metadata(filename.with_suffix(".parquet")))

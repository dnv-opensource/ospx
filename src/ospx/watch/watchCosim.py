# pyright: reportUnknownMemberType=false
# pyright: reportUnnecessaryTypeIgnoreComment=false
# pyright: reportGeneralTypeIssues=false
import contextlib
import logging
import os
import re
from math import sqrt as sqrt
from pathlib import Path
from typing import Any, Dict, List, MutableMapping, MutableSequence, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dictIO import DictReader, DictWriter
from matplotlib import cm
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from numpy import ndarray
from pandas import DataFrame

from ospx.utils.plotting import create_meta_dict, save_figure

logger = logging.getLogger(__name__)


class CosimWatcher:
    """CosimWatcher allows to monitor a running simulation,
    plot trends and dump simulation results into a resultDict file.
    """

    def __init__(
        self,
        csv_file_names: MutableSequence[str],
        skip_values: int,
        latest_values: int,
        scale_factor: float,
    ):
        self.watch_dict_file: Union[Path, None] = None
        self.watch_dict: MutableMapping[Any, Any] = {}
        self.csv_file_names: MutableSequence[str] = csv_file_names
        self.title: str = "watch"
        self.delimiter: str = ","  # default
        self.data_sources: Dict[str, Dict[str, Union[List[int], List[str], int, str]]] = {}
        self.results_dir: str = "results"
        self.number_of_columns: int = 3
        self.number_of_subplots: int = 0
        self.skip_values: int = skip_values
        self.latest_values: int = latest_values
        self.scale_factor: float = scale_factor
        self.figure: Figure
        self.terminate: bool = False
        self.max_row: int = 0
        return

    def read_watch_dict(self, watch_dict_file: Union[str, os.PathLike[str]]):
        """Read watchDict file.

        The watchDict file contains the parameters to be plotted.

        Parameters
        ----------
        watch_dict_file : Union[str, os.PathLike[str]]
            watchDict file. Contains the parameters to be plotted.

        Raises
        ------
        FileNotFoundError
            if watch_dict_file does not exist
        """

        # Make sure watch_dict_file argument is of type Path. If not, cast it to Path type.
        watch_dict_file = watch_dict_file if isinstance(watch_dict_file, Path) else Path(watch_dict_file)
        if not watch_dict_file.exists():
            logger.error(f"CosimWatcher: File {watch_dict_file} not found.")
            raise FileNotFoundError(watch_dict_file)

        logger.info(f"Configure CosimWatcher with {watch_dict_file}..")

        self.watch_dict_file = watch_dict_file

        self.watch_dict = DictReader.read(Path(self.watch_dict_file), comments=False)

        # read datasources, if available.
        # normally this part should be written by ospCaseBuilder entirely
        self.data_sources = self.watch_dict["datasources"]

        if "delimiter" in self.watch_dict:
            self.delimiter = self.watch_dict["delimiter"]

        if "simulation" in self.watch_dict:
            self.title = f"{self.watch_dict_file.name}-{self.watch_dict['simulation']['name']}"

        self._define_data_source_properties_for_plotting()
        return

    def plot(self, converge: bool = False):
        """Plot trends.

        Plotting + convergence checker (future task)

        Parameters
        ----------
        converge : bool, optional
            if True, convergence is checked, by default False
        """

        self._initialize_plot()

        if converge:
            terminate_loops = 0
            max_no_change_loops = 4
        else:
            terminate_loops = 10
            max_no_change_loops = 0

        df_row_size = 0

        while True:  # do as long as not interrupted
            df = self._read_csv_files_into_dataframe()

            # cumulate counter for termination if no changes
            if df_row_size == len(df):
                terminate_loops += 1
            else:
                terminate_loops = 0
            df_row_size = len(df)
            df_col_size = len(list(df)) - 1  # reduced by one because 1st col is to remove from list

            # axs = [None for x in range(df_col_size)]
            axs: MutableSequence[Axes] = []
            plot: Axes
            # for index in range(self.nSubplots):
            for index in range(df_col_size):
                current_key = list(df)[index + 1]  # 0 is Time, StepCount was removed for simplification

                plot = self.figure.add_subplot(self.max_row, self.number_of_columns, index + 1)

                try:
                    _ = plot.plot(
                        "Time",
                        current_key,
                        linewidth=2,
                        color=cm.get_cmap("gist_rainbow")(index / self.number_of_subplots),
                        data=df[["Time", current_key]],
                    )
                except (TypeError, ValueError):
                    pass
                except Exception as e:
                    logger.exception(e)
                # subplot.set_title(currentKey,  fontsize=10)
                _ = plot.grid(color="#66aa88", linestyle="--")
                _ = plot.xaxis.set_tick_params(labelsize=8)
                _ = plot.yaxis.set_tick_params(labelsize=8)
                _ = plot.legend(fontsize=8)
                axs.append(plot)
                # if isinstance(plot, Axes):
                #     axs.append(plot)
                # else:
                #     raise TypeError(
                #         f"CosimWatcher.plot(): plot is of type {type(plot)}. Expected type was matplotlib.axes.Axes ."
                #     )

            _ = self.figure.suptitle(self.title)

            if converge:
                plt.show(block=False)
                plt.pause(3)

            if terminate_loops >= max_no_change_loops:
                save_figure(
                    self.figure,
                    extension="png",
                    path=self.results_dir,
                    title=self.title,
                    meta_dict=create_meta_dict(self.title),
                )
                break
            plt.clf()

            # @TODO: Implement keypress for termination

        return

    def dump(self):
        """Write dataframe to dump."""

        df = self._read_csv_files_into_dataframe()

        result_dict = {}
        for header in list(df):
            values: ndarray[Any, Any] = df[header].dropna().to_numpy()
            _first_value: Any = values[0]
            _last_value: Any = values[-1]
            _mean: Union[float, str] = "None"
            _stddev: Union[float, str] = "None"
            _min: Union[float, str] = "None"
            _max: Union[float, str] = "None"
            with contextlib.suppress(TypeError):
                _mean = np.mean(values)  # type: ignore
            with contextlib.suppress(TypeError):
                _stddev = np.std(values)  # type: ignore
            with contextlib.suppress(TypeError):
                _min = np.min(values)
            with contextlib.suppress(TypeError):
                _max = np.max(values)
            result_dict[header] = {
                "latestValue": _last_value,
                "firstValue": _first_value,
                "mean": _mean,
                "stdev": _stddev,
                "min": _min,
                "max": _max,
            }

        # debug
        # result_dict.update({'_datasources':self.data_sources})
        result_dict_name = "-".join([self.title, "resultDict"])

        target_file_path = Path.cwd() / self.results_dir / result_dict_name
        DictWriter.write(result_dict, target_file_path, mode="w")

        dump_dict_name = "-".join([self.title, "dataFrame.dump"])
        target_file_path = Path.cwd() / self.results_dir / dump_dict_name
        df.to_pickle(str(target_file_path.absolute()), compression="gzip")
        return

    def _define_data_source_properties_for_plotting(self):
        """Details out the properties of all data sources for plotting.

        Details out the properties of all data source, making sure they contain the following fields required for plotting
            - file name
            - column names (= variable names)
        """

        pattern = re.compile(r"(^#|\s+\[.*?\]$)")
        # pattern = re.compile(r'(^#|\s+\[[\w\d\s]+\]$)')

        for (
            data_source_name,
            data_source_properties,
        ) in self.data_sources.items():  # loop over all data sources
            for csv_file_name in self.csv_file_names:
                if re.match(data_source_name, csv_file_name):  # find the correct csv file
                    data_source_properties.update({"csvFile": csv_file_name})

                    # extract the header row from the csv file to determine the variable names
                    data_header: List[str] = []
                    with open(csv_file_name, "r") as f:
                        data_header = f.readline().strip().split(self.delimiter)
                    if not data_header:
                        continue
                    columns: List[int] = []
                    read_only_shortlisted_columns: bool = False
                    # @TODO: The following line is commented out, currently,
                    #        as the column indices shortlisted in watch dict
                    #        are incorrect if variableGroups are used in connectors.
                    #        Once this issue is solved and shortlisted columns are correctly written to the watch dict again,
                    #        the following line can be activated and this TODO comment be deleted.
                    #        CLAROS, 2022-09-26
                    # read_only_shortlisted_columns = True if 'columns' in data_source_properties else False
                    if read_only_shortlisted_columns:
                        # if columns were explicitely specified (shortlisted) in watch dict:
                        # Read only shortlisted columns.
                        if "columns" in data_source_properties and isinstance(data_source_properties["columns"], List):
                            columns = [int(col) for col in data_source_properties["columns"]]
                    else:
                        # if columns were not explicitely specified in watch dict:
                        # Read all columns except settings.
                        columns.extend(
                            index
                            for index, col_name in enumerate(data_header)
                            if not re.match(r"^(settings)", col_name)
                        )

                    _column_names: List[str] = [data_header[column] for column in columns]
                    data_source_properties.update({"colNames": _column_names})

                    _display_column_names: List[str] = [
                        pattern.sub("", col_name) for col_name in data_source_properties["colNames"]  # type: ignore
                    ]
                    _display_column_names = ["Time", "StepCount"] + [
                        data_source_name + "|" + col_name
                        for col_name in _display_column_names
                        if col_name not in ["Time", "StepCount"]
                    ]
                    data_source_properties.update({"displayColNames": _display_column_names})

                    data_source_properties.update({"xColumn": columns[0]})
                    data_source_properties.update({"yColumns": columns[1:]})
        return

    def _initialize_plot(self):
        """Initialize the plot.

        Collects data and sets plot header line
        """
        self.figure = plt.figure(figsize=(16 * self.scale_factor, 9 * self.scale_factor), dpi=150)
        # self.fig.tight_layout()  # constraint_layout()
        _ = self.figure.subplots_adjust(
            left=0.1,
            bottom=0.05,
            right=0.95,
            top=0.9,
            wspace=0.2,
            hspace=0.2,
        )
        self.terminate = False

        df = self._read_csv_files_into_dataframe()  # do it once to find the number of respective columns

        self.number_of_subplots = len(list(df)) - 1  # one of the columns is the abscissa
        self.number_of_columns = int(sqrt(self.number_of_subplots - 1)) + 1
        self.max_row = int(self.number_of_subplots / self.number_of_columns - 0.1) + 1
        return

    def _read_csv_files_into_dataframe(self) -> DataFrame:
        """Read all csv files into one joint Pandas dataframe.

        Read all csv files (=all data sources, one csv file per data source) into one joint Pandas dataframe.
        The returned dataframe hence contains the data of all datas ources.
        This dataframe can then be used for plotting and to dump a pickle.

        Returns
        -------
        pandas.core.frame.DataFrame
            Pandas dataframe containing the data of all csv files
        """

        df_all_data_sources = pd.DataFrame()  # initialize empty df

        for _, data_source_properties in self.data_sources.items():
            # mapping dict for display column names
            column_name_to_display_column_name_mapping: Dict[str, str] = dict(
                zip(
                    data_source_properties["colNames"],  # type: ignore
                    data_source_properties["displayColNames"],  # type: ignore
                )
            )
            """it could be so easy
            but we have to remove Time and StepCount because they are in each csv file and need to be filtered
            could be also required here to specify an abscissa differing from column 1 or 2
            but, anyways this is only applicable to cosim
            """
            # for remove_item in ['Time', 'StepCount']:
            #    column_name_to_display_column_name_mapping.pop(remove_item, None)
            _column_names: List[str] = []
            if "colNames" in data_source_properties and isinstance(data_source_properties["colNames"], List):
                _column_names = [str(col_name) for col_name in data_source_properties["colNames"]]
            # Alternative value for _column_names which excludes 'Time' and 'StepCount':
            # _column_names = [col_name for col_name in data_source_properties['colNames'] if col_name not in ['Time', 'StepCount']],
            if "csvFile" in data_source_properties and isinstance(data_source_properties["csvFile"], str):
                df_single_data_source: DataFrame
                df_single_data_source = pd.read_csv(
                    Path(data_source_properties["csvFile"]),
                    usecols=_column_names,
                )

                df_single_data_source = df_single_data_source.rename(columns=column_name_to_display_column_name_mapping)

                if df_all_data_sources.empty:
                    # first df inherit all columns from single df
                    df_all_data_sources = df_single_data_source
                else:
                    # all subsequent merge row-wise by time column,
                    # ignoring index
                    # (after setting individual time steps for each individual component)

                    # concatenate column-wise
                    # df_all_data_sources = pd.concat([df_all_data_sources, df_single_data_source], axis=1)

                    # df_all_data_sources = pd.concat([df_all_data_sources, df_single_data_source], ignore_index=True)
                    df_all_data_sources = pd.concat([df_all_data_sources, df_single_data_source])

                    # potential solution
                    # interpolating non-matching time data
                    # otherwise should component-wise dataframes do a better job
                    # bypass StepCound yielding in big holes, not plotted by mpl.
                    # df_all_data_sources = pd.merge_asof(
                    #    df_all_data_sources,
                    #    df_single_data_source,
                    #    on = 'Time',
                    #    by = 'StepCount',
                    #    direction = 'nearest',
                    #    #tolerance = pd.Timedelta('1ms')
                    # )

        # find latest common start point for skip and latest
        # consider skipping negative values due to wrong inputs
        start: int = 0
        if df_all_data_sources.shape[0] - self.skip_values < 0:  # safety
            logger.error(f"there will be no data, consider adjusting --skip: {self.skip_values}")
            # cases
        if self.skip_values > 0 and self.latest_values > 0:
            start = max(self.skip_values, df_all_data_sources.shape[0] - self.latest_values)
        elif self.skip_values > 0 and self.latest_values == 0:
            start = self.skip_values
        elif self.latest_values > 0 and self.skip_values == 0:
            start = df_all_data_sources.shape[0] - self.latest_values
        else:
            start = 0

        # if skip latest n steps is to be implemented, no changes to start, but an additional command option is required
        length: int = df_all_data_sources.shape[0]
        return df_all_data_sources.iloc[start:length, :]

    def _determine_optimum_screen_size(self):
        """Determine the optimum screen size."""
        # Opening and closing of window may be deprecated when a better solution is found
        mgr = plt.get_current_fig_manager()
        mgr.full_screen_toggle()
        self.screenSize = (mgr.canvas.width(), mgr.canvas.height())  # type: ignore
        mgr.window.close()  # type: ignore
        return

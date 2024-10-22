# pyright: reportUnknownMemberType=false
# pyright: reportArgumentType=false
# pyright: reportCallIssue=false
# ruff: noqa: ERA001

import contextlib
import logging
import os
import re
from collections.abc import MutableMapping, MutableSequence, Sequence
from math import sqrt
from pathlib import Path
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dictIO import DictReader, DictWriter
from matplotlib import colormaps
from numpy import ndarray
from pandas import DataFrame

from ospx.utils.plotting import create_meta_dict, save_figure

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


class CosimWatcher:
    """Watcher to monitor a running simulation.

    CosimWatcher allows to monitor a running simulation,
    plot trends and dump simulation results into a resultDict file.
    """

    def __init__(
        self,
        csv_file_names: MutableSequence[str],
        skip_values: int,
        latest_values: int,
        scale_factor: float,
        *,
        timeline_data: bool,
    ) -> None:
        self.watch_dict_file: Path | None = None
        self.watch_dict: MutableMapping[Any, Any] = {}
        self.csv_file_names: MutableSequence[str] = csv_file_names
        self.title: str = "watch"
        self.delimiter: str = ","  # default
        self.data_sources: dict[str, dict[str, list[int] | list[str] | int | str]] = {}
        self.results_dir: str = "results"
        self.number_of_columns: int = 3
        self.number_of_subplots: int = 0
        self.skip_values: int = skip_values
        self.latest_values: int = latest_values
        self.scale_factor: float = scale_factor
        self.timeline_data: bool = timeline_data
        self.figure: Figure
        self.terminate: bool = False
        self.max_row: int = 0
        self.screenSize: tuple[float, float]
        return

    def read_watch_dict(
        self,
        watch_dict_file: str | os.PathLike[str],
    ) -> None:
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

    def plot(
        self,
        *,
        converge: bool = False,
    ) -> None:
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
            data = self._read_csv_files_into_dataframe()

            # cumulate counter for termination if no changes
            if df_row_size == len(data):
                terminate_loops += 1
            else:
                terminate_loops = 0

            df_row_size = len(data)
            df_col_size = len(list(data)) - 1  # reduced by one because 1st col is time column

            # axs = [None for x in range(df_col_size)]
            axs: MutableSequence[Axes] = []
            plot: Axes
            time_key: Sequence[float] = list(data)[0]  # type: ignore[assignment, reportAssignmentType]  # noqa: RUF015
            for index in range(df_col_size):
                # 0 is time column and thus removed
                current_key: Sequence[float] = list(data)[index + 1]  # type: ignore[assignment, reportAssignmentType]

                plot = self.figure.add_subplot(self.max_row, self.number_of_columns, index + 1)

                try:
                    _ = plot.plot(
                        time_key,
                        current_key,
                        linewidth=2,
                        color=colormaps["gist_rainbow"](index / self.number_of_subplots),
                        data=data[[time_key, current_key]],
                    )
                except (TypeError, ValueError):
                    pass
                except Exception:
                    logger.exception("CosimWatcher.plot(): An error occurred while plotting.")

                # subplot.set_title(currentKey,  fontsize=10)
                plot.grid(color="#66aa88", linestyle="--")
                plot.xaxis.set_tick_params(labelsize=8)
                plot.yaxis.set_tick_params(labelsize=8)
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

    def dump(self) -> None:
        """Write dataframe to dump."""
        data = self._read_csv_files_into_dataframe()

        result_dict = {}
        for header in list(data):
            values: ndarray[Any, Any] = data[header].dropna().to_numpy()
            _first_value: Any = values[0]
            _last_value: Any = values[-1]
            _mean: float | str = "None"
            _stddev: float | str = "None"
            _min: float | str = "None"
            _max: float | str = "None"
            with contextlib.suppress(TypeError):
                _mean = float(np.mean(values))
            with contextlib.suppress(TypeError):
                _stddev = float(np.std(values))
            with contextlib.suppress(TypeError):
                _min = float(np.min(values))
            with contextlib.suppress(TypeError):
                _max = float(np.max(values))
            result_dict[header] = {
                "latestValue": _last_value,
                "firstValue": _first_value,
                "mean": _mean,
                "stdev": _stddev,
                "min": _min,
                "max": _max,
            }
            if self.timeline_data:
                result_dict[header].update({"values": values})

        # debug
        # result_dict.update({'_datasources':self.data_sources})
        result_dict_name = f"{self.title}-resultDict"

        target_file_path = Path.cwd() / self.results_dir / result_dict_name
        DictWriter.write(result_dict, target_file_path, mode="w")

        dump_dict_name = f"{self.title}-dataFrame.dump"
        target_file_path = Path.cwd() / self.results_dir / dump_dict_name
        data.to_pickle(str(target_file_path.absolute()), compression="gzip")
        return

    def _define_data_source_properties_for_plotting(self) -> None:
        """Details out the properties of all data sources for plotting.

        Details out the properties of all data source, making sure they contain
        the following fields required for plotting:
            - file name
            - column names (= variable names)
        """
        # Remove all leading #'s and spaces and all trailing [.*]'s
        pattern = re.compile(r"(^#{0,2}\s*|\s+\[.*?\]$)")

        for (
            data_source_name,
            data_source_properties,
        ) in self.data_sources.items():  # loop over all data sources
            for csv_file_name in self.csv_file_names:
                if re.match(data_source_name, csv_file_name):  # find the correct csv file
                    data_source_properties.update({"csvFile": csv_file_name})

                    # extract the header row from the csv file to determine the variable names
                    data_header: list[str] = []
                    with Path(csv_file_name).open() as f:
                        data_header = f.readline().strip().split(self.delimiter)
                    if not data_header:
                        continue

                    time_column: int = 0  # frl 2023-11-07 default first column
                    if "timeColumn" in data_source_properties and isinstance(data_source_properties["timeColumn"], int):
                        time_column = data_source_properties["timeColumn"]

                    _time_name: str = data_header[time_column]
                    data_source_properties.update({"timeName": _time_name})
                    _display_time_name: str = pattern.sub("", _time_name)
                    data_source_properties.update({"displayTimeName": _display_time_name})

                    data_columns: list[int] = []
                    read_only_shortlisted_columns: bool
                    # NOTE: Greedy approach needs to be updated on demand; hence commnted out. @FRALUM, 2023-11-07
                    # read_only_shortlisted_columns = False

                    read_only_shortlisted_columns = "dataColumns" in data_source_properties
                    if read_only_shortlisted_columns and (
                        "dataColumns" in data_source_properties
                        and isinstance(data_source_properties["dataColumns"], list)
                    ):
                        data_columns = [int(col) for col in data_source_properties["dataColumns"]]
                    # else: frl 2023-11-07 simx heritage?
                    #    # if columns were not explicitely specified in watch dict:
                    #    # Read all columns except settings.
                    #    columns.extend(
                    #        index
                    #        for index, col_name in enumerate(data_header)
                    #        if not re.match(r"^(settings)", col_name)
                    #    )

                    _column_names: list[str] = [data_header[column] for column in data_columns]
                    data_source_properties.update({"colNames": _column_names})
                    _display_column_names: list[str] = [pattern.sub("", col_name) for col_name in _column_names]
                    # _display_column_names = ["Time", "StepCount"] + [
                    _display_column_names = [
                        data_source_name + "|" + col_name
                        for col_name in _display_column_names
                        # if col_name not in ["Time", "StepCount"] frl 2023-11-07
                    ]

                    data_source_properties.update({"displayColNames": _display_column_names})
                    data_source_properties.update({"xColumn": time_column})
                    data_source_properties.update({"yColumns": data_columns})

        return

    def _initialize_plot(self) -> None:
        """Initialize the plot.

        Collects data and sets plot header line
        """
        self.figure = plt.figure(figsize=(16 * self.scale_factor, 9 * self.scale_factor), dpi=150)
        # self.fig.tight_layout()  # constraint_layout()
        self.figure.subplots_adjust(
            left=0.1,
            bottom=0.05,
            right=0.95,
            top=0.9,
            wspace=0.2,
            hspace=0.2,
        )
        self.terminate = False

        # do it once to find the number of respective columns of all datasources
        data = self._read_csv_files_into_dataframe()
        # one of the columns is the abscissa, frl: check if this works for multiple datasources and merged time columns
        self.number_of_subplots = len(list(data)) - 1

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

        for data_source_properties in self.data_sources.values():
            # mapping dict for display column names
            column_name_to_display_column_name_mapping: dict[str, str] = dict(
                zip(
                    [data_source_properties["timeName"]] + data_source_properties["colNames"],  # type: ignore[arg-type, operator, reportOperatorIssue]
                    [data_source_properties["displayTimeName"]] + data_source_properties["displayColNames"],  # type: ignore[arg-type, operator, reportOperatorIssue]
                    strict=False,
                )
            )

            _column_names: list[str] = []
            if "colNames" in data_source_properties and isinstance(data_source_properties["colNames"], list):
                _column_names = [str(col_name) for col_name in data_source_properties["colNames"]]
            if "timeName" in data_source_properties and isinstance(data_source_properties["timeName"], str):
                _column_names = [data_source_properties["timeName"], *_column_names]

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
                    df_all_data_sources = pd.concat(
                        [df_all_data_sources, df_single_data_source]
                    )  # frl check for duplicated timeName columns for multiple datasources

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

    def _determine_optimum_screen_size(self) -> None:
        """Determine the optimum screen size."""
        # Opening and closing of window may be deprecated when a better solution is found
        mgr = plt.get_current_fig_manager()
        if mgr is None:
            return
        mgr.full_screen_toggle()
        self.screenSize = (mgr.canvas.width(), mgr.canvas.height())  # type: ignore[attr-defined, reportAttributeAccessIssue]
        mgr.window.close()  # type: ignore[attr-defined, reportAttributeAccessIssue]
        return

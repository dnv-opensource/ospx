import logging
import re
from pathlib import Path
from typing import MutableSequence

import matplotlib
import matplotlib.axes
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from math import sqrt as sqrt
from matplotlib import cm
from dictIO.dictReader import DictReader
from dictIO.dictWriter import DictWriter
from ospx.utils.plotting import create_meta_dict, save_figure
from typing import Union
import os


logger = logging.getLogger(__name__)


class CosimWatcher:

    def __init__(
        self,
        csv_file_names: MutableSequence,
        skip_values: int,
        latest_values: int,
    ):
        self.watch_dict_file = None
        self.csv_file_names = csv_file_names
        self.title = 'watch'
        self.delimiter = ','    # default
        self.data_sources = {}
        self.results_dir = 'results'
        self.number_of_columns = 3
        self.number_of_subplots = 0
        self.skip_values = skip_values
        self.latest_values = latest_values

    def read_watch_dict(self, watch_dict_file: Union[str, os.PathLike[str]]):
        """Reads watchDict file. The watchDict file Ccntains the parameters to be plotted

        Parameters
        ----------
        watch_dict_file : Union[str, os.PathLike[str]]
            watchDict file in C++ dictionary format. Contains the parameters to be plotted.

        Raises
        ------
        FileNotFoundError
            if watch_dict_file does not exist
        """

        # Make sure watch_dict_file argument is of type Path. If not, cast it to Path type.
        watch_dict_file = watch_dict_file if isinstance(watch_dict_file,
                                                        Path) else Path(watch_dict_file)
        if not watch_dict_file.exists():
            logger.error(f"CosimWatcher: File {watch_dict_file} not found.")
            raise FileNotFoundError(watch_dict_file)

        logger.info(f"Configure CosimWatcher with {watch_dict_file}..")

        self.watch_dict_file = watch_dict_file

        self.config_dict = DictReader.read(Path(self.watch_dict_file), comments=False)

        # read datasources, if available.
        # normally this part should be written by ospCaseBulder entirely
        self.data_sources = self.config_dict['datasources']

        if 'delimiter' in self.config_dict:
            self.delimiter = self.config_dict['delimiter']

        if 'simulation' in self.config_dict:
            self.title = f"{self.watch_dict_file.name}-{self.config_dict['simulation']['name']}"

    def _determine_optimum_screen_size(self):
        """Determines the optimum screen size.
        """
        # Opening and closing of window may be deprecated when a better solution is found
        mgr = plt.get_current_fig_manager()
        mgr.full_screen_toggle()
        self.screenSize = (mgr.canvas.width(), mgr.canvas.height())
        mgr.window.close()

    def define_data_source_properties_for_plotting(self):
        """Details out the properties of all data source for plotting.

        Details out the properties of all data source, making sure they contain the following fields required for plotting
            - file name
            - column names (= variable names)
        """

        for data_source_name, data_source_properties in self.data_sources.items():                                    # loop over all data sources
            for csv_file_name in self.csv_file_names:
                if re.match(data_source_name, csv_file_name):                                       # find the regarding csv file
                    data_source_properties.update({'csvFile': csv_file_name})
                    with open(csv_file_name, 'r') as f:
                        data_header = f.readline().strip().split(
                            self.delimiter
                        )                                                                           # extract the header line to find the variable names
                        if 'columns' in data_source_properties:                                     # if key columns was given
                            data_source_properties.update(
                                {
                                    'colNames':
                                    [data_header[x] for x in data_source_properties['columns']]
                                }
                            )
                            data_source_properties.update(
                                {
                                    'displayColNames': [
                                        re.sub(
                                            r'(^#|\s*\[.*?\]$)',
                                            '',
                                            data_source_name + '|' + col_name
                                        ) for col_name in data_source_properties['colNames']
                                    ]
                                }
                            )

                        else:                                                                       # if no columns is given, extract all relevant columns avoiding settings. and StepCount
                            data_source_properties.update(
                                {
                                    'colNames': [
                                        col_name for col_name in data_header
                                        if not re.match(r'^(StepCount|settings)', col_name)
                                    ]
                                }
                            )
                            data_source_properties.update(
                                {
                                    'displayColNames': [
                                        re.sub(
                                            r'(^#|\s*\[.*?\]$)',
                                            '',
                                            data_source_name + '|' + col_name
                                        ) for col_name in data_source_properties['colNames']
                                    ]
                                }
                            )
                            data_source_properties.update(
                                {'columns': list(range(len(data_source_properties['colNames'])))}
                            )

                    data_source_properties.update(
                        {'xColumn': data_source_properties['columns'][0]}
                    )
                    data_source_properties.update(
                        {'yColumns': data_source_properties['columns'][1:]}
                    )

    def _read_csv_files_into_dataframe(self):
        """Reads all csv files into one joint Panda dataframe.

        Read all csv files (=all data sources, one csv file per data source) into one joint Pandas dataframe.
        The returned dataframe hence contains the data of all datas ources.
        This dataframe can then be used for plotting and to dump a pickle.

        Returns
        -------
        pandas.core.frame.DataFrame
            Pandas dataframe containing the data of all csv files
        """

        df_all_data_sources = pd.DataFrame()    # initialize empty df

        for index, (data_source_name,
                    data_source_properties) in enumerate(self.data_sources.items()):
            # create the mapping dict
            map = dict(
                zip(data_source_properties['colNames'], data_source_properties['displayColNames'])
            )
            '''it could be so easy
            but we have to remove Time and StepCount because they are in each csv file and need to be filtered
            could be also required here to specify an abscissa differing from column 1 or 2
            but, anyways this is only applicable to cosim
            '''
            for remove_item in ['Time', 'StepCount']:
                map.pop(remove_item, None)

            if index == 0:                                                              # first call, also include Time (and StepCount)
                df_single_data_source = pd.read_csv(
                    Path(data_source_properties['csvFile']),
                    usecols=data_source_properties['colNames'],
                )
            else:
                df_single_data_source = pd.read_csv(
                    Path(data_source_properties['csvFile']),
                    usecols=[
                        col_name for col_name in data_source_properties['colNames']
                        if col_name not in ['Time', 'StepCount']
                    ],
                )

            df_single_data_source = df_single_data_source.rename(columns=map)   # rename

            df_all_data_sources = pd.concat(
                [df_all_data_sources, df_single_data_source], axis=1
            )                                                           # concatenate column-wise

        # find latest common start point for skip and latest
        # consider skipping negative values due to wrong inputs
        if df_all_data_sources.shape[0] - self.skip_values < 0:     # safety
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
        return df_all_data_sources.iloc[start:df_all_data_sources.shape[0], :]

    def initialize_plot(self):
        """Initializes the plot.

        Collects data and sets plot header line
        """
        self.figure = plt.figure(figsize=(16, 9), dpi=150)
        # self.fig.tight_layout() #constraint_layout()
        self.figure.subplots_adjust(
            left=0.1,
            bottom=0.05,
            right=0.95,
            top=0.9,
            wspace=0.2,
            hspace=0.2,
        )
        self.terminate = False

        df = self._read_csv_files_into_dataframe(
        )                                           # do it once to find the number of respective columns

        self.number_of_subplots = len(list(df)) - 1     # one of the columns is the abscissa
        self.number_of_columns = int(sqrt(self.number_of_subplots - 1)) + 1
        self.maxRow = int(self.number_of_subplots / self.number_of_columns - 0.1) + 1

    def plot(self, converge: bool = False):
        """Plotting

        Plotting + convergence checker (future task)

        Parameters
        ----------
        converge : bool, optional
            if True, convergence is checked, by default False
        """

        if converge:
            terminate_loops = 0
            max_no_change_loops = 4
        else:
            terminate_loops = 10
            max_no_change_loops = 0

        df_row_size = 0

        while True:     # do as long as not interrupted

            df = self._read_csv_files_into_dataframe()

            # cumulate counter for termination if no changes
            if df_row_size == len(df):
                terminate_loops += 1
            else:
                terminate_loops = 0
            df_row_size = len(df)
            df_col_size = len(list(df)) - 1     # reduced by one because 1st col is to remove from list

            # axs = [None for x in range(df_col_size)]
            axs: MutableSequence[matplotlib.axes.SubplotBase] = []

            # for index in range(self.nSubplots):
            for index in range(df_col_size):

                current_key = list(df)[index + 1
                                       ]            # 0 is Time, StepCount was removed for simplification

                subplot: matplotlib.axes.SubplotBase = self.figure.add_subplot(
                    self.maxRow, self.number_of_columns, index + 1
                )
                subplot.plot(
                    'Time',
                    current_key,
                    linewidth=2,
                    color=cm.get_cmap('gist_rainbow')(index / self.number_of_subplots),
                    data=df[['Time', current_key]],
                )
                # subplot.set_title(currentKey,  fontsize=10)
                subplot.grid(color='#66aa88', linestyle='--')
                subplot.xaxis.set_tick_params(labelsize=8)
                subplot.yaxis.set_tick_params(labelsize=8)
                subplot.legend(fontsize=8)

                axs.append(subplot)

            self.figure.suptitle(self.title)

            if converge:
                plt.show(block=False)
                plt.pause(3)

            if terminate_loops >= max_no_change_loops:
                save_figure(
                    plt,
                    self.figure,
                    extension='png',
                    path=self.results_dir,
                    title=self.title,
                    meta_dict=create_meta_dict(self.title)
                )
                break
            plt.clf()

            # implement keypress for termination

    def dump(self):
        """Write dataframe to dump.
        """

        df = self._read_csv_files_into_dataframe()

        result_dict = {}
        for item in list(df):
            arr = df[item].to_numpy()
            result_dict[item] = {
                'latestValue': arr[-1],
                'firstValue': arr[0],
                'mean': np.mean(arr),
                'stdev': np.std(arr),
                'min': np.min(arr),
                'max': np.max(arr)
            }

        # debug
        # result_dict.update({'_datasources':self.data_sources})
        result_dict_name = '-'.join([self.title, 'resultDict'])

        target_file_path = Path.cwd() / self.results_dir / result_dict_name
        DictWriter.write(result_dict, target_file_path, mode='a')

        dump_dict_name = '-'.join([self.title, 'dataFrame.dump'])
        target_file_path = Path.cwd() / self.results_dir / dump_dict_name
        df.to_pickle(str(target_file_path.absolute()), compression='gzip')

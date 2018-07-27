import datetime
import pandas as pd
import matplotlib.pyplot as plt

# todo create plots for graphs
# todo output df as json

class Analyse(object):

    def __init__(self, json_data):
        self.df_raw = pd.DataFrame(json_data)
        self.df = None
        self.df_bar = None
        self.df_line = None

    def transform(self):
        """
        Transforms raw work_tracker_log data into a more useful DataFrame
        with the following structure:
        | TASK | STARTED | FINISHED | TIME_SPENT |
        """

        # Copy from our original DataFrame
        self.df = self.df_raw.copy(deep=True)

        # Remove the user_id col as it is not needed
        del self.df['user_id']

        # Rename TSTAMP column to STARTED
        self.df.rename(columns={'tstamp': 'started'}, inplace=True)

        # As each new task starts at the same time as the previous one finished
        # we can sort by tstamp (or started) and shift by -1 to get the finish time
        # for each task
        self.df.sort_values(by='started')
        self.df['finished'] = self.df.started.shift(-1)

        # Last row will have a null as it has no finish date, so we remove it
        self.df = self.df[self.df.finished.notnull()]

        # Calculate the time spect on each task by taking the difference
        # between the finish and the start
        self.df['time_spent'] = (self.df.finished - self.df.started).astype('timedelta64[s]')

    def set_bar_grouping(self):
        """
        Creates a new bar graph Dataframe from the transformed DataFrame. It shows
        the total time spent on each task. It has the following structure:
        | TASK | TIME_SPENT |
        """

        # Make sure we have ran transform
        if self.df is None:
            self.transform()

        # Copy from our transformed DataFrame
        self.df_bar = self.df.copy(deep=True)

        # Group by task and sum the time spent for each task
        self.df_bar = self.df.groupby(['task'])[['time_spent']].sum().reset_index()
        return self.df_bar

    def set_line_grouping(self):
        """
        Creates a newline graph Dataframe from the transformed DataFrame. It shows
        the accumulative time spent on each task over time. It has the following structure:
        |||||
        """
        if self.df is None:
            self.transform()

        # Copy from our transformed DataFrame
        self.df_line = self.df.copy(deep=True)

        # Calculate the accumulative time spent at the end of each task, for each task
        self.df_line['total_time_spent_at_finish'] = self.df_line.groupby('task').time_spent.cumsum()

        # Shift by 1 to get the accumulative time spent at the start of each task.
        # This generates nulls for the first instance. We can set these nulls to 0 to indicate the
        # start of time
        self.df_line['total_time_spent_at_start'] = self.df_line.groupby(['task'])['total_time_spent_at_finish'].shift(1).fillna(0)

        # We want to merge the start and the finish into one column, and the total_time_spent_at_start and
        # total_time_at_finish into one column respectively.
        # Doing this by splitting the DataFrames and appending them together.
        # NOTE: There is almost definitely a better way to do this, but running out of time
        df_start = self.df_line[['task', 'started', 'total_time_spent_at_start']]
        df_start.rename(columns={'started': 'time', 'total_time_spent_at_start': 'total_time_spent'}, inplace=True)

        df_finish = self.df_line[['task', 'finished', 'total_time_spent_at_finish']]
        df_finish.rename(columns={'finished': 'time', 'total_time_spent_at_finish': 'total_time_spent'}, inplace=True)
        self.df_line = df_start.append(df_finish, ignore_index=True)#.sort_values('time')

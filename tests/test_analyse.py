import unittest
import datetime
from pandas import DataFrame
from pandas.util.testing import assert_frame_equal
from analyse import Analyse


class TestAnalyse(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # Construct our original data set
        cls.data = [{'user_id': 'test user', 'task': '1', 'tstamp': datetime.datetime(2018, 7, 26, 20, 00, 00, 000000)},
                    {'user_id': 'test user', 'task': '2', 'tstamp': datetime.datetime(2018, 7, 26, 20, 10, 00, 000000)},
                    {'user_id': 'test user', 'task': '1', 'tstamp': datetime.datetime(2018, 7, 26, 20, 15, 00, 000000)},
                    {'user_id': 'test user', 'task': '2', 'tstamp': datetime.datetime(2018, 7, 26, 20, 20, 00, 000000)},
                    {'user_id': 'test user', 'task': '1', 'tstamp': datetime.datetime(2018, 7, 26, 20, 40, 00, 000000)}
                    ]

        # Initalise our instance of Analyse
        cls.analyse = Analyse(cls.data)

        # Construct some DataFrames to use later in our unit test package

        # For comparing analyse.df_raw
        cls.raw_df = DataFrame(cls.data)

        # For comparing analyse.df_transform
        cls.transform_df = DataFrame([
            {'task': '1', 'started': datetime.datetime(2018, 7, 26, 20, 00, 00, 000000),
             'finished': datetime.datetime(2018, 7, 26, 20, 10, 00, 000000), 'time_spent': 600.00},
            {'task': '2', 'started': datetime.datetime(2018, 7, 26, 20, 10, 00, 000000),
             'finished': datetime.datetime(2018, 7, 26, 20, 15, 00, 000000), 'time_spent': 300.00},
            {'task': '1', 'started': datetime.datetime(2018, 7, 26, 20, 15, 00, 000000),
             'finished': datetime.datetime(2018, 7, 26, 20, 20, 00, 000000), 'time_spent': 300.00},
            {'task': '2', 'started': datetime.datetime(2018, 7, 26, 20, 20, 00, 000000),
             'finished': datetime.datetime(2018, 7, 26, 20, 40, 00, 000000), 'time_spent': 1200.00}
        ])
        cls.transform_df = cls.transform_df[['task', 'started', 'finished', 'time_spent']]

        # For comparing analyse.df_bar
        cls.bar_df = DataFrame([
            {'task': '1', 'time_spent': 900.00},
            {'task': '2', 'time_spent': 1500.00}
        ])
        cls.bar_df = cls.bar_df[['task', 'time_spent']]

        # For comparing analyse.df_line
        cls.line_df = DataFrame([
            {'task': '1', 'time': datetime.datetime(2018, 7, 26, 20, 00, 00, 000000), 'total_time_spent': 0.00},
            {'task': '2', 'time': datetime.datetime(2018, 7, 26, 20, 10, 00, 000000), 'total_time_spent': 0.00},
            {'task': '1', 'time': datetime.datetime(2018, 7, 26, 20, 15, 00, 000000), 'total_time_spent': 600.00},
            {'task': '2', 'time': datetime.datetime(2018, 7, 26, 20, 20, 00, 000000), 'total_time_spent': 300.00},
            {'task': '1', 'time': datetime.datetime(2018, 7, 26, 20, 10, 00, 000000), 'total_time_spent': 600.00},
            {'task': '2', 'time': datetime.datetime(2018, 7, 26, 20, 15, 00, 000000), 'total_time_spent': 300.00},
            {'task': '1', 'time': datetime.datetime(2018, 7, 26, 20, 20, 00, 000000), 'total_time_spent': 900.00},
            {'task': '2', 'time': datetime.datetime(2018, 7, 26, 20, 40, 00, 000000), 'total_time_spent': 1500.00},

        ])
        cls.line_df = cls.line_df[['task', 'time', 'total_time_spent']]

    def test_transform(self):
        """ Testing the transform_raw functionality """

        # Run transform_raw to get cleaned usable DataFrame
        self.analyse.transform()

        # Check that the DataFrames are the same
        assert_frame_equal(self.analyse.df, self.transform_df)

        # Check that the raw DataFrame is still in its correct state
        assert_frame_equal(self.analyse.df_raw, self.raw_df)

    def test_set_bar_grouping(self):
        """ Testing the bar graph grouping """

        # Run get_bar_grouping
        self.analyse.set_bar_grouping()

        # Check that the DataFrames are the same
        assert_frame_equal(self.analyse.df_bar, self.bar_df)

        # Check that the raw DataFrame is still in its correct state
        assert_frame_equal(self.analyse.df, self.transform_df)
        assert_frame_equal(self.analyse.df_raw, self.raw_df)

    def test_set_line_grouping(self):
        """ Testing the bar graph grouping """

        # Run set_line_grouping
        self.analyse.set_line_grouping()

        # Check that the DataFrames are the same
        # This fails as self.line_df.index is RangeIndex
        assert_frame_equal(self.analyse.df_line, self.line_df)

        # Check that the raw DataFrame is still in its correct state
        assert_frame_equal(self.analyse.df, self.transform_df)
        assert_frame_equal(self.analyse.df_raw, self.raw_df)

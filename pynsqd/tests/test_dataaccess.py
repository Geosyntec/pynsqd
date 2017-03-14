from pkg_resources import resource_filename

import numpy as np
import pandas

import pytest
import numpy.testing as nptest

from wqio import Location

import pynsqd
import pynsqd.dataAccess as da


class Test_NSQData:
    def setup(self):
        self.testfile = resource_filename('pynsqd.data', 'testdata.csv')

        self.data = da.NSQData(datapath=self.testfile)
        self.known_landuses = np.array([
            'Commercial', 'Freeway', 'Industrial', 'Institutional',
            'Open Space', 'Residential', 'Unknown'
        ])

        self.known_columns = [
            'epa_rain_zone', 'state', 'location_code', 'station_name',
            'jurisdiction_county', 'jurisdiction_city', 'primary_landuse',
            'secondary_landuse', 'percent_impervious', 'start_date',
            'days since last rain', 'precipitation_depth_(in)', 'season',
            'parameter', 'fraction', 'units', 'res', 'qual',
            'drainage_area_acres', 'latitude', 'longitude', 'station'
        ]

        self.known_commerical_copper_shape = (329, 22)

    def test_data(self):
        assert (hasattr(self.data, 'data'))
        assert isinstance(self.data.data, pandas.DataFrame)
        assert (self.data.data.columns.tolist() == self.known_columns)

    def test_data_season(self):
        known_seasons = ['autumn', 'spring', 'summer', 'winter']
        seasons = sorted(self.data.data['season'].unique().tolist())
        assert (seasons == known_seasons)

    def test_landuses(self):
        assert (hasattr(self.data, 'landuses'))
        assert isinstance(self.data.landuses, list)
        nptest.assert_array_equal(
            sorted(self.data.landuses),
            sorted(self.known_landuses)
        )

    def test_parameters(self):
        '''Doesn't test values -- too many to list out'''
        assert (hasattr(self.data, 'parameters'))
        assert isinstance(self.data.parameters, list)

    def test__check_col_bad(self):
        with pytest.raises(ValueError):
            self.data._check_col('junk')

    def test_check_col_good(self):
        self.data._check_col('res')

    def test_getColumnValues(self):
        plu = self.data.getColumnValues('primary_landuse')
        assert isinstance(self.data.landuses, list)
        nptest.assert_array_equal(
            sorted(self.data.landuses),
            sorted(self.known_landuses)
        )

    def test_getData(self):
        assert (hasattr(self.data, 'getData'))
        subset = self.data.getData(
            primary_landuse=self.known_landuses[0],
            parameter='Copper',
            fraction='Total'
        )
        assert isinstance(subset, pandas.DataFrame)
        assert (subset.columns.tolist() == self.known_columns)
        assert (subset.shape == self.known_commerical_copper_shape)

    def test_getData_as_Location(self):
        subset = self.data.getData(
            primary_landuse=self.known_landuses[0],
            parameter='Copper',
            fraction='Total',
            as_location=True
        )
        assert isinstance(subset, Location)

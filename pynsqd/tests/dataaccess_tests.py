import nose.tools as nt
import numpy as np
import numpy.testing as nptest
import pandas

from wqio import Location

import pynsqd.dataAccess as da

class test_NSQData:
    def setup(self):
        self.data = da.NSQData()
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

        self.known_commerical_copper_shape = (1153, 22)

    def test_data(self):
        nt.assert_true(hasattr(self.data, 'data'))
        nt.assert_is_instance(self.data.data, pandas.DataFrame)
        nt.assert_list_equal(self.data.data.columns.tolist(), self.known_columns)

    def test_data_season(self):
        known_seasons = ['autumn', 'spring', 'summer', 'winter']
        seasons = sorted(self.data.data['season'].unique().tolist())
        nt.assert_list_equal(seasons, known_seasons)

    def test_landuses(self):
        nt.assert_true(hasattr(self.data, 'landuses'))
        nt.assert_is_instance(self.data.landuses, list)
        nptest.assert_array_equal(
            sorted(self.data.landuses),
            sorted(self.known_landuses)
        )

    def test_parameters(self):
        '''Doesn't test values -- too many to list out'''
        nt.assert_true(hasattr(self.data, 'parameters'))
        nt.assert_is_instance(self.data.parameters, list)

    @nt.raises(ValueError)
    def test__check_col_bad(self):
        self.data._check_col('junk')

    def test_check_col_good(self):
        self.data._check_col('res')

    def test_getColumnValues(self):
        plu = self.data.getColumnValues('primary_landuse')
        nt.assert_is_instance(self.data.landuses, list)
        nptest.assert_array_equal(
            sorted(self.data.landuses),
            sorted(self.known_landuses)
        )

    def test_getData(self):
        nt.assert_true(hasattr(self.data, 'getData'))
        subset = self.data.getData(
            primary_landuse=self.known_landuses[0],
            parameter='Copper',
            fraction='Total'
        )
        nt.assert_is_instance(subset, pandas.DataFrame)
        nt.assert_list_equal(subset.columns.tolist(), self.known_columns)
        nt.assert_tuple_equal(subset.shape, self.known_commerical_copper_shape)

    def test_getData_as_Location(self):
        subset = self.data.getData(
            primary_landuse=self.known_landuses[0],
            parameter='Copper',
            fraction='Total',
            as_location=True
        )
        nt.assert_is_instance(subset, Location)

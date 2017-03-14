import os
import sys
import warnings
from pkg_resources import resource_filename

import numpy as np
import pandas

import wqio


__all__ = ['NSQData']


class NSQData(object):
    """ Class representing the National Stormwater Quality Dataset.

    Parameters
    ----------
    datapath : string, optional.
        Optional path the file to read. If not provided, the bundeled
        data will be used.

    """

    def __init__(self, datapath=None):
        # read my heavily modified version of the database
        datapath = datapath or wqio.download('nsqd')

        self.datapath = datapath
        self._cols = [
            'primary_landuse', 'secondary_landuse', 'season',
            'epa_rain_zone', 'parameter', 'units', 'qual', 'res'
        ]

        self._data = None
        self._landuses = None
        self._parameters = None

    @property
    def data(self):
        if self._data is None:
            landuses = {
                'CO': 'Commercial',
                'FW': 'Freeway',
                'ID': 'Industrial',
                'IS': 'Institutional',
                'OP': 'Open Space',
                'RE': 'Residential',
                'UNK': 'Unknown',
            }
            for key in list(landuses.keys()):
                landuses[key+'_MIX'] = landuses[key]

            df = pandas.read_csv(self.datapath, na_values=['--', "nan"])

            self._data = (
                df.assign(primary_landuse=df['primary_landuse'].replace(to_replace=landuses))
                  .assign(secondary_landuse=df['secondary_landuse'].replace(to_replace=landuses))
                  .assign(start_date=df['start_date'].apply(wqio.validate.timestamp))
                  .assign(season=df['start_date'].apply(wqio.utils.getSeason))
                  .assign(station='outflow')
            )
        return self._data

    @property
    def landuses(self):
        if self._landuses is None:
            self._landuses = self.getColumnValues('primary_landuse')
        return self._landuses

    @property
    def parameters(self):
        if self._parameters is None:
            self._parameters = self.getColumnValues('parameter')
        return self._parameters

    def _check_col(self, column):
        if column not in self.data.columns:
            raise ValueError("{} is not a valid column".format(column))

    def getColumnValues(self, column):
        self._check_col(column)
        return self.data[column].unique().tolist()

    def getData(self, check_vals=False, as_location=False, **kwargs):
        """ Returns a pandas.DataFrame copy of a filtered dataset

        Parameters
        ----------
        check_vals : bool, optional (default = False)
            If set to True, will warn users when filter values specified
            are not in the dataset.
        as_location : bool, optional (default = False)
            If True, data are returned as a wqio.Location object.
            Otherwise, a pandas.DataFrame is returned.
        **kwargs : keyword arguments
            Key-value pairs for filtering the dataset. Must be valid
            coumns in the dataset.

        Examples
        --------
        >>> import nsqd
        >>> swdata = nsqd.NSQData()
        >>> total_copper = swdata.getData(
        ... fraction='Total', parameter='Copper'
        ... )

        Notes
        -----
        Setting `check_vals` to True will prevent surprises, but likely
        slow down this method.

        See Also
        --------
        NSQData.getColumnValues to confirm that a column exists and return
            the distinct values inside that column.

        """

        # filter the data by landuse and parameteter
        definition = {}
        data = self.data.copy()
        for key in list(kwargs.keys()):
            self._check_col(key)
            val = kwargs.pop(key)
            if np.isscalar(val):
                val = [val]

            if check_vals:
                all_values = self.getColumnValues(key)
                for v in val:
                    if v not in all_values:
                        warnings.warn("{} is not in {}".format(v, key))

            definition[key] = val
            data = data[data[key].isin(val)]

        if as_location:
            loc = wqio.Location(data, rescol='res', qualcol='qual')
            loc.definition = definition
            return loc
        else:
            return data

    def to_DataCollection(self, *args, **kwargs):
        return wqio.DataCollection(self.data, *args, **kwargs)

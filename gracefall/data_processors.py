
import pandas as pd

__all__ = ['inject_aggregate_stats']


def inject_aggregate_stats(test_data):
    """
    This function will add rows to the measurements dataframe that correspond to averaging at different hierarchical
    levels for the data: globally, across each lot, and across individual chips.
    """
    data = test_data['Measurements']
    data['aggtype'] = 'None'
    # Averaging must be conducted on a per parameter type basis
    for prm in data['param'].unique():
        to_agg = data.loc[data['param'] == prm]
        for instant in data['time'].unique():
            # First calculate global level
            sub1 = to_agg.loc[to_agg['time'] == instant]
            avg, min, max = sub1['measured'].mean(), sub1['measured'].min(), sub1['measured'].max()
            to_add = pd.Series({'aggtype': 'Global', 'param': prm, 'device #': 0, 'chip #': 0, 'lot #': 0,
                                'time': instant, 'measured': avg})
            data = pd.concat([data, to_add.to_frame().T], ignore_index=True)
            # Now for each lot
            for lot in sub1['lot #'].unique():
                sub2 = sub1.loc[sub1['lot #'] == lot]
                avg = sub2['measured'].mean()
                to_add = pd.Series({'aggtype': 'Lot', 'param': prm, 'device #': 0, 'chip #': 0, 'lot #': lot,
                                    'time': instant, 'measured': avg})
                data = pd.concat([data, to_add.to_frame().T], ignore_index=True)
                # Finally chip level
                for chp in sub2['chip #'].unique():
                    sub3 = sub2.loc[sub2['chip #'] == chp]
                    avg = sub3['measured'].mean()
                    to_add = pd.Series({'aggtype': 'Chip', 'param': prm, 'device #': 0, 'chip #': chp, 'lot #': lot,
                                        'time': instant, 'measured': avg})
                    data = pd.concat([data, to_add.to_frame().T], ignore_index=True)

    test_data['Measurements'] = data
    return test_data

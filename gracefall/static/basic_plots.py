"""
Generators for common plots used to visualize parameter degradation data over time.
"""

from matplotlib import pyplot as plt

__all__ = ['gen_basic_line_chart', 'gen_stress_line_chart']

SECONDS_PER_HOUR = 3600


def gen_basic_line_chart(rprt, params: list[str], avg_similar_times: bool = False):
    manual_ranges = {}

    # First we convert the time values to be simple hours, as we want time as our horizontal axis for all plots
    test_meas = rprt
    test_meas['time'] = test_meas['time'].apply(lambda t: t / SECONDS_PER_HOUR)

    # Next create the figure and determine the device and lot quantities that were measured
    fig, axes = plt.subplots(1, len(params))
    num_chps = test_meas['chip #'].max() + 1
    num_lots = test_meas['lot #'].max() + 1

    i = 0
    for prm in params:
        prm_meas = test_meas.loc[test_meas['param'] == prm]
        # Environmental condition plots need to be handled separately, these are identified by having no circuit #'s
        # associated with the measurements
        if len(prm_meas['device #'].value_counts()) == 0:
            prm_meas = prm_meas.set_index('time')
            axes[i].plot(prm_meas['measured'])
        else:
            # Degradation parameter plots are generated with each measured circuit as a separate curve
            num_devs = prm_meas['device #'].max() + 1
            for lot in range(0, num_lots):
                for chp in range(0, num_chps):
                    for dev in range(0, num_devs):
                        dev_meas = prm_meas.loc[(test_meas['device #'] == dev) &
                                                  (test_meas['chip #'] == chp) &
                                                  (test_meas['lot #'] == lot)]
                        dev_meas = dev_meas.set_index('time')
                        axes[i].plot(dev_meas['measured'])

        # Now perform common figure formatting tasks
        axes[i].set_title(prm)
        axes[i].set_xlabel('time (hours)')
        if prm in manual_ranges:
            axes[i].set_ylim(*manual_ranges[prm])
        i += 1
    fig.tight_layout()
    

def gen_stress_line_chart(strs_data):
    pass

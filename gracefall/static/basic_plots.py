"""
Generators for common plots used to visualize parameter degradation data over time.
"""

import numpy as np
import seaborn as sb
from matplotlib import pyplot as plt

__all__ = ['gen_basic_line_chart', 'gen_stress_line_chart', 'gen_joint_time_plot',
           'gen_boxplot_init', 'gen_boxplot_degraded', 'gen_multiple_plot_with_inset',
           'gen_boxplot_vth_sensor', 'gen_joint_time_plot_vth_sensor']

SECONDS_PER_HOUR = 3600


def gen_basic_line_chart(rprt, params: list[str], ylims: dict = None):
    manual_ranges = ylims if ylims is not None else {}

    # Next create the figure and determine the device and lot quantities that were measured
    if type(params[0]) == list:
        fig, axes = plt.subplots(len(params), len(params[0]))
        params_flat = []
        for sublist in params:
            params_flat.extend(sublist)
    else:
        fig, axes = plt.subplots(1, len(params))
        params_flat = params

    i = 0
    for prm in params_flat:
        ax = axes[int(i / len(params[0]))][i % len(params[0])] if type(params[0]) == list else axes[i]
        prm_meas = rprt.loc[rprt['param'] == prm].copy()
        num_chps = prm_meas['chip #'].max() + 1
        num_lots = prm_meas['lot #'].max() + 1
        # We convert the time values to be simple hours, as we want time as our horizontal axis for all plots
        prm_meas['time'] = prm_meas['time'].apply(lambda t: t / SECONDS_PER_HOUR)

        # Environmental condition plots need to be handled separately, these are identified by having no circuit #'s
        # associated with the measurements
        if len(prm_meas['device #'].value_counts()) == 0:
            prm_meas = prm_meas.set_index('time')
            ax.plot(prm_meas['measured'])
        else:
            clrs = iter(plt.cm.get_cmap('plasma')(np.linspace(0, 1, num_chps * num_lots)))
            # Degradation parameter plots are generated with each measured circuit as a separate curve
            num_devs = prm_meas['device #'].max() + 1
            for lot in range(0, num_lots):
                for chp in range(0, num_chps):
                    c = next(clrs)
                    for dev in range(0, num_devs):
                        dev_meas = prm_meas.loc[(prm_meas['device #'] == dev) &
                                                  (prm_meas['chip #'] == chp) &
                                                  (prm_meas['lot #'] == lot)]
                        dev_meas = dev_meas.set_index('time')
                        ax.plot(dev_meas['measured'], c=c)

        # Now perform common figure formatting tasks
        ax.set_title(prm)
        ax.set_xlabel('time (hours)')
        if prm in manual_ranges:
            ax.set_ylim(*manual_ranges[prm])
        i += 1
    #plt.subplot_tool(fig)
    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.1, hspace=0.4)
    

def gen_stress_line_chart(strs_data):
    sb.set_theme(style='ticks', font='Times New Roman')
    sb.set_context('notebook')
    
    fig, p = plt.subplots(2, 1, sharex=True)

    measd = strs_data.copy()
    measd = measd.set_index('time')
    p[0].plot(measd.loc[measd['param'] == 'temp', 'measured'], color='darkred')
    p[1].plot(measd.loc[measd['param'] == 'vdd', 'measured'], color='goldenrod')


def gen_joint_time_plot(data, prms: dict, fill_zones: list[dict] = None):
    sb.set_theme(style='ticks', font='Times New Roman')
    sb.set_context('notebook')
    
    fills = [] if fill_zones is None else fill_zones
    
    fig, p = plt.subplots(1, 1)
    chp_colours = [['mediumblue', 'darkviolet'], ['lightseagreen', 'deeppink']]
    measd = {}
    for prm in prms:
        measd[prm] = data.loc[data['param'] == prm].copy()
        measd[prm]['time'] = measd[prm]['time'].apply(lambda t: t / SECONDS_PER_HOUR)
        measd[prm] = measd[prm].set_index('time')
        clrs = iter(plt.cm.get_cmap('plasma')(np.linspace(0, 0.9, 4)))
        for chp in measd[prm]['chip #'].unique():
            for lot in measd[prm]['lot #'].unique():
                # We convert the time values to be simple hours, as we want time as our horizontal axis for all plots
                p.plot(measd[prm].loc[(measd[prm]['chip #'] == chp) & (measd[prm]['lot #'] == lot), 'measured'], color=next(clrs), **prms[prm])

    for fill in fills:
        clrs = iter(plt.cm.get_cmap('plasma')(np.linspace(0, 0.9, 4)))
        for chp in measd[fill['u']]['chip #'].unique():
            for lot in measd[fill['u']]['lot #'].unique():
                to_fill_l = measd[fill['l']].loc[(measd[fill['l']]['chip #'] == chp) & (measd[fill['l']]['lot #'] == lot)]
                to_fill_u = measd[fill['u']].loc[(measd[fill['u']]['chip #'] == chp) & (measd[fill['u']]['lot #'] == lot)]
                p.fill_between(to_fill_l.index, to_fill_l['measured'], to_fill_u['measured'], color=next(clrs), alpha=0.2)
        
    p.axvline(1000, color='black', alpha=0.4, linestyle='dotted')
    p.axvspan(0, 1000, color='lightcoral', alpha=0.05)
    p.axvspan(1000, 1500, color='maroon', alpha=0.1)
    
    p.set_title('Die-to-Die Variability in Sensor Frequency - Four Chips')
    p.set(xlabel='Time (hours)', xlim=(0, 1500), ylim=(405, 465)) #, yticks=[0, -0.025, -0.05, -0.075, -0.1, -0.125, -0.15])
    p.set_yticks([])
    p.set_ylabel("Frequency (A.U.)")
    p.annotate('standard deviation region', xy=(890, 455.5), xytext=(600, 450), fontsize='small', ha='center', arrowprops={'color': 'black', 'width': 0.5, 'headwidth': 4})
    
    p.grid(visible=True, alpha=0.8, linestyle='dotted')

    p.text(500, 408, '<- 125°C, 1.1x nominal Vdd ->', fontsize='small', ha='center', color='maroon')
    p.text(1250, 408, '<- 130°C, 1.25x nominal Vdd ->', fontsize='small', ha='center', color='maroon')

    #p.legend(loc='lower left', fontsize=12)


def gen_joint_time_plot_vth_sensor(data, prms: dict, fill_zones: list[dict] = None):
    sb.set_theme(style='ticks', font='Times New Roman')
    sb.set_context('notebook')

    fills = [] if fill_zones is None else fill_zones

    fig, p = plt.subplots(1, 1)
    measd = {}
    for prm in prms:
        measd[prm] = data.loc[data['param'] == prm].copy()
        measd[prm]['time'] = measd[prm]['time'].apply(lambda t: t / SECONDS_PER_HOUR)
        measd[prm] = measd[prm].set_index('time')
        clrs = iter(plt.cm.get_cmap('plasma')(np.linspace(0, 0.9, 20)))
        for chp in measd[prm]['chip #'].unique():
            for lot in measd[prm]['lot #'].unique():
                # We convert the time values to be simple hours, as we want time as our horizontal axis for all plots
                p.plot(measd[prm].loc[(measd[prm]['chip #'] == chp) & (measd[prm]['lot #'] == lot), 'measured'],
                       color=next(clrs), **prms[prm])

    for fill in fills:
        clrs = iter(plt.cm.get_cmap('plasma')(np.linspace(0, 0.9, 20)))
        for chp in measd[fill['u']]['chip #'].unique():
            for lot in measd[fill['u']]['lot #'].unique():
                to_fill_l = measd[fill['l']].loc[
                    (measd[fill['l']]['chip #'] == chp) & (measd[fill['l']]['lot #'] == lot)]
                to_fill_u = measd[fill['u']].loc[
                    (measd[fill['u']]['chip #'] == chp) & (measd[fill['u']]['lot #'] == lot)]
                p.fill_between(to_fill_l.index, to_fill_l['measured'], to_fill_u['measured'], color=next(clrs),
                               alpha=0.2)

    p.axvline(1000, color='black', alpha=0.4, linestyle='dotted')
    p.axvspan(0, 1000, color='lightcoral', alpha=0.05)
    p.axvspan(1000, 1500, color='maroon', alpha=0.1)

    p.set_title('Die-to-Die Variability in Sensor Output Voltage - Four Chips')
    p.set(xlabel='Time (hours)', xlim=(0, 1500))
    p.set_yticks([])
    p.set_ylabel("Output Voltage (A.U.)")
    #p.annotate('standard deviation region', xy=(890, 455.5), xytext=(600, 450), fontsize='small', ha='center',
    #           arrowprops={'color': 'black', 'width': 0.5, 'headwidth': 4})

    p.grid(visible=True, alpha=0.8, linestyle='dotted')

    #p.text(500, 408, '<- 125°C, 1.1x nominal Vdd ->', fontsize='small', ha='center', color='maroon')
    #p.text(1250, 408, '<- 130°C, 1.25x nominal Vdd ->', fontsize='small', ha='center', color='maroon')

    # p.legend(loc='lower left', fontsize=12)


def gen_multiple_plot_with_inset(data, prms, insets):
    sb.set_theme(style='ticks', font='Times New Roman')
    sb.set_context('notebook')

    fig, p = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 2]}, sharex=True)
    measd = {}
    for prm in prms:
        measd[prm] = data.loc[data['param'] == prm].copy()
        # We convert the time values to be simple hours, as we want time as our horizontal axis for all plots
        measd[prm]['time'] = measd[prm]['time'].apply(lambda t: t / SECONDS_PER_HOUR)
        measd[prm] = measd[prm].set_index('time')
        p[0].plot(measd[prm]['measured'], **prms[prm])
        
    for inset in insets:
        measd[inset] = data.loc[data['param'] == inset].copy()
        # We convert the time values to be simple hours, as we want time as our horizontal axis for all plots
        measd[inset]['time'] = measd[inset]['time'].apply(lambda t: t / SECONDS_PER_HOUR)
        measd[inset] = measd[inset].set_index('time')
        p[1].plot(measd[inset]['measured'], **insets[inset])

    p[0].axvline(1000, color='black', alpha=0.4, linestyle='dotted')
    p[1].axvline(1000, color='black', alpha=0.4, linestyle='dotted')
    p[0].axvspan(0, 1000, color='lightcoral', alpha=0.05)
    p[1].axvspan(0, 1000, color='lightcoral', alpha=0.05)
    p[0].axvspan(1000, 1500, color='maroon', alpha=0.1)
    p[1].axvspan(1000, 1500, color='maroon', alpha=0.1)

    p[0].set_title('Ring Oscillator Matching using Interwoven Layout - Detail View')
    p[0].set(xlim=(0, 1500))
    p[0].get_xaxis().set_visible(False)
    p[1].set(xlabel='Time (hours)', xlim=(0, 1500)) #, yticks=[0, -0.025, -0.05, -0.075, -0.1, -0.125, -0.15])
    #p[0].set_ylabel(r"Frequency (A.U.)")
    p[1].set_ylabel(r"Frequency Difference (Megahertz)")
    p[0].set_yticks([])
    p[1].set(ylim=(-2, 2))

    p[0].grid(visible=True, alpha=0.8, linestyle='dotted')
    p[1].grid(visible=True, alpha=0.8, linestyle='dotted')

    p[1].text(500, -1.5, '<- 125°C, 1.1x nominal Vdd ->', fontsize=11, ha='center', color='maroon')
    p[1].text(1250, -1.5, '<- 130°C, 1.25x nominal Vdd ->', fontsize=11, ha='center', color='maroon')

    #p[1].legend(loc='upper left', fontsize=11)
    fig.subplots_adjust(hspace=0)
    
    
def gen_boxplot_init(data, boxes: list, plot_points: list = None, title: str = None):
    sb.set_theme(style='ticks', font='Times New Roman')
    sb.set_context('notebook')
    fig, p = plt.subplots(1, 1)

    if plot_points:
        for i in range(len(plot_points)):
            p.plot([i for j in range(len(plot_points[i]))], plot_points[i], color='sienna', marker='_',
                   markersize=15, linestyle='dotted')

    sb.set_palette(sb.color_palette(['blue', 'green']))
    ro_colours = ['mediumblue', 'darkviolet', 'lightseagreen', 'deeppink', 'cornflowerblue', 'mediumorchid', 'turquoise', 'hotpink']
    #sb.boxplot(data, x='param', y='measured', ax=p, boxprops={'alpha': 0.4}, fliersize=0, palette=ro_colours)
    sb.stripplot(data, x='param', y='measured', hue='param', ax=p, alpha=0.8, palette=ro_colours)

    p.set_title(title) #, fontweight='bold')
    
    p.set_xticks([0, 1, 2, 3, 4, 5, 6, 7], labels=['NMOS BTI', 'PMOS BTI', 'NMOS HCI', 'PMOS HCI', 'NMOS BTI', 'PMOS BTI', 'NMOS HCI', 'PMOS HCI'])
    p.annotate('|--------------------------- Standard ----------------------------|', xy=(1.5, 367), horizontalalignment='center', annotation_clip=False)
    p.annotate('|------------------ Complementary Biasing ------------------|', xy=(5.5, 367), horizontalalignment='center', annotation_clip=False)
    p.set_ylabel('Relative Frequency (Megahertz)')
    p.set_yticks([390, 410, 430, 450, 470, 490, 510, 530, 550], labels=['-80', '-60', '-40', '-20', '0', '+20', '+40', '+60', '+80'])
    p.set_xlabel(None)

    p.grid(visible=True, alpha=0.8, linestyle='dotted')
    p.legend().set_visible(False)
    fig.tight_layout()


def gen_boxplot_degraded(data, boxes: list, plot_points: list = None, title: str = None, means = None, devs = None):
    sb.set_theme(style='ticks', font='Times New Roman')
    sb.set_context('notebook')
    fig, p = plt.subplots(1, 1)

    if plot_points:
        for i in range(len(plot_points)):
            p.plot([i for j in range(len(plot_points[i]))], plot_points[i], color='sienna', marker='_',
                   markersize=20, linestyle='dotted')

    sb.set_palette(sb.color_palette(['blue', 'green']))
    ro_colours = ['grey', 'mediumblue', 'darkviolet', 'lightseagreen', 'deeppink', 'cornflowerblue', 'mediumorchid', 'turquoise', 'hotpink']
    #sb.boxplot(data, x='param', y='measured', ax=p, boxprops={'alpha': 0.4}, fliersize=0, palette=ro_colours)
    sb.stripplot(data, x='param', y='measured', hue='param', ax=p, alpha=0.8, palette=ro_colours)

    p.set_title(title)
    
    p.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8], labels=['Conventional RO', 'NMOS BTI', 'PMOS BTI', 'NMOS HCI', 'PMOS HCI', 'NMOS BTI', 'PMOS BTI', 'NMOS HCI', 'PMOS HCI'])
    p.annotate('|--------------------------- Standard ----------------------------|', xy=(2.5, -140), horizontalalignment='center', annotation_clip=False)
    p.annotate('|------------------- Complementary Biasing -------------------|', xy=(6.5, -140), horizontalalignment='center', annotation_clip=False)
    p.set_ylabel('Frequency Shift (Megahertz)')
    p.set_xlabel(None)

    p.grid(visible=True, alpha=0.8, linestyle='dotted')
    p.legend().set_visible(False)
    fig.tight_layout()


def gen_boxplot_vth_sensor(data, boxes, plot_points: list = None, title: str = None):
    sb.set_theme(style='ticks', font='Times New Roman')
    sb.set_context('notebook')
    fig, p = plt.subplots(1, 1)

    if plot_points:
        for i in range(len(plot_points)):
            p.plot([i for j in range(len(plot_points[i]))], plot_points[i], color='sienna', marker='_',
                   markersize=20, linestyle='dotted')

    sb.set_palette(sb.color_palette(['blue', 'green']))
    ro_colours = ['grey', 'mediumblue', 'darkviolet', 'lightseagreen', 'deeppink', 'cornflowerblue', 'mediumorchid',
                  'turquoise', 'hotpink']
    # sb.boxplot(data, x='param', y='measured', ax=p, boxprops={'alpha': 0.4}, fliersize=0, palette=ro_colours)
    sb.stripplot(data, x='param', y='measured', hue='param', ax=p, alpha=0.8, palette=ro_colours)

    p.set_title(title)

    p.set_xticks([0, 1, 2, 3],
                 labels=['NMOS BTI', 'PMOS BTI', 'NMOS HCI', 'PMOS HCI'])
    #p.annotate('|--------------------------- Standard ----------------------------|', xy=(2.5, -140),
    #           horizontalalignment='center', annotation_clip=False)
    #p.annotate('|------------------- Complementary Biasing -------------------|', xy=(6.5, -140),
    #           horizontalalignment='center', annotation_clip=False)
    p.set_ylabel('Frequency Shift (Megahertz)')
    p.set_xlabel(None)

    p.grid(visible=True, alpha=0.8, linestyle='dotted')
    p.legend().set_visible(False)
    fig.tight_layout()

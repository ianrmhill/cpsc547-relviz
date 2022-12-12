"""Generator functions that produce the Altair chart objects."""

import altair
from .pca_view_utils import create_table, seperate_ts

__all__ = ['gen_plot_view', 'gen_strs_view', 'gen_time_hint_view', 'gen_pca_view']


def gen_plot_view(deg_data, time_sel, components = None):
    # Setup multi-index ID column
    deg_data = deg_data.set_index(['param', 'circuit #', 'device #', 'lot #'])
    deg_data['sample #'] = deg_data.index
    deg_data = deg_data.reset_index()

    # Setup averaging selector
    agg_bind = altair.binding_select(options=['None', 'Global', 'Lot', 'Chip'], name='Averaging Mode')
    agg_sel = altair.selection_single(fields=['aggtype'], bind=agg_bind)

    # PCA selector
    seperate_ts(deg_data, set_idx=True) # give label to each time series
    multi_sel = altair.selection_multi(fields=['t_idx'])
    multi_opc = altair.condition(multi_sel,  altair.value(6.0), altair.value(4))

    # Setup series selection boxes
    lots = [lot for lot in deg_data['lot #'].unique()]
    chps = [chp for chp in deg_data['device #'].unique()]
    lot_sel = altair.selection_multi(fields=['lot #'])
    chp_sel = altair.selection_multi(fields=['device #'])

    # Set up the colouring for the data series based on lot number
    lot_colour = altair.condition(lot_sel, altair.Color('lot #:N', scale=altair.Scale(scheme='plasma'), legend=None), altair.value('lightgrey'))
    chp_saturation = altair.condition(chp_sel, altair.value('black'), altair.value('lightgrey'))

    # Set up legend selector charts for lots and chips
    lot_leg = altair.Chart(deg_data.loc[deg_data['aggtype'] == 'None']).mark_point(size=400, filled=True).encode(
        y=altair.Y('lot #', axis=altair.Axis(orient='right', tickCount=len(lots), grid=False), title='Lot Filter'),
        color=lot_colour
    ).add_selection(
        lot_sel
    ).properties()
    chp_leg = altair.Chart(deg_data.loc[deg_data['aggtype'] == 'None']).mark_point(size=400, filled=True).encode(
        y=altair.Y('device #', axis=altair.Axis(orient='right', tickCount=len(chps), grid=False), title='Chip Filter'),
        color=chp_saturation
    ).add_selection(
        chp_sel
    )

    # Define the full chart view
    #view = altair.Chart(deg_data.loc[deg_data['aggtype'] == 'None']).mark_line().encode(
    view = altair.Chart(deg_data).mark_line().encode(
        x=altair.X('time', title='Time', scale=altair.Scale(domain=time_sel)),
        y='measured',
        detail='sample #', # Has to be a non-existent column for all series to display individually
        color=lot_colour,
        size=multi_opc
    ).add_selection(lot_sel, 
                    chp_sel, 
                    agg_sel, 
                    multi_sel
                    ).\
        transform_filter(lot_sel).transform_filter(chp_sel).transform_filter(agg_sel).properties(
        height=400, width=1000)

    if not (components is None):
        components["lot_sel"] = lot_sel
        components["chp_sel"] = chp_sel
        components["agg_sel"] = agg_sel
        components["lot_colour"] = lot_colour
        components["multi_sel"] = multi_sel
        components["multi_opc"] = multi_opc

    # Assemble the chart with the legends
    legends = lot_leg | chp_leg
    return view | legends



def gen_time_hint_view(measurements):
    # Define how the user can interactively select the time region of interest to display on the main chart
    time_intrvl = altair.selection_interval(encodings=['x'], empty='none')

    # Generate the hint view plot, we want to only display a single series or two to avoid visual clutter
    # Just give the user a general trend that makes it clear what they will be selecting
    hint_view = altair.Chart(measurements).mark_line().encode(
        x=altair.X('time', title='', axis=altair.Axis(grid=False)),
        y=altair.Y('measured', aggregate='average', axis=altair.Axis(labels=False, tickCount=0, grid=False), title='')
    ).add_selection(
        time_intrvl
    ).properties(height=40, width=1000)

    # Need to return the selection object as well so that it can be linked to the X axes of other component views
    return hint_view, time_intrvl


def gen_strs_view(strs_data, time_selector):
    # For first release version, allow for up to 3 conditions to be visualized simultaneously
    # Could likely increase this limit by a lot with the current method of displaying little magnitude bars
    conditions = [col for col in strs_data.columns if col not in ['stress step', 'duration', 'start time', 'end time']]
    if len(conditions) > 3:
        conditions = conditions[:3]
        raise UserWarning(f"Test contains more than three stress conditions, "
                          f"only visualizing {conditions[0]}, {conditions[1]}, and {conditions[2]}.")

    color_def = {'temp': 'firebrick', 'vdd': 'goldenrod'}
    views = []
    for cond in conditions:
        # Construct a 0-centered vertical scale, this allows us to cleanly display the stress magnitudes
        # Currently the minimum value of the stress condition is displayed as 0 magnitude, may want to change this
        strs_data[cond + '_top'] = (strs_data[cond] - strs_data[cond].min())
        strs_data[cond + '_bot'] = - (strs_data[cond] - strs_data[cond].min())
        views.append(altair.Chart(strs_data).mark_rect(
            color=color_def[cond]
        ).encode(
            x=altair.X('start time', axis=altair.Axis(labels=False, tickCount=0, grid=False, title=''),
                       scale=altair.Scale(domain=time_selector) ),
            x2='end time',
            y=altair.Y(cond + '_bot', axis=altair.Axis(labels=False, tickCount=0, grid=False,
                                                       title=cond, titleAngle=0, titleAlign='right', titleY=15)),
            y2=cond + '_top',
            tooltip=[cond, 'duration']
        ).properties(height=20, width=1000))
    # Concatenate all the condition views
    return altair.vconcat(*views, spacing=2)


def gen_pca_view(ms, components):
    ms = ms.set_index(['param', 'circuit #', 'device #', 'lot #'])
    ms['sample #'] = ms.index
    ms = ms.reset_index()
    
    # format into altair friendly table
    table = create_table(ms)

    # area_chart = altair.Chart(table).mark_point(size=400, opacity=0.3, filled=True).encode(
    #     x="x",
    #     y="y",
    #     color="k_class:N"
    # )

    pnt_chart = altair.Chart(table).mark_point(filled=True).encode(
        x="x",
        y="y",
        color=components["lot_colour"],
        size=components["multi_opc"]
    )

    pca_plot = pnt_chart # + area_chart
    pca_plot.add_selection(
        components["lot_sel"],
        components["chp_sel"],
        components["agg_sel"],
        components["multi_sel"]
    ).transform_filter(components["agg_sel"])

    return pca_plot
    

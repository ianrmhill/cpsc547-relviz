"""Generator functions that produce the Altair chart objects."""

import altair
from .pca_view_utils import create_table

__all__ = ['gen_plot_view', 'gen_strs_view', 'gen_time_hint_view', 'gen_pca_view']


def gen_plot_view(deg_data, selectors=None):
    # Setup averaging selector
    agg_bind = altair.binding_select(options=['None', 'Global', 'Lot', 'Chip'], name='Averaging Mode')
    agg_sel = altair.selection_single(fields=['aggtype'], bind=agg_bind)

    # Setup series selection boxes
    lots = [lot for lot in deg_data['lot #'].unique()]
    chps = [chp for chp in deg_data['device #'].unique()]
    lot_sel = altair.selection_multi(fields=['lot #'])
    chp_sel = altair.selection_multi(fields=['device #'])

    # Set up the colouring for the data series based on lot number
    lot_colour = altair.condition(lot_sel, altair.Color('lot #:N', scale=altair.Scale(scheme='viridis'), legend=None), altair.value('lightgrey'))
    chp_saturation = altair.condition(chp_sel, altair.value('black'), altair.value('lightgrey'))

    # Set up legend selector charts for lots and chips
    lot_leg = altair.Chart(deg_data.loc[deg_data['aggtype'] == 'None']).mark_point(size=400, filled=True).encode(
        y=altair.Y('lot #', axis=altair.Axis(orient='right', tickCount=len(lots), grid=False), title='Lot Filter'),
        color=lot_colour
    ).add_selection(
        lot_sel
    ).properties(view={'fill': '#B0B0B0'})

    chp_leg = altair.Chart(deg_data.loc[deg_data['aggtype'] == 'None']).mark_point(size=400, filled=True).encode(
        y=altair.Y('device #', axis=altair.Axis(orient='right', tickCount=len(chps), grid=False), title='Chip Filter'),
        color=chp_saturation
    ).add_selection(
        chp_sel
    ).properties(view={'fill': '#B0B0B0'})

    # Define the full chart view
    #view = altair.Chart(deg_data.loc[deg_data['aggtype'] == 'None']).mark_line().encode(
    view = altair.Chart(deg_data).mark_line().encode(
        x=altair.X('time', title='Time', scale=altair.Scale(domain=selectors['interval'])),
        y='measured',
        detail='sample #', # Has to be a non-existent column for all series to display individually
        color=lot_colour
    ).add_selection(lot_sel, chp_sel, agg_sel).\
        transform_filter(lot_sel).transform_filter(chp_sel).transform_filter(agg_sel).properties(
        height=400, width=1000)

    if selectors is not None:
        selectors['lot'] = lot_sel
        selectors['chp'] = chp_sel
        selectors['agg'] = agg_sel
        selectors['colour'] = lot_colour

    # Assemble the chart with the legends
    legends = lot_leg | chp_leg
    return view | legends



def gen_time_hint_view(measurements, selectors):
    # Define how the user can interactively select the time region of interest to display on the main chart
    time_intrvl = altair.selection_interval(encodings=['x'], empty='none')
    selectors['interval'] = time_intrvl

    # Generate the hint view plot, we want to only display a single series or two to avoid visual clutter
    # Just give the user a general trend that makes it clear what they will be selecting
    hint_view = altair.Chart(measurements).mark_line(color='black').encode(
        x=altair.X('time', title='', axis=altair.Axis(grid=False)),
        y=altair.Y('measured', aggregate='average', axis=altair.Axis(labels=False, tickCount=0, grid=False), title='')
    ).add_selection(
        time_intrvl
    ).properties(height=40, width=1000)

    # Need to return the selection object as well so that it can be linked to the X axes of other component views
    return hint_view


def gen_strs_view(strs_data, selectors):
    # For first release version, allow for up to 3 conditions to be visualized simultaneously
    # Could likely increase this limit by a lot with the current method of displaying little magnitude bars
    conditions = [col for col in strs_data.columns if col not in ['stress step', 'duration', 'start time', 'end time']]
    if len(conditions) > 3:
        conditions = conditions[:3]
        raise UserWarning(f"Test contains more than three stress conditions, "
                          f"only visualizing {conditions[0]}, {conditions[1]}, and {conditions[2]}.")

    color_def = {'temp': 'firebrick', 'vdd': 'goldenrod', 'voltage': 'goldenrod',
                 'humidity': 'lightblue', 'pressure': 'purple', 'tau': 'brown'}
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
                       scale=altair.Scale(domain=selectors['interval']) ),
            x2='end time',
            y=altair.Y(cond + '_bot', axis=altair.Axis(labels=False, tickCount=0, grid=False,
                                                       title=cond, titleAngle=0, titleAlign='right', titleY=15)),
            y2=cond + '_top',
            tooltip=[cond, 'duration']
        ).properties(height=20, width=1000))
    # Concatenate all the condition views
    return altair.vconcat(*views, spacing=2)


def gen_pca_view(ms, selectors):

    # Format into altair friendly table
    pca_data = create_table(ms)

    # Setup up an area selection for the pca plot
    zoom_sel = altair.selection_interval(bind='scales')

    pnt_chart = altair.Chart(pca_data).mark_point(filled=True).encode(
        x=altair.X('x', title=''),
        y=altair.Y('y', title=''),
        detail='sample #',
        color=selectors['colour']
    ).add_selection(
        selectors['lot'],
        selectors['chp'],
        selectors['agg'],
        zoom_sel
    ).transform_filter(selectors['lot']).transform_filter(selectors['chp']).transform_filter(selectors['agg']
    ).properties(height=400, width=400)

    return pnt_chart
    

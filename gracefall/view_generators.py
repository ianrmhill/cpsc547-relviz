"""Generator functions that produce the Altair chart objects."""

import altair
from .pca_view_utils import create_table

__all__ = ['gen_plot_view', 'gen_strs_view', 'gen_time_hint_view', 'gen_pca_view']


def gen_plot_view(deg_data, selectors=None):
    # Setup series selection boxes
    lots = [lot for lot in deg_data['lot #'].unique()]
    chps = [chp for chp in deg_data['chip #'].unique()]
    lot_sel = altair.selection_multi(fields=['lot #'])
    chp_sel = altair.selection_multi(fields=['chip #'])

    # Single series selection box
    item_sel = altair.selection_single(on='mouseover', empty='none', fields=['sample #'])
    line_size = altair.condition(item_sel, altair.value(10), altair.value(2))

    # Set up the colouring for the data series based on lot number
    if len(lots) > 1:
        lot_colour = altair.condition(lot_sel, altair.Color('lot #:N', scale=altair.Scale(scheme='viridis'), legend=None), altair.value('lightgrey'))
        chp_colour = altair.condition(chp_sel, altair.value('black'), altair.value('lightgrey'))
    else:
        chp_colour = altair.condition(chp_sel, altair.Color('chip #:N', scale=altair.Scale(scheme='viridis'), legend=None), altair.value('lightgrey'))
        lot_colour = altair.condition(lot_sel, altair.value('black'), altair.value('lightgrey'))
    colourer = lot_colour if len(lots) > 1 else chp_colour

    # Set up legend selector charts for lots and chips
    lot_leg = altair.Chart(deg_data.loc[deg_data['aggtype'] == 'None']).mark_point(size=400, filled=True).encode(
        y=altair.Y('lot #', axis=altair.Axis(orient='right', tickCount=len(lots), grid=False), title='Lot Filter'),
        color=lot_colour
    ).add_selection(
        lot_sel
    ).properties(view={'fill': '#B0B0B0'})

    chp_leg = altair.Chart(deg_data.loc[deg_data['aggtype'] == 'None']).mark_point(size=400, filled=True).encode(
        y=altair.Y('chip #', axis=altair.Axis(orient='right', tickCount=len(chps), grid=False), title='Chip Filter'),
        color=chp_colour
    ).add_selection(
        chp_sel
    ).properties(view={'fill': '#B0B0B0'})

    # Define the full chart view
    #view = altair.Chart(deg_data.loc[deg_data['aggtype'] == 'None']).mark_line().encode(
    view = altair.Chart(deg_data).mark_line().encode(
        x=altair.X('time', title='Time (hours)', scale=altair.Scale(domain=selectors['interval'])),
        y=altair.Y('measured', title='Parameter Value', scale=altair.Scale(zero=False)),
        detail='sample #', # Has to be a non-existent column for all series to display individually
        color=colourer,
        size=line_size
    ).add_selection(lot_sel, chp_sel, selectors['agg'], selectors['prm'], item_sel).\
        transform_filter(lot_sel).transform_filter(chp_sel).transform_filter(selectors['agg']).transform_filter(selectors['prm']).properties(
        height=400, width=1000)

    if selectors is not None:
        selectors['lot'] = lot_sel
        selectors['chp'] = chp_sel
        selectors['colour'] = colourer
        selectors['item'] = item_sel

    # Assemble the chart with the legends
    legends = lot_leg & chp_leg
    return view | legends



def gen_time_hint_view(measurements, selectors):
    # Define how the user can interactively select the time region of interest to display on the main chart
    time_intrvl = altair.selection_interval(encodings=['x'], empty='none')
    selectors['interval'] = time_intrvl

    # Generate the hint view plot, we want to only display a single series or two to avoid visual clutter
    # Just give the user a general trend that makes it clear what they will be selecting
    hint_view = altair.Chart(measurements).mark_line(color='black').encode(
        x=altair.X('time', title='', axis=altair.Axis(grid=False, tickCount=0)),
        y=altair.Y('measured', aggregate='average', axis=altair.Axis(labels=False, tickCount=0, grid=False),
                   title='', scale=altair.Scale(zero=False)),
        detail='param'
    ).add_selection(
        time_intrvl,
        selectors['prm']
    ).transform_filter(selectors['prm']).properties(height=40, width=1000)

    # Need to return the selection object as well so that it can be linked to the X axes of other component views
    return hint_view


def gen_strs_view(strs_data, selectors):
    # For first release version, allow for up to 3 conditions to be visualized simultaneously
    # Could likely increase this limit by a lot with the current method of displaying little magnitude bars
    conditions = [col for col in strs_data.columns if col not in ['stress step', 'duration', 'start time', 'end time']]
    if len(conditions) > 4:
        conditions = conditions[:4]
        raise UserWarning(f"Test contains more than three stress conditions, "
                          f"only visualizing {conditions[0]}, {conditions[1]}, and {conditions[2]}.")

    color_def = {'temp': 'firebrick', 'vdd': '#228a78', 'voltage': '#228a78',
                 'humidity': '#2a3954', 'pressure': 'purple', 'tau': '#452f17'}
    views = []
    for cond in conditions:
        # Construct a 0-centered vertical scale, this allows us to cleanly display the stress magnitudes
        # Currently the minimum value of the stress condition is displayed as 0 magnitude, may want to change this
        range = strs_data[cond].max() - strs_data[cond].min()
        strs_data[cond + '_top'] = (strs_data[cond] - strs_data[cond].min() - (0.1 * range))
        strs_data[cond + '_bot'] = - (strs_data[cond] - strs_data[cond].min() - (0.1 * range))
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
    item_size = altair.condition(selectors['item'], altair.value(400), altair.value(100))

    # Setup up an area selection for the pca plot
    zoom_sel = altair.selection_interval(bind='scales')

    pnt_chart = altair.Chart(pca_data).mark_point(size=100, filled=True).encode(
        x=altair.X('x', title=''),
        y=altair.Y('y', title=''),
        detail='sample #',
        color=selectors['colour'],
        size=item_size
    ).add_selection(
        selectors['lot'],
        selectors['chp'],
        selectors['agg'],
        selectors['prm'],
        selectors['item'],
        zoom_sel
    ).transform_filter(selectors['lot']).transform_filter(selectors['chp']).transform_filter(selectors['agg']
    ).transform_filter(selectors['prm']).properties(height=400, width=400)

    return pnt_chart
    

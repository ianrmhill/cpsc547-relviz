"""Generator functions that produce the Altair chart objects."""

import altair

__all__ = ['gen_plot_view', 'gen_strs_view', 'gen_time_hint_view', 'gen_pca_view']


def gen_plot_view(deg_data, average=False):
    # Setup multi-index ID column
    deg_data = deg_data.set_index(['param', 'circuit #', 'device #', 'lot #'])
    deg_data['sample #'] = deg_data.index
    deg_data = deg_data.reset_index()

    if average:
        return altair.Chart(deg_data).mark_line().encode(
            x='time',
            y='average(measured)'
        )
    else:
         return altair.Chart(deg_data).mark_line().encode(
            x=altair.X('time', title='Time'),
            y='measured',
            detail='sample #',
            color='lot #'
        ).properties(height=400, width=1000)


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


def gen_pca_view(measurements):
    # TODO
    pass

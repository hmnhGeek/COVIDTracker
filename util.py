import altair as alt

def get_line_chart(df, line_color, xcol, ycol):
    # The basic line
    line = alt.Chart(df).mark_line(interpolate="basis").encode(
        x=alt.X(xcol, axis=alt.Axis(tickCount=5)),
        y=ycol,
        color=alt.value(line_color),
        tooltip=[xcol, ycol]
    )
    
    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=[xcol], empty='none')

    selectors = alt.Chart(df).mark_point().encode(
        x=xcol,
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    # Draw points on the line, and highlight based on selection
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = line.mark_text(align='right', dx=5, dy=-5).encode(
        text=alt.condition(nearest, ycol, alt.value(' '))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(df).mark_rule(color='gray').encode(
        x=xcol,
    ).transform_filter(
        nearest
    )

    return alt.layer(
        line, selectors, points, rules, text
    ).properties(
        width=600, height=300
    )
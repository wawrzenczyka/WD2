import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

__df = pd.read_csv(os.path.join(THIS_FOLDER, 'data', 'ceidg_data_formated.csv'))
__pkd_names = pd.read_csv(os.path.join(THIS_FOLDER, 'data', 'pkd_data.csv'), encoding='UTF-8')


def __build_hierarchical_dataframe(df, pkd_names, levels, value_column, color_columns=None):
    """
    Build a hierarchy of levels for Sunburst or Treemap charts.

    Levels are given starting from the bottom to the top of the hierarchy,
    ie the last level corresponds to the root.
    """
    df_all_trees = pd.DataFrame(columns=['id', 'parent', 'value', 'color'])
    for i, level in enumerate(levels):
        df_tree = pd.DataFrame(columns=['id', 'parent', 'value', 'color'])
        dfg = df.groupby(levels[:i + 1]).sum()
        dfg = dfg.reset_index()
        df_tree['id'] = dfg[level].copy()
        df_tree.id = df_tree.id.astype(str).str.replace(r'\.[0-9]*', '')
        df_tree = df_tree.merge(pkd_names \
                                .loc[pkd_names.typ == level],
                                left_on='id',
                                right_on='symbol'
                                )
        if i > 0:
            df_tree['parent'] = dfg[levels[i - 1]].copy()
        else:
            df_tree['parent'] = 'Wszystkie sekcje PKD'
        df_tree['value'] = dfg[value_column]
        df_tree['color'] = df.groupby(levels[:i + 1]).median().reset_index()[color_columns[0]]
        df_all_trees = df_all_trees.append(df_tree, ignore_index=True)
    total = pd.Series(dict(id='Wszystkie sekcje PKD', parent='',
                           value=df[value_column].sum(),
                           color=df[color_columns[0]].median(),
                           nazwa=''))
    df_all_trees = df_all_trees.append(total, ignore_index=True)
    return df_all_trees


def __format_strings(df_all_trees):
    df_all_trees = df_all_trees \
        .assign(years=df_all_trees.color // 12,
                months=df_all_trees.color % 12)
    df_all_trees = df_all_trees \
        .assign( \
        years=np.where(df_all_trees.years == 0,
                       '',
                       np.where(np.isin(df_all_trees.years, [1]),
                                '1 rok',
                                np.where(np.isin(df_all_trees.years, [2, 3, 4]),
                                         df_all_trees.years.astype(int).astype(str) + ' lata',
                                         df_all_trees.years.astype(int).astype(str) + ' lat')
                                )
                       ),
        months=np.where(df_all_trees.months == 0,
                        '',
                        np.where(np.isin(df_all_trees.months, [1]),
                                 ', 1 miesiąc',
                                 np.where(np.isin(df_all_trees.months, [2, 3, 4]),
                                          ', ' + df_all_trees.months.astype(int).astype(str) + ' miesiące',
                                          ', ' + df_all_trees.months.astype(int).astype(str) + ' miesięcy')
                                 )
                        )
    )

    df_all_trees = df_all_trees.assign(
        id=np.where(
            df_all_trees.typ == 'PKDMainSection',
            'Sekcja ',
            np.where(
                df_all_trees.typ == 'PKDMainDivision',
                'Dywizja ',
                np.where(
                    df_all_trees.typ == 'PKDMainGroup',
                    'Grupa ',
                    np.where(
                        df_all_trees.id == 'Wszystkie sekcje PKD',
                        '',
                        'Klasa '
                    )
                )
            )
        ) + df_all_trees.id
    )

    df_all_trees = df_all_trees.assign(
        parent=np.where(
            df_all_trees.typ == 'PKDMainDivision',
            'Sekcja ',
            np.where(
                df_all_trees.typ == 'PKDMainGroup',
                'Dywizja ',
                np.where(
                    df_all_trees.typ == 'PKDMainClass',
                    'Grupa ',
                    np.where(
                        df_all_trees.id == 'Wszystkie sekcje PKD',
                        '',
                        ''
                    )
                )
            )
        ) + df_all_trees.parent
    )

    return df_all_trees


def build_pkd_treemap(voivodeship=[]):
    df = __df

    if voivodeship is not None and voivodeship != []:
        df = df.loc[np.isin(df.MainAddressVoivodeship, voivodeship), :].reset_index(drop=False)

    pkd_names = __pkd_names

    levels = ['PKDMainSection',
              'PKDMainDivision']  # levels used for the hierarchical chart
    color_columns = ['DurationOfExistenceInMonths']
    value_column = 'Count'

    df_all_trees = __build_hierarchical_dataframe(df, pkd_names, levels, value_column, color_columns)

    df_all_trees = __format_strings(df_all_trees)

    median_duration = df_all_trees['color'].median()
    min_duration = df_all_trees['color'].min()
    max_duration = df_all_trees['color'].max()

    pkd_fig = go.Figure(go.Treemap(
        labels=df_all_trees['id'],
        parents=df_all_trees['parent'],
        values=df_all_trees['value'],
        branchvalues='total',
        marker=dict(
            colors=df_all_trees['color'],
            colorscale='balance',
            cmax=max_duration,
            cmid=median_duration,
            colorbar=dict(thickness=20, title='Przetrwane miesiące', titleside='right')),
        maxdepth=2,
        # texttemplate = "%{label}<br>%<b>%{customdata[2]}<\b><br>",
        customdata=df_all_trees[['years', 'months', 'nazwa']],
        hovertemplate='<b>%{label} </b> <br>%{customdata[2]} <br> - Liczba firm: %{value}<br> - Czas życia przeciętnej firmy: <b>%{customdata[0]}%{customdata[1]}</b>',
        name=''
    ))

    pkd_fig.update_layout(
        title={
            'text': "Czas życia przeciętnej firmy",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        margin=dict(l=20, r=20, t=70, b=20),
    )

    return pkd_fig

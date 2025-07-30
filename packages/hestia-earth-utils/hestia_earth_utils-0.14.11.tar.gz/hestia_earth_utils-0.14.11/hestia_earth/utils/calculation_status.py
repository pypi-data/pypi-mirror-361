import pandas as pd

from .cycle import get_cycle_emissions_calculation_status


def _emissions_color(row):
    color = (
        'red' if row['emissions-missing'] > 0 else
        'yellow' if row['emissions-incomplete'] > 0 else
        'lightgreen'
    )
    return [f"background-color: {color}"] * len(row)


def _emissions_with_status(cycle: dict):
    emissions = get_cycle_emissions_calculation_status(cycle)
    all_emissions = list(emissions.keys())
    # an emission is missing if there is no value
    missing_emissions = [
        k for k, v in emissions.items()
        if not v
    ]
    # an emission is incomplete if it has subvalues and at least one has no value
    incomplete_emissions = [
        k for k, v in emissions.items()
        if any([
            isinstance(vv, dict) and not vv for kk, vv in v.items()
        ])
    ]
    return {
        'emissions-total': len(all_emissions),
        'emissions-missing': len(missing_emissions),
        'emissions-incomplete': len(incomplete_emissions),
        'emissions': emissions,
    }


def get_nodes_calculations_status_dataframe(nodes: list, file_format: str = 'excel'):
    cycles_status = [
        {
            'id': cycle.get('@id') or cycle.get('id')
        } | _emissions_with_status(cycle)
        for cycle in nodes
        if (cycle.get('@type') or cycle.get('type')) == 'Cycle'
    ]
    df = pd.json_normalize(cycles_status, errors='ignore')
    return df.style.apply(_emissions_color, axis=1) if file_format == 'excel' else df

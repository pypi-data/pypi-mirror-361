from hestia_earth.schema import TermTermType

from .blank_node import get_blank_nodes_calculation_status


def get_cycle_emissions_calculation_status(cycle: dict):
    """
    Get calculation status for Cycle emissions included in the HESTIA system boundary.

    Parameters
    ----------
    cycle : dict
        The dictionary representing the Cycle.

    Returns
    -------
    dict
        A dictionary of `key:value` pairs representing each emission in the system boundary,
        and the resulting calculation as value, containing the recalculated `value`, `method` and `methodTier`.
        Note: if a calculation fails for an emission, the `value` is an empty dictionary.
    """
    status = get_blank_nodes_calculation_status(cycle, 'emissions', TermTermType.EMISSION)
    input_ids = [v.get('term', {}).get('@id') for v in cycle.get('inputs', [])]
    return {
        k: v | (
            {
                i: v.get(i, {}) for i in input_ids
            } if k.endswith('InputsProduction') else {}
        )
        for k, v in status.items()
    }

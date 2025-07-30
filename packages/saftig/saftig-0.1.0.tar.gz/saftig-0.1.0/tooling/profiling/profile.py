MULTITHREAD = True

from typing import Iterable
import saftig as sg
import numpy as np
from icecream import ic

DEBUG = False
IGNORE_FILTER_OPTIONS = {'coefficient_clipping', 'step_scale'}

# filter, additional_filter_config, skip_conditioning
FILTER_CONFIGURATIONS = [
    (sg.WienerFilter, {}, False),
    (sg.UpdatingWienerFilter, {'context_pre': 300}, True),
    (sg.UpdatingWienerFilter, {'context_pre': 300}, True),
    (sg.LMSFilter, {'normalized': True, 'coefficient_clipping': 10}, False),
    (sg.LMSFilter, {'normalized': False, 'coefficient_clipping': 10, 'step_scale': 0.001}, False),
    (sg.LMSFilterC, {'normalized': True}, False),
    (sg.LMSFilterC, {'normalized': False}, False),
    (sg.PolynomialLMSFilter, {'order': 1, 'coefficient_clipping': 10}, False),
    (sg.PolynomialLMSFilter, {'order': 2, 'coefficient_clipping': 10}, False),
    (sg.PolynomialLMSFilter, {'order': 3, 'coefficient_clipping': 10}, False),
]

if DEBUG:
    FILTER_CONFIGURATIONS = [
            (sg.WienerFilter, {}, False),
            (sg.LMSFilter, {'normalized': True}, False),
            (sg.UpdatingWienerFilter, {'context_pre': 1000}, True),
    ]

def filter_configs_to_str(configs):
    """ build documenting strings for the given list of configuations """
    def additional_filter_config_to_str(conf):
        if len(conf) == 0:
            return ''
        return '('+', '.join(f'{k}={v}' for k, v in conf.items() if k not in IGNORE_FILTER_OPTIONS)+')'
    return [f'{fc.filter_name} {additional_filter_config_to_str(settings)}' for fc, settings, _ignore_conditioning in configs]
filter_configuration_strings = filter_configs_to_str(FILTER_CONFIGURATIONS)

def run_profiling(config, n_samples, n_filter, n_channel, idx_target=0):
    """ execute a profiling run for specific configuration for a list of filter configurations
    to unwrap config list and replace irrelevant restuls with nans

    :param config: filter configurations as a list of (filter_instance, additional_filter_params, clear_conditioning_runtime)
                    setting clear_conditioning_runtime to True will set the conditioning runtime to np.nan
    :params n_samples, n_filter, n_channel, idx_target: passed on to saftig.measure_runtime()
    """
    filters = map(lambda x: x[0], config)
    additional_settings = map(lambda x: x[1], config)
    skip_conditioning = list(map(lambda x: x[2], config))

    results = sg.measure_runtime(filters, n_samples, n_filter=n_filter, n_channel=n_channel, additional_filter_settings=additional_settings, idx_target=idx_target)
    results = np.array(results)
    results[0,skip_conditioning] = np.nan
    return results

def profiling_scan(target:str,
                   target_values:Iterable[float],
                   other_values:dict,
                   filter_configs) -> np.array:
    """ scan through one variable and record the runtime of the selected filters

    :param target: the target variable; one of 'n_filter', 'n_samples', 'idx_target', 'n_channel'
    :param target_values: the list of values for the target parameter
    :param other_values: dict of remaining values (may contain the target, but that value will be overwritten)
    :param filter_configs: The filter configuration as required by run_profiling

    :return: list of run_profiling results as processing rate in Sps
            array dimensions: (target_value, stage, filter_method)
            stage is conditioning=0, applying=1
    :raises: AssertionError
    """
    all_values = ['n_filter', 'n_samples', 'idx_target', 'n_channel']
    assert target in all_values, f"target must be one of {all_values}"
    for key in all_values:
        assert (key == target) or (key in other_values), f"A {key} must be provided through target_values"

    results = []
    for target_value in target_values:
        other_values[target] = target_value

        result = run_profiling(filter_configs, **other_values)
        results.append(other_values['n_samples']/result)
    other_values = tuple((k, v) for k, v in other_values.items() if k!=target)
    return {'target': target,
            'target_values': target_values,
            'results': np.array(results),
            'filter_configs': filter_configs_to_str(filter_configs),
            'filter_names': [i[0].filter_name for i in filter_configs],
            'other_values': other_values,
            }

def run_and_save_scan(target, values, default_values, filter_config, **file_additions):
    results = profiling_scan(target, values, default_values, filter_config)
    np.savez(f'results/results_{target}_{"mt" if MULTITHREAD else "st"}.npz',
             multithreaded=MULTITHREAD,
             **results,
             **file_additions)

def main():
    print('n_filter')
    default_values = {'n_samples':int(1e4), 'n_channel': 1, 'n_filter': 128, 'idx_target': 0}
    n_filter_values = [10, 30, 100, 300, 1000]
    run_and_save_scan('n_filter', n_filter_values, default_values, FILTER_CONFIGURATIONS)

    print('n_channel')
    default_values = {'n_samples':int(1e4), 'n_channel': 1, 'n_filter': 32, 'idx_target': 0}
    n_channel_values = [1, 2, 3]
    run_and_save_scan('n_channel', n_channel_values, default_values, FILTER_CONFIGURATIONS, x_log=False)

    print('n_samples')
    default_values = {'n_samples':int(1e4), 'n_channel': 1, 'n_filter': 32, 'idx_target': 0}
    n_samples_values = np.array([1e3, 3e3, 1e4, 3e4], dtype=np.int64)
    run_and_save_scan('n_samples', n_samples_values, default_values, FILTER_CONFIGURATIONS)

if __name__ == "__main__":
    main()

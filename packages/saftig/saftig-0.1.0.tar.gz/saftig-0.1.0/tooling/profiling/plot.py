import numpy as np
import matplotlib.pyplot as plt
from icecream import ic
from glob import glob

MARKER_MAPPING = {
    'WF': 'o',
    'UWF': '^',
    'LMS': 'x',
    'LMS_C': 'P',
    'LMS_C': 'P',
    'PolyLMS': 'v',
}

if __name__ == "__main__":
    for fname in glob('results/*.npz'):
        results = np.load(fname)
        ic(fname, results)
        fname_core = '.'.join(fname.split('/')[-1].split('.')[:-1])

        target = results['target']
        target_values = results['target_values']
        data = results['results']
        other_values = results['other_values']
        filter_configs = results['filter_configs']
        filter_names = results['filter_names']
        x_log = results['x_log'] if 'x_log' in results else True
        multithreaded = results['multithreaded']

        filter_types = dict()

        fig, ax = plt.subplots(2, sharex=True, sharey=True, figsize=(10, 8))
        for idx_method, method in enumerate(['Conditioning', 'Application']):
            markers = [MARKER_MAPPING[fn] for fn in filter_names]
            for filter_name, dataset, label in zip(filter_names, data[:,idx_method,:].T, filter_configs):
                ax[idx_method].plot(target_values, dataset, marker=MARKER_MAPPING[filter_name], label=label)

            ax[idx_method].set_ylabel(f'Processing rate\n{method} [Sps]')
            if x_log:
                ax[idx_method].set_xscale('log')
            ax[idx_method].set_yscale('log')
            ax[idx_method].grid()

        ax[0].legend(ncol=3, loc=(0.1, 1.15))
        ax[1].set_xlabel(target)
        p1 = ('Multi-thread' if multithreaded else 'Single-thread')
        p2 = ', '.join([f'{k}={v}' for k, v in other_values])
        ax[0].set_title(p1 + ' ' + p2)
        plt.subplots_adjust(top=0.8)

        plt.savefig(f'plots/{fname_core}.png')

    #plt.show()

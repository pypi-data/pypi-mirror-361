import doctest
import saftig as sg

module_list = [
    sg.common,
    sg.evaluation,
    sg.wf,
    sg.uwf,
    sg.lms,
    sg.lms_c,
    sg.polylms,
]

def load_tests(_loader, tests, _ignore):
    """ load doctests as unittests """
    for module in module_list:
        tests.addTests(doctest.DocTestSuite(module))
    return tests

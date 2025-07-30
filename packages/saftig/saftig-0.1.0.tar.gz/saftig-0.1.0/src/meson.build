# load meson support for python
py = import('python').find_installation(pure: false)

# get numpy dependencies
numpy_dep = dependency('numpy', required: true)

# define build instructions for c extensions
extensions = py.extension_module(
  '_lms_c',
  'saftig/_lms_c/_lms_c.cpp',
  dependencies: numpy_dep,
  install: true,
  subdir: 'saftig',
)

python_sources = [
  'saftig/lms_c.py',
  'saftig/polylms.py',
  'saftig/wf.py',
  'saftig/evaluation.py',
  'saftig/__init__.py',
  'saftig/common.py',
  'saftig/lms.py',
  'saftig/uwf.py',
]

# actually install the python module
py.install_sources(
  python_sources,
  pure: false,
  subdir: 'saftig'
)

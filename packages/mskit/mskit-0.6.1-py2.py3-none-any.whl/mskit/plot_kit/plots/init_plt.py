import platform
import warnings

from matplotlib import rcParams


if (system := platform.system().lower()) == 'linux':
    rcParams['font.family'] = 'Liberation Sans'
elif system == 'windows':
    rcParams['font.family'] = 'sans-serif'
else:
    warnings.warn(f'')
    rcParams['font.family'] = 'sans-serif'

rcParams['font.sans-serif'] = ['Arial']
rcParams['font.size'] = 8.
rcParams['figure.dpi'] = 300

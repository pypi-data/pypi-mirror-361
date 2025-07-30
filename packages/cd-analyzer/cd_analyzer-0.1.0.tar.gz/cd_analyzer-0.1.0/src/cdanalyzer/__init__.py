# src/cdanalyzer/__init__.py

# 这样用户就可以通过 from cdanalyzer import tm_calc_cd 来使用
# 而不是 from cdanalyzer.analysis import tm_calc_cd
from .analysis import tm_calc_cd, plot_dtemp_cd, plot_single_wl_dtemp, sigmoid

print("CD Analyzer package loaded.") # 可以加一句加载信息，也可以不加
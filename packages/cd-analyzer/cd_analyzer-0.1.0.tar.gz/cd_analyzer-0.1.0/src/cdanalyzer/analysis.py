import pandas as pd
import numpy as np
import re
from pathlib import Path
import struct
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter
from scipy.signal import savgol_filter
from typing import List, Tuple, Dict, Any, Optional

def parse_dsx(filepath, debug=False):

    with open(filepath, 'rb') as f:
        content = f.read()

    # --- 1. & 2. 解析元数据和列名 (此逻辑对所有文件通用) ---
    metadata = {}
    metadata_matches = re.findall(b'#([^:]+):\s*([^\x00]+)', content)
    for key_bytes, value_bytes in metadata_matches:
        try:
            metadata[key_bytes.decode('ascii').strip()] = value_bytes.decode('ascii').strip()
        except UnicodeDecodeError:
            continue
    
    start_anchor = b'Misc_AutoShutter:1\x00'
    end_anchor = b'\x00Wavelength -en'
    start_pos = content.find(start_anchor)
    if start_pos == -1: return None
    start_of_cols_pos = start_pos + len(start_anchor)
    end_of_cols_pos = content.find(end_anchor)
    if end_of_cols_pos == -1: return None
    
    column_blob = content[start_of_cols_pos:end_of_cols_pos]
    potential_names = column_blob.split(b'\x00')
    data_column_candidates = []
    for s_bytes in potential_names:
        if not s_bytes: continue
        try:
            s = s_bytes.decode('ascii').strip()
            if s and ':' not in s and s.isprintable() and len(s) > 1 and not s.isdigit():
                data_column_candidates.append(s)
        except (UnicodeDecodeError, TypeError): continue

    column_names = ['Wavelength_nm']
    if data_column_candidates:
        for col in data_column_candidates:
            column_names.append(col.split(' ')[0].strip())
    
    if debug:
        print(f"[DEBUG] 解析出的原始列名顺序: {column_names}")

    if len(column_names) <= 1: return None

    # --- 3. 解析核心参数并根据文件类型动态计算指针 ---
    try:
        range_marker = b'-range\x00'
        range_pos = content.find(range_marker, end_of_cols_pos)
        num_points_pos = range_pos + len(range_marker)
        num_points = struct.unpack('<i', content[num_points_pos : num_points_pos + 4])[0]
        wavelength_data_start_pos = num_points_pos + 4
        
        wavelength_bytes_size = num_points * 4
        wavelength_end_pos = wavelength_data_start_pos + wavelength_bytes_size

        num_repeats = 1
        data_columns_start_pos = 0
        
        repeat_marker = b'Repeat -iter\x00'
        repeat_pos = content.find(repeat_marker)

        if repeat_pos != -1:
            # --- 情况 A: 这是一个多Repeat文件，Padding与N相关 ---
            if debug: print("[DEBUG] 检测到 'Repeat -iter' 标记，按“多Repeat文件”模式解析。")
            
            num_repeats_pos = repeat_pos + len(repeat_marker)
            num_repeats = struct.unpack('<i', content[num_repeats_pos : num_repeats_pos + 4])[0]
            
            # 动态计算Padding: Padding = 4 * N + 4
            dynamic_padding_size = 4 * num_repeats + 4
            
            data_columns_start_pos = repeat_pos + len(repeat_marker) + 4 + dynamic_padding_size

            if debug:
                print(f"[DEBUG] N = {num_repeats}, 动态计算出的Padding为: {dynamic_padding_size} 字节。")
            
        else:
            # --- 情况 B: 这是一个单Repeat文件，Padding固定为4 ---
            if debug: print("[DEBUG] 未检测到 'Repeat -iter' 标记，按“单Repeat文件”模式解析。")
            
            num_repeats = 1
            # 单Repeat文件在Wavelength数据后有一个固定的4字节填充
            SINGLE_REPEAT_PADDING_SIZE = 4
            data_columns_start_pos = wavelength_end_pos + SINGLE_REPEAT_PADDING_SIZE

    except (struct.error, TypeError, IndexError) as e:
        print(f"错误: 解析核心参数失败: {e}")
        return None
    
    if debug:
        print(f"[DEBUG] 数据点数 (num_points): {num_points}")
        print(f"[DEBUG] 重复次数 (num_repeats): {num_repeats}")
        print(f"[DEBUG] 数据列将从 {data_columns_start_pos} 开始读取。")

    # --- 4. & 5. 读取数据 ---
    results_data = [{} for _ in range(num_repeats)]
    
    # 读取Wavelength数据
    try:
        wavelengths = struct.unpack(f'<{num_points}f', content[wavelength_data_start_pos : wavelength_end_pos])
        for i in range(num_repeats):
            results_data[i]['Wavelength_nm'] = wavelengths
    except (struct.error, IndexError): return None
    
    current_pos = data_columns_start_pos
    
    data_columns = column_names[1:]
    for col_name in data_columns:
        if debug: print(f"\n[DEBUG] 正在读取列 '{col_name}' 的所有 repeats...")
        for i in range(num_repeats):
            try:
                col_bytes_size = num_points * 4
                col_data_block = content[current_pos : current_pos + col_bytes_size]
                
                if len(col_data_block) < col_bytes_size:
                     print(f"错误: 文件提前结束。在读取列 '{col_name}' (Repeat #{i+1}) 时数据不足。")
                     return None

                col_data = struct.unpack(f'<{num_points}f', col_data_block)
                results_data[i][col_name] = col_data
                current_pos += col_bytes_size

            except (struct.error, ValueError, IndexError) as e:
                print(f"错误: 读取列 '{col_name}' (Repeat #{i+1}) 数据时失败: {e}")
                return None
    
    # --- 6. 整理并返回结果 ---
    final_results = []
    final_column_order = column_names 

    for i in range(num_repeats):
        df = pd.DataFrame(results_data[i])
        final_results.append((df[final_column_order], metadata))

    return final_results



# --- 1. Sigmoid 函数 ---
# 保持不变，但添加了详细的文档字符串和类型提示
def sigmoid(x: np.ndarray, a: float, Tm: float, b: float, c: float) -> np.ndarray:
    """
    Sigmoid函数（玻尔兹曼函数），用于拟合蛋白解链曲线。

    公式: f(x) = a / (1 + exp((x - Tm) / b)) + c

    Parameters
    ----------
    x : np.ndarray
        自变量，通常是温度 (°C)。
    a : float
        曲线的总振幅（y轴变化范围）。
    Tm : float
        熔解温度（中点），即曲线拐点处的x值。
    b : float
        斜率因子，描述了过渡的陡峭程度。
    c : float
        曲线的垂直偏移量（y轴基线）。

    Returns
    -------
    np.ndarray
        计算出的y值。
    """
    return a / (1 + np.exp((x - Tm) / b)) + c

# --- 2. 绘制变温CD光谱图 ---
def plot_dtemp_cd(ax: plt.Axes, 
                  data: np.ndarray, 
                  temp_lst: List[float], 
                  factor: float = 1.0, 
                  add_colorbar: bool = True,
                  smooth: None | int = None) -> Tuple[plt.Axes, cm.ScalarMappable]:
    """
    在指定的坐标轴上绘制一系列变温CD光谱。

    Parameters
    ----------
    ax : plt.Axes
        用于绘图的matplotlib坐标轴对象。
    data : np.ndarray
        CD数据，第一列是波长，其余列是对应温度的CD信号。
        形状应为 (n_wavelengths, n_temperatures + 1)。
    temp_lst : List[float]
        与数据列对应的温度列表。
    factor : float, optional
        CD信号的缩放因子，默认为 1.0。
    add_colorbar : bool, optional
        是否在图旁添加表示温度的颜色条，默认为 True。

    Returns
    -------
    Tuple[plt.Axes, cm.ScalarMappable]
        返回原始的坐标轴对象和一个ScalarMappable对象（用于外部创建颜色条）。
    """
    min_temp, max_temp = min(temp_lst), max(temp_lst)
    norm = plt.Normalize(vmin=min_temp, vmax=max_temp)
    # 使用 'coolwarm' 或 'viridis' 等色谱图
    scalar_mappable = cm.ScalarMappable(norm=norm, cmap=cm.coolwarm)

    for i, temp in enumerate(temp_lst):
        x,y = data[:, 0], data[:, i + 1] * factor
        if smooth:
            y = savgol_filter(y,smooth,2)
        ax.plot(x,y, 
                color=scalar_mappable.to_rgba(temp), lw=2)

    if add_colorbar:
        cbar = plt.colorbar(scalar_mappable, ax=ax, orientation='vertical')
        cbar.set_label('Temperature (°C)', fontsize=14)
        cbar.ax.tick_params(labelsize=12)

    ax.set_xlabel("Wavelength (nm)", fontsize=16)
    ax.set_ylabel("CD (mdeg)", fontsize=16)
    ax.tick_params(labelsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    
    return ax, scalar_mappable

# --- 3. 绘制单波长解链曲线 ---
# 此函数在 tm_calc_cd 中已有类似功能，但作为一个独立的快速绘图工具也很有用。
def plot_single_wl_dtemp(ax: plt.Axes, 
                         data: np.ndarray, 
                         temp_lst: List[float], 
                         wl: float = 222.0, 
                         factor: float = 1.0, 
                         color: str = '#e57373'):
    """
    绘制指定单个波长的CD信号随温度的变化曲线。

    Parameters
    ----------
    ax : plt.Axes
        用于绘图的matplotlib坐标轴对象。
    data : np.ndarray
        CD数据，格式同 plot_dtemp_cd。
    temp_lst : List[float]
        温度列表。
    wl : float, optional
        要监测的波长，默认为 222.0 nm。
    factor : float, optional
        CD信号的缩放因子，默认为 1.0。
    color : str, optional
        曲线颜色，默认为 '#e57373' (红色系)。
    """
    # 找到最接近指定波长的索引
    index = np.argmin(np.abs(data[:, 0] - wl))
    actual_wl = data[index, 0]
    
    y = data[index, 1:] * factor
    x = np.array(temp_lst)
    
    ax.plot(x, y, color=color, lw=2.5, marker='o', markersize=5, linestyle='-')
    ax.set_title(f'Melting Curve at {actual_wl:.1f} nm', fontsize=16)
    ax.set_xlabel("Temperature (°C)", fontsize=16)
    ax.set_ylabel("CD (mdeg)", fontsize=16)
    ax.tick_params(labelsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)

# --- 4. Tm 计算与拟合 ---
# 这是改动最大的核心函数
def tm_calc_cd(data: np.ndarray, 
               temp_lst: List[float], 
               wavelength: str | float = 'auto', 
               ax: Optional[plt.Axes] = None,
               r2_threshold: float = 0.95) -> Dict[str, Any]:
    """
    通过对单波长解链曲线进行Sigmoid拟合来计算熔解温度(Tm)。

    该函数会自动选择信号变化最大的波长（当wavelength='auto'时），
    并使用智能初始值和参数边界进行稳健的非线性拟合。

    Parameters
    ----------
    data : np.ndarray
        CD数据，格式同 plot_dtemp_cd。
    temp_lst : List[float]
        温度列表。
    wavelength : str | float, optional
        用于计算的波长。
        - 'auto': 自动选择第一个和最后一个温度下信号差异最大的波长（推荐）。
        - float: 指定一个具体波长（如 222.0）。
        默认为 'auto'。
    ax : Optional[plt.Axes], optional
        如果提供，将在该坐标轴上绘制原始数据点和拟合曲线。默认为 None。
    r2_threshold : float, optional
        R-squared (R²) 值的阈值，低于此值的拟合被认为不可靠。默认为 0.95。

    Returns
    -------
    Dict[str, Any]
        一个包含拟合结果的字典：
        - 'Tm' (float): 计算出的熔解温度。如果拟合失败或不可靠，则为 np.nan。
        - 'params' (list | None): 拟合参数 [a, Tm, b, c]。失败则为 None。
        - 'r_squared' (float): 拟合的R²值。失败则为 np.nan。
        - 'wavelength' (float): 实际用于计算的波长。
    """
    # --- 步骤1: 确定用于拟合的波长和数据 ---
    if wavelength == 'auto':
        # 找到信号变化最大的波长
        signal_change = np.abs(data[:, 1] - data[:, -1])
        idx = np.argmax(signal_change)
    else:
        # 找到最接近指定波长的索引
        idx = np.argmin(np.abs(data[:, 0] - float(wavelength)))
    
    actual_wavelength = data[idx, 0]
    y_data = data[idx, 1:]
    x_data = np.array(temp_lst)
    
    print(f"--- Tm Calculation ---")
    print(f"Wavelength selected for fitting: {actual_wavelength:.1f} nm")

    # --- 步骤2: 智能生成初始猜测值 (p0) ---
    y_min, y_max = np.min(y_data), np.max(y_data)
    # 猜测c (offset)
    c_guess = y_data[-1] if y_data[0] > y_data[-1] else y_data[0]
    # 猜测a (amplitude)
    a_guess = y_max - y_min
    if y_data[0] > y_data[-1]: # 解链信号减小 (e.g., alpha-helix)
        a_guess = -a_guess
        c_guess = y_data[0]

    # 猜测Tm (midpoint)
    mid_y = (y_max + y_min) / 2.0
    tm_guess_idx = np.argmin(np.abs(y_data - mid_y))
    tm_guess = x_data[tm_guess_idx]
    
    # 猜测b (slope factor) - 通常是一个小的正数
    b_guess = 5.0
    
    p0 = [a_guess, tm_guess, b_guess, c_guess]
    print(f"Smart initial guess [a, Tm, b, c]: [{p0[0]:.2f}, {p0[1]:.2f}, {p0[2]:.2f}, {p0[3]:.2f}]")

    # --- 步骤3: 设置参数边界 (bounds) 以增加拟合稳健性 ---
    bounds = (
        [-np.inf, min(temp_lst) - 20, 0.1, -np.inf], # Lower bounds
        [np.inf,  max(temp_lst) + 20, 20,  np.inf]   # Upper bounds
    )

    # --- 步骤4: 执行曲线拟合 ---
    try:
        params, _ = curve_fit(sigmoid, x_data, y_data, p0=p0, bounds=bounds, maxfev=5000)
        
        # --- 步骤5: 评估拟合质量 (R-squared) ---
        residuals = y_data - sigmoid(x_data, *params)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y_data - np.mean(y_data))**2)
        if ss_tot == 0: # 避免除以零
            r_squared = 1.0 if ss_res == 0 else 0.0
        else:
            r_squared = 1 - (ss_res / ss_tot)
        
        Tm_fit = params[1]
        
        # --- 步骤6: 检查拟合结果是否合理 ---
        fit_is_reliable = True
        if r_squared < r2_threshold:
            print(f"Warning: R-squared ({r_squared:.3f}) is below the threshold ({r2_threshold}). The fit may be unreliable.")
            fit_is_reliable = False
        
        # 检查Tm是否在合理范围内（例如，在测量温度范围内）
        if not (min(temp_lst) < Tm_fit < max(temp_lst)):
            print(f"Warning: Fitted Tm ({Tm_fit:.2f}°C) is outside the experimental temperature range. The result is an extrapolation.")
            # 可以选择性地将此也视为不可靠
            # fit_is_reliable = False

        final_Tm = Tm_fit if fit_is_reliable else np.nan
        print(f"Fitted parameters: a={params[0]:.2f}, Tm={params[1]:.2f}, b={params[2]:.2f}, c={params[3]:.2f}")
        print(f"R-squared: {r_squared:.4f}")
        print(f"Final calculated Tm: {final_Tm:.2f} °C" if not np.isnan(final_Tm) else "Final Tm: Unreliable")
        
        results = {
            'Tm': final_Tm,
            'params': params,
            'r_squared': r_squared,
            'wavelength': actual_wavelength
        }

    except RuntimeError:
        print("Error: Curve fitting failed. Could not find optimal parameters.")
        results = {
            'Tm': np.nan,
            'params': None,
            'r_squared': np.nan,
            'wavelength': actual_wavelength
        }

    # --- 步骤7: 如果提供了ax，则绘图 ---
    if ax is not None:
        ax.scatter(x_data, y_data, s=40, color='black', label='Experimental Data', zorder=10, alpha=0.8)
        if results['params'] is not None:
            temp_fine = np.linspace(min(temp_lst), max(temp_lst), 200)
            ax.plot(temp_fine, sigmoid(temp_fine, *results['params']), 'r-', lw=2, label='Fitted Sigmoid Curve')
            
            # 添加文本框显示Tm和R²
            tm_text = f'Tm = {results["Tm"]:.2f} °C' if not np.isnan(results["Tm"]) else 'Tm = Unreliable'
            r2_text = f'R² = {results["r_squared"]:.4f}'
            
            ax.text(0.95, 0.95, f'{tm_text}\n{r2_text}',
                    transform=ax.transAxes, fontsize=12,
                    verticalalignment='top', horizontalalignment='right',
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8))

        ax.set_xlabel("Temperature (°C)", fontsize=16)
        ax.set_ylabel("CD (mdeg)", fontsize=16)
        ax.tick_params(labelsize=12)
        ax.legend(fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.6)
    
    print("-" * 22 + "\n")
    return results


def help_read_multifile(path):
    path = Path(path)
    f_lst = list(path.rglob("*.dsx"))
    data_dic = {}
    for fname in f_lst:
        data = parse_dsx(fname)[0][0]
        if 'buf' in fname.stem.lower():
            k = 'buffer'
        else:
            k = float(round(data['Temperature'].mean(),1))
        dic = {k:data[k] for k in ['Wavelength_nm','CircularDichroism','Temperature']}
        df_new = pd.DataFrame(dic)
        data_dic[k] = df_new
    new_dic = {}
    if 'buffer' in data_dic.keys():
        for k,v in data_dic.items():
            if k == 'buffer':
                continue
            v['CircularDichroism'] = v['CircularDichroism']-data_dic['buffer']['CircularDichroism']
            new_dic[k] = v
    k_lst = sorted(new_dic.keys())
    cd = np.dstack([new_dic[k]['CircularDichroism'].to_list() for k in k_lst])[0]
    wl = np.array(new_dic[k_lst[0]]['Wavelength_nm'].to_list())
    wl = wl.reshape(wl.shape[0],1)
    arr = np.concatenate([wl,cd],axis=1)
    arr0 = np.array([0]+k_lst)
    arr0 = arr0.reshape(1,arr0.shape[0])
    arr = np.concatenate([arr0,arr])
    return arr
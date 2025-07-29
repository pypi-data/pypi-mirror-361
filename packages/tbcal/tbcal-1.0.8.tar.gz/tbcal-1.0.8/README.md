# TB_model_calculation
计算 tight-binding 模型，并绘制交互式能带及场分布图

## 安装包：
安装本包：
pip install tbcal  
安装依赖：
pip install numpy

推荐安装（如果需要使用tbplot和jupyter）  
pip install plotly ipywidget dash  
pip install ipykernel  


## 案例：BBH 模型

python 代码：  
```python  
import numpy as np
from math import pi
import tbcal.tbmodel as tbm
import tbcal.tbcalculation as tbc
import tbcal.tbplot as tbp

n = 4       # 单个原胞内原子个数
h = tbm.tbsquare(n)   # 创建四方晶格紧束缚模型类的实例
N = 8       # 晶胞个数 N*N
h.N = N
w = 1       # 原胞内最近邻耦合系数
v = 2       # 原胞间最近邻耦合系数

# 添加耦合（厄米），1-2,2-1只写一次
# 格式为 h.add_coupling((delta_cell_x_index, delta_cell_y_index), atom1, atom2, coupling_strength)
h.add_coupling((0,0), 0, 1, w)
h.add_coupling((0,0), 1, 3, w)
h.add_coupling((0,0), 3, 2, w)
h.add_coupling((0,0), 2, 0, -w)
h.add_coupling((1,0), 1, 0, v)
h.add_coupling((1,0), 3, 2, v)
h.add_coupling((0,1), 3, 1, v)
h.add_coupling((0,1), 2, 0, -v)

# 原子坐标（默认原胞中心为(0,0)， 大小为1*1）
atom_position = [(-0.3,-0.3), (0.3,-0.3), (-0.3,0.3), (0.3, 0.3)] 

# 计算PBC能带
kx, ky = tbc.high_symmetry_line()  # 获取高symmetry line的k点（默认为M-X-Γ-M）
val,vec = tbc.get_val_vec(h.get_H_PBC, [kx,ky])  # 计算能带和本征矢量
num = [i//n for i in range(kx.shape[0]*n)]
x,y = h.get_site_pos('PBC', position = atom_position)  # 获取原子位置
# 绘制交互式能带图（Dash）
tbp.plot_interactive_bands_dash(num, val, vec, x, y, port = 8051)

# 计算投影能带
k = np.linspace(-pi,pi,101)
val,vec = tbc.get_val_vec(h.get_H_xPBC, k)
num = [i//n for i in range(k.shape[0]*n*N)]
x,y = h.get_site_pos('xPBC', position = atom_position)
tbp.plot_interactive_bands_dash(num, val, vec, x, y, port = 8052)

# 计算开边界能谱
val,vec = tbc.get_val_vec(h.get_H_OBC)
num = np.arange(val.shape[0])
x,y = h.get_site_pos('OBC', position = atom_position)
tbp.plot_interactive_bands_dash(num, val, vec, x, y, port = 8053)
```

Dash app 端口号可通过port参数调整，运行后会打印出网址，如：http://127.0.0.1:8051， ctrl+左键打开即可。

点击左侧能带点，更新右侧波函数图。点击 pin 按钮，在下方暂存波函数图，点击 clear all 按钮，清除下方所有图。下拉列表选择场分布颜色和波函数展示形式（模值/实部）。

页面如下：
![alt text](image.png)

tests文件夹中包含了四个案例：BBH model、haldane model、SSH model 拼接、non-hermitian model。

如果不想安装dash等库，不要使用 tbcal.tbplot。计算得到结果后另外画图，其他部分只依赖numpy库。
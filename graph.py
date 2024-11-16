import numpy as np
import plotly.graph_objects as go

# Tạo lưới điểm cho x và y
x = np.linspace(0, 5, 100)
y = np.linspace(0, 5, 100)
x, y = np.meshgrid(x, y)

# Điều kiện cho bất đẳng thức
z = 3*x + 2*y  # Hàm bề mặt

# # Tạo mask cho miền giá trị
mask = (x + y <= 4) & (x <= 2) & (y <= 3) & (x >= 0) & (y >= 0)
z_masked = np.where(mask, z, np.nan)

# Tạo bề mặt và miền giá trị
fig = go.Figure()

# Vẽ bề mặt 3D với colorscale hợp lệ
fig.add_trace(go.Surface(z=z_masked, x=x, y=y, opacity=0.5, colorscale='Viridis', name='Bề mặt z = 3x + 2y'))

# Cài đặt các thông số cho đồ thị
fig.update_layout(title='Miền giá trị của x và y và bề mặt z = 3x + 2y',
                  scene=dict(
                      aspectratio=dict(x=1, y=1, z=1),
                      xaxis_title='x',
                      yaxis_title='y',
                      zaxis_title='z',
                      xaxis=dict(range=[0, 5]),
                      yaxis=dict(range=[0, 5]),
                      zaxis=dict(range=[0, 20])
                  ))

# Hiển thị đồ thị
fig.show()


# import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D

# # Tạo lưới điểm cho x và y
# x = np.linspace(0, 5, 100)
# y = np.linspace(0, 5, 100)
# x, y = np.meshgrid(x, y)

# # Tạo hàm bề mặt
# z = 3*x + 2*y

# # Tạo mask cho miền giá trị
# mask1 = (x >= 0) & (y >= 0) & (x + y <= 4)
# mask2 = (x > 2) | (y > 3)
# z_masked1 = np.where(mask1, z, np.nan)
# z_masked2 = np.where(mask2, np.nan, z_masked1)
# # Tạo hình
# fig = plt.figure(figsize=(12, 8))

# # Vẽ miền giá trị 2D
# ax1 = fig.add_subplot(121)  # Trục 2D
# plt.fill_between(x[0], np.minimum(4 - x[0], 3), where=(x[0] <= 2), color='lightblue', alpha=0.5)
# plt.xlim(0, 5)
# plt.ylim(0, 5)
# plt.title('Miền giá trị của x và y')
# plt.xlabel('x')
# plt.ylabel('y')
# plt.axhline(0, color='black', linewidth=0.5, ls='--')
# plt.axvline(0, color='black', linewidth=0.5, ls='--')
# plt.grid()

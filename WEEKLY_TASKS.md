# 文化遗产数字化学习计划 - 周度任务清单（32周完整版）

**计划周期**：2025-12-01 ~ 2026-07-31（32周）  
**学习节奏**：每周 8-12 小时  
**版本**：v1.0（2025-11-26 生成）

---

## 第一阶段（第1-4周）：环境搭建与基础补强

### 第1周（2025-12-01 ~ 2025-12-07）：环境安装与验证

- [ ] **周一任务**：Conda 环境创建与 Python 依赖安装
  - 创建 conda 环境：`heritage_py`（Python 3.13）
  - 验证 `torch.cuda.is_available()` 返回 True
  - 验证 OpenCV 与 numpy 可导入
  - **关键检验**：运行 PyTorch GPU 检测脚本
  
- [ ] **周二任务**：Node.js 与 npm 安装（前端基础）
  - 验证 `node -v` 与 `npm -v`
  - 安装 npm 全局工具：`npm install -g vite`
  - **关键检验**：能否创建 Vite 项目

- [ ] **周三任务**：Docker Desktop 与数据库安装
  - 安装 Docker Desktop（Windows）
  - 验证 `docker --version`
  - 安装 MySQL 8.0 或 MongoDB（任选一个）
  - **关键检验**：Docker 能否启动容器

- [ ] **周四任务**：Blender 与 3D 工具安装
  - 下载并安装 Blender 4.0+
  - 安装 CloudCompare、MeshLab
  - 验证 Blender Python API 可用
  - **关键检验**：Blender 能否导出 glTF 格式

- [ ] **周五-周日任务**：VSCode 插件配置与环境检查
  - 安装推荐插件：Python、Pylance、Jupyter、Docker、REST Client
  - 配置 Python 默认解释器指向 conda 环境
  - 创建 `.env` 配置文件
  - **关键检验**：VSCode 能否正确识别 Python 解释器

**本周验收标准**：
- ✅ 能运行 `python -c "import torch; print(torch.cuda.is_available())"`
- ✅ 能创建并激活 Vite + React 项目
- ✅ Docker 可用，MySQL/MongoDB 可连接
- ✅ Blender 可打开并导出 glTF

**费曼讲解任务**：写一份 5-10 分钟讲稿解释"为什么文化遗产项目需要这些工具"

---

### 第2周（2025-12-08 ~ 2025-12-14）：Python 深入与 OpenCV 基础

- [ ] **周一-周二**：NumPy 与 Pandas 核心操作
  - NumPy：数组创建、切片、广播、统计操作
  - Pandas：DataFrame 读写、聚合、时间序列
  - 完成 3-5 个练习题
  - **输出物**：`week2_numpy_pandas_exercises.py`

- [ ] **周三-周四**：OpenCV 图像处理入门
  - 图像读写、色彩空间转换（RGB ↔ HSV ↔ Gray）
  - 基础滤波（高斯、中值）、边缘检测（Canny、Sobel）
  - 简单的图像修复（inpainting）试验
  - **输出物**：`week2_opencv_demo.py` + 处理前后对比图

- [ ] **周五-周六**：Matplotlib 数据可视化
  - 创建多种图表（线图、散点图、直方图）
  - 图像可视化（叠加）
  - **输出物**：`week2_visualization.py`

- [ ] **周日**：回顾与复习卡片
  - 用 Obsidian 或 OneNote 记录 5 张"费曼卡片"（概念理解）
  - 录制 3 分钟短视频讲解 OpenCV 一个使用场景

**本周验收标准**：
- ✅ 完成 OpenCV 修复 demo（处理有缺损区域的图像）
- ✅ 代码结构清晰，有 docstring 和注释
- ✅ 完成费曼讲解任务

---

### 第3周（2025-12-15 ~ 2025-12-21）：JavaScript 与 Three.js 入门

- [ ] **周一-周二**：JavaScript 基础与 HTML5 Canvas
  - ES6+ 语法（let/const、箭头函数、Promise、async/await）
  - DOM 操作、事件监听
  - Canvas 基础绘图
  - **输出物**：`week3_js_basics.html` + 简单 Canvas 演示

- [ ] **周三-周四**：Three.js 核心概念
  - Scene、Camera、Renderer 三大要素
  - Geometry、Material、Mesh 创建与操作
  - 灯光（光源、阴影）与相机控制
  - **输出物**：`week3_threejs_demo.html`（展示旋转立方体 + 照明）

- [ ] **周五**：glTF 格式加载
  - 使用 `GLTFLoader` 加载模型文件
  - 模型缩放、位置调整
  - **输出物**：`week3_gltf_loader.html`

- [ ] **周六-周日**：交互与性能初步
  - 鼠标控制（旋转、缩放）
  - 性能监测（FPS 显示）
  - 简单响应式设计
  - **输出物**：改进版 demo + 交互功能

**本周验收标准**：
- ✅ 本地 Three.js demo 能在浏览器中流畅运行
- ✅ 能加载外部 glTF 模型
- ✅ 完成鼠标交互功能

---

### 第4周（2025-12-22 ~ 2025-12-28）：Blender 导出与点云概念

- [ ] **周一-周二**：Blender 基础建模
  - 模型导入（OBJ、FBX）
  - 基础修饰符（Decimate 简化面数、Subdivision 细分）
  - **输出物**：简化后的文物模型 .blend 文件

- [ ] **周三-周四**：Blender 导出工作流
  - 导出为 glTF 2.0 格式
  - 贴图烘焙与导出
  - 验证导出模型能在 Three.js 中正确加载
  - **输出物**：`artifact_model.glTF` + `artifact_model.bin`

- [ ] **周五**：Open3D 点云基础
  - 点云文件格式（.ply、.pcd、.xyz）
  - 使用 Open3D 读取、下采样、统计滤波
  - 点云可视化
  - **输出物**：`week4_pointcloud_demo.py`

- [ ] **周六**：点云法线与简单重建
  - 估算点云法线
  - 简单 Poisson 表面重建
  - 导出为 mesh（.obj 或 .glTF）
  - **输出物**：重建的 mesh 文件

- [ ] **周日**：第一阶段总结
  - 对比四周学习成果
  - 记录遇到的问题和解决方案
  - 录制 5-7 分钟"环境与基础"总结视频

**本周验收标准**：
- ✅ Blender 导出的模型能在 Three.js 中正确显示
- ✅ 完成点云→mesh→glTF 完整流水线
- ✅ 所有代码上传至 GitHub（主分支或 `week1-4` 分支）

**第一阶段关键产出**：
- 📁 配置完整的开发环境
- 📁 OpenCV + Blender + Three.js 集成示例
- 📁 点云处理流水线脚本
- 🎥 5 分钟阶段总结视频

---

## 第二阶段（第5-17周）：图像 AI、点云处理与前端展示

### 模块 A（第5-8周）：图像预处理与计算摄影

#### 第5周（2025-12-29 ~ 2026-01-04）：相机校正与色彩处理

- [ ] **周一-周二**：相机标定基础
  - 棋盘标定、标定参数计算
  - 使用标定参数进行畸变矫正
  - **输出物**：`week5_camera_calibration.py`

- [ ] **周三**：图像色彩空间与白平衡
  - 色彩空间转换（RGB、HSV、YCrCb）
  - 白平衡算法（灰世界、完美反射）
  - **输出物**：色彩校正 demo

- [ ] **周四-周五**：直方图均衡化与对比度增强
  - CLAHE（限制对比度自适应直方图均衡化）
  - Gamma 校正
  - **输出物**：增强对比 demo

- [ ] **周六-周日**：本周总结与费曼讲解
  - 撰写实验报告（含图表对比）
  - 录制 4 分钟讲解视频

---

#### 第6-8周：数据增强与综合实验

- [ ] 数据增强技术（旋转、翻转、缩放、噪声注入）
- [ ] 创建增强后的文物图像数据集（200+ 张）
- [ ] **第一阶段验收**：图像预处理实验报告（8-10 页）+ 所有代码

---

## 后续阶段规划

- **模块 B（第9-12周）**：超分辨率与图像修复（PyTorch）
- **模块 C（第13-15周）**：点云处理（Open3D）
- **模块 D（第16-17周）**：Three.js 深入与交互
- **模块 E（第18-21周）**：后端 API（FastAPI/SpringBoot）
- **模块 F（第22-24周）**：数据库设计
- **模块 G（第25-27周）**：区块链确权原型
- **第四阶段（第28-32周）**：综合项目开发与部署

---

## 艾宾浩斯复习计划

| 学习天数 | 复习间隔 | 推荐复习形式 |
|---------|---------|----------|
| D0 | 首次学习 | 深入学习 + 记笔记 |
| D+1 | 次日 | 快速回顾（15 分钟） |
| D+3 | 第三天 | 做练习题（30 分钟） |
| D+7 | 一周后 | 讲解给他人（5 分钟视频） |
| D+14 | 两周后 | 完整复习 + 新应用（60 分钟） |
| D+30 | 一个月后 | 综合应用练习 |

---

## 资源链接

- Three.js: https://threejs.org/docs/
- Open3D: https://www.open3d.org/docs/
- FastAPI: https://fastapi.tiangolo.com/
- PyTorch: https://pytorch.org/tutorials/
- SRGAN: https://arxiv.org/abs/1609.04802
- ESRGAN: https://arxiv.org/abs/1809.00219

# Xue–Finke–Johansen：在线滚动控制 SMC、冻结重放与可认证的后向残差

## 来源、版本与实际阅读

- 研究员：Pro-C。归档日期：2026-11-27，Asia/Shanghai。
- Liwen Xue, Axel Finke, Adam M. Johansen, **Online Rolling Controlled Sequential Monte Carlo**。
- 精确版本：[arXiv:2508.00696v1](https://arxiv.org/abs/2508.00696v1)，提交于 2025-08-01 15:12:58 UTC。核验时官方历史仍只有 v1。PDF 扉页打印 August 4, 2025，不能用这个排版日期替代版本提交日期。
- 原始 [16 页 PDF](https://arxiv.org/pdf/2508.00696v1) 与 [TeX source](https://arxiv.org/src/2508.00696v1) 均已取得。主读者读完 `quasi-online.tex` 全部 581 行、缩写文件和 27 条实际书目。覆盖摘要、§§1–5、全部数学公式、Algorithms 1–4、Figures 1–8、致谢、data availability 和全部 references。没有附录、实验表、脚注或单独的 ORCSMC 定理证明。
- 视觉核对原始 PDF pp.1,5,7–14，覆盖全部算法、全部图及 Figure 7 的两个子图。原文有 8 个编号图，对应 9 个图形文件。书目在 pp.14–16。读完参考文献条目不等于读过这些论文的正文。
- 证据状态：**完整阅读该预印本**。TeX 中保留 JCGS 投稿模板配置，不能据此认定论文已获录用。未核实另一个正式出版全文。
- 论文没有发现 AI assistance 声明。不是 OpenAI 或 Anthropic 官方论文。本文新增的恒等式、残差界、受约束拟合方案均标为独立推导，不冒充原作者定理或形式化验证。
- 作者公开代码：[Sempreteamo/orc.smc](https://github.com/Sempreteamo/orc.smc/tree/main)。限定核对时 main 为 `e2727c14b70384229e461f1ad0dacae377b66b10`，2026-07-29，包版本 0.1.0。这个提交晚于 v1，README 还涉及 v1 没有的 Figure 9 和 adaptive 示例，未建立版本对应。只检查公开存在、目录、元数据和部分 README，没有安装、运行、完整实现审计或复现实验。
- 原始材料在忽略跟踪的 `literature/corpus/pro_c/xue2025orcsmc/`。本笔记与精确版本索引是提交成果。

## 1. 可以直接取用的构造

本文把离线 controlled SMC 的后向 proposal 学习搬到一个滚动窗口。每次新观测到达，先用学习粒子反复改进窗口内的引导函数，再冻结这些函数，从保留的估计边界重新采样整个窗口。窗口移出部分不再重做。[原文 §§2.4–3]

这个安排同时保留两件事：近期信息可以改进近期状态的计算方式，而原模型的未归一化目标仍由正确的重要性修正保留。固定窗口不是把所有较早观测从目标里删除。较早信息通过边界粒子测度继续进入当前推断。

本文有明确算法和数值展示，没有给出 ORCSMC 的时间一致误差定理、维数无关复杂度定理或 guide 学习收敛定理。最有用的严格接口是权重抵消。本笔记把它补写成三个可独立使用的结果：

1. 冻结边界和 guide 后，重新生成窗口的未归一化测度满足精确条件期望恒等式。
2. 完美后向 guide 消除窗口重放的条件方差，保留前缀的不确定性。
3. 可达支持上的统一后向残差界，给出显式的条件相对方差证书。

另给出一个保持对角二次参数数量的凸约束拟合方案，保证 Gaussian twisting 的可积性。它是可实现的文献工具，不是对 FP 核心架构的修改建议。

## 2. 原模型、目标与可计算性条件

固定观测序列 $y_{1:t}$。模型给定

\[
X_1\sim\mu,\qquad X_s\mid X_{s-1}=x\sim f_s(\cdot\mid x),
\qquad g_s(x):=g_s(y_s\mid x).
\]

令 $f_1(\cdot\mid x_0)=\mu$，初始虚拟状态无实际作用。写

\[
F_s\phi(x)=\int f_s(dx'\mid x)\phi(x'),
\qquad Q_s\phi(x)=F_s(g_s\phi)(x).
\]

未归一化状态测度为 $\gamma_s$，其质量

\[
Z_s=\gamma_s(1)=p(y_{1:s}).
\]

原文同时讨论当前 filtering、固定维度 smoothing marginals 和完整祖先路径的表示。[§2.1] 它们在存储上不是同一个任务。

给定正函数 $\psi_s$，twisted transition 是

\[
f_s^\psi(dx'\mid x)
=\frac{f_s(dx'\mid x)\psi_s(x')}{F_s\psi_s(x)}.
\]

需要明确保留以下接口条件：

- 在所有会使用的父状态上，$0<F_s\psi_s(x)<\infty$。初始步对应 $0<\mu(\psi_1)<\infty$。连续且严格为正并不单独保证积分有限。
- 能正确计算这些积分，并从对应的 twisted transition 采样。用未经修正的近似积分或近似 sampler 替换，不能直接继承下面的精确恒等式。
- 重采样的 offspring counts 满足给定权重下的条件无偏性。自适应 ESS 决策必须在本步抽样之前作出。
- 目标质量有限。以下归一化公式限定每步 $0<B_s<\infty$ 几乎处处，讨论相对方差时边界质量也严格为正。原文三个实验模型的 likelihood 严格为正且有限。一般允许零 likelihood 的模型需要另定零权重运行的处理方式，不能直接继续除以 $B_s$。

这些是已知模型下的推断条件，论文没有同时学习未知 transition、识别隐状态维度或证明未知模型的一致恢复。

## 3. Algorithm 1：把未来 preweight 推迟到下一步

上一层估计系统含粒子 $X_{s-1}^i$、归一化权重 $W_{s-1}^i$、祖先索引和 $\widehat Z_{s-1}$。定义

\[
a_i=F_s\psi_s(X_{s-1}^i),\quad
A_s=\sum_iW_{s-1}^i a_i,\quad
p_i=\frac{W_{s-1}^i a_i}{A_s}.
\]

原文 Algorithm 1 的实际计算顺序为：

1. normalizer 先乘 $A_s$。
2. 用 $p_i$ 算 ESS。若低于 $\kappa N$，按 $p_i$ 重采样父索引，并把子权重设为 $V_s^j=1/N$。否则保持父索引 $j\mapsto j$，置 $V_s^j=p_j$。
3. 从 $f_s^\psi(\cdot\mid X_{s-1}^{A_{s-1}^j})$ 生成 $X_s^j$。
4. 置

\[
w_s^j=V_s^j\frac{g_s(X_s^j)}{\psi_s(X_s^j)},\qquad
B_s=\sum_jw_s^j,
\]

\[
\widehat Z_s=\widehat Z_{s-1}A_sB_s,
\qquad W_s^j=w_s^j/B_s.
\]

初始 $W_0^i=1/N$，$\widehat Z_0=1$。实验采用 residual–multinomial resampling。[§2.4]

常见 twisted-potential 写法把 $F_{s+1}\psi_{s+1}$ 乘在时刻 $s$ 的 potential 上。这里把它推迟到第 $s+1$ 步的 preweight，因此当前更新不需要已经知道下一个 guide。原文说明这只是同一计算的重新分组。

$\psi_s\equiv1$ 退化为 bootstrap filter。$\psi_s=g_s$ 给出 fully adapted APF。文中引用 Guarniero–Johansen–Lee 2017 的 Proposition 1 支持 normalizer 无偏性，引用 Proposition 2 支持最优 guide 的零方差性质。本次没有例行全文重读这篇历史文献。

## 4. 独立推导一：未归一化的一步恒等式

定义

\[
\widehat\gamma_s(\varphi)
=\widehat Z_s\sum_jW_s^j\varphi(X_s^j).
\]

把上一节的两次权重更新代入，得到

\[
\widehat\gamma_s(\varphi)
=\widehat Z_{s-1}A_s
\sum_j V_s^j
\frac{g_s(X_s^j)\varphi(X_s^j)}{\psi_s(X_s^j)}.
\]

给定父状态和抽样前信息，twisted proposal 满足

\[
\mathbb E\left[
\frac{g_s(X_s)\varphi(X_s)}{\psi_s(X_s)}
\,\middle|\,X_{s-1}=x
\right]
=\frac{Q_s\varphi(x)}{F_s\psi_s(x)}.
\]

若不重采样，直接以 $p_i$ 求和。若重采样，条件无偏计数给出同样的 $p_i$ 加权和。因此

\[
\boxed{
\mathbb E[\widehat\gamma_s(\varphi)\mid
\text{过去生产粒子与本步冻结 guide}]
=\widehat\gamma_{s-1}(Q_s\varphi).
}
\]

证明中的消去是 $A_s p_i/a_i=W_{s-1}^i$。ESS 阈值只决定使用哪个条件无偏分支，不改变这个等式。对有界可测 $\varphi$ 和有限目标质量，所需可积性由非负质量界控制。

对祖先路径的版本，把 $Q_s$ 换为附加新状态的路径 kernel，论证相同。**无偏对象是带 normalizer 的测度，不是自归一化粒子平均，也不是 $\log\widehat Z_s$。**

这是对原文 Algorithm 1 的直接推导，不依赖数值图，也不是作者额外给出的新定理。

## 5. Algorithm 4：两套粒子的滚动执行

在日历时刻 $t$ 接收 $y_t$，令

\[
a=\max(1,t-L+1),\qquad \ell_t=\min(t,L).
\]

学习系统用 $\widetilde H$，估计系统用 $H$。已有窗口 guides warm start，新时刻 guide 初始为 1，终端 $\psi_{t+1}=1$。[§3, Algorithm 4]

1. 从 $\widetilde H_{t-1}$ 先推进一次学习 filter，得到新层 $\widetilde H_t$。
2. 重复 $K$ 次：从 $s=t$ 到 $a$ 后向拟合 guide，再从冻结的学习边界 $\widetilde H_{a-1}$ 正向重新生成 $\widetilde H_{a:t}$。
3. 冻结最后得到的全部 $\psi_{a:t}$，从估计边界 $H_{a-1}$ 用新随机数重新生成 $H_{a:t}$。
4. 输出当前 normalizer、过滤粒子及仍有保存的祖先信息。窗口移出部分不再更改。可丢弃过老 guide 和两套粒子。

后向拟合的点值目标是

\[
\psi_s^\star(x)\approx g_s(x)F_{s+1}\psi_{s+1}(x).
\]

Algorithm 3 只规定在当前学习粒子上生成这些目标，具体函数拟合在 §4.1 实现。没有证明有限 $K$ 改善每次估计风险，也没有证明迭代趋于最优 guide。

### 5.1 在线的信息含义

当前输出使用 $y_{1:t}$，不需要 $y_{t+1}$。$L$ 是回看和重做的窗口长度，不是要求等待 $L$ 个未来观测的输出延迟。

固定 $L$ 没有把目标改成 $p(x_t\mid y_{t-L+1:t})$。保留的边界估计仍编码较早观测。它限制近期计算的重新学习范围，有限粒子误差和祖先退化则仍然存在。

### 5.2 两套 filter 的正确条件依赖

估计 filter 通过 guide 依赖学习 filter，两者**不是无条件独立**。可固定整个学习随机性和观测，此时 guides 及其不同历史版本成为确定量。估计的每次 replay 使用新的条件随机性。

对给定输出时刻 $t$，状态层 $s$ 最终采用的 guide 版本来自日历时刻

\[
\min\{t,s+L-1\}.
\]

此前丢弃的估计窗口不再影响当前输出。当前保留前缀加窗口，等价于用这组确定 guides 从初始状态执行一次完整 APF。该等价只用于给定时刻的分布，不声称不同日历输出组成普通单次 APF 的同一条运行轨迹。

反复使用上一节的一步恒等式得到

\[
\mathbb E[\widehat\gamma_t(\varphi)
\mid\text{全部学习随机性},y_{1:t}]
=\gamma_t(\varphi),
\]

从而 $\mathbb E[\widehat Z_t]=Z_t$。这里要求学习系统仅由观测和自身随机流驱动，不读取估计粒子或估计随机流。估计 replay 在给定全部学习信息后使用新的条件随机性，遵循指定 kernels，且积分和重采样满足第 2 节条件。原文 Algorithm 4 的两套系统符合这个结构。下一小节允许依赖估计边界的 pilot，其条件期望右侧相应保留随机边界，不能混同为本节的确定目标。

### 5.3 更一般的冻结边界接口

给定一个已保存的边界

\[
\widehat\gamma_{a-1}
=\widehat Z_{a-1}\sum_iW_{a-1}^i\delta_{X_{a-1}^i},
\]

先用 pilot 得到并冻结窗口 guides，再独立重放窗口，则

\[
\boxed{
\mathbb E[\widehat\gamma_t(\varphi)
\mid\text{边界、pilot 与冻结 guides}]
=\widehat\gamma_{a-1}(Q_a\cdots Q_t\varphi).
}
\]

pilot 可以依赖该边界。关键是丢弃 pilot 的随机估计结果，把它的作用限定为选取 guides，并随后按正确条件分布重新生成生产窗口。

这个恒等式清楚区分 proposal 学习和最终估计。它也说明边界误差不会被无偏重放自动消除。

## 6. 独立推导二：完美窗口 guide 与总方差的分解

设

\[
\psi_{t+1}^\star=1,\qquad
\psi_s^\star=g_sF_{s+1}\psi_{s+1}^\star,
\quad s=t,\ldots,a.
\]

则

\[
F_a\psi_a^\star(x)=p(y_{a:t}\mid X_{a-1}=x).
\]

按下一节的路径恒等式，窗口输出精确等于

\[
\boxed{
\widehat Z_t=
\widehat Z_{a-1}
\sum_iW_{a-1}^i p(y_{a:t}\mid X_{a-1}^i).
}
\]

给定边界，其 replay 条件方差为零。若 $a=1$，边界是确定初始质量，这恢复完整最优 guide 的零方差情形。若 $a>1$，右侧仍由随机边界决定。

当相关二阶矩有限时，全方差公式把误差分为

\[
\operatorname{Var}(\widehat Z_t)
=\mathbb E\!\left[
\operatorname{Var}(\widehat Z_t\mid\text{冻结信息})
\right]
+\operatorname{Var}\!\left(
\widehat\gamma_{a-1}(Q_a\cdots Q_t1)
\right).
\]

学习 guide 可降低第一项。第二项要求改进保留边界或其近似质量，不能只从“窗口内完美控制”推出它也消失。

## 7. 独立推导三：后向残差的条件相对方差证书

定义冻结 guides 的乘法残差

\[
r_s(x)=\frac{g_s(x)F_{s+1}\psi_{s+1}(x)}{\psi_s(x)},
\quad a\le s<t,
\qquad r_t(x)=\frac{g_t(x)}{\psi_t(x)}.
\]

假设在 replay 的全部可达支持上已经认证

\[
0<l_s\le r_s(x)\le u_s<\infty.
\]

另设冻结后

\[
0<C_0=
\widehat Z_{a-1}\sum_iW_{a-1}^iF_a\psi_a(X_{a-1}^i)
<\infty.
\]

### 7.1 路径上的精确分组

使用第 3 节抽样后的归一化 $V_s^j$，下一步 preweight 满足

\[
B_s A_{s+1}
=\sum_jV_s^j
\frac{g_s(X_s^j)F_{s+1}\psi_{s+1}(X_s^j)}{\psi_s(X_s^j)}
=\sum_jV_s^j r_s(X_s^j).
\]

末端 $B_t=\sum_jV_t^j r_t(X_t^j)$。因此在每一条实际抽样路径上

\[
\widehat Z_t
=C_0\prod_{s=a}^t
\left[\sum_jV_s^j r_s(X_s^j)\right].
\]

每个方括号是 residual 的凸组合，故

\[
\boxed{
C_0\prod_{s=a}^t l_s
\le\widehat Z_t
\le C_0\prod_{s=a}^t u_s.
}
\]

该路径界只要求权重非负并归一化。条件无偏重采样用于识别其均值等于上一节的 checkpoint 目标。

### 7.2 不隐藏常数的相对方差界

一般地，若 $0<A\le U\le B$，均值为 $m$，则

\[
\operatorname{Var}(U)\le(B-m)(m-A).
\]

这是对 $(U-A)(B-U)\ge0$ 取期望。将右侧除以 $m^2$，在 $m\in[A,B]$ 上最大化，最优点为 $2AB/(A+B)$，所以

\[
\frac{\operatorname{Var}(U)}{m^2}
\le\frac{(B-A)^2}{4AB}.
\]

代入上一节的上下界并记

\[
R=\prod_{s=a}^t\frac{u_s}{l_s},
\]

得到

\[
\boxed{
\operatorname{CV}^2(\widehat Z_t\mid\text{冻结信息})
\le\frac{(R-1)^2}{4R}
=\sinh^2\!\left(
\frac12\sum_{s=a}^t\log\frac{u_s}{l_s}
\right).
}
\]

若各 $r_s$ 为正的状态无关常数，$R=1$，窗口条件方差为零。前节完美 guide 是常数都等于 1 的特例。正标量缩放各 guide 不改变 proposal 或最终估计，残差比 $u_s/l_s$ 也不受这类缩放影响。

若直接认证 $|\log r_s(x)-c_s|\le\epsilon_s$，则上述证书给出

\[
\operatorname{CV}^2\le\sinh^2\!\left(\sum_{s=a}^t\epsilon_s\right).
\]

这里的 $c_s$ 只是残差的标量中心，可以吸收入 guide 的标度。

### 7.3 证书的适用边界

这是全支持的条件性充分保证，不是从有限学习样本自动得到的泛化结论。原文 log-OLS 的训练残差小，不能直接代入 $l_s,u_s$。这也不是关于 $N\to\infty$ 的速率定理。

在无界 Gaussian 状态空间，非恒定二次 log-residual 通常无法同时具有有限上界和严格正的全局下界。因而该证书不自动覆盖原文所有数值设置。紧支持、经独立证明的 residual envelope 或其他专门尾部分析才能提供缺少的条件。若改用截断模型，还需另外核算目标变化的误差。

零边界质量导致恒零输出，但相对方差没有定义，故上面的正质量条件不能省略。

## 8. Gaussian twisting：可积性与可实施的约束拟合

原文 §4.1 使用

\[
\psi(x)=\exp(x^\top\mathsf A x+\mathsf b^\top x+\mathsf c),
\]

其中 $\mathsf A$ 对角，通过粒子点上的 log-quadratic least squares 拟合。共有 $p=2d+1$ 个系数。所有实验的潜在转移都是线性 Gaussian，observation likelihood 可以非 Gaussian。

### 8.1 精确积分条件

对基准 $\nu=N(m,B)$，直接完成平方得到必要且充分条件

\[
J=B^{-1}-2\mathsf A\succ0.
\]

此时记 $h=B^{-1}m+\mathsf b$，有

\[
\nu^\psi=N(J^{-1}h,J^{-1}),
\]

\[
\log\nu(\psi)
=\mathsf c-\tfrac12\log\det B-\tfrac12\log\det J
-\tfrac12m^\top B^{-1}m+\tfrac12h^\top J^{-1}h.
\]

转移步用其 covariance $B$，初始步需另外满足 $\Sigma^{-1}-2\mathsf A_1\succ0$。只限制 $\mathsf A$ 为对角矩阵，不保证这些正定性条件。原文没有完整说明如何强制它们。这里记录需要补全的数学接口，不据此断言未审计的 R 实现已经失败。

### 8.2 一个保守而凸的拟合方案

改用显式参数化

\[
\psi(x)=\exp\left(-\tfrac12 x^\top R x+u^\top x+c\right),
\qquad R=\operatorname{diag}(r_1,\ldots,r_d),\quad r_j\ge0.
\]

令学习点的 log-target 为

\[
z_n=\log g_s(x_n)+\log F_{s+1}\psi_{s+1}(x_n).
\]

要求这些训练点的 $z_n$ 均为有限实数，再求解

\[
\min_{r\ge0,u,c}
\sum_n\omega_n
\left[-\tfrac12\sum_jr_jx_{nj}^2+u^\top x_n+c-z_n\right]^2,
\qquad\omega_n\ge0.
\]

这是有线性不等式约束的凸二次问题，仍是 $2d+1$ 参数。对任意正定 $B$，$J=B^{-1}+R\succ0$，故积分和 twisted Gaussian 自动存在。guide 自身不需要能作为 Lebesgue 密度归一化，基准 Gaussian 的积分有限即可。

这个保守类可能降低拟合能力，不能保证优于原文拟合。它解决的是 proposal 是否有定义，而不是学习风险和样本复杂度。正标量缩放不改变 APF 输出，因此实现可在 log 域对 $c$ 作中心化，降低数值范围。该操作也不能代替精确积分条件。

### 8.3 维度成本

若 covariance 为稠密矩阵，每个新 guide 的 Gaussian 分解可需 $O(d^3)$，每粒子均值和采样可需 $O(d^2)$。若 covariance 与二次参数均为对角，积分和噪声采样可降至线性操作，但稠密动力学矩阵乘状态仍可需 $O(d^2)$。

普通稠密最小二乘的典型算术成本为 $O(Np^2+p^3)$，受约束求解器另有自身工作量。参数数量是 $O(d)$，并不推出训练或传播总成本也是 $O(d)$。这些是本笔记的结构核算，不是论文测出的耗时结果。

## 9. 每个观测的执行成本与存储

按 Algorithm 4 每次均输出估计的版本，日历时刻 $t$ 有

\[
\boxed{1+(K+1)\ell_t\text{ 次 APF 单步更新}},
\qquad
\boxed{K\ell_t\text{ 次 guide 拟合}}.
\]

其中 1 是学习 filter 的新层延伸，$K\ell_t$ 是学习重放，最后 $\ell_t$ 是估计重放。因此若一次 APF 与拟合的成本分别记为 $C_{\rm APF},C_{\rm fit}$，总成本为

\[
[1+(K+1)\ell_t]C_{\rm APF}+K\ell_t C_{\rm fit},
\]

另加管理和输出。固定 $L,K,N,d$ 及固定成本子程序时，它不随完整历史长度 $t$ 增长。论文没有实际测量响应延迟或吞吐量，因此 “real-time” 在这里首先是这个算法成本性质。

启用 discard 后，两套系统各保留边界与窗口约 $L+1$ 层，粒子、权重、祖先索引成本为 $O(LNd)$，guide 存储为 $O(Lp)$，再加拟合工作空间。无限时域的“把全部 $\psi_1,\psi_2,\ldots$ 初始化为 1”应实现为按需默认值，不能实际分配无限数组。

若保留完整 $X_{1:t}$ 祖先路径以输出任意旧时刻平滑边缘，则存储随历史增长。原文在 Algorithm 4 后明确承认 optional discard 与全历史 smoothing 不可同时保留。Figures 4–5 的早期时刻平滑展示不构成固定内存运行的证据。

若只在部分时刻输出，原文允许非输出时刻省略估计窗口的大部分重放，但必须按规定推进即将冻结的最早窗口层。学习窗口的 $K$ 次循环仍存在。比较成本应明确使用哪个输出协议。

## 10. 实验证据与实际比较范围

原文全部实验使用对角二次 guide，$K=5$，总述为 100 次重复。Figure 4 特别注明每个维度仅展示一次运行。没有单独的计时、硬件、内存或统计置信区间定义表。[§4]

### 10.1 线性 Gaussian

$T=100$，$d\in\{2,4,8,16,32,64\}$，ORCSMC $N=1000$。对角模型的动力学矩阵为 $0.415I$，非对角模型为 $A_{ij}=0.415^{|i-j|+1}$。初始和相关噪声 covariance、观测矩阵按正文设为 identity。[§4.2]

比较 BPF 使用 $N=320000$，离线 CSMC 使用 $N=14000$。作者称它们用于平衡计算成本，但没有给出每个维度、lag 的严格等时依据。增大 $L$ 也增加拟合、重放和存储，故 lag 消融不是固定总资源的消融。

离线 CSMC 从一开始可以用完整 $y_{1:T}$ 学 guide，ORCSMC 按到达顺序更新。最终 $Z_T$ 的比较有意义，但不具有相同的在线信息时序。

| 图 | 实际测量与边界 |
|---|---|
| Figure 1，p.9 | 对角模型的 $\widehat Z_T/Z_T$。Kalman 给出真值。高维 BPF 的箱线图接近零，不能据有限重复宣布理论有偏，可能未采到重尾大估值，数值下溢也未独立评估。 |
| Figure 2，p.10 | 非对角模型的相对 normalizer。ORCSMC 明显改善该 BPF 配置，离线 CSMC 常更集中。受限对角 guide 与非对角依赖的失配保留在比较中。 |
| Figure 3，p.10 | 相对 normalizer 的 RMSE。实际横轴另含 $L=3,5$，正文主要设置只列 2、4、8、16。误差条构造未说明。曲线改善后趋平或波动，不能称为严格单调定理。 |
| Figure 4，p.11 | 每个维度一次运行，第一坐标的若干标准化平滑边缘与标准正态比较。不是全部坐标或联合 law 的检验。 |
| Figure 5，p.12 | $s=1,T/2,T$ 的一维坐标边缘 $W_1$，再跨坐标平均。不是 $d$ 维联合 $W_1$。高维的早期边缘误差明显高于末时刻。 |

### 10.2 Stochastic volatility

一维 Gaussian AR transition，$\alpha=.986$，$\sigma=.13$，observation 为 $N(0,\beta^2\exp x)$，$\beta=.69$。用 1981-10-01 至 1985-06-28 的 945 个工作日汇率，ORCSMC $N=200$。参数借用旧文献对完整序列的近似后验众数，是给定参数的在线状态推断，不是在线学习这些参数。[§4.3]

Figure 6 的纵轴实际为 log-normalizer，只比较 ORCSMC 的不同 $L$。没有真值和 BPF 或 CSMC 对照。图支持该数据设置下更长窗口的估计分散度减小，不能单独认证准确度或无偏性。

### 10.3 Binomial-logistic observation

$Y_t\mid X_t=x\sim\operatorname{Bin}(50,\operatorname{sigmoid}(x))$，潜在 AR 参数 $\alpha=.99$，$\sigma^2=.11$。多维扩展使用 $A=.99I$、$B=.11I$ 和坐标 likelihood 的乘积，因此坐标彼此独立。[§4.4]

这是明确数学状态空间模型，不提供耦合神经系统计算机制的证据。

- Figure 7$a$，p.13：单维 ESS 轨迹，图内标示 resampling $N/2$ 线，没有跨重复置信带。
- Figure 7$b$，p.13：单维 log-normalizer，比较不同窗口。
- Figure 8，p.14：多维 log-normalizer，维度至 64，仍只比较 ORCSMC 的不同窗口，没有真值或其他方法基线。

正文没有完整、清楚地列出这一实验族每个配置的 $N,T$。不能从单个 ESS 图的轴范围替作者补写全部多维配置。

### 10.4 经验结论的等级

这些是概念验证实验。Gaussian 模型的真值比较与正确性声明相容，SV 和 binomial 的 log-normalizer 箱线图则不检验 normalizer 无偏性。未做本地复现、独立统计尾部核查或严格资源匹配。原文的性能结论应限于这些已报告模型和参数，不提升为一般高维过滤规律。

## 11. 原文呈现细节与版本边界

1. Algorithms 2 和 4 的祖先路径初始条件打印为 $X_1^{(n)}:=X_t^n$。按其递归定义应是 $X_1^{(n)}:=X_1^n$。后续论证采用一致的路径语义。
2. Algorithm 2 每轮先 forward 再 backward，返回最后一轮 forward 的粒子。按打印程序，最后一次 backward 更新不用于该返回值，返回 estimate 使用此前 $K-1$ 次学习循环形成的 guide。Algorithm 4 则在最后学习后另做 estimation replay。没有把这处顺序差异归咎于未审计实现。
3. SV 段落的 transition 条件下标有一处写成当前状态，按模型定义应为上一状态。
4. 对角二次 guide 的可积性条件和拟合负对数时的系数符号需要显式区分，不能只靠“Gaussian conjugacy”略去。
5. Figure 3 的 lag 配置和 Figure 6 的 log 纵轴按实际图记录。当前公开代码晚于论文，README 的新图号不用于补齐 v1 的缺失实验细节。

这些是限定的符号、执行顺序和证据范围说明，没有否定其滚动重放思想。

## 12. 与已读文献的精确关系

[Ning 的 twisted block PF 笔记](NING-2026-TWISTED-BLOCK-PF.md) 改变有限候选池上的子粒子数组分布，并用整个数组的平均 guide 作修正。其精确对象是有限 $N$ bootstrap PF 的期望。它不要求计算任意连续模型的 $F_s\psi_s$。

本论文则直接改变连续状态 proposal，要求可计算 $F_s\psi_s$ 和可采样的 $f_s^\psi$。正确修正直接保留原 HMM 的未归一化目标。两者都能用 guide 影响计算分配，但 correction 对象、原语和精确性条件不同，不能把其中一个的有限池可实现性或方差公式移植给另一个。

[Dalla Pria 的 partition filter 笔记](DALLAPRIA-2026-PD-FILTER.md) 给出特定 conjugate family 的精确正混合闭包和可认证压缩。这里的粒子表示是随机近似，没有由 conjugacy 产生有限维确定闭包。后向 residual 是控制 proposal 的工具，不是已学得的最小 predictive state。

对于 FP，本文尚不提供“预测目标自动形成新计算状态”的完整迁移结论。能严格保留的候选工具是：给定可计算的正 transition 和 likelihood，先在学习系统上构造控制函数，再通过条件重放维护原目标，并用可认证 residual 判断局部随机计算质量。FP 是否拥有这些对象、能否支付 replay 和积分成本、是否需要此类随机估计，都须由 Astra 的实际对象决定。本次没有修改核心定义、架构、学习规则或实验协议。

## 13. 已完成与保留的问题

已完成该精确版本的完整阅读、算法时序分析、全部图核对和有限 artifact 元数据检查。独立数学工作包括一步未归一化恒等式、窗口冻结重放证明、完美 guide 的边界方差分解、显式 residual 相对方差界及 Gaussian 可积性约束拟合。

保留的问题是 guide 学习的样本外控制、uniform residual 条件的可实现性、时间一致误差、与维度相关的真实代价及 paper-aligned artifact 的实验复现。它们是本论文没有解决的条件，不构成本次要求额外验证或建立新任务系统的理由。

后续普通阅读仍先检查最新共享历史、Astra 请求、精确版本索引和其他研究员当前工作。Xue 的直接当代引用 Huang 等 `2507.14535` 可作窄范围来源筛选，当前笔记不预先把它标成已读或认领。

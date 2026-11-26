# Wieck-Sosa–Shalizi 2026：预测特征坐标、相关测试状态与固定长度生成

## 1. 版本、来源与实际阅读范围

- **标题：** Generative sequence modeling for infinite memory processes via predictive states
- **作者：** Michael Wieck-Sosa、Cosma Rohilla Shalizi
- **固定版本：** [arXiv 2609.38524v4](https://arxiv.org/abs/2609.38524v4)，2026-11-17 18:19:49 UTC。首次版本为 2026-09-29 20:42:08 UTC。读取时官方 latest 仍指向 v4。
- **原始全文：** [52 页 PDF](https://arxiv.org/pdf/2609.38524v4) 与 [完整 TeX](https://arxiv.org/src/2609.38524v4)。
- **出版身份：** PDF 页眉为 Preprint。官方记录未列独立出版 DOI 或 journal reference。ICLR 2027 样式、源文件中的 finalcopy 开关及作者主页的会议栏目不等于录用认证。
- **阅读人及日期：** Pro-C，2026-11-27，Asia/Shanghai。
- **原有覆盖：** 本次补全同一 v4 的局部记录，保留 [11 月 25 日请求笔记](REQUEST-2026-11-25-LEARNED-FINITE-STATE-UPDATES.md) 的历史范围，不把它当成另一篇论文。
- **实际范围：** 主阅读者完成 gen_seq.tex 全部 4671 行、相关记号、全部正文 §§1–4、Appendices A–E、7 个 Theorem、10 个 Lemma、12 个 Assumption、8 个 Definition、全部证明与推导、2 个 Algorithm、5 张 Figure、AI/ethics/reproducibility 声明及 88 条参考文献。PDF 正文与声明为 pp1–11，参考文献 pp12–17，附录目录与 A 从 p18 开始，B 从 p22、C 从 p23、D 从 p26、E 从 p29 开始，至 p52。
- **视觉核对：** 原 PDF pp5–7、9–10、22、24、32–33，覆盖全部图与算法、核心假设、率定理及空间分割证明。没有 Table 或 footnote。五张正式 Figure 包含六个外部图文件与一个内嵌 TikZ 架构图，不能按图文件数计数。
- **验证边界：** 完整阅读与下文独立条件推导已完成。没有逐项重证全部统计学习依赖、形式化证明、代码执行或经验复现。读到引用不代表读完所引用论文。

PDF SHA-256 为 ae5538ace22b9951558763b1d5b20617b42c889efa02d09a73eac9ff31644631。TeX 包 SHA-256 为 25f25b34fc67801e877e7cdcaf9414b905fd7d1e636260d2e21d17d48a6e4aa3。固定来源可恢复本次版本。

## 2. 可以带走的数学构造

本文给出三个相接但强度不同的结果。[§§2.1–2.4，Appendices A–E]

1. **精确状态的闭包。** 历史可测的一步充分状态，只要能由当前状态和新观测确定性更新，就对整个未来充分。
2. **可观察的状态坐标。** 对一个满足有限块可识别性和解析几何条件的 $p$ 维状态族，$k\ge2p+1$ 个随机 Fourier 测试函数的精确条件期望，几乎必然同时区分全部状态。
3. **条件性的学习率。** RNN 回归这些条件期望，再用 MDN 估计下一步密度。在紧支撑、平滑性、创新可逆性、混合性、函数类与优化条件下，获得密度误差率。持续使用拟合 RNN 的样本外状态误差另作为 Eq.35 的假设。

本笔记增加三项建设性推导。

- 将原文相关测试状态的空间分割证明改写为一般 covering 指数，得到更直接的几何误差接口。
- 从每个固定真实延续位置的一步一致性，推出同一冻结模型的**固定长度理想生成分布**一致性，并给出有界路径统计量的 Monte Carlo 误差。
- 从原文创新可逆性条件抽取精确预测坐标的块收缩，再在额外的有效更新访问条件下给出有限原型近似及存储预算。

这些是文献层面的数学结果和迁移候选，不修改 FP 的核心对象或要求 Astra 采用特定架构。

## 3. 历史可测、更新闭合和全未来充分

设

\[
\mathcal F_t=\sigma(X_t,X_{t-1},\ldots),\qquad
X_{t+1}=G(\varepsilon_{t+1},S_t),
\]

\[
S_t=\tau(S_{t-1},X_t)=R(X_{-\infty:t}),
\qquad \varepsilon_{t+1}\perp\mathcal F_t.
\]

$G,\tau,R$ 可测，观测空间与状态空间为标准 Borel 空间。Euclidean Borel 子集是正文特例。[Eq.3，Theorems 1、7]

必须保留 $S_t=R(X_{-\infty:t})$。一般 hidden Markov model 的不可观察物理状态并不自动是这种状态。由历史可测性和独立创新，

\[
\mathcal L(X_{t+1}\mid\mathcal F_t)
=\mathcal L(X_{t+1}\mid S_t).
\]

再用确定性递推，

\[
S_{t+L}=\tau^{(L)}(S_t,X_{t+1:t+L}).
\]

因此每个有限未来块的条件分布只依赖 $S_t$。证明先对 $L$ 归纳，在最后一步把下一步 kernel 写成 $(S_t,X_{t+1:t+L})$ 的可测函数，再对 cylinder events 使用单调类论证，得到

\[
X_{t+1:\infty}\perp X_{-\infty:t}\mid S_t.
\]

这里的未来分布产品是沿已生成前缀进行的 kernel composition，不是把各未来边际独立相乘。[Appendix E.4，pp49–51]

**边界：** 单独的一步充分性没有给出这个结论，递推闭合是实质条件。原文模型没有动作或外生控制输入，作者把 exogenous covariates 扩展留到以后。该定理不直接成为任意策略干预下的控制充分性定理。

## 4. 有限随机特征如何成为状态坐标

### 4.1 对象与三个条件

取固定 $m\ge0$，

\[
P_s=\mathcal L(X_{t+1:t+m+1}\mid S_t=s).
\]

要求以下三条同时成立。[Assumption 1，p5]

| 条件 | 实际作用 |
|---|---|
| $\mathcal S\subset\mathbb R^r$ 紧、半代数，Hausdorff dimension 为 $p$ | 控制全体状态的几何复杂度，允许有限 witness 定理同时分离不可数多个状态对 |
| $s\mapsto P_s$ 单射 | 同一个有限长度块已区分所有状态 |
| characteristic function 的实部与虚部，在 $(s,\omega)$ 上有到 $O\times\mathbb R^{d(m+1)}$ 的联合实解析延拓 | 使不等分布对应的 witness 相等集具有所需维数亏损 |

第二条不是由“状态有限维”直接获得的。选出一个足够大的统一 $m$ 也是结构前提。训练还要求 $n>2m+1$。

独立于数据取

\[
\varphi_i(x_{1:m+1})
=\cos\!\left(\sum_{j=1}^{m+1}\Omega_{i,j}^{\mathsf T}x_j+\alpha_i\right),
\]

其中 $\Omega_{i,j}\sim N(0,I_d)$，$\alpha_i\sim U(-\pi,\pi)$，并定义

\[
Y_{t+1}=\varphi(X_{t+1:t+m+1}),\qquad
\Phi(s)=\int\varphi\,dP_s,
\]

\[
Z_t=\Phi(S_t)=\mathbb E[Y_{t+1}\mid\mathcal F_t]\in[-1,1]^k.
\]

### 4.2 Theorem 2 的证明机制

设一个 witness 的参数为 $\vartheta=(\omega,\alpha)$。相应期望是

\[
M_\vartheta(s)
=\cos\alpha\,\operatorname{Re}\psi_s(\omega)
-\sin\alpha\,\operatorname{Im}\psi_s(\omega).
\]

若两个状态对所有 $\vartheta$ 给出相同值，分别取 $\alpha=0,-\pi/2$，就得到 characteristic function 完全相同，继而 $P_s=P_{s'}$。由识别性，$s=s'$。

Amir et al.2023 的有限 witness 定理将“对全部参数可分离”变成“几乎每组 $2p+1$ 个参数同时可分离全部状态”。源文使用的是一般 $\sigma$-subanalytic 版本，不能只用适用于仿射集合的简化版本。[Appendix C，D.2]

所以

\[
\Pr_\varphi\{\Phi:\mathcal S\longrightarrow[-1,1]^k
\text{ 单射}\}=1,\qquad k\ge2p+1.
\]

这不是 kernel approximation 的大随机特征极限，也不是估计误差概率界。$2p+1$ 是充分数目，本文没有证明它在本任务中为最小数目。

### 4.3 坐标闭包及有限精度的实际含义

固定一个单射 realization。$\Phi$ 连续且 $\mathcal S$ 紧，所以 $\Phi^{-1}$ 在 $\mathcal Z=\Phi(\mathcal S)$ 上连续。因此

\[
\sigma(Z_t)=\sigma(S_t).
\]

Theorem 3 明确给出下一步 kernel 相等。结合 Theorem 1，还立即有整个未来的条件分布相等，并能写出精确更新

\[
T(z,x)=\Phi\!\left(\tau(\Phi^{-1}(z),x)\right).
\]

这是精确状态坐标的结果，实际拟合的 $\widehat Z_t=\widehat\lambda(\widehat H_{t+1})$ 不自动获得仅由 $\widehat Z_t$ 闭合的更新。

一个直接的稳定性接口是

\[
\omega_\Phi(a)=
\sup\{\|s-s'\|:\|\Phi(s)-\Phi(s')\|\le a\}.
\]

紧性与单射性给出 $\omega_\Phi(a)\to0$。若观测坐标误差至多 $\epsilon$，先投影到紧集 $\mathcal Z$，再解码，则状态误差至多 $\omega_\Phi(2\epsilon)$。证明只用最近点距离和三角不等式。

该结论没有显式幂次或常数。一般解析单射也可以具有退化导数，例如标量立方映射的逆不是 Lipschitz。若另有

\[
\|\Phi(s)-\Phi(s')\|\ge c\|s-s'\|^\nu,
\]

才可读出 $(2\epsilon/c)^{1/\nu}$ 的误差预算。本文的随机 witness 数目没有自动提供 $c,\nu$ 或每坐标 bit 数。

固定随机特征后，$Z_t$ 有明确的可观察条件期望含义，可用于不同拟合的坐标比较。它不使未知物理隐变量的任意参数化获得唯一身份。

## 5. 两阶段估计器的信息时序

第一阶段是平方损失回归。[§2.4.1，Eq.16]

\[
I_{t+1}=(X_{t-m:t},Y_{t-m}),\qquad
H_{t+1}=\sigma_{v_h}(W_hH_t+\rho(I_{t+1})),
\]

\[
\widehat Z_t=\widehat\lambda(\widehat H_{t+1}).
\]

这里

\[
Y_{t-m}=\varphi(X_{t-m:t})
\]

只使用截至 $t$ 的已观测数据。真正的未来块 $Y_{t+1}$ 是监督标签，求和范围 $t=m+1,\ldots,n-m-1$ 使标签完全留在 $X_{1:n}$ 内。不能把输入中的 $Y_{t-m}$ 误读成未来信息泄漏。

第二阶段把条件联合密度按观测坐标分解，

\[
f(x\mid z)=
\prod_{j=1}^d f_j(x_j\mid z,x_{1:j-1}),
\]

并用以 $\widehat Z_t$ 为 covariate 的 Gaussian MDN 最大化经验条件 log-likelihood。[§2.4.2]

给定目标向量的前 $j-1$ 个坐标是同一步联合密度的链式分解。生成时必须逐坐标抽样，不是提前获取未来时刻观测。

Algorithm 1 的 $k,m$ 和网络超参数通过某个 criterion 共同选择。原文建议 cross-validated log-likelihood，但没有固定选择规则或证明自适应选择后的率。理论先固定一个满足条件的随机特征 realization。

Algorithm 2 冻结拟合器，输入各自已经生成的前缀，重复抽样整条未来路径，再用经验路径测度估计指定 functional。原文明确将其 functional 理论与实验留到另一稿件。下文独立推导仅覆盖明示的有限长度与有界 functional 情形。

## 6. 学习率所用的条件与误差预算

### 6.1 十二项假设的角色

| 原文编号 | 条件摘要 |
|---|---|
| 1–2 | 上述紧半代数状态族、有限块识别、联合解析性，固定一个单射特征 realization |
| 3 | $X_t$ 几乎处处落在固定紧集 $\mathcal X\subset\mathbb R^d$ |
| 4 | 下述 $g^*$ 有全立方体上的 $\eta$-Hölder 延拓，$\eta\in\mathbb N$ |
| 5 | 延拓对创新坐标的绝对偏导行和上界严格小于 1 |
| 6 | 特定 ReLU RNN sieve，$W_h$ 上三角、对角绝对值小于 $1-\epsilon_{\rm RNN}$，权重和网络宽度按指定方式增长 |
| 7 | 条件密度有统一 Gaussian mixture 逼近、均值/尺度界、系数 Sobolev 延拓、真密度在支撑上正下界 |
| 8 | MDN 的正上下界、尺度与归一权重约束，以及在 $z$ 上的统一 log-density Hölder 模量 $\Lambda_n\|z-z'\|^\kappa$ |
| 9 | 各 MDN 的层数、权重数、hidden units 随 $n,M_j$ 增长的 sieve |
| 10 | 理想 Gaussian mixture 落在紧支撑外的平均质量至多 $C M_j^{-2\omega_1}$ |
| 11 | 在受限 MDN 类内存在同时满足密度逼近和平方阶尾质量界的 comparator |
| 12 | 增广过程 $(X_t,Y_t,Z_t,\xi_t)$ 平稳且指数 $\beta$-mixing |

其中

\[
\xi_{t+1}=Y_{t+1}-Z_t,\qquad
\mathbb E[\xi_{t+1}\mid\mathcal F_t]=0,
\]

\[
g^*(y,e,x)=
\Phi\!\left(\tau^{(m+1)}(\Phi^{-1}(y-e),x)\right).
\]

$g^*$ 原定义域只包括 $y-e\in\mathcal Z$ 且更新终点在 $\mathcal S$ 的组合。其全立方体平滑延拓及创新收缩是额外假设，不能由 Theorem 2 的连续逆自动推出。[Lemma 1，Appendix A.1]

Assumption 12 针对整个增广过程，不是只假设原始 $X_t$ mixing。上三角 recurrent matrix 的对角幅度条件也不等于所有时刻任意范数中的一步收缩，其 off-diagonal 和网络宽度仍影响截断成本。

### 6.2 紧凑写出原文误差率

定义

\[
D_R=2k+d(m+1),\qquad
a_R=\min\!\left\{
\frac{\eta}{\eta+2D_R},
\frac{D_R+3}{5D_R+3}
\right\},
\]

\[
b_n=n^{-a_R}(\log n)^{11},
\qquad q=k+d-1,
\]

\[
u_n=
M^{-\omega_1}
+M^{(\gamma+q)/(2\gamma)+4\omega_2}
n^{-\gamma/(2\gamma+q)}
\log^3(nM),
\]

\[
R_n=u_n+\Lambda_n^{1/2}b_n^{\kappa/4}.
\]

Theorem 4 在 Assumptions 1–12、指定 sieve 与理论 argmin/argmax 下给出

\[
\left[
\int_{\mathcal Z}\int_{\mathcal X}
|\widehat f(x\mid z)-f(x\mid z)|^2\,dx\,dP_Z(z)
\right]^{1/2}
=O_{\mathbb P}(R_n).
\]

这是真实 covariate 处的 integrated density error，即使训练时已使用估计 covariate。[Eq.34，p22]

$\Lambda_n=O(1)$ 时，原文取

\[
M\asymp
n^{\frac{2\gamma^2}
{(2\gamma+q)[(2\omega_1+1+8\omega_2)\gamma+q]}}
\]

来平衡前两项。这里 $m,k,d,p$ 固定，不能把公式解释为维数随样本量任意增长的保证。

Theorem 5 另外假设，每个考虑的固定 $L$，沿真实已观测延续继续同一拟合 recurrence 时，

\[
\mathbb E\|\widehat Z_{n+L-1}-Z_{n+L-1}\|_2^2
\le C_L b_n.
\tag{W35}
\]

原文 Eq.35 的证明明确留待未来工作。随后得到

\[
r_{n,L}:=
\|\widehat f(\cdot\mid\widehat Z_{n+L-1})
-f(\cdot\mid Z_{n+L-1})\|_{L^2(\mathcal X)}
\]

\[
=O_{\mathbb P}\!\left(
\Lambda_n^{k/(2\kappa+k)}
R_n^{2\kappa/(2\kappa+k)}
\right).
\]

当 $\Lambda_n=O(1)$、$R_n\to0$ 时，它趋于零。若 $\Lambda_n$ 增长，必须检查整个显示的 rate，而不能只看 $R_n$。[Eq.36]

Theorem 6 单独处理真实 covariate 的 oracle MDN，允许 $P_Z$ 为低维或奇异分布。它给出 $u_n$ 型率，失败概率 $O(n^{-1})$，不需要先把 $P_Z$ 当作 $k$ 维 Lebesgue density。这个支持范围扩展并不把 rate 中的 $k$ 自动替换成 $p$。

### 6.3 证明中可复用的四个接口

**第一，固定网络预测的条件正交性。** 对 $\mathcal F_t$ 可测的固定候选 $h_t$，

\[
\mathbb E[\xi_{t+1}^{\mathsf T}(Z_t-h_t)]=0.
\]

$m>0$ 时 $Y_{t+1}$ 未必是 $\mathcal F_{t+1}$ 可测的 martingale difference 标签，原文因此直接检查正交、boundedness 和有限窗口 mixing，再用对网络类统一的 covering/concentration 将结论用于数据依赖的拟合器。不能只把“固定网络可测”直接套在使用全部训练标签的 fitted predictor 上。[Appendix E.1]

**第二，生成 covariate 的误差进入经验目标。** 令

\[
B_n=\frac1{n-2m-1}
\sum_{t=m+1}^{n-m-1}
\|\widehat Z_t-Z_t\|_2^2.
\]

MDN log-Hölder 性与 argmax 给出 comparator 扰动至多

\[
2\Lambda_n B_n^{\kappa/2}.
\]

密度 $L^2$ 风险取平方根后，形成 $\Lambda_n^{1/2}B_n^{\kappa/4}$。这解释了第一阶段误差为什么损失一个幂次，而不把两阶段误差简单相加。

若实际第二阶段只达到**归一经验 log-likelihood gap** $\epsilon_{n,\rm opt}$，同一个 basic inequality 多一项 $\epsilon_{n,\rm opt}$，于是密度界增加 $C\sqrt{\epsilon_{n,\rm opt}}$。这是条件推导，不是本文已经证明实际神经优化器达到所需 gap。

**第三，支撑外质量不能从 KL 展开中丢掉。** 对真密度 $p$ 支持于紧集 $A$、候选全空间归一密度 $q$，沿 $p+a(q-p)$ 的 Taylor 展开得到

\[
K(p,q)=q(A^c)+
\int_0^1(1-a)
\int_A
\frac{p(x)[q(x)-p(x)]^2}
{[p(x)+a(q(x)-p(x))]^2}\,dx\,da.
\]

因此在正上下界下，KL 与支撑内平方误差及支撑外质量相接。源证明通过向下 clipping 再归一的 mixture weights，保持近似权重至多真权重的两倍，再用 Gaussian Hellinger 距离控制 tail perturbation。[Appendix E.3，Steps 1.1–1.2]

**第四，mixing 与联合密度拼接。** MDN 证明使用长度 $b\asymp\log n$ 的 Berbee blocks，even/odd 两列各有约 $n/\log n$ 个独立块。局部 Rademacher、pseudo-dimension 和递归 localization 给出因子误差，再用 product telescoping 合成联合密度。其常数依赖固定 $d$ 和 density bounds，不能据此声称消除观测维数的代价。

## 7. 独立推导：相关测试状态由 covering 控制

原文 Theorem 5 的一个实质技巧是允许测试状态与拟合器相关。[Appendix E.2，尤其 Eqs.62–68]

设 $q_n(z)\ge0$ 是任意数据依赖函数，满足

\[
|q_n(z)-q_n(z')|\le H_n\|z-z'\|^\kappa,
\qquad
\|q_n\|_{L^2(P)}=O_{\mathbb P}(a_n),
\]

其中 $H_n\ge1$ 是确定性上界，$a_n\to0$。测试点 $Z^*$ 的边际为 $P$，无需独立于 $q_n$。

追加一个可核验的几何条件：对足够小的 $r$，固定支持集 $\mathcal Z$ 有确定性可测分割，cell 直径至多 $r$、数目满足

\[
J(r)\le C_{\rm cov}r^{-s}.
\tag{C}
\]

取 $r=(v/(2H_n))^{1/\kappa}$。若某个 cell 含有 $q_n(Z^*)>v$，则该 cell 上所有点的值均大于 $v/2$。当 $\|q_n\|_{L^2(P)}\le\delta$，这个 cell 的确定性 $P$-质量至多 $4\delta^2/v^2$。

对所有这种低质量 cell 求和，

\[
\Pr(q_n(Z^*)>v)
\le
\Pr(\|q_n\|_{L^2(P)}>\delta)
+C\delta^2H_n^{s/\kappa}v^{-2-s/\kappa}.
\tag{P}
\]

这一步只用了测试点的边际概率，完全没有把随机坏集与测试点错误地独立化。

代入平衡尺度得到

\[
\boxed{
q_n(Z^*)=
O_{\mathbb P}\!\left(
H_n^{s/(2\kappa+s)}
a_n^{2\kappa/(2\kappa+s)}
\right).
}
\]

原文用整个 $[-1,1]^k$ 的网格，故取 $s=k$。若有显式低维 covering 证书，可在**这个求值步骤**取更小的 $s$。

例如，若 $\mathcal S$ 由有限个有界 $p$ 维 Lipschitz 参数片覆盖，且 $\Phi$ 在这些片上 Lipschitz，将参数网格推送到 $\mathcal Z$ 就得到 $s=p$。仅凭一般集合的 Hausdorff dimension 为 $p$，不能跳过 covering 条件。这里给的是可核验的充分条件，不借未计算的几何常数宣称一个统一数值收益。

对本文应用，

\[
q_n(z)=\|\widehat f(\cdot\mid z)-g_n(\cdot\mid z)\|_{L^2(\mathcal X)},
\quad H_n=C_0\Lambda_n,
\]

且 $a_n$ 可取 $R_n$。完整 pointwise density bound 还应加上 comparator approximation 和 state substitution，

\[
O_{\mathbb P}\!\left(
\Lambda_n^{s/(2\kappa+s)}R_n^{2\kappa/(2\kappa+s)}
+R_n+\Lambda_n b_n^{\kappa/2}
\right).
\]

在原文用于吸收余项的条件下，后两项由第一项控制。该改进不更改 RNN/MDN 训练率中的 $k$，也没有证明 (W35)。

## 8. 独立推导：真实延续的一步一致性可以支持固定长度生成

### 8.1 冻结模型与条件目标

固定 $L<\infty$，将使用 $X_{1:n}$ 拟合好的 RNN、MDN、特征 realization 和初始化冻结。对每个 $i=1,\ldots,L$，让模型在**真实未来前缀**上运行，得到

\[
e_{n,i}
=\operatorname{TV}\!\left(
p_i(\cdot\mid\mathcal F_{n+i-1}),
q_{n,i}(\cdot\mid X_{1:n+i-1})
\right).
\]

$q_{n,i}$ 必须与生成时使用的同一个 frozen predictor 相同。其输入 lag buffer、初始化和已处理的观测也必须一致。假设这些 kernel 在所有生成历史上可测且归一，Gaussian MDN 的合法逐坐标抽样给出这种 kernel。

记 $P_{n,L}$ 为给定完整过去的真未来路径 law，$Q_{n,L}$ 为冻结模型的**理想 rollout law**。这里暂不加入有限次模拟得到的经验测度。

### 8.2 Kernel telescoping

对每个固定完整过去，

\[
P_{1:L}-Q_{1:L}
=
\sum_{i=1}^L
P_{1:i-1}(P_i-Q_i)Q_{i+1:L}.
\]

右侧各项的前缀服从真 law，后缀是 learned Markov kernels。后缀核在 TV 中为收缩，因此

\[
\boxed{
D_{n,L}:=\operatorname{TV}(P_{n,L},Q_{n,L})
\le
\sum_{i=1}^L
\mathbb E[e_{n,i}\mid\mathcal F_n].
}
\tag{R}
\]

如拟合含独立随机种子，可把它们加入条件信息。关键是它们不使用真实未来。

如果目标只条件于可见训练段 $X_{1:n}$，而不是完整 $\mathcal F_n$，不能把其真下一步 kernel 直接写成 $f(\cdot\mid Z_n)$。正确做法是先得到 (R)，再对未见的过去条件平均，利用 TV 的凸性。冻结模型只依赖可见训练数据和种子，故仍有相同形式的上界，其右侧改为条件于这些可见信息的期望。

### 8.3 支撑内密度误差足以控制完整 TV

设真 $p$ 支持于 $\mathcal X$，候选 $q$ 在 $\mathbb R^d$ 全空间归一。则

\[
q(\mathcal X^c)
=\int_{\mathcal X}(p-q)
\le\int_{\mathcal X}|p-q|.
\]

约定 $\operatorname{TV}=\tfrac12\|\cdot\|_1$，得到

\[
\operatorname{TV}(p,q)
=\tfrac12\left[
\int_{\mathcal X}|p-q|+q(\mathcal X^c)
\right]
\le
\int_{\mathcal X}|p-q|
\]

\[
\le
\sqrt{\operatorname{vol}(\mathcal X)}
\,\|p-q\|_{L^2(\mathcal X)}.
\tag{T}
\]

最后还可与 1 取最小值。不能漏掉支撑外质量后多保留一个没有根据的 $1/2$ 因子。

### 8.4 条件一致性结论

假设 Theorem 5 的条件对每个固定 $i\le L$ 成立，尤其 (W35) 在这些真实延续位置成立，并且其实际 rate 趋于零，例如 $\Lambda_n=O(1)$、$R_n\to0$。于是

\[
r_{n,i}\xrightarrow{\mathbb P}0,
\qquad e_{n,i}\xrightarrow{\mathbb P}0.
\]

由于 $0\le e_{n,i}\le1$，有 $\mathbb E e_{n,i}\to0$。由 (R)，

\[
\mathbb E D_{n,L}\le\sum_{i=1}^L\mathbb E e_{n,i}\to0,
\]

进而

\[
\boxed{
D_{n,L}\xrightarrow{\mathbb P}0
\quad\text{对每个固定 }L.
}
\]

这给出原文条件性一步结果到固定长度生成的一个严格桥梁。无需再假设 learned transition 的全局 Lipschitz 性，也无需训练与未来独立。原因是 telescoping 沿真前缀取误差，已经覆盖生成 law 的比较。

**保留的限制：**

- (W35) 仍为未经原文证明的条件，本推导没有替它补证。
- 不从 $O_{\mathbb P}$ 密度率单独推出同阶期望率。
- 不把固定 $L$ 的结论提升为任意增长 $L_n$。若另有统一期望误差 $\sup_{i\le L_n}\mathbb E e_{n,i}\le\epsilon_n$，则 $L_n\epsilon_n\to0$ 才提供一个明确的充分条件。
- 结论关于未来观测路径 law，不是状态坐标误差、控制 regret 或长时间 invariant law 的结论。

### 8.5 有限 Monte Carlo 的正确结论

给定冻结模型，独立生成 $N$ 条长度 $L$ 的路径。对任何固定可测 $h\in[0,1]$，以条件概率至少 $1-\delta$，

\[
\boxed{
\left|
\frac1N\sum_{j=1}^N h(\widehat X^{(j)}_{n+1:n+L})
-\mathbb E_{P_{n,L}}h
\right|
\le D_{n,L}
+\sqrt{\frac{\log(2/\delta)}{2N}}.
}
\]

这是理想模型误差加模拟误差。一般有界 $h$ 按 range 缩放。未来事件概率与有界路径成本均是实例。

有限样本经验测度是离散的，对非原子的连续真路径 law，其 TV 仍为 1。因此不能写成“Algorithm 2 输出的经验测度 TV 一致”。任意 functional $\Gamma$、quantile 或无界风险还需要各自的连续性、尾部或复杂度条件。

## 9. 独立推导：创新可逆性含有精确坐标的块收缩

这一结论抽取原文 Assumptions 4–5 的实际内容。

令 $b=m+1$，对共同有效的观测块 $x\in\mathcal X^b$ 定义

\[
T_b(z,x)=\Phi(\tau^{(b)}(\Phi^{-1}(z),x)).
\]

因为 $z\in\mathcal Z\subset[-1,1]^k$，

\[
T_b(z,x)=g^*(0,-z,x).
\]

设原文偏导界为 $\Delta_{ij}$，并令

\[
\rho_*=\max_i\sum_j\Delta_{ij}<1.
\]

对 $e=-z$ 到 $e'=-z'$ 的线段使用全立方体延拓。其 Hölder 正则性和弱偏导界给出相应 Lipschitz 代表，故

\[
\boxed{
\|T_b(z,x)-T_b(z',x)\|_\infty
\le\rho_*\|z-z'\|_\infty.
}
\]

端点必须属于 $g^*$ 的有效域。全延拓使连线中间点不必仍落在 $\mathcal Z$。若要把结论用于所有未来 blocks，还要保证相应 update domain 对这些 blocks 闭合。

这解释了原文创新 invertibility 的一项建设性作用。它是**精确坐标每 $m+1$ 步**的共同输入收缩，不是 fitted readout 的一步更新定理。

### 9.1 有限原型实现的条件性证书

追加以下访问条件：已知或能以误差至多 $\delta_T$ 评估 $T_b$，且有覆盖 $\mathcal Z$ 的有限 $\epsilon$-net $\mathcal C\subset\mathcal Z$。本小节的 net、更新误差与最近点距离均使用 $\ell_\infty$ 范数。设 $R_{\mathcal C}$ 是最近原型选择。

以

\[
\bar z_{j+1}
=R_{\mathcal C}(\widetilde T_b(\bar z_j,x_j))
\]

作块边界更新。若近似输出未落在 $\mathcal Z$，最近原型距离至多 $\delta_T+\epsilon$，故保守的一步误差为

\[
E_{j+1}\le\rho_* E_j+2\delta_T+\epsilon.
\]

因此

\[
\boxed{
E_j\le
\rho_*^jE_0+
\frac{(2\delta_T+\epsilon)(1-\rho_*^j)}{1-\rho_*}.
}
\]

若能直接保证输出原型对精确 $T_b$ 的距离至多 $\eta_T$，就把 $2\delta_T+\epsilon$ 换成 $\eta_T$。精确更新情形 $\delta_T=0$ 恢复通常的 $\epsilon/(1-\rho_*)$ 舍入预算。

有限码本总能由紧性存在。若另有第 7 节的 covering 证书，

\[
|\mathcal C|\le C\epsilon^{-s},
\qquad
\lceil\log_2|\mathcal C|\rceil
\le s\log_2(1/\epsilon)+O(1).
\]

这仅是**动态原型编号**的存储量。还应计入码本约 $k|\mathcal C|$ 个坐标、update evaluator 参数、输入 block buffer、数值精度与最近点搜索。直接扫描码本每次可需 $O(k|\mathcal C|)$ 工作。连续输入并不自动成为一个有限 transition table。

原文没有从数据构造这个码本和 update oracle，也未证明实际 $\widehat\lambda(\widehat H)$ 是该量化更新。该证书用于说明一组明确条件下怎样获得稳定有限原型近似，不冒充已完成的状态学习算法。

## 10. 实际状态、参数与计算成本

Theorem 4 使用

\[
w_n\asymp
n^{\max\{D_R/(4D_R+2\eta),\,D_R/(5D_R+3)\}},
\qquad
w_{h,n}\asymp w_n\log n,
\]

以及 $O(\log n)$ 的 feedforward depth。因此固定的特征数 $k$ 与随 $n$ 增长的 RNN hidden width 是不同资源。

一次在线预测至少保留 recurrent hidden state、所需 $m+1$ 个观测的 buffer、固定随机特征参数、RNN/MDN 权重。参数不计入动态状态时也必须单列。直接计算随机特征的成本约 $O(kd(m+1))$，稠密 recurrent multiplication 约 $O(w_{h,n}^2)$，另外还有两层 DNN 与 $d$ 个 MDN 因子的评估。上三角只改变常数或可利用结构，不自动给出线性于 hidden width 的实现。

第 $j$ 个 MDN 的参数量量级为

\[
M_j^{(k+j-1+\gamma)/\gamma}
n^{(k+j-1)/(2\gamma+k+j-1)}
\log(M_jn).
\]

低维预测坐标减少的是 conditioning complexity 的一部分。观测维数 $d$、预测标签块长度 $m+1$、输出 mixture 复杂度和参数精度都没有消失。

理论假设精确或充分近似的统计优化，未给实际 SGD 的运行时间或成功概率。本文没有 finite-bit learning complexity 或固定总参数量随训练长度增长的一致性定理。

## 11. 实验的实际证据

### 11.1 四个受控过程

所有观测采用协方差参数 $I_d$、截断域 $[-2.5,2.5]^d$ 的 truncated Gaussian。[§3.1，Figures 2–3，pp8–9]

| DGP | 精确递推 | 观测均值 | 维数 |
|---|---|---|---|
| 1 | $\tanh(A_1^SS_{t-1}+A_1^XX_t)$ | $S_t$ | $r=p=d=3$ |
| 2 | $\cos(A_2^SS_{t-1}+A_2^XX_t)$ | $S_t$ | $r=p=d=3$ |
| 3 | $\tanh(A_3^SS_{t-1}+A_3^XX_t)$ | $A_3^OS_t$ | $r=p=1,d=10$ |
| 4 | $\cos(\pi/2+A_4^SS_{t-1}+A_4^XX_t)$ | $A_4^OS_t$ | $r=p=1,d=10$ |

作者说矩阵保证唯一平稳分布，但未给出具体矩阵、初始化和 burn-in 配置。唯一平稳分布本身也不认证全部解析性、mixing 和创新可逆性条件。

训练长度为 250、500、1000、2000。每个结果平均 100 条独立模拟轨迹，测试后续 500 个目标观测。指标先对每条轨迹计算时间平均 integrated squared density error，再开平方，最后跨轨迹平均。Eq.25 的 $t=n,\ldots,n+499$ 是 conditioning-time 索引，对应目标 $X_{n+1:n+500}$。

唯一 baseline 是 Direct MDN，lag window 作为超参数，允许的最大 lag 随 $n$ 增长。作者总结为 comparable。曲线确实没有统一优势，DGP4 的本文方法从 $n=250$ 到 500 还略上升。四个 sample sizes 和没有误差条的均值不验证渐近幂率。

TeX 注释提到每个时点 512 次真/拟合密度评估，但这没有印入 PDF，也没有给出积分抽样规则。本笔记把它保留为源码注释，不当作已认证的运行配置。

### 11.2 单只 worm 的条件密度

真实例子是一只 C. elegans 的一条 41 维序列。[§3.2，Figure 4，pp9–10]

处理方式为每 3 个时间点取可用值中位数，保留最长连续片段，按前 1000 bins 的各维标准差缩放，再一阶差分。总长 3395。训练长度为 1000、2000、3000，固定测试段为最后 250 个观测，图中结果平均 5 个网络训练种子。

$k=3,10,25$ 的曲线在这条序列上按较小 $k$ 给出较低测试 NLL，均优于图中的 Direct MDN。没有误差条。五个种子不是五个独立生物样本。

前 1000-bin 的尺度估计位于最小训练窗口内，未见该步骤使用测试尺度。训练末端与固定测试段之间有间隔，作者称继续 recurrence，但没有完整展开 gap handling 或调参验证时间段。不能据此断言泄漏，也不能认证所有 selection 都与最终 test 隔离。

这是使用真实已观测历史的一步密度评估。没有多步自主生成、控制、语言模型或未知状态维数恢复实验。较小读出对应较好预测是结果，低维真实预测结构是作者解释。$k=3$ 也不代表实际内部 $H$ 和 buffer 只占三维。

### 11.3 可复现性与 AI 披露

论文未报告实际网络宽深、hidden width、mixture 数目、optimizer、学习率、epochs、batching、lag-grid、参数匹配预算或运行时间。Appendix A 是理论 sieve，不能替代实验超参数。

p11 声明代码将在接受后公开并向审稿人提供。当前论文与[作者主页](https://mwiecksosa.github.io/)的该条目未提供公开代码仓库，没有 artifact commit 可认证。数据通过 Javer et al.2018 和 OpenWorm 文献引用，没有具体 worm 文件及修订身份。未进行复现实验。

AI use statement 印在 pp10–11。作者披露 AI 用于文献搜索、概念讨论、文字/证明/代码修改建议、参数建议、找遗漏、实验反馈和 Figure 1 的 TikZ。作者同时否认 AI 制定数学命题、提供关键证明成分、解释结果或生成合成数据，并声明已审阅及承担责任。这是作者披露，不是独立审计结果。

## 12. 与 FP 的可选数学接口

| 原文对象 | 可迁移的条件接口 | 需要另外验证的部分 |
|---|---|---|
| $Z_t=\mathbb E[\varphi(\text{future block})\mid\mathcal F_t]$ | 用一组可观察预测任务固定状态坐标的含义 | 同一有限未来块识别、实际回归误差和稳定性 |
| 一步充分性与确定性更新 | 以 closure 证明全未来充分，而不从一步 loss 直接推出全部未来性质 | learned representation 是否真能只依赖自身和新输入更新 |
| 同一冻结模型沿真实延续的一步 density error | 第 8 节把其变为固定长度路径 law 与有界功能量的保证 | Eq.35 或其他有效的一步误差证书 |
| 增广空间中的创新收缩 | 第 9 节给出精确坐标 block stability 与条件性有限原型预算 | 更新 oracle 的可获取性、域闭合、码本与完整资源成本 |
| 支持的 covering 数 | 第 7 节区分表示坐标数和求值时的几何复杂度 | 可核验的 covering 常数与 exponent |

原论文没有动作干预、策略变化或控制价值误差。若未来映射到 FP 的交互决策对象，需要另给 action-conditioned kernels、覆盖/识别条件和干预语义，不能把纯观察充分性直接换成因果或控制充分性。

本次只新增文献笔记并更新该版本索引与已有恢复记录。没有修改 research/frontier/、核心定义、学习架构、实验协议或实现。

## 13. 完成状态与后续边界

v4 已完整阅读，取代该 edition 的 partially read 状态。原先关于 Eq.35 的限定依然成立，但全文还提供了可复用的有限 witness、相关测试点分割、Gaussian mixture tail 控制和块稳定性工具。

新推导严格区分精确状态、拟合读出、理想生成 law 与有限模拟统计量。固定长度生成结论仍以原文未证明的样本外状态条件为前提。内部学习参数与隐藏态增长、有限精度识别、任意增长预测长度和控制充分性均没有被本次结果解决。

下一篇按最新共享历史、Astra 请求与其他研究员占用重新选择。参考文献中的 Chen et al.2026、Amir et al.2023、Zhou et al.2023 在此仅作为原文已阅读证明的依赖，未启动整棵依赖文献的重复精读。


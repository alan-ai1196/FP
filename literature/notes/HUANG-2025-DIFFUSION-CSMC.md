# Huang 等：扩散伪似然的粒子编译、像集上的 Strang 变换与噪声尺度

## 版本、来源与阅读范围

- 研究员 Pro-C，2026-11-27，Asia/Shanghai。
- Shu Huang, Richard G. Everitt, Massimiliano Tamborrino, Adam M. Johansen，**Inference for Diffusion Processes via Controlled Sequential Monte Carlo and Splitting Schemes**。
- 精确来源：[arXiv:2507.14535v1](https://arxiv.org/abs/2507.14535v1)，2025-07-19 08:33:26 UTC。官方 latest 核验时仍只有 v1。PDF 扉页日期 July 22, 2025 不代表新版本。
- 取得 [29 页 PDF](https://arxiv.org/pdf/2507.14535v1) 和 [原始 TeX](https://arxiv.org/src/2507.14535v1)。主读者读完 refJRSSB.tex 全部 940 行，包括 §§1–6、Appendices A–H、所有公式、3 个 Proposition、唯一独立 proof 环境、另两项命题的分解论证、4 个算法、9 个图、致谢、数据声明及 40 条实际书目。参考文献在 pp.20–22，Appendix A 从 p.22 下部开始。
- 主读者视觉核对原 PDF pp.9–11,14,16–18,22–23,25–29，覆盖全部算法、全部图、条件 Gaussian 公式、cubic covariance、FHN matrix exponential 和 Jacobian。没有编号表或脚注。正文用一个 tabularx 并排展示两个子方程，不是实验表。
- 状态：**完整阅读 v1**。没有认证另一个正式期刊全文。源文件名 refJRSSB.tex 和 accepted-manuscript 许可措辞不构成录用证明。未发现 AI assistance 声明，不推断实际是否使用 AI。
- [公开 artifact](https://github.com/adamjohansen/csmc-diffusions) 的 main 核验为 29685844a1d396de08602a500922d61b4255054b，2025-07-14 19:18:34 UTC，早于 v1。仅检查目录、README 和元数据。根目录 cSMC 是指向 7d6d77898bee72931493bff1a71e73f36b080098 的 gitlink，返回树没有其包实现。因此不声称依赖已完整恢复或实现已与论文公式对齐。没有代码执行、完整审计或实验复现。
- 原始资料在忽略跟踪的 literature/corpus/pro_c/huang2025diffusion/。独立推导在相应小节标明，没有把作者的经验解释当成已证定理，也没有形式化证明。

## 1. 主要贡献与可取用结果

本文提供一条可计算路线：把半线性 SDE 拆成线性 Gaussian 子过程和确定性非线性流，用 splitting 产生显式数值 transition，再把无噪声部分观测的伪似然编译成 Feynman–Kac normalizer。controlled SMC 学习 proposal guide，降低该 normalizer 的 Monte Carlo 方差。桥内插入更细时间点，改变所近似的离散模型，从另一层面减少时间离散偏差。[§§2–4]

核心接口是连续动力系统到数值 transition、无噪声观测端点到 hidden coordinates，以及 proposal 学习到固定伪似然的精确重要性修正。笔记保留作者的三项分解构造，并给出三组独立数学工具：

1. 用线性可控性判据认证一步 Gaussian covariance 非退化，并对 FHN 的不同时间尺度给出显式预条件化。
2. 将过强的全空间 Strang 可逆假设改成像集上的密度变换，保留观测端点 Jacobian、初始分布和参数支持。
3. 用固定数据的统一 log-likelihood 误差，推导近似优化和后验误差接口。该误差证书不是原论文已经提供的结果。

这些工具属于已知模型的推断与数值计算，不表示已经从预测经验中学得最小状态、未知方程或可复用 FP 算子。

## 2. 连续模型与三种误差

原文研究

\[
dX_t=(AX_t+\gamma(X_t))dt+\Sigma dW_t,\qquad X_t\in\mathbb R^d.
\]

$A$、$\Sigma$ 是常矩阵，$\gamma$ 为二次连续可微的非线性函数。Assumption 2.1 要求 one-sided Lipschitz 和多项式局部 Lipschitz 控制：

\[
\langle\gamma(x)-\gamma(y),x-y\rangle\le c_1\|x-y\|^2,
\]

\[
\|\gamma(x)-\gamma(y)\|^2
\le c_2(1+\|x\|^{2\chi-2}+\|y\|^{2\chi-2})\|x-y\|^2.
\]

初始分布已知且有相应有限矩。原文还假设连续过程具有光滑 transition density。强解存在、splitting 的强收敛和部分高阶结论来自被引数值分析文献，本次不标成独立重证。

设 observation interval 为 $\Delta$，每段分为 $K$ 个子步，$\delta=\Delta/K$。以下把桥内双层时间索引统一写成 $(k,n)$。需要分开：

- **数值模型误差**：$f_\delta$ 连乘并积分形成的 $K$ 步 transition 与真正连续过程 transition 不同。
- **粒子误差**：有限 $N$ 对已经固定的 $f_\delta$ 伪似然的随机估计误差。
- **外层推断误差**：SPSA 尚未找到全局最优点，或者 PMMH 链尚未充分混合。

增加 $N$ 不会消除第一项。增加 $K$ 增加潜在桥维度与计算成本，也不自动降低给定预算下的第二项。一次低方差 likelihood 评估不保证外层方法收敛。

原文讨论完全观测、无噪声部分观测和带测量噪声观测。带噪声情形可直接用普通 state-space likelihood potentials，主要新构造集中于无噪声端点。[§§1.2,3–4]

## 3. Splitting 的可计算原语

将模型拆为

\[
dX_t^{[1]}=AX_t^{[1]}dt+\Sigma dW_t,\qquad
dX_t^{[2]}=\gamma(X_t^{[2]})dt.
\]

记非线性 ODE 的时间 $\delta$ 流为 $\Gamma_\delta$。线性子过程的精确 transition 为

\[
X'=e^{A\delta}x+\xi_\delta,\qquad
\xi_\delta\sim N(0,C_\delta),
\]

\[
C_\delta=\int_0^\delta e^{As}\Sigma\Sigma^\top e^{A^\top s}\,ds.
\]

Lie–Trotter 更新先非线性、后线性：

\[
X'=e^{A\delta}\Gamma_\delta(x)+\xi_\delta.
\]

只要 $C_\delta\succ0$，它有全维 Gaussian 密度

\[
f_\delta^{\rm LT}(x'\mid x)
=\mathcal N\!\left(x'\mid e^{A\delta}\Gamma_\delta(x),C_\delta\right).
\]

Strang 更新为

\[
X'=\Gamma_{\delta/2}\!
\left(e^{A\delta}\Gamma_{\delta/2}(x)+\xi_\delta\right).
\]

它通常不再是 Gaussian，但在可逆坐标变换下可转为 LT 形式。第 7 节给出支持和初始条件处理。

原文引用 LT 和 Strang 的强阶均为 1，以及在指定条件下的一步条件均值误差分别为 $O(\delta^2)$ 与 $O(\delta^3)$。[§2.3] 后者是均值的局部误差结论，不能单靠它推出 transition density、log-likelihood 或参数估计偏差也具有相同阶数。文中 Strang 参数偏差较小的展示仍属具体数值证据。

## 4. 独立推导一：可控性认证与 Gaussian 条件化

### 4.1 一步非退化的有限代数证书

对任意 $\delta>0$，

\[
\boxed{
C_\delta\succ0
\iff\operatorname{rank}[\Sigma,A\Sigma,\ldots,A^{d-1}\Sigma]=d.
}
\]

从主文 covariance 积分直接得到，对向量 $v$，

\[
v^\top C_\delta v
=\int_0^\delta\|\Sigma^\top e^{A^\top s}v\|^2\,ds.
\]

积分为零要求连续非负的 integrand 在整个区间为零。矩阵指数解析，故所有导数给出

\[
\Sigma^\top(A^\top)^jv=0,\qquad j\ge0.
\]

Cayley–Hamilton 把无限条件归约为 $j=0,\ldots,d-1$，反向显然成立。这是标准可控性 Gramian 的直接推导，提供有限矩阵证书，不是对原 SDE 的完整 Hörmander 理论重证。

判据作用于**所选线性子问题**。不能把“完整非线性 SDE 有光滑密度”直接当成该具体 splitting 已有非退化 Gaussian transition 的计算证书。

矩阵指数和 covariance 可共同由一次 block exponential 计算：

\[
\exp\!\left[
\delta\begin{pmatrix}
A&\Sigma\Sigma^\top\\0&-A^\top
\end{pmatrix}\right]
=
\begin{pmatrix}
E_\delta&D_\delta\\0&E_\delta^{-\top}
\end{pmatrix},
\qquad C_\delta=D_\delta E_\delta^\top.
\]

由 block 微分方程即可验证。它避免手写模型专属三角函数，是精确代数表达，不是浮点稳定性的自动保证。稠密矩阵的一次预计算量为 $O(d^3)$。

### 4.2 从 Gaussian transition 编译观测端点

把 $x'=(v',u')$ 分为 observed 与 hidden coordinates，设条件 Gaussian 均值为 $(m_v,m_u)$，covariance 为

\[
C=\begin{pmatrix}C_{vv}&C_{vu}\\C_{uv}&C_{uu}\end{pmatrix}.
\]

则

\[
f^1(v'\mid x)=\mathcal N(v'\mid m_v,C_{vv}),
\]

\[
\boxed{
f^2(u'\mid v',x)=
\mathcal N\!\left(
u'\mid m_u+C_{uv}C_{vv}^{-1}(v'-m_v),
C_{uu}-C_{uv}C_{vv}^{-1}C_{vu}
\right).
}
\]

这是把已观测端点的信息直接编入 proposal 的可计算步骤，无需尝试从连续 proposal 恰好命中无噪声观测值。

原文 §4.3 的条件均值两次打印成 $C_{uv}C_{uu}^{-1}(v'-m_v)$，正确逆矩阵应为 $C_{vv}^{-1}$。observed 与 hidden 维数不同时，打印式不满足维度匹配。bridge 版本还把端点写成 $v_{t,M}$，应为 $v_{k,K}$。后续使用正确的 Schur 条件式，没有据此认定未审计代码使用了错误公式。

## 5. 三项 Feynman–Kac 编译

### 5.1 Proposition 1：无桥、部分观测

给定 $v_{0:M}$，写初始密度

\[
\mu(v_0,u_0)=\mu^1(v_0)\mu^2(u_0\mid v_0),
\]

并分解每个 transition 为 $f_k^1(v_k\mid x_{k-1})f_k^2(u_k\mid v_k,x_{k-1})$。部分伪似然为

\[
L(v_{0:M})=
\int \mu^1(v_0)\mu^2(u_0\mid v_0)
\prod_{k=1}^M
f_k^1(v_k\mid v_{k-1},u_{k-1})
f_k^2(u_k\mid v_k,v_{k-1},u_{k-1})
\,du_{0:M}.
\]

最后一个 $f_M^2$ 对 $u_M$ 积分为 1，故只需保留 $u_0,\ldots,u_{M-1}$。作者的 FK 对为

\[
M_0(u_0)=\mu^2(u_0\mid v_0),\qquad
G_0(u_0)=\mu^1(v_0)f_1^1(v_1\mid v_0,u_0),
\]

\[
M_k(u_k\mid u_{k-1})
=f_k^2(u_k\mid v_k,v_{k-1},u_{k-1}),
\]

\[
G_k(u_k)=f_{k+1}^1(v_{k+1}\mid v_k,u_k),
\qquad1\le k\le M-1.
\]

非负积分换序给出 $Z=L(v_{0:M})$。[Proposition 1, Appendix C] FK horizon 是 $M-1$，不是背景公式默认的 $M$。若需要最终 hidden state，可添 $M_M=f_M^2$ 和 $G_M=1$，normalizer 不变。

这是**消去一个已归一化的末端 transition**，不是删去最后观测。$v_M$ 已通过 $G_{M-1}$ 进入目标。

### 5.2 Proposition 2：完全观测、桥接 transition

一段从已知 $x_{k-1}$ 到已知 $x_k$，定义

\[
f_\delta^{[K]}(x_k\mid x_{k-1})
=\int\prod_{n=1}^K f_\delta(x_{k,n}\mid x_{k,n-1})
\,dx_{k,1:K-1}.
\]

$K$ 是子步数，只有 $K-1$ 个内部状态。对 $K\ge2$，先传播这些内部状态，中间 potential 为 1，最后置

\[
G_{k,K-1}(x)=f_\delta(x_k\mid x).
\]

这段 FK normalizer 正是上述 $K$ 步 transition。各段连接后加上适当初始因子，得到完全观测的 bridged pseudolikelihood。[§4.1]

$K=1$ 时直接评估 $f_\Delta(x_k\mid x_{k-1})$，不能把包含 $K-1$ 和 $K-2$ 的显示公式机械套到零长度状态序列。

若每段分别估计再相乘，需要保证乘积无偏的条件独立生产抽样，或直接按完整 FK 程序生成。任意相关的无偏数相乘不会自动保持无偏性。

### 5.3 Proposition 3：部分观测、桥接 transition

给定 $u_0\sim\mu^2(\cdot\mid v_0)$，初始 potential 为 $\mu^1(v_0)$。每段执行：

1. 把已知 $v_{k-1}$ 与 hidden particle $u_{k-1}$ 拼成起点。
2. 用 $K-1$ 次 full-state transition 生成内部桥点。
3. 在最后内部点用 $f_\delta^1(v_k\mid x_{k,K-1})$ 加权。
4. 从 $f_\delta^2(u_k\mid v_k,x_{k,K-1})$ 采样 hidden endpoint，再进入下一段。

状态空间随时间在 $\mathcal U$ 与 $\mathcal X$ 间变化。这是合法 FK kernel 链，实现中须相应改变 guide 输入维数。将 kernels 与 endpoint potentials 相乘并消去积分，直接恢复 bridged partial pseudolikelihood。[Proposition 3]

原文多重积分的域与微分索引有若干不一致。上面的逐步程序明确其意图：每段恰有 $K-1$ 个 full-state 内点和一个 hidden endpoint。末端 $u_M$ 可保留用于状态推断，也可在只求 normalizer 时积分消去。

确定初始 $x_0$ 的实验应把 likelihood 条件于该起点，不能把 Dirac point mass 当作普通 Lebesgue 密度值 $\mu(x_0)$。

## 6. 独立推导二：FHN 的低噪声坐标与稳定尺度

在 hypoelliptic FHN 中，令 $\sigma=\sigma_2>0$，$\sigma_1=0$。源文采用

\[
A=\begin{pmatrix}0&-1/\epsilon\\\gamma&-1\end{pmatrix},
\qquad\Sigma=\begin{pmatrix}0\\\sigma\end{pmatrix},
\qquad\epsilon>0.
\]

可控性矩阵

\[
[\Sigma,A\Sigma]
=\begin{pmatrix}0&-\sigma/\epsilon\\\sigma&-\sigma\end{pmatrix}
\]

满秩。任意正步长的 $C_\delta$ 都正定，尽管瞬时 noise rank 只有 1。所选 linear split 通过动力学耦合把噪声传入 observed coordinate。

由矩阵指数展开并积分，固定参数下有

\[
C_{11}(\delta)=\frac{\sigma^2\delta^3}{3\epsilon^2}+O(\delta^4),
\quad
C_{12}(\delta)=-\frac{\sigma^2\delta^2}{2\epsilon}+O(\delta^3),
\]

\[
C_{22}(\delta)=\sigma^2\delta+O(\delta^2).
\]

因此

\[
\det C_\delta=\frac{\sigma^4\delta^4}{12\epsilon^2}+O(\delta^5),
\qquad
\operatorname{cond}_2(C_\delta)\sim\frac{12\epsilon^2}{\delta^2}.
\]

数值 transition 有非退化密度，不代表小步长下没有矩阵病态。不同坐标的 $\delta^3$ 与 $\delta$ variance 解释了这个区别。

### 6.1 显式预条件化

对 innovation $x'-e^{A\delta}\Gamma_\delta(x)$ 使用

\[
S_\delta=\operatorname{diag}\!\left(
\frac{\epsilon}{\sigma\delta^{3/2}},
\frac1{\sigma\sqrt\delta}\right).
\]

则

\[
S_\delta C_\delta S_\delta^\top
\longrightarrow C_0=
\begin{pmatrix}1/3&-1/2\\-1/2&1\end{pmatrix},
\qquad\det C_0=1/12.
\]

极限正定，缩放后的谱条件数有有限极限。固定矩阵

\[
R_0=\begin{pmatrix}\sqrt3&0\\3&2\end{pmatrix}
\]

满足 $R_0C_0R_0^\top=I$，故

\[
(R_0S_\delta)C_\delta(R_0S_\delta)^\top\to I.
\]

这是给定参数的坐标变换，不改变 Gaussian law。保留相应 determinant 后，可在缩放坐标计算密度和条件 Gaussian。它减少小步长造成的主要尺度差异，没有证明整个 CSMC 的方差与 $\delta$ 无关，也不消除时间离散误差。

### 6.2 端点条件化的尺度

Schur complement 和条件均值系数为

\[
\operatorname{Var}(U'\mid V',x)
=\frac{\sigma^2\delta}{4}+O(\delta^2),
\]

\[
C_{21}C_{11}^{-1}=-\frac{3\epsilon}{2\delta}+O(1).
\]

observed residual 只有 $\delta^{3/2}$ 尺度，但其条件均值增益为 $1/\delta$，所以对 hidden coordinate 的影响仍为 $\delta^{1/2}$。不能因观测坐标方差较小就忽略这个耦合。

上述极限均为固定 $\epsilon,\sigma,\gamma$ 的结论。未经参数范围控制，不提升为对 $\epsilon\downarrow0$ 或 $\sigma\downarrow0$ 统一的保证。

## 7. 独立推导三：Strang 在像集上的可逆密度

### 7.1 原假设与实际流的范围

原文 Assumption 4.2 要求小步长下 $\Gamma_\delta^{-1}$ 在整个 $\mathbb R^d$ 有定义。但 Appendix A/B 的标量 cubic 流为

\[
g_h(v)=\frac{v}{\sqrt{a+(1-a)v^2}},
\qquad a=e^{-2h/\epsilon}\in(0,1).
\]

cubic 例子取 $\epsilon=1$，FHN 的另一个坐标只平移 $\beta h$。对每个 $h>0$，该流严格单调，其像却是

\[
I_h=\left(-\frac1{\sqrt{1-a}},\frac1{\sqrt{1-a}}\right).
\]

所以它不是整个 $\mathbb R$ 到自身的满射。任意细子步都没有实现原假设的全空间可逆性。

可用修补是：$g_h$ 是 $\mathbb R$ 到 $I_h$ 的光滑双射。其逆与导数为

\[
g_h^{-1}(v)=\frac{\sqrt a\,v}{\sqrt{1-(1-a)v^2}},
\]

\[
J_h(v):=\left|\frac{d}{dv}g_h^{-1}(v)\right|
=\frac{\sqrt a}{[1-(1-a)v^2]^{3/2}},
\]

仅在 $v\in I_h$ 使用。

### 7.2 单步密度与 LT 坐标

设 $h=\delta/2$，$G_h(v,u)=(g_h(v),u+\beta h)$，像为 $D_h=I_h\times\mathbb R$。Strang step 为

\[
X'=G_h(e^{A\delta}G_h(x)+\xi_\delta).
\]

对任意起点 $x$，正确单步密度为

\[
\boxed{
p_{\rm S,\delta}(x'\mid x)=
\mathcal N\!\left(
G_h^{-1}(x')\mid e^{A\delta}G_h(x),C_\delta
\right)
J_h(v')\,\mathbf1_{D_h}(x').
}
\]

这个分段表达的含义是像外密度为零，像内才评估 inverse 和 Gaussian，避免实际计算非实数逆式。

若当前 $x=G_h(z)$ 也在像内，flow semigroup 性给出

\[
G_h(x)=G_h(G_h(z))=\Gamma_\delta(z).
\]

于是 $Z=G_h^{-1}(X)$ 的后续 transition 恰为

\[
q_\delta(z'\mid z)
=\mathcal N(z'\mid e^{A\delta}\Gamma_\delta(z),C_\delta),
\]

即 LT 型 Gaussian transition。初始点若在像外，原 Strang step 仍有定义，不能宣布整段 likelihood 为零。只需第一步保留

\[
Z_1\mid X_0=x_0
\sim N(e^{A\delta}G_h(x_0),C_\delta),
\]

从第二步起再用 LT transition。

### 7.3 观测端点 Jacobian 与初始分布

仅观测 $v_{0:M}$，每个输出端点 $v_k$，$k\ge1$，都在 $I_h$。对 fine-grid hidden variables 作变量替换后，全部内部 full-state Jacobian 与积分测度抵消，每个 observed endpoint 留下一个 $J_h(v_k)$。

若 $v_0\in I_h$，令 $z_{v,0}=g_h^{-1}(v_0)$，并用条件初始 hidden 密度

\[
\widetilde\mu_0(z_u)=\mu^2(z_u+\beta h\mid v_0).
\]

则

\[
\boxed{
L_{\rm S,\delta}^{[K]}(v_{0:M})
=\mu^1(v_0)
\left[\prod_{k=1}^M J_h(v_k)\right]
L_{\rm LT,\delta}^{[K]}
\left(z_{v,1:M}\mid z_{v,0},\widetilde\mu_0\right).
}
\]

右侧最后的 $L$ 是经相同细子步积分、条件于初始观测与 hidden prior 的 Gaussian-kernel 部分 likelihood。初始 marginal factor 保留原 $\mu^1(v_0)$，不再多乘一个 $J_h(v_0)$。

若改为变换完整初始 joint density，

\[
\mu_Z(z)=\mu_X(G_hz)|\det DG_h(z)|,
\]

其总质量一般只是 $\Pr_{\mu_X}(X_0\in D_h)$。只有原 prior 支持于 $D_h$ 才自动归一化。若另行除以这个质量，必须在 likelihood 中保留对应因子。条件初始构造避免了这个不必要的积分。

若 $v_0\notin I_h$，保留原 $u_0\mid v_0$ 和专门第一步，后续推导不变。初始观测与之后 Strang 输出的支持应分开。

这里使用 FHN 的 block-separable flow。更一般的 block-triangular flow 在完整 inverse 存在且可计算时也可处理，但 initial conditional prior 与 observed-coordinate inverse 仍须单独给出。这不是对任意 nonlinear observation map 的 Gaussian 编译定理。

### 7.4 有限数据的显式细化条件

由于 $h=\delta/2$，$a=e^{-\delta/\epsilon}$。令 $V=\max_{1\le k\le M}|v_k|$。

- 若 $V\le1$，任意正步长都满足这些输出端点的像条件。
- 若 $V>1$，所需条件为

\[
\boxed{\delta<\epsilon\log\frac{V^2}{V^2-1}.}
\]

因此一个严格可行的整数选择为

\[
K\ge\max\!\left\{
1,\
\left\lfloor
\frac{\Delta}{\epsilon\log[V^2/(V^2-1)]}
\right\rfloor+1
\right\}.
\]

若还要直接变换 $v_0$，可把它纳入 $V$。细化使有限数据落入像内，并没有使 $\Gamma_h$ 变成全空间满射。

Jacobian 和支持约束依赖 $\epsilon$，参数推断时不能丢掉。在固定 $\delta$ 且 $V>1$ 时，某些小 $\epsilon$ 的 Strang 伪似然为零，而连续模型 likelihood 可能为正。log 参数 Gaussian prior 覆盖这些区域，故有限步长伪后验与连续后验的差异不会由 particle unbiasedness 消除。若 $V$ 随参数变化，相应地在该参数处检查 $V(\theta)>1$。

当 $V$ 很大时，所需子步数的尺度可达 $\Delta V^2/\epsilon$。若每个参数另行恢复去掉的均值，则 $V$ 也依赖该参数及均值模拟，需要使用实际重构值检查支持。像集修补给出了可执行条件及细化成本。

## 8. Controlled SMC 的精确性与拟合接口

原文 FK twist 在 kernel 中乘 $\psi_k$，在 potential 中乘补偿比，使完整 path density 不变。产品必须包含 $G_0$。§3.3 一处显示式从 1 起乘漏写初始 potential，以下采用一致的 $0,\ldots,M$ 产品。

Algorithm 1 使用 multinomial resampling，ESS 阈值 $N/2$。Algorithm 2 从后向 log-Bellman targets 回归 quadratic log-guide。Figure 1 在学习终止后另做一次新的 filter run，避免报告用于选取 guide 或停止学习的那次随机估计。给定全部学习结果，正确最终生产运行的 normalizer 对**固定数值模型伪似然**无偏。[§§3.3–3.5]

这与 [Xue 的冻结重放接口](XUE-2025-ONLINE-ROLLING-CSMC.md) 相容，但本文反复学习整段离线 bridge，不自动具有固定每观测成本。

### 8.1 二次 guide 的符号与可积性

源文打印

\[
\log\psi(x)=x^\top Bx+b^\top x+c,\qquad B\succeq0.
\]

对基础 Gaussian $N(m,C)$，twisted Gaussian 存在的实际条件为

\[
C^{-1}-2B\succ0.
\]

$B\succeq0$ 单独不保证该条件，非恒定正二次 log-guide 也不满足此前“$\psi$ 有界”的假设。Appendix F 用另一种正定参数措辞描述拟合失败后的宽 Gaussian fallback，不能仅由文字确定代码实际符号约定。

保守可计算类为

\[
\log\psi(x)=-\tfrac12x^\top Rx+u^\top x+c,\qquad R\succeq0,
\]

它保证 Gaussian 可积性。若还要严格保留 bounded-guide 前提，可令 $R\succeq\rho I$，$\rho>0$。拟合 quadratic log-target 得到凸二次目标与正半定约束。完整二次系数数目

\[
p_d=(d+1)(d+2)/2.
\]

这与 Xue 的对角 $2d+1$ 参数类不同。精确积分、正确抽样、非零有限权重和有限 log-target 仍须成立。训练池上的低残差不是整条 bridge 的风险保证。有限大方差 Gaussian fallback 近似平坦，但不等于严格常数 policy。

### 8.2 参数推断的实际目标

非负无偏 likelihood estimator 可用于 pseudo-marginal MH，在有效 proposal 与相应辅助变量构造下，目标是数值模型 posterior。拒绝时保留旧 likelihood 估计是其中重要部分。有限 $K$ 不会因 PMMH 精确性自动变为连续模型 posterior。

Algorithm 4 的一般 proposal ratio 打印反了。正确接受率为

\[
1\wedge
\frac{\widehat L(\theta')\pi(\theta')q(\theta\mid\theta')}
{\widehat L(\theta)\pi(\theta)q(\theta'\mid\theta)}.
\]

源实验使用 log 参数空间的对称 Gaussian random walk，proposal ratio 抵消。因此这处通用印刷错误不足以断言实际对照失败。prior 是 log 参数上的 standard Gaussian，对物理正参数而言为相应 lognormal prior。

SPSA 用随机两侧扰动估计优化方向，adaptive 版本每次要 5 次 measurements。[Appendix D] 若实际用 log-normalizer，其无偏性不能由 $\widehat L$ 无偏推出。本文没有新增 SPSA 全局收敛证明。

## 9. 独立条件推导：数值 likelihood 到推断误差

固定数据，假设 $L_h(\theta)$ 和 $L^\star(\theta)$ 正、有限、可归一化，且在相关参数支持上

\[
\sup_\theta|\log L_h(\theta)-\log L^\star(\theta)|\le E.
\]

### 9.1 优化误差

若 $\widehat\theta$ 对数值 log-likelihood 的优化 gap 至多 $\eta$，$\theta^\star$ 最大化连续 log-likelihood，则加减两端近似值给出

\[
\log L^\star(\theta^\star)-\log L^\star(\widehat\theta)\le2E+\eta.
\]

若连续 log-likelihood 在包含二者的凸可行域上另有 $\lambda$ 强凹性，则全局最大点的一阶最优条件给出

\[
\|\widehat\theta-\theta^\star\|
\le\sqrt{\frac{2(2E+\eta)}{\lambda}}.
\]

没有曲率或可识别性条件，likelihood 值接近不保证参数接近。

### 9.2 后验 TV

同一 prior 下，令 $\Pi_h,\Pi^\star$ 为对应 posteriors。写

\[
w(\theta)=L_h(\theta)/L^\star(\theta)\in[a,b],
\qquad a=e^{-E},\quad b=e^E,\quad m=\mathbb E_{\Pi^\star}w.
\]

由 $|w-m|$ 在 $[a,b]$ 的线性弦上界，

\[
\operatorname{TV}(\Pi_h,\Pi^\star)
=\frac{\mathbb E_{\Pi^\star}|w-m|}{2m}
\le\frac{(m-a)(b-m)}{m(b-a)}.
\]

右侧在 $m=\sqrt{ab}$ 最大，得到

\[
\boxed{\operatorname{TV}(\Pi_h,\Pi^\star)\le\tanh(E/2).}
\]

约定 $\operatorname{TV}=\tfrac12\|\cdot\|_1$。$E=0$ 时直接为零。

这些结论依赖实际的**统一 log-likelihood 误差证书**。原文 Assumption 4.1 是耦合离散和连续随机状态上 density 值的 $L_1$ 收敛，不自动给出参数统一界，也不是通常对状态坐标积分的 density-TV 收敛。强路径收敛和一步均值阶都不能代替这里的假设。尤其有限步长参数支持差异可能使有限 $E$ 不存在。

这是可供数值分析连接的条件工具，不是把模拟提升为 posterior consistency 定理。Pedersen 1995 的外部 MLE 结果保留被引身份与额外正则条件，本次没有重读或认证其全部适用性。

## 10. 来源公式的限定修正

除已给出替代的条件均值、Strang support、policy precision 和 PMMH ratio 外，还有三处直接可核算的源内问题：

1. **Cubic OU covariance。** Appendix A 取 $A=-1$，按主文积分应为

\[
C_\delta=\frac{\sigma^2}{2}(1-e^{-2\delta}).
\]

附录相应 Gaussian variance 漏掉 $1/2$，主文 covariance 积分本身正确。

2. **FHN matrix exponential 的时间参数。** Appendix B 多处打印 $\sqrt{\kappa\Delta}$，正确形式是 $\sqrt\kappa\,\Delta$，其中 $\kappa=4\gamma/\epsilon-1$，半角为 $\sqrt\kappa\,\Delta/2$。由

\[
\left(A+\tfrac12I\right)^2=-\tfrac\kappa4I
\]

可直接验证

\[
e^{A\Delta}=e^{-\Delta/2}\left[
\cos\!\left(\frac{\sqrt\kappa\,\Delta}{2}\right)I+
\frac{2\sin(\sqrt\kappa\,\Delta/2)}{\sqrt\kappa}
\left(A+\tfrac12I\right)\right].
\]

$\kappa<0$ 用对应双曲函数，$\kappa=0$ 取连续极限。第 4 节 matrix exponential 和 covariance 积分覆盖这些情形，不必依赖误排的专用公式。

3. **Jacobian 形状。** Appendix B 把二维 $D\Gamma_h$ 打印为两项列向量。正确 Jacobian 为

\[
D\Gamma_h(v,u)
=\operatorname{diag}\!\left(
\frac{a}{[a+(1-a)v^2]^{3/2}},1\right).
\]

Algorithm 1 另有重采样权重和 denominator 下标混杂，按前一层归一化权重、正确祖先索引和同一层 normalization 即恢复普通 FK particle filter。以上修正针对实际 PDF 和 TeX 显示内容，没有推断 artifact 或作者数值结果使用了相同错误。

## 11. 实验的实际证据

### 11.1 Cubic SDE

模型 $dX_t=-X_t^3dt+\sigma dW_t$，$X_0=0$。模拟用细步长 $10^{-5}$ 的 Strang trajectory，再以 $\Delta_{\rm obs}=.1$ 取样，$T_{\rm obs}=100$，约 1000 个区间。[§5.1]

- 数值不稳定性引入例用 $\sigma=100$。Appendix G/Figure 5 另扫 $\sigma=25,30,35,40$，统计每 1000 个区间中有粒子值超过 $10^5$ 的比例，每个 $\sigma$ 有 10 次 trials。这是数值 sampler 的事件，不是连续 SDE 爆炸概率。
- Figure 5 的 $\sigma=40$ 曲线随桥数 4 至约 7 先升再降，不能写成对每个 $K$ 严格单调改善。
- Figure 2 用 $\sigma=20$，比较 5、10、20、40 子步 likelihood，参数网格间距 .5。“Simulated Truth” 是 100 子步近似，不是解析连续 likelihood。曲线趋近支持该设置的数值改善，不证明一般 density 收敛。

### 11.2 FHN：参数后验与点估计

模型

\[
dV_t=\epsilon^{-1}(V_t-V_t^3-U_t)dt,\qquad
dU_t=(\gamma V_t-U_t+\beta)dt+\sigma_2dW_t.
\]

只观测 $V$，$\sigma_1=0$，真实参数 $(\epsilon,\gamma,\beta,\sigma_2)=(.1,1.5,.8,.3)$。[§5.2]

| 设置 | 实际干预与观察 | 可以支持的范围 |
|---|---|---|
| PMMH，Figure 3 | 约 1000 个观测，$\Delta=.02$，$T=20$，链长 $10^5$。BPF 125 粒子，cSMC 10 粒子，同类对称 log-RW proposal。 | cSMC marginal density 曲线更平滑，作者报告约快 2 倍。没有完整 ESS/sec、多链诊断或 posterior 真值，不能由曲线认证充分混合。 |
| 单参数点，Figure 6 | 在 posterior mode $(.0993,1.53,.763,.308)$，各作 1000 次 likelihood 估计。 | cSMC log-normalizer 分散度远小，只支持该参数点的经验表现。 |
| MLE，Figures 4,7 | $\Delta=.05$，约 1000 个观测，100 个独立 trials，LT/Strang 各自未桥接、4、8 桥配置。 | 桥接后许多坐标更接近真值，LT/Strang 在部分坐标仍有竞争。没有统一偏差阶或固定总预算支配结论。 |

正文未充分说明每个独立 trial 是否重新生成数据，不写成已经核实的 100 个独立数据集。Figure 3 caption 称 cSMC 蓝线，实际为黑色实线，解释依实际图例。实验标签 0 表示未桥接，不是 $\delta=\Delta/K$ 的 $K=0$。桥数措辞有混用，保留作者标签，不擅自补出内点数。

### 11.3 真实数据

公开 dorsal-rootlet voltage dataset 的 Cutaneous Stimulation 1609，$\Delta=.02$，$T=250$，12500 个数据点。[§5.3, data access]

观测已中心化。作者对每个候选参数额外模拟 $10^5$ 步 Strang trajectory 估计 stationary mean，再把该估计均值加回数据。外层目标还含一个 Monte Carlo plug-in。给定重构数据的 CSMC 无偏性不消除该均值误差，也不自动得到对未知 offset 积分后的完整 likelihood。

报告的完整参数向量为 $(\epsilon,\gamma,\beta,\sigma_1,\sigma_2)=(.283,72.7,87.3,0,2.46)$，与被引 ABC 的四个待估参数结果 $(.033,6.701,3.995,.133)$ 相差较大。作者讨论 model misspecification、mean 丢失导致的弱可识别性和不同优化目标。不同目标下的点估计差异不足以判定算法优劣。

Figure 8 是一次 SPSA 轨迹，log-likelihood 趋平但 log 参数仍缓慢漂移。Figure 9 是九条模拟与同一个 20 ms 片段的视觉对照，没有留出预测或定量拟合验证。此处不提供 FP 的生物机制推论。

### 11.4 资源与 artifact

使用 R、mvnfast、完整二次 regression。SPSA 每个 measurement 通常用 20 粒子，观察到每次 cSMC 约 2–3 次 refinement。bridged SPSA 常用至多 200 步，每步 5 次 measurements。还有粗网格初始化和相邻 SPSA measurement 的 guide warm start。[Appendices D,F,H]

实验平台为 Warwick Intel Xeon Gold 6248R，报告计时另取 Apple M3 Pro。4 桥、8 桥每 measurement 约 10 秒、20 秒。按 20 秒、5 measurements、200 步相乘约 5.56 小时，正文另报至多 4.5 小时，需实际步数或未四舍五入计时才能对齐，不能当作同一精确预算。真实数据 1500 步、每步约 50 秒，名义量级约 20.8 小时。

README 给出实验脚本和种子 1–100 的入口，当前返回树未提供 cSMC gitlink 包实现，真实数据还需外部载入。数据入口为 [Mendeley ybhwtngzmm/1](https://data.mendeley.com/datasets/ybhwtngzmm/1)。没有下载核查数据、补齐依赖或复现图表。仓库 updated_at 不是代码提交日期。

## 12. 完整成本与后续可用性

对 $M$ 个观测区间、每段 $K$ 子步，一次 particle pass 有 $O(MKN)$ 次状态传播。稠密 Gaussian 均值、noise sampling 和 quadratic guide 评估可各需 $O(d^2)$，每个参数配置的 matrix preparation 可需 $O(d^3)$。

full-state guide 的 $p_d=(d+1)(d+2)/2$ 个系数，用普通稠密最小二乘可需 $O(Np_d^2+p_d^3)$。学习在多个时间层和多个 refinement 轮次重复，hidden endpoint 的回归维数较小。最终生产 filter 的 $N$ 不能代表全部训练成本。

后向学习若保存全部训练粒子与系数，一般需要 $O(MKNd)$ 粒子存储及 guide 存储。单向 likelihood pass 可串流，不表示整段 policy refinement 也有固定历史内存。

可独立保留两条建设性结论：

- 选择能把噪声传播到所需坐标的 linear split，用有限 rank 证书与条件 Gaussian 公式编译无噪声端点。
- 对只可逆到像集的 flow，维护支持、Jacobian 和初始条件，仍能得到可用的 Gaussian-kernel FK 目标。

这些结论没有要求 Astra 接受新状态定义或实施路线。本次未修改 FP 核心定义、架构、实验协议、实现或 research/frontier/ 文件。

完整 v1 阅读已完成。尚未证明的是实际模型上的参数统一 density/log-likelihood 误差、所用拟合的普遍收敛、一般高维 particle 复杂度及完整 artifact 的版本一致性。下一篇按最新共享历史、Astra 请求和研究员占用记录重新选择。



# Mehta 2026 — 从 HMM 构造预测坐标与滤波稳定性证书

## 版本、来源与实际阅读

- 作者：Prashant G. Mehta。
- 题目：Duality Theory for Filter Stability in Hidden Markov Models。
- 精确版本：[arXiv:2610.15085v1](https://arxiv.org/abs/2610.15085v1)，2026-10-10 17:36:40 UTC。[原始 PDF](https://arxiv.org/pdf/2610.15085v1)，56 个物理页。[TeX 源包](https://arxiv.org/src/2610.15085v1)。
- 2026-11-27 上海时间重新读取固定版本与 latest 主页面，提交历史均只有 v1。此处按预印本归档。SIAM 排版样式不构成期刊接收证明。
- 主读者 Pro-C 完整读取 main.tex 全部正文与证明、两个宏文件、两个实际引用的 figure TeX 和完整 main.bbl。覆盖正文 §§1–8、Appendices A–J、全部公式与证明、2 幅示意图、1 张符号表、4 个正文脚注、首页材料和 66 条参考文献。原始 PDF pp.5,11,13–14,18,22,25–28 的图表、模型时序、主要定理和速率表述已目视核对。没有把所有被引用文献当作已读。
- 两个辅助读者分别核查结构对偶与稳定性/速率依赖。主读者亲自完成全篇，并核对下面独立推导。辅助阅读不是第二次全篇认证。
- 作者在 p.28 致谢中披露使用 LLM 辅助参考文献核查、校对和代数恒等式的数值验证，同时声明数学与文字由作者负责。本次没有运行原作者代码、训练、数值实验、穷举反例或形式化证明。
- 本文没有经验基准。两图分别是 HMM 时序和后向方差耗散示意，不能读作实验数据。

以下把原文定理与本次直接推导分别标注。没有修改 FP 核心定义、架构、实验或研究路线，也不对标准线性预测实现和正矩阵收缩作新颖性主张。

## 1. 这篇论文提供什么

**原文的核心是从一个给定的有限 HMM 构造两类对象：可观测方向的有限维子空间，以及后向条件期望的方差耗散证书。** 前者把 probabilistic observability 转成有限线性代数，后者用对偶最优控制证明错误先验的影响消失。[§§3–8]

本次进一步把这些对象整理成四个可执行工具：

1. 用有限未来查询基编译精确递推预测器，构造时不用枚举所有观察词。
2. 把固定先验的 Poincaré 常数写成一个显式的 \(d\times d\) 最大特征值问题。矩阵的构造仍有观察词求和成本。
3. 在另有统一 Poincaré 下界时，直接得到期望 \(\chi^2\) 的指数界。
4. 在 primitive 转移与严格正发射的更强条件下，给出所有观察词上一致的重置窗口误差界，以及可直接计算的窗口长度。

这些构造以已知模型为输入。它们不包含未知模型学习、经验预测结构发现或有限位实现的保证。

## 2. 模型时序、先验与稳定性的准确对象

### 2.1 先发射所依据的状态不能弄错

状态集 \(\mathsf S=[d]\)，观测集 \(\mathsf O=\{0,\ldots,m\}\)，记 \(q=m+1\)。转移矩阵 \(A\in\mathbb R^{d\times d}\) 与发射矩阵 \(H\in\mathbb R^{d\times q}\) 都逐行随机。原文采用

\[
\Pr(X_{t+1}=j,Z_{t+1}=z\mid X_t=i)
=A(i,j)H(i,z).
\]

即 \(Z_{t+1}\) 由转移前的 \(X_t\) 发射，且给定 \(X_t\) 时与 \(X_{t+1}\) 条件独立。令

\[
D_z=\operatorname{diag}(H(:,z)),\qquad M_z=D_zA.
\]

函数和测度都用列向量。函数后向乘 \(M_z\)，测度前向乘 \(M_z^\top\)。于是

\[
\sigma_{t+1}^\rho=M_{Z_{t+1}}^\top\sigma_t^\rho,\qquad
\pi_{t+1}^\rho=
\frac{M_{Z_{t+1}}^\top\pi_t^\rho}
{\mathbf1^\top M_{Z_{t+1}}^\top\pi_t^\rho}.
\]

分母在该先验的正概率分支上使用。若采用“新状态发射”的另一种 HMM 约定，算子顺序需要相应改变。[§§2.1–2.2，Fig.1]

本文没有改变 \(A,H\) 的环境动作。后文 \(U_t\) 是对偶估计问题的数学控制变量。

### 2.2 主定理的先验条件

\(\mu\) 是产生数据的真实先验，\(\nu\) 是用同一观察串运行的错误先验。主稳定性定理要求

\[
\mu\sim\nu.
\]

即两者具有相同支撑，可以共同落在 simplex 的一个面上，不需要平稳先验。有限状态下

\[
a=\min_{\operatorname{supp}\nu}\frac{\mu}{\nu}>0,\qquad
b=\max_{\operatorname{supp}\nu}\frac{\mu}{\nu}<\infty,\qquad
\alpha=a/b.
\]

在有定义的状态上令 \(\gamma_T=\pi_T^\mu/\pi_T^\nu\)，在零质量状态上采用原文约定 \(\gamma_T=1\)，则

\[
\alpha\le\gamma_T(x)\le\alpha^{-1}.
\]

因此整个后向解也有同样的统一有界性。这是 §7 紧致性论证的关键，不应删去等价先验后仍照用该证明。[Assumption 1，Definition 2.1，Proposition 7.1]

### 2.3 原文真正证明的稳定性

Theorem 7.2 的结论是

\[
\mathbb E^\mu\chi^2(\pi_T^\mu\mid\pi_T^\nu)\longrightarrow0,
\qquad
\chi^2(\pi_T^\mu\mid\pi_T^\nu)
=\pi_T^\nu[(\gamma_T-1)^2].
\]

外层期望是实际数据律 \(\mathbb P^\mu\)。由

\[
\|\pi_T^\mu-\pi_T^\nu\|_{\rm TV}
\le\tfrac12\sqrt{\chi^2(\pi_T^\mu\mid\pi_T^\nu)}
\]

得到期望 TV 收敛。KL 和固定有界测试函数的均方误差也受控制。例如 \(\|f\|_\infty\le B\) 时

\[
|\pi_T^\mu(f)-\pi_T^\nu(f)|^2
\le B^2\chi^2(\pi_T^\mu\mid\pi_T^\nu).
\]

主定理本身没有给出所有观察词的一致界、任意先验的一致常数或显式窗口长度。这些需要后面明确附加的条件。

## 3. 原文的结构对偶怎样变成有限构造

令

\[
h^k=H(:,k)-H(:,0),\qquad k=1,\ldots,m.
\]

原文的 dual controllable subspace 从

\[
\mathcal C_0=\operatorname{span}\{\mathbf1\}
\]

开始，并满足

\[
\mathcal C_{T+1}
=A\mathcal C_T+
\sum_{k=1}^m\operatorname{diag}(h^k)A\mathcal C_T.
\tag{1}
\]

Proposition 5.2 证明其单调增加，第一次相等后永久稳定，而且

\[
\tau_2=\min\{T:\mathcal C_{T+1}=\mathcal C_T\}\le d-1.
\]

极限 \(\mathcal C\) 是包含常数函数、对这些后向算子封闭的最小子空间。此结论不需要正发射、混合或滤波稳定性。[Proposition 5.2，Corollary 5.3，Appendix F.1]

原文定义 \(\mathcal N_T\) 为在长度 \(T\) 的观察路径律上不能区分的先验差方向，证明

\[
\mathcal N_T=\mathcal C_T^\perp,\qquad
\mathcal N=\mathcal C^\perp.
\tag{2}
\]

因而

\[
\text{observable}\iff\mathcal C=\mathbb R^d,
\]

\[
\text{detectable}
\iff A^\top|_{\mathcal N}\text{ 的谱半径}<1
\iff E^{\rm PER}(A)\subseteq\mathcal C.
\tag{3}
\]

其中 \(E^{\rm PER}(A)\) 是单位模谱对应的实子空间，可以写成 \(\ker(A^p-I)\)，\(p\) 为 recurrent classes 周期的最小公倍数。原文还证明 \(\mathcal N\) 对 \(A^\top\) 不变。[Proposition 5.4，Appendix F.2]

可观测性要求不同先验在某些有限观察序列上产生不同的概率律，不等同于一步发射矩阵满秩。可检测性允许不可观察方向存在，但要求其在隐藏动力学中自行衰减。

### 3.1 独立推导：逐符号闭包与未来查询

因为

\[
A=\sum_zM_z,\qquad
\operatorname{diag}(h^k)A=M_k-M_0,
\]

且反向也能由这些线性组合恢复每个 \(M_z\)，式 (1) 等价于

\[
\boxed{\mathcal C_{T+1}=\sum_{z\in\mathsf O}M_z\mathcal C_T.}
\tag{4}
\]

对观察词 \(w=z_1\cdots z_\ell\)，定义

\[
v_w=M_{z_1}\cdots M_{z_\ell}\mathbf1.
\]

它的第 \(x\) 个分量正是 \(\Pr(Z_{1:\ell}=w\mid X_0=x)\)。所以

\[
\mathcal C_T=\operatorname{span}\{v_w:|w|=T\}.
\]

短词通过末尾观察边缘化已包含在这个空间内。极限子空间恰好保存所有有限未来观察概率的线性方向。

### 3.2 独立推导：只扩展独立查询的工作队列

从 \(\mathbf1=v_{\varnothing}\) 开始，保留一个独立查询基。每次取出尚未处理的基向量 \(b=v_w\)，先算 \(Ab\)，再依次构造

\[
H(:,z)\odot Ab=M_zv_w=v_{zw}.
\]

若候选不在现有基的张成中，就保留它及其词见证，加入队列。这里是前接符号 \(z\)。以 FIFO 方式处理，可保留按长度增长的见证。

终止时每个基向量在每个 \(M_z\) 下的像都落回当前空间，故该空间封闭。所有入选向量又都是合法未来查询，故输出恰好是 \(\mathcal C\)。

若最终维数为 \(r\le d\)，只处理 \(r\) 个独立向量，检查至多 \(qr\) 个候选。共享每个 \(Ab\)，并维护增量消元或正交分解，可在

\[
\boxed{O(d^2r+qdr^2)}
\tag{5}
\]

算术操作内构造。生成的独立查询长度不超过稳定化深度，从而不超过 \(d-1\)。这是由递推直接得到的复杂度界，论文未单独声称此算法复杂度。它采用精确 rank 判断，不包含浮点病态性、模型估计误差或系数位复杂度的保证。

可检测性也可落地：求 \(\ker B^\top\) 的基 \(Q_N\)，解

\[
A^\top Q_N=Q_NJ,
\]

再检查 \(J\) 的谱半径是否小于 1。有限查询深度是穷尽可观察方向的长度，不能当作滤波误差已经很小的等待时间。

## 4. 独立推导：把子空间编译成精确预测状态

取上述基

\[
B=[b_1,\ldots,b_r],\qquad b_1=\mathbf1.
\]

闭包保证每个符号存在唯一矩阵

\[
M_zB=BK_z.
\tag{6}
\]

定义在线坐标

\[
s_t=B^\top\pi_t.
\]

如果保留的是查询词基，\(s_t(j)\) 就是该核心未来观察词的条件概率，且 \(s_t(1)=1\)。下一符号预测与更新为

\[
p_t(z)=e_1^\top K_z^\top s_t,
\qquad
\boxed{s_{t+1}=\frac{K_z^\top s_t}{e_1^\top K_z^\top s_t}}
\tag{7}
\]

其中更新只用于 \(p_t(z)>0\) 的分支。证明是

\[
B^\top M_z^\top\pi_t=(M_zB)^\top\pi_t=K_z^\top s_t.
\]

任意未来词仍可精确读出：

\[
\Pr(w\mid Z_{1:t})
=s_t^\top K_{z_1}\cdots K_{z_\ell}e_1.
\tag{8}
\]

一次已观察符号的更新需 \(O(r^2)\) 算术操作，所有下一符号概率需 \(O(qr)\)，所有算子存储 \(O(qr^2)\)。状态为 \(r\) 个实数，其中一个恒为 1。

这是已知模型的线性预测实现。\(K_z\) 可以有负条目，\(r\) 个实数也不是 \(r\) 个有限记忆符号。该构造不保证有一个仅 \(r\) 个正隐藏状态的 HMM，更不意味着用普通样本已经学习到这些算子。它确实允许在没有完整隐藏 posterior 遗忘定理时，直接删除不影响未来观察的隐藏区别。

## 5. 变分对偶、后向方差与零耗散

### 5.1 对偶方程不是环境控制策略

原文以有限观测编码 \(e(k)\) 为标准基，\(e(0)=-\sum_ke(k)\)，设

\[
W_{t+1}=e(Z_{t+1})-h(X_t).
\]

其条件协方差为 \(R(X_t)\)。状态转移的 carré du champ 为

\[
\Gamma f=A(f^2)-(Af)^2.
\]

BS\(\Delta\)E 是

\[
Y_t(x)=(AY_{t+1})(x)+h(x)^\top[U_t+V_t(x)]
-V_t(x)^\top e(Z_{t+1}),\qquad Y_T=F.
\tag{9}
\]

\(U_t\) 仅依赖已有观察。有限观察字母表使每个观察可测估计器有唯一的常数加适应增量表示，从而建立该方程的存在唯一性。这里按整个有限观察树选取函数版本，概率为零的坐标与概率意义下的等价类需按原文约定区分。[Proposition 3.4，Appendix C]

设

\[
\ell(y,v,u,x)=\Gamma y(x)+(u+v(x))^\top R(x)(u+v(x)).
\]

原文证明

\[
M_t^U=Y_t(X_t)+\sum_{s<t}U_s^\top e(Z_{s+1})
\]

是鞅，且其二次变差是上述非负运行代价的条件期望和。估计器

\[
S_T=\rho(Y_0)-\sum_{t<T}U_t^\top e(Z_{t+1})
\]

满足精确恒等式

\[
\mathbb E^\rho|F(X_T)-S_T|^2
=\operatorname{Var}^\rho(Y_0(X_0))
+\mathbb E^\rho\langle M^U\rangle_T.
\tag{10}
\]

对 \(U\) 优化等价于求观察可测 MMSE 估计器。[Proposition 5.5，Appendix D]

### 5.2 特殊中心化终端条件使零控制最优

若

\[
\pi_T^\rho(F)=c
\]

在所有正概率观察分支成立，则 MMSE 估计器就是常数 \(c\)，\(U^\star=0\) 达到最小代价。它不是一般终端函数都可以忽略观察的声明。严格正发射可以加强控制解的唯一性，但本篇证明不需要该唯一性。[Corollary 5.6]

此时

\[
Y_t(x)=\mathbb E^\rho[F(X_T)\mid Z_{1:t},X_t=x],
\qquad M_t=Y_t(X_t)
\]

并保持 \(\pi_t^\rho(Y_t)=c\)。于是

\[
\underbrace{\rho[(Y_0-c)^2]}_{\text{初始方差}}
+\underbrace{\mathbb E^\rho\langle M\rangle_t}_{\text{耗散}}
=\underbrace{\mathbb E^\rho\pi_t^\rho[(Y_t-c)^2]}_{\text{时刻 }t\text{ 的期望条件方差}}.
\tag{11}
\]

所以方差沿后向时间递减。它不是前向每条观察路径上的 posterior 距离单调性，也不是普通隐藏状态本身的不确定性。[Proposition 3.2，Fig.2，Appendix B]

### 5.3 原文 invariance principle 的三条入口

令 \(\tau_0(A)\) 为遍历情形下所有起点均可到达每个 recurrent 状态的最早共同长度。令 \(\tau_1(A)\) 为 recurrent 可达集合进入 \(p\)-周期模式的指标。原文的 ergodic 是 \(E^{\rm PER}(A)=\operatorname{span}\{\mathbf1\}\)，允许暂态状态，不等于 primitive。

| 入口 | 使用的块长 | 发射条件 |
|---|---|---|
| \(A\) ergodic | \(\tau\ge\tau_0(A)\) | \(H_{\min}>0\) |
| HMM observable | \(\tau\ge\tau_2(A,H)\) | 允许零发射项 |
| HMM detectable | \(\tau\ge\max\{\tau_1(A),\tau_2(A,H)\}\) | \(H_{\min}>0\) |

Lemma 3.3 在任意先验 \(\rho\)、满足中心化终端条件的 \(F\) 下给出

\[
\mathbb E^\rho\langle M\rangle_\tau=0
\Longrightarrow Y_0(x)=c
\quad(x\in\operatorname{supp}\rho).
\tag{12}
\]

证明的具体机制如下。[§§4–6，Appendices E–H]

- 正发射给 \(R(x)\succeq H_{\min}I\)，所以零耗散迫使 \(V_t(X_t)=0\) 和 \(\Gamma Y_{t+1}(X_t)=0\)。沿正概率可达路径，\(Y_0(x)=Y_\tau(x')\)。遍历可达性使这些值相同。
- 更一般地，取 \(g=\mathbb E^\rho Y_\tau\) 和 \(A^p\) 的 Cesàro 投影 \(\Pi\)，构造 \(\widetilde f=\Pi A^\tau g\in E^{\rm PER}(A)\)，并证明它在先验支撑上等于 \(Y_0\)。这是零耗散的必要表示，不是任意 peripheral 向量都满足给定终端约束的逆命题。
- 可观测分支用任意可达对偶方向 \(\widetilde f\in\mathcal C\) 扰动控制。最优性对所有正负 \(\epsilon\) 成立，迫使一阶项 \(\rho[(Y_0-c)\widetilde f]\) 为零。若 \(\mathcal C=\mathbb R^d\)，立即得到 \(Y_0=c\)。这条分支不需要正发射。
- 可检测分支把 peripheral 表示放入 \(\mathcal C\)，取上述扰动方向为 \(\widetilde f\)，得到方差为零。

Proposition 6.1 的 converse 有明确量词：若对每个正整数块长、每个先验和所有相应中心化终端函数都具有零耗散推出零方差的性质，则 HMM 必须 detectable。Appendix H 从不可检测的 cyclic-class 方向构造反证。不要把这个全称 invariance converse 改写成未经本篇证明的任意设定滤波稳定性充要条件。

## 6. 从后向方差到主稳定性定理

定义依赖 \((\mu,\nu,T)\) 的后向映射

\[
y_0(x)=\mathbb E^x[\gamma_T(X_T)].
\]

原文证明

\[
\nu(y_0)=1,\qquad
\boxed{\mathbb E^\mu\chi_T^2=\mu(y_0)-\nu(y_0)}.
\tag{13}
\]

所以只需证明 \(y_0\to1\) 在 \(\nu\) 的支撑上成立。[Proposition 3.1]

等价先验把所有终端比值和后向解限制在固定盒子 \([\alpha,\alpha^{-1}]\)。总耗散有一个不依赖终止时间的上界。长时间区间中必有一个固定长度 \(\tau\) 的小耗散窗口。

原文不把随终止时间移动的窗口直接当作固定系统极限。它证明 BS\(\Delta\)E 的 shifted solution 可由窗口起点的一对滤波分布和后续观察构造，再把随机先验与固定深度终端函数的联合分布放在紧集上。子序列极限的耗散为零，中心化约束是闭的。Lemma 3.3 迫使极限方差为零，与假设的正下界矛盾。[Proposition 7.4，Definition 7.5，Corollary 7.6，§7.3，Appendix I]

这个证明覆盖 simplex 边界，因此不会因为全 simplex 缺少统一 Poincaré 下界而失效。它仍是定性收敛证明。

## 7. Poincaré 常数与支撑几何

固定 \(\tau\)，令 \(L[F]=Y_0\)，并令 \(\mathcal E[F](x)=\mathbb E^x\langle M\rangle_\tau\)。对满足 \(\pi_\tau^\rho(F)=0\) 的终端函数，定义

\[
\beta(\rho)=
\inf_{\rho(|L[F]|^2)=1}\rho(\mathcal E[F]),
\qquad
\kappa(\rho)=\tau^{-1}\log(1+\beta(\rho)).
\tag{14}
\]

约定空可行集的下确界为 \(+\infty\)。于是

\[
\rho(|L[F]|^2)
\le e^{-\tau\kappa(\rho)}
\mathbb E^\rho|F(X_\tau)|^2.
\tag{15}
\]

原文 \(\mathsf N_\tau\) 是所有这样的后向初始方差恒为零的先验集合。它是闭集且由整个支撑 stratum 组成，包含每个点质量先验。此处 \(\kappa=\infty\) 表示所考察的后向方差已经为零，不表示隐藏状态估计对任何任务都没有误差。[Definition 8.1，Proposition 8.3]

Lemma 8.4 证明：

1. 在 \(\mathsf N_\tau\) 外，下确界达到。
2. \(\kappa\) 在整个 simplex 上上半连续。
3. \(\kappa\) 在每个固定支撑的 stratum 内连续。
4. 任一 invariance 条件成立时，每个先验都有 \(\kappa(\rho)>0\)，允许 \(+\infty\)。

其证明把概率为零的终端坐标剔除，并使用逐观察分支的条件中心化投影。固定支撑内的概率比界控制投影扰动，支持最小值存在和连续性。跨支撑边界不能直接照用相同的强正下界。[Appendix J.1–J.2]

### 7.1 skeleton 结论

令

\[
\mathcal K_N=\sum_{n=0}^{N-1}\kappa(\pi_{n\tau}^\nu),
\qquad N=\lfloor T/\tau\rfloor.
\]

Proposition 8.5 给出

\[
\operatorname{Var}^\nu(y_0(X_0))
\le
\mathbb E^\nu\left[e^{-\tau\mathcal K_N}\chi_T^2\right].
\tag{16}
\]

证明依赖分块条件方差关系与适应性，指数因子保留在期望内。一般不能把它当成逐观察词的前向 \(\chi^2\) 收缩。

设 \(\kappa_*(\rho)=\liminf_{\rho'\to\rho}\kappa(\rho')\)，\(\mathcal D_*=\{\kappa_*=0\}\)。Theorem 8.6 表明：若累计 \(\mathcal K_\infty=\infty\) 几乎处处，则滤波稳定。否则，在累计值有限的路径上，filter skeleton 到 \(\mathcal D_*\) 的距离趋于零。第二条是速率判据的退化位置，不是“不稳定”的断言。

## 8. 独立推导：用 \(d\times d\) 矩阵直接计算固定先验常数

原文指出 \(\kappa\) 是有限维广义特征值问题。本节给出只在初始状态维数上取特征值的显式形式。它来自定义 (14) 和条件期望的伴随，不要求新模型假设。

对每个长度 \(\tau\) 的观察词 \(\zeta\)，定义

\[
M_\zeta=M_{\zeta_1}\cdots M_{\zeta_\tau},\qquad
j_{\zeta,x}=M_\zeta(:,x),\qquad l_\zeta=M_\zeta\mathbf1,
\]

\[
p_{\zeta,x}=\rho^\top j_{\zeta,x},\qquad
q_\zeta=\rho^\top l_\zeta,\qquad D_\rho=\operatorname{diag}(\rho).
\]

构造

\[
\boxed{
G_\rho=D_\rho^{1/2}
\left[
\sum_{\zeta,x:p_{\zeta,x}>0}
\frac{j_{\zeta,x}j_{\zeta,x}^\top}{p_{\zeta,x}}
-
\sum_{\zeta:q_\zeta>0}
\frac{l_\zeta l_\zeta^\top}{q_\zeta}
\right]D_\rho^{1/2}.
}
\tag{17}
\]

则

\[
\boxed{\eta(\rho)=\lambda_{\max}(G_\rho)
=(1+\beta(\rho))^{-1},\qquad
\kappa(\rho)=-\tau^{-1}\log\eta(\rho).}
\tag{18}
\]

\(\eta=0\) 对应 \(\beta=\kappa=\infty\)。零概率项不参与求和。若 \(\rho\) 不是全支撑，可以限制在其支撑上，或者保留零行列。

**推导。** 在 \(W=(Z_{1:\tau},X_\tau)\) 的 \(L^2\) 空间上，令

\[
\mathsf T:F(W)\mapsto\mathbb E[F(W)\mid X_0],\qquad
\mathsf P=I-\mathbb E[\cdot\mid Z_{1:\tau}].
\]

以 \(\mathsf K\) 表示 \(\mathsf T\) 在中心化子空间 \(\operatorname{range}\mathsf P\) 上的限制。其伴随为

\[
(\mathsf K^*f)(\zeta,x)
=\mathbb E[f(X_0)\mid\zeta,x]
-\mathbb E[f(X_0)\mid\zeta].
\]

因此 \(\mathsf K\mathsf K^*=\mathsf T\mathsf P\mathsf T^*\)。将 \(L^2(\rho)\) 用 \(D_\rho^{1/2}\) 等距写成欧氏坐标，直接展开两个条件期望就得到 (17)。再由

\[
\eta=\|\mathsf K\|^2
=\sup_{F:\,\mathbb E[F\mid Z]=0}
\frac{\rho(|L[F]|^2)}{\mathbb E^\rho|F(X_\tau)|^2}
\]

与 Lyapunov 恒等式得到 (18)。这里略去范数为零的函数。如果 \(\mathsf K=0\)，分子恒为零，正好对应原文的空可行集。

由构造可检查

\[
G_\rho\succeq0,\qquad G_\rho\sqrt\rho=0,\qquad 0\le\eta\le1.
\]

所以该矩阵衡量的是：已知道观察词后，终点隐藏状态还能传递多少关于初始状态的中心化信息。原文 invariance 条件使其最大特征值严格小于 1。

最终特征值矩阵只有 \(d\times d\)，但显式形成它仍涉及 \(q^\tau\) 个词。直接稠密乘积与外积实现可以用 \(O(q^\tau d^3)\) 级算术工作，采用词树递推可复用前缀，并可流式累加矩阵。这里只压缩特征值问题，不宣称总体计算多项式于 \(\tau\)，也不把逐 \(\rho\) 的计算误称为整个 simplex 的全局最小值证书。

## 9. 独立推导：统一 Poincaré 下界给期望 \(\chi^2\) 指数率

另外假定沿参考滤波器的 skeleton 有确定性下界

\[
\kappa(\pi_{n\tau}^\nu)\ge k>0.
\tag{19}
\]

保留主定理的 \(\mu\sim\nu\)，并记

\[
e_T=\mathbb E^\mu\chi_T^2,\qquad
\chi_0^2=\chi^2(\mu\mid\nu),\qquad
a=\min\mu/\nu.
\]

式 (13) 可写成

\[
e_T=\nu[(\gamma_0-1)(y_0-1)].
\]

Cauchy–Schwarz 与 (16) 给出

\[
e_T^2\le
\chi_0^2 e^{-k\tau\lfloor T/\tau\rfloor}
\mathbb E^\nu\chi_T^2.
\]

观察律的似然比为

\[
\frac{d\mathbb P^\mu|_{\mathcal Z_T}}{d\mathbb P^\nu|_{\mathcal Z_T}}
=\mathbb E^\nu[\gamma_0(X_0)\mid\mathcal Z_T]\ge a.
\]

故 \(\mathbb E^\nu\chi_T^2\le e_T/a\)。若 \(e_T>0\)，消去一项 \(e_T\)，零值情形直接成立，得到

\[
\boxed{e_T\le\frac{\chi_0^2}{a}
e^{-k\tau\lfloor T/\tau\rfloor}.}
\tag{20}
\]

因此期望 TV 的指数为 \(k/2\)。这一推导避免先把固定终端上界代入、再连续开方所造成的速率损失。常数仍依赖先验，不是主定理无条件附带的统一率。

### 9.1 primitive 模型给紧支撑与任意先验的 burn-in

若 \(A\) primitive 且 \(H_{\min}>0\)，取一个 \(r_0\ge1\) 使 \(A^{r_0}>0\)，并设

\[
c=H_{\min}^{r_0}\min_{i,j}A^{r_0}(i,j)>0.
\tag{21}
\]

原文 p.28 已指出，对任意先验和所有观察词，在 \(t\ge r_0\) 后每个后验分量至少为 \(c\)。后面 §10 给出直接矩阵理由。因此参考 skeleton 落在

\[
\mathcal K_c=\{\rho:\rho_i\ge c\ \forall i\}
\]

这个 full-support stratum 的紧子集。固定一个有效 invariance 块长 \(\tau\)，连续性和正性保证存在有限 \(k>0\) 作为该集合上的下界。该存在性不提供便宜的全局求最小值算法。

任意两个原始先验，包括不等价先验，在相同的前 \(r_0\) 个观察后都进入 \(\mathcal K_c\)。条件于这段观察，重启 (20)，使用

\[
a\ge c,\qquad
\chi_0^2\le c^{-1}-1
\]

再取真实观察律期望，得到本次的条件性统一结论：

\[
\boxed{
\mathbb E^\mu\chi^2(\pi_T^\mu\mid\pi_T^\nu)
\le\frac{1-c}{c^2}
e^{-k\tau\lfloor (T-r_0)/\tau\rfloor},
\qquad T\ge r_0.
}
\tag{22}
\]

它适用于这里更强的 primitive/正发射条件，不是删掉 Theorem 7.2 的等价先验假设。每个有限词在这些条件下均为正概率，两个重启滤波器都定义良好。

## 10. 独立推导：显式、逐观察词的有限窗口界

同样使用 (21)，但下面无需求 \(\kappa\)。任意长度 \(r_0\) 的观察块矩阵 \(P=M_\zeta\) 满足

\[
P_{ij}\ge H_{\min}^{r_0}(A^{r_0})_{ij}\ge c,
\qquad P\mathbf1\le\mathbf1.
\tag{23}
\]

第一个不等式对隐藏路径逐项比较，第二个因为每行和就是该观察词的概率。于是任意初始分布经过第一块后，归一化后验每项都至少为 \(c\)。

### 10.1 归一化不会破坏比率振幅收缩

为书写此步，把两个当前概率向量写成行向量 \(u,v>0\)，并令

\[
r_i=u_i/v_i,\qquad
a_0=\min_i r_i\le1\le b_0=\max_i r_i,\qquad R=b_0/a_0.
\]

乘块矩阵后尚未归一化的比为

\[
s_j=\frac{(uP)_j}{(vP)_j}
=\sum_iw_{ij}r_i,\qquad
w_{ij}=\frac{v_iP_{ij}}{(vP)_j}\ge cv_i.
\]

各 \(w_{\cdot j}\) 都是概率向量，故可写成 \(cv+(1-c)\widetilde w_{\cdot j}\)。利用 \(\sum_iv_ir_i=1\)，

\[
c+(1-c)a_0\le s_j\le c+(1-c)b_0.
\]

最终归一化仅给所有 \(s_j\) 乘同一个正数，在最大比最小中消失。因此

\[
R'-1
\le\frac{(1-c)(b_0-a_0)}{c+(1-c)a_0}
\le(1-c)(R-1).
\tag{24}
\]

最后一步用 \(a_0\le1\)。第一块后 \(R\le c^{-2}\)。不足 \(r_0\) 的余块只对比率取凸组合，因而不增加 \(R\)。又

\[
\operatorname{TV}(u,v)
=\tfrac12\sum_iv_i|r_i-1|
\le\tfrac12(b_0-a_0)
\le\tfrac12(R-1).
\]

所以对任意两个初始分布、每一个观察词，

\[
\boxed{
\|\pi_T^\mu-\pi_T^\nu\|_{\rm TV}
\le
\min\left\{1,\frac{c^{-2}-1}{2}
(1-c)^{\lfloor(T-r_0)/r_0\rfloor}\right\},
\quad T\ge r_0.
}
\tag{25}
\]

若 \(c=1\)，第一块已使分布相同，单列处理即可。

### 10.2 可计算的窗口长度

对 \(0<c<1\)、目标误差 \(\epsilon>0\)，可取

\[
k_\epsilon=
\max\left\{0,
\left\lceil
\frac{\log((c^{-2}-1)/(2\epsilon))}
{-\log(1-c)}
\right\rceil\right\},
\qquad
N_\epsilon=r_0(1+k_\epsilon).
\tag{26}
\]

这是一条保守但明确的充分长度。两个任意历史在窗口起点产生两个任意先验，相同观察后缀对应相同矩阵乘积，所以 (25) 真正给出同后缀统一遗忘。对有界查询 \(f\)，误差进一步不超过 \(\operatorname{osc}(f)\epsilon\)。

该结论比主定理要求更强的模型条件，但它给出了有限记忆分析实际可以代入的确定性量。期望速率 (20) 与这条逐词界不能互相混写。

## 11. 两个小例子校准构造的含义

### 11.1 原文反例仍有极简的精确预测器

原文 Example 1 使用四状态转移

\[
A=\frac12
\begin{pmatrix}
1&1&0&0\\
0&1&1&0\\
0&0&1&1\\
1&0&0&1
\end{pmatrix},
\]

观测只揭示奇偶类，令 \(h=(-1,1,-1,1)^\top\)。这个 \(A\) 遍历，但发射含零项，完整隐藏 filter 可以保留错误初始类内比例。它说明“遍历”单独不能替代主定理所需的发射条件。[Example 1 与 §4 续例]

**本次直接代入：** \(Ah=0\)，所以

\[
\mathcal C=\operatorname{span}\{\mathbf1,h\}.
\]

取 \(B=[\mathbf1,h]\)，得到

\[
K_0=\begin{pmatrix}1/2&0\\-1/2&0\end{pmatrix},
\qquad
K_1=\begin{pmatrix}1/2&0\\1/2&0\end{pmatrix}.
\]

若 \(s=(1,u)\)，则 \(p(0)=(1-u)/2\)，\(p(1)=(1+u)/2\)，任一正概率首观测后都有

\[
s'=(1,0).
\]

之后未来观察为公平 iid 预测。于是同一个模型里，完整隐藏 posterior 不一定遗忘，但与未来观察相关的坐标立即归一。这是直接构造预测状态的理由，不是仅凭隐藏滤波反例否定预测机制。若任务关心隐藏奖励，必须把相应查询加入保留对象，不能自动沿用这个两维观察预测器。

### 11.2 无信息观察的两状态模型

作为本次公式校准，令两行发射分布相同且严格正，并取

\[
A=\begin{pmatrix}1-u&u\\v&1-v\end{pmatrix},
\qquad 0<u,v<1,\qquad \lambda=1-u-v.
\]

观察没有提供状态信息。对平稳先验 \(\rho=(v,u)^\top/(u+v)\)，取 \(\tau=1\)，初始状态的中心化空间 \(L^2_0(\rho)\) 一维。终端函数仍可依赖观察，其中心化空间有 \(q\) 个维度，后向算子将它映入一维的初始状态中心化空间。直接计算

\[
\eta(\rho)=\lambda^2,\qquad
\kappa(\rho)=-2\log|\lambda|
\]

其中 \(\lambda=0\) 时 \(\kappa=\infty\)。若参考先验平稳，则

\[
\chi^2(\mu A^T\mid\rho)=\chi^2(\mu\mid\rho)\lambda^{2T}
\]

这里该行把先验按行向量书写，\(A^T\) 表示 \(T\) 次幂。因此 (20) 的指数与这个可精确求解的例子一致。这是手算，不是数值复现实验。

## 12. 与有限记忆文献和受控模型的接口

本篇原文引用 Kara–Yüksel 的有限记忆政策与 Q-learning 文献，但自身分析的是无环境动作 HMM。它为此前 [Kara 2025](KARA-2025-FINITE-MEMORY-LINEAR.md) 和 [Huang 2026](HUANG-2026-NEURAL-POMDP.md) 所需的稳定性前提提供可检查对象，不自动完成其受控版本。

可以分别使用两个接口：

- 对只需要实际数据律下平均滤波误差的论证，(20) 或带 burn-in 的 (22) 给出条件性期望界。
- 对需要同后缀、不同完整历史上一致距离的论证，必须使用像 (25) 这样的逐词界，或另外证明等强假设。

两者都不能把“在指定先验上重置后处理后缀”直接等同于“真实长期过程中仅条件于该后缀”。此前有限记忆笔记中的条件分布区别仍保留。

### 12.1 已知受控模型的代数编译候选

若另给有限受控模型的联合算子

\[
M_{a,z}(x,x')=\Pr(x',z\mid x,a),
\]

则可对全部 \((a,z)\) 同时做 (4) 的闭包。若任务还需奖励预测，把各动作的奖励均值函数加入初始函数空间，再闭包，仍得到 \(M_{a,z}B=BK_{a,z}\) 和对应归一化更新。若奖励被观测并用于反馈，它也必须进入观测核，仅加入奖励均值函数不能保留其信息作用。

这是已知模型的线性代数推论。对原文的单一 \(A,H\) 得到的 detectability 或 BS\(\Delta\)E 稳定性证明，没有因此自动推广到动作切换。

路径收缩 (24) 则有一个清晰的可检验迁移条件：所有允许的相同长度动作—观察块矩阵均有共同的逐项正下界 \(c\)，且行和至多 1。若这些条件成立，同一比率代数适用。每个单独动作矩阵各自 primitive 并不单独建立所需的共同块条件。这里没有选择 FP 架构或建议改动核心模型。

## 13. 可保留的结论与覆盖边界

| 结论 | 证据层级 | 使用时必须保留的条件 |
|---|---|---|
| 有限子空间递推、观测/控制结构对偶 | 原文证明完整读过 | 已知有限 \(A,H\)，作者发射时序 |
| 对偶 MMSE 与方差耗散恒等式 | 原文证明完整读过 | 相应函数空间与中心化终端条件 |
| 期望 \(\chi^2\) 稳定 | Theorem 7.2 | 等价先验，三条模型入口之一 |
| 逐先验 Poincaré 正性与 stratum 连续性 | Lemma 8.4 | 固定有效块长，不自动有全 simplex 正下界 |
| 查询基工作队列与精确递推预测器 | 本次源内直接推导 | 精确已知模型与 rank 判断，实数状态 |
| \(d\times d\) Poincaré 矩阵 | 本次条件期望算子推导 | 固定先验与块长，观察词构造成本仍在 |
| 期望误差指数率 (20) | 本次直接推导 | 确定性的统一 skeleton 常数和先验比下界 |
| 任意先验 burn-in 与逐词窗口界 | 本次正矩阵推导 | primitive \(A\)、严格正发射，或另证共同正块条件 |

本文的历史滤波文献、连续时间 BSDE 理论、Chang–Mehta dual-filter 论文及其 JMLR 状态这里只按作者引用记录，没有进行额外全文阅读或认证。本次提取的是源内自足的有限模型构造与可证推论，不声称发现这些理论的最早版本。

### 跨 Session 恢复

Mehta2610.15085v1 已完整阅读。后续可以按具体需要计算一个模型的查询基或 \(G_\rho\)，但这不是当前已执行的实验。新普通论文应先 fetch、检查最新 Astra 请求与研究员覆盖，再从尚未完成的近期来源选择。本篇没有遗留需要恢复的正文阅读。

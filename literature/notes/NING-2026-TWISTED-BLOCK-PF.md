# Ning 2026 — 有限粒子池的精确引导、可验证方差学习与联合重采样

## 版本、来源与实际阅读

- 作者：Ning Ning，Texas A&M University。
- 题目：Twisted Block Particle Filters: A Local Particle-System Change of Measure for High-Dimensional State-Space Models。
- 精确版本：[arXiv:2611.28848v1](https://arxiv.org/abs/2611.28848v1)，提交于 2026-11-21 15:00:25 UTC。[44 页原始 PDF](https://arxiv.org/pdf/2611.28848v1)，[完整 TeX 源包](https://arxiv.org/src/2611.28848v1)。2026-11-27 上海时间复查官方版本历史，仍只有 v1。所读官方记录未认证一个已接受的期刊或会议版本。
- Pro-C 主读者完整读取 ms8.tex 的全部 2040 行、参考文献源文件及原始 PDF 的图表布局。覆盖正文 §§1–5、Appendices A–F、全部数学陈述和证明、Algorithm 1/S1、5 幅图、Tables 1–3 与 S1–S9、有限池例子的未编号表及一个署名脚注。PDF pp.9–10 印出 30 条参考文献，bib 文件有 31 条，未排出的键为 whiteleysupp。主读者均已读取。原始 PDF pp.1,3,4,6–8,14,16,27,36–44 的标题、全部图表和算法布局已目视检查。完整 TeX 中的 DIFadd 是活跃正文，正文后没有 DIFdel 删除段落。没有把注释当作已印出的论文内容。
- 两个辅助读者分别核对精确改变测度、辅助记录和实验范围，以及局部矩、方差判据和一致性证明。主读者完成全篇。独立推导经过有限手算核对，没有运行作者实验、审计代码、穷举状态空间或形式化证明。
- TeX 有一段被注释的 AI 使用披露，提及 OpenAI ChatGPT/Codex 参与草拟、理论推导、证明、文献检查、分析代码、实验与图。它没有出现在实际 PDF 中。该源注释是公开材料中的作者记录，不等于已印出的正式声明，更不表示这是一篇 OpenAI 官方论文。没有从披露推出实际正确性或错误性。

以下“原文”指作者的数学结论，“独立推导”指本次在明确条件下补充的构造。对标准概率方法不主张新颖性，不把独立构造写成作者定理。未修改 FP 核心对象、架构、实验或实现。

## 1. 可复用的核心工具

**作者在每个 block 的有限加权粒子池上，只倾斜一个随机位置的 offspring。对整个 offspring array 的密度比是引导值的经验平均，因此只需有限求和和 categorical 抽样即可精确校正。** 不必为任意连续引导函数计算解析积分，也不必改变模型传播核。[正文 §2，Appendix B]

该工具可以使用有偏、近似或随机训练得到的正引导值。正确性来自同一张冻结值表的抽样与校正，不来自引导函数已经等于真实未来似然。引导质量决定效率，而校正恒等式保持既定有限粒子基线的期望。

本次进一步构造：

1. 把有限池引导学习写成有显式梯度的凸二阶矩优化。
2. 用独立 continuation 样本，给出有限候选引导的高概率安全采用规则。
3. 把一个 distinguished child 扩展成联合倾斜的 r 个 children，保留精确校正，并给出 overlap 控制的校正二阶矩。
4. 给出一个严格二元交互例：所有非恒定单 child 引导都增大方差，双 child 联合引导则使校正 payoff 成为常数。

这些是已知模型、固定池与指定后续过程上的可执行工具。没有证明未知环境中的自主状态发现，也没有证明整个递归算法普遍降方差。

## 2. 必须分开的三个目标

### 2.1 模型、精确滤波与 block recursion

有限图顶点集 V 的大小为 d。状态空间为各点空间的乘积，转移和观测似然满足

\[
f_t(x,dz)=\prod_{v\in V}f_t^v(x^{N(v)},dz^v),
\qquad g_t(z)=\prod_{v\in V}g_t^v(z^v).
\tag{1}
\]

转移在给定旧状态后逐点独立，但各点条件分布可以依赖邻域。固定观测 y_{1:T}，记 P_t 为预测算子、C_t 为乘似然并归一化的算子。对于固定分区 \(\mathcal K\)，定义

\[
B\mu=\bigotimes_{K\in\mathcal K}\mu^K.
\]

精确滤波和确定性 block filter 分别为

\[
\pi_t=C_tP_t\pi_{t-1},
\qquad
\widetilde\pi_t=C_tBP_t\widetilde\pi_{t-1}.
\tag{2}
\]

block 操作发生在当前观测修正之前。它丢弃预测分布的跨块相关。原文从 block-product 初始分布开始。[正文 §2.1，Appendix B.1]

### 2.2 有限 N 的基线

从过去 recombined particles 传播

\[
Z_t^i\sim f_t(X_{t-1}^i,\cdot),\qquad i=1,\ldots,N.
\]

对每块计算

\[
a_t^K=\frac1N\sum_i g_t^K(Z_t^{i,K}),
\quad
w_t^{i,K}=\frac{g_t^K(Z_t^{i,K})}{Na_t^K},
\quad
\nu_t^K=\sum_iw_t^{i,K}\delta_{Z_t^{i,K}}.
\tag{3}
\]

普通 BPF 从每个 \(\nu_t^K\) 独立抽 N 个 children，再把相同 row 的块拼起来。它的 normalizer 为

\[
\widehat Z_T^B=\prod_{t,K}a_t^K,
\tag{4}
\]

在其自己的整条 BPF history 上求值。确定性 block recursion 的 normalizer 为

\[
Z_T^{\mathrm{block}}=
\prod_{t,K}(P_t\widetilde\pi_{t-1})^K(g_t^K).
\tag{5}
\]

必须区分原模型 likelihood \(Z_T\)、\(Z_T^{\mathrm{block}}\) 和有限 N 的 \(\mathbb E_B\widehat Z_T^B\)。一般三者不同。单块，或初始分布及动力学都与分区对齐的独立子系统，才恢复相应普通 PF likelihood 无偏结论。[正文 Theorem 1 后说明，Appendix B.2]

### 2.3 独立推导：一步、两块的精确分离

令 T=1、两个块，iid proposal \(Z_i\sim q=P_1\pi_0\)，块似然为 g_1、g_2。按两个求和索引是否相等分组，

\[
\mathbb E_B\widehat Z_1^B
=\left(1-\frac1N\right)q(g_1)q(g_2)
+\frac1Nq(g_1g_2).
\tag{6}
\]

右侧第一项是 block target，第二项是原模型 target。有限 N 期望可以同时不同于二者。这个公式只用于这里的一步两块 iid 情形，不是一般多步插值定理。

## 3. 一个 distinguished child 的完整有限池算法

### 3.1 抽样与校正

令 \(\mathcal G_t\) 包含旧 history、当前 proposal pool 及 guide 构造的随机记录，尚未包含当前 children。每块的正、有限、状态函数 \(\psi_t^K\) 必须在生成任何当前 offspring 前固定。

省略 t,K，令

\[
c=\nu(\psi),\qquad
H(x^{1:N})=\frac1N\sum_{j=1}^N\psi(x^j).
\tag{7}
\]

普通 array law 是 \(R=\nu^{\otimes N}\)。作者的 twisted law 为

\[
\widetilde R(dx)=R(dx)\frac{H(x)}c.
\tag{8}
\]

构造它只需要：

1. 均匀选位置 \(J\in[N]\)。
2. 其余 N−1 个位置 iid 抽自 \(\nu\)。
3. J 位置抽自 \(\nu_\psi(dx)=\psi(x)\nu(dx)/c\)。
4. 用同一张 guide 表计算实际 array 上的 H，乘校正 \(C=c/H\)。

每块独立选择自己的位置和抽样随机性。给定 J，各 children 独立。对 J 边缘化后，children 一般不独立。让所有 children 都从 \(\nu_\psi\) 抽样，或让所有 blocks 共享一个 distinguished 位置，都不是原文 Eq.8 的构造。[Algorithm 1/S1，Appendix B]

若不同 proposal labels 对应相同状态，它们的状态 guide 值应一致。有限池上采样只读取缓存值

\[
s_i=\psi(Z^i),\quad c=\sum_iw_is_i,\quad
\widetilde w_i=w_is_i/c.
\]

随机 guide 在求 H 时不能重新生成。常数 guide 恢复 BPF。N=1 时有限池为点质量，任何 guide 都不改变它。

### 3.2 实现成本

在 guide 值已经得到后，每块计算 c、倾斜权重、H 需要 O(N) 操作。采用线性预处理的 categorical sampling，总计每步新增算术可做到 \(O(N|\mathcal K|)\)。缓存所有块的 guide 表需要 \(O(N|\mathcal K|)\) 值。状态传播、复制和 guide 构造成本另计。

H 可以在复制 children 的循环里累计。这是实数操作计数，不是位复杂度、总 wall-clock 或等算力优势定理。

末时刻作者设 \(\psi_T^K=1\)。当前 \(a_T^K\) 已在重采样前得到，terminal children 不再影响 normalizer，没有必要再引入随机校正。

## 4. 增广 history 上的精确改变测度

沿同一条 TBPF history 定义

\[
D_T=\prod_{t,K}\frac{c_t^K}{H_t^K(X_t)},
\qquad
\widehat Z_T^{TB}
=D_T\prod_{t,K}a_t^K.
\tag{9}
\]

原文在包含 guide 随机性与必要 marks 的增广空间上证明

\[
D_T=\frac{d\mathbb P_B}{d\mathbb P_{TB}},
\qquad
\mathbb E_{TB}[D_TF]=\mathbb E_B[F].
\tag{10}
\]

对非负 F 可以用扩展期望，对有符号 F 要求 \(\mathbb E_B|F|<\infty\)。\(\mathbb P_B\) 的粒子边缘是普通 BPF。因此

\[
\boxed{\mathbb E_{TB}\widehat Z_T^{TB}
=\mathbb E_B\widehat Z_T^B.}
\tag{11}
\]

这不是一般的 \(Z_T\) 或 \(Z_T^{\mathrm{block}}\) 无偏定理。[正文 Theorem 1，Appendix B.2]

### 4.1 辅助 marks 不能随意添加

未来 guide 可以读取过去的 distinguished labels 或 ancestor marks。作者为两条路径使用相同的 pre-offspring guide-generation kernel。参考律先生成普通 BPF array，再按 TBPF 给定该已完成 array 后的条件 mark kernel 附加 marks。这样公共辅助 kernel 才消去。

条件于 array 后，参考 mark 一般不是独立均匀 J。标准 Borel 的记录空间保证所需条件 kernel 的存在。若 guide 具有额外随机性，D_T 也未必只由粒子 arrays 决定。

### 4.2 独立推导：校正是 Rao–Blackwell 化

固定一块与一个池。给定完整 array X，

\[
\Pr_{TB}(J=j\mid X)
=\frac{\psi(X^j)}{\sum_\ell\psi(X^\ell)}.
\]

所以

\[
\mathbb E_{TB}\left[
\frac c{\psi(X^J)}\middle|X\right]=\frac c{H(X)}.
\tag{12}
\]

对只依赖 X 的平方可积 payoff F，条件期望缩减方差：

\[
\operatorname{Var}_{TB}\left[F(X)\frac c{H(X)}\right]
\leq
\operatorname{Var}_{TB}\left[F(X)\frac c{\psi(X^J)}\right].
\tag{13}
\]

若后续条件 kernel 只依赖 array 而不依赖 J，同样可用于 continuation payoff。若未来 guide 读取 J，应保留增广 history，不能直接把标签消去。

### 4.3 weighted filter 不是 corrected normalizer

原文返回的 weighted output 是

\[
\widehat\pi_t^{TB}=\bigotimes_K\nu_t^K,
\tag{14}
\]

它位于当前重采样之前，没有乘 D_T。它与重拼后的 empirical measure \(\eta_t^N=N^{-1}\sum_i\delta_{X_t^i}\) 不同，也不由 Eq.10 自动得到与 BPF 相同的有限 N 滤波均值。

## 5. 原文局部矩、路径校正和一致性

### 5.1 同一冻结池上的精确矩

对在当前 offspring 前固定、可依赖 \(\mathcal G_t\) 的有界测试 u，

\[
\mathbb E_{TB}\eta_N(u)
=\nu(u)+\frac{\nu_\psi(u)-\nu(u)}N,
\tag{15}
\]

\[
\operatorname{Var}_{TB}\eta_N(u)
=\frac{(N-1)\operatorname{Var}_\nu u+
\operatorname{Var}_{\nu_\psi}u}{N^2}.
\tag{16}
\]

这里全部条件于当前冻结信息。若 \(|u|\leq1\)，相对 \(\nu(u)\) 的 MSE 至多 \(N^{-1}+4N^{-2}\)。原文通过替换一名 child 的 coupling 证明这些结论。[Theorem 2，Appendix C]

对于覆盖 q(J) 个 blocks 的局部测试，

\[
|\eta_N^{\mathrm{rep}}(u)-\eta_N^{\mathrm{ref}}(u)|
\leq\frac{2q(J)\|u\|_\infty}{N}.
\tag{17}
\]

这比较同一冻结池的重采样，不比较两条已经递归分离的算法 histories。

若 u_N 一致有界且 \(\operatorname{Var}_{\nu_N}u_N\to\sigma^2\) 在概率下成立，\(\sigma^2\) 为确定常数，作者得到一次重采样的条件特征函数 CLT：

\[
\sqrt N\{\eta_N(u_N)-\nu_N(u_N)\}
\Rightarrow\mathcal N(0,\sigma^2).
\tag{18}
\]

它不需要统一 guide range，但不是 normalizer CLT，也不覆盖无界状态坐标的 RMSE。

### 5.2 correction 的二阶矩

设当前池 guide 最小和最大值为 a,b，r=b/a。原文证明

\[
\mathbb E_{\widetilde R}C=1,\quad
\mathbb E_{\widetilde R}C^2-1
=\mathbb E_R\frac{(H-c)^2}{cH}
\leq\frac{(\sqrt r-1)^2}{N}.
\tag{19}
\]

关键是 \(H\geq a\)、\(\operatorname{Var}_RH=\operatorname{Var}_\nu\psi/N\)，以及
\(\operatorname{Var}_\nu\psi\leq(c-a)(b-c)\)。[Proposition 3，Appendix C]

若存在对所有 histories 和随机 pools 都成立的确定性上界 \(r_t^K\leq\rho_t^K\)，则

\[
\mathbb E_{TB}D_T^2
\leq\prod_{t,K}\left[1+\frac{(\sqrt{\rho_t^K}-1)^2}{N}\right]
\leq e^{S/N},
\quad S=\sum_{t,K}(\sqrt{\rho_t^K}-1)^2.
\tag{20}
\]

有限池上的实际最大比值不是自动成立的跨历史统一界。

原文已经给出路径层面的

\[
\chi^2(\mathbb P_B\mid\mathbb P_{TB})
=\mathbb E_{TB}D_T^2-1,\quad
\|\mathbb P_B-\mathbb P_{TB}\|_{\mathrm{TV}}
\leq\tfrac12\sqrt{e^{S/N}-1}.
\tag{21}
\]

若 \(S_N/N\to0\)，同一个可测 history statistic 的分布极限可以通过这条 TV 界转移。Eq.21 是作者结果，不是本次独立发现。它控制路径测度失配，不直接保证 corrected normalizer 降方差。

### 5.3 固定时域的一致性

固定 d、T、分区及观测，假定状态分量 Polish、转移 Feller、观测因子有界连续且严格正、初始粒子 iid 来自 block-product 分布。只要 guides 在各有限池上正、有限并提前冻结，即使其值随 N 急剧变化，

\[
\eta_t^N,\ \widehat\pi_t^{TB}
\xrightarrow{\mathrm{weak},\mathbb P}\widetilde\pi_t.
\tag{22}
\]

证明先控制预测抽样，再利用极限分母为正处理 Bayes 比值，最后通过每块一个替换转移普通重采样的一致性。似然不需要全空间统一正下界。[Theorem 5，Appendix D]

若 Eq.20 的 \(\rho_t^K\) 还对 N 统一，则

\[
D_T\to1,\quad
\widehat Z_T^{TB}\to Z_T^{\mathrm{block}}
\quad\text{in }L^2.
\tag{23}
\]

这些是固定设置下的结论，没有消除 blocking error，没有给 d,T 同时增长的统一保证。\(D_T-1=O_{L^2}(N^{-1/2})\) 本身也不足以把普通 BPF normalizer 的 CLT 直接转给校正后的不同 statistic。

## 6. 原文的方差学习判据

### 6.1 全路径恒等式

令 \(\mathcal Z_T=\prod_{t,K}a_t^K\) 是同一个 history functional。假定 \(\mathbb E_B\mathcal Z_T^2<\infty\) 且 \(\mathbb E_{TB}(D_T\mathcal Z_T)^2<\infty\)，精确改变测度给出

\[
\operatorname{Var}_{TB}(D_T\mathcal Z_T)
-\operatorname{Var}_B(\mathcal Z_T)
=\mathbb E_B[(D_T-1)\mathcal Z_T^2].
\tag{24}
\]

均值相同，因此相对任何共同确定性参照值的平方误差风险差也等于 Eq.24。校正二阶矩小并不决定这个表达式的符号。[正文 Eq.12]

### 6.2 固定 continuation 的可下降方向

冻结一块的池和 \(R=\nu^{\otimes N}\)。指定一个不随候选 guide 改变的后续 kernel \(\mathsf M(x,du)\) 与非负 payoff W，定义

\[
P_0(dx,du)=R(dx)\mathsf M(x,du),\quad
A(x)=\mathbb E[W^2\mid X=x].
\]

取 \(\psi_\theta=1+\theta h>0\)，\(m_h=\nu(h)\)、\(\bar h=N^{-1}\sum_jh(X^j)\)，则

\[
\Lambda_\theta=\frac{1+\theta\bar h}{1+\theta m_h},
\quad Q_\theta=\Lambda_\theta P_0,\quad
V(\theta)=\operatorname{Var}_{Q_\theta}(W/\Lambda_\theta).
\]

当 A 可积且 h 有界，

\[
V'(0)=-\operatorname{Cov}_R(A,\bar h).
\tag{25}
\]

这一方向存在正的 admissible 步长使方差下降，当且仅当上式 covariance 为正。[Proposition 4，Appendix C]

记 \(s=\bar h-m_h\)、\(\alpha_\theta=\theta/(1+\theta m_h)\)。作者还给出精确有限步恒等式

\[
V(\theta)-V(0)
=-\alpha_\theta\mathbb E_R[As]
+\alpha_\theta^2
\mathbb E_R\frac{As^2}{1+\alpha_\theta s}.
\tag{26}
\]

对中心化 \(h_0=h-\nu h\)，令 \(H_0=\|h_0\|_\infty\)、\(c_{\rm step}=\mathbb E[As]>0\)、\(b_{\rm step}=\mathbb E[As^2]\)。作者的可执行安全步长为

\[
\alpha_{\rm safe}
=\frac{c_{\rm step}}{2(b_{\rm step}+H_0c_{\rm step})},
\]

\[
V_c(\alpha_{\rm safe})-V_c(0)
\leq-\frac{c_{\rm step}^2}
{2(2b_{\rm step}+H_0c_{\rm step})}.
\tag{27}
\]

在 \(0<\alpha<c_{\rm step}/(b_{\rm step}+H_0c_{\rm step})\) 内都严格改善。它要求这些真实条件矩已知或另行估计。候选改变时不能同时暗中改掉 \(\mathsf M\) 或 W。[Corollary C.6，原文 C.8–C.9]

### 6.3 log 方差是另一个目标

若 W>0 且 \(\mathbb E_{P_0}(\log W)^2<\infty\)，定义

\[
Y_\theta=\log W-\log\Lambda_\theta,\quad
\mu_\theta=\mathbb E_{Q_\theta}Y_\theta,\quad
\zeta_\theta=\partial_\theta\log\Lambda_\theta.
\]

原文证明

\[
\partial_\theta\operatorname{Var}_{Q_\theta}Y_\theta
=\mathbb E_{Q_\theta}\left[
\zeta_\theta\{(Y_\theta-\mu_\theta)^2
-2(Y_\theta-\mu_\theta)\}\right].
\tag{28}
\]

在零点，\(\zeta_0=s\)。风险方向涉及 conditional log payoff 的中心二次项减去两倍中心一次项，不是 A。普通估计量的均值保持，并不意味着 log 均值保持。[Proposition C.5，原文 C.6–C.7]

### 6.4 作者的完整有限池例

N=2、\(\nu\) 在 0,1 上均匀，\(g(0)=1,g(1)=3\)，
\(W=(g(X^1)+g(X^2))/2\)，\(\psi=g^\beta\)。令 q=3^\beta，则

\[
V(\beta)=\frac{(q-3)^2}{8q}.
\tag{29}
\]

基线方差为 1/2，\(\beta=1\) 方差为零，\(0<\beta<2\) 改善。反向 guide \(4-g\) 给出方差 8/3。该枚举说明 source 本身没有声称任意 positive guide 都降方差。[正文 §3，Appendix C.2]

## 7. 独立推导：有限池凸引导学习

### 7.1 正值、归一化的参数化

合并重复池状态后，\(\nu\) 有 m 个正权重原子，权重向量 w。保持上一节的 R、\(\mathsf M\)、W 固定，使用 guide 值向量 u，约束

\[
\mathcal U=\{u:w^\top u=1,\quad a\leq u_i\leq b\},
\quad0<a\leq1\leq b<\infty.
\tag{30}
\]

常数 guide \(\boldsymbol1\) 在此集合内。令 o(X) 是 array 各状态的占比向量，则 \(\sum_i o_i=1\)，
\(\Lambda_u=o(X)^\top u\in[a,b]\)。方差优化等价于二阶矩优化

\[
F(u)=\mathbb E_{P_0}\frac{W^2}{o(X)^\top u}
=\mathbb E_R\frac{A(X)}{o(X)^\top u}.
\tag{31}
\]

原因是 \(\mathbb E_{Q_u}(W/\Lambda_u)=\mathbb E_{P_0}W\)，与 u 无关。

### 7.2 凸性和学习信号

对任意有限二阶矩 W，正分母允许在紧约束内微分：

\[
\nabla F(u)=-\mathbb E\frac{W^2o(X)}{(o(X)^\top u)^2},
\quad
\nabla^2F(u)=2\mathbb E
\frac{W^2o(X)o(X)^\top}{(o(X)^\top u)^3}\succeq0.
\tag{32}
\]

所以 F 在 \(\mathcal U\) 上凸，经验平均目标也凸。若额外有 \(0\leq W\leq B\)，则

\[
\|\nabla^2F(u)\|_{\rm op}\leq2B^2/a^3.
\tag{33}
\]

这是一个明确的学习问题：用 baseline rollout 的 array occupancy 和未来 payoff 平方拟合当前池 guide，而不是把“预测未来”只写成口头目标。优化所需模型访问、rollout 和计算仍须付费。

另一种解析描述是

\[
a_*(z)=\frac1N\sum_{j=1}^N
\mathbb E_R[A(X)\mid X^j=z].
\]

由条件期望和 iid array，

\[
\operatorname{Cov}_R(A,\bar h)
=\operatorname{Cov}_\nu(a_*,h).
\tag{34}
\]

若 \(a_*\) 有界，取 \(h=a_*-\nu a_*\) 得到方向收益 \(\operatorname{Var}_\nu a_*\)。A 本身不要求置换对称，平均 j 已处理这一点。目标是 squared payoff 的单 child 投影，不等同于平均未来 likelihood。

## 8. 独立推导：有限候选的安全采用规则

### 8.1 先训练，再用独立数据选择

固定当前池。先用任意训练随机性得到 G 个满足 Eq.30 的候选，包含 \(\boldsymbol1\)。训练之后固定整个候选集。再独立生成 L 个 baseline \((R,\mathsf M)\) validation rollouts，记为 \((X_s,U_s,W_s)\)。额外假定已知 \(0\leq W_s\leq B\)。

所有候选共用这些样本，评价

\[
\widehat F_L(u)=\frac1L\sum_{s=1}^L
\frac{W_s^2}{o(X_s)^\top u}.
\tag{35}
\]

每项在 \([0,B^2/a]\)。Hoeffding 加有限 union bound 给出，条件于训练和当前池，以至少 \(1-\delta\) 的概率，所有候选同时满足

\[
|\widehat F_L(u)-F(u)|\leq
\epsilon_L,\qquad
\epsilon_L=\frac{B^2}{a}
\sqrt{\frac{\log(2G/\delta)}{2L}}.
\tag{36}
\]

只在经验最优候选满足

\[
\widehat F_L(\boldsymbol1)-\widehat F_L(u)>2\epsilon_L
\tag{37}
\]

时采用它，否则采用常数 guide。Eq.36 的事件上，采用后的真实条件普通方差不超过基线。若某候选真实 gap 大于 \(4\epsilon_L\)，一定触发采用。

这是一条高概率条件风险保证，不是失败事件上也不增风险的断言，更不是无条件平均风险必然下降。没有已知 payoff bound 时，不能直接套用 Eq.36，可改用另有证明的尾部控制，但本次未建立这种替代定理。

### 8.2 与精确校正如何组合

生产阶段使用新的 offspring 随机性，先把训练、validation 和选中 guide 记录进 pre-offspring 信息，再执行 Eq.8。每次选出的 guide 都正、有限、冻结，因此 Eq.10 的精确均值保持仍成立，不依赖 Eq.36 的成功事件。

两条 history laws 必须共用同一套 guide-generation kernel。候选风险评价时的 continuation 必须固定。若实施时把未来 guides 随当前候选一起重新优化，已改变 \(\mathsf M\)，本证明不自动评价那个联合策略。

### 8.3 资源与获得的数据

一次 validation rollout 的 continuation 可供全部 G 个候选复用。普通数组生成与 occupancy 累计需 O(LN) 工作，直接评价 G 个候选需 O(LGm)，另加 L 次 continuation 的代价及训练成本。候选存储 O(Gm)，validation loss 可流式累计。

它需要已知模型或允许反事实 continuation 抽样的接口。一般在线未知环境不会免费提供这些条件样本。固定 a,b 还提供统一 range \(b/a\)，可同时接入 Eq.20 的路径校正界。

## 9. 独立推导：r 个 children 的联合倾斜

### 9.1 从单状态 guide 到 tuple guide

固定一个池 \(\nu\)，取 \(1\leq r\leq N\)，正、有限、对称的 r 元状态函数 \(\Psi\)，并令

\[
c=\nu^{\otimes r}(\Psi).
\]

均匀选 r 个 offspring 位置 J。在这些位置联合抽取

\[
\frac{\Psi(z^{1:r})}{c}\nu^{\otimes r}(dz^{1:r}),
\]

其余 N−r 个位置 iid 抽自 \(\nu\)，并与这组联合 draw 独立。对 J 边缘化，array density 为

\[
\frac{dQ}{dR}(X)=\frac{H_\Psi(X)}c,\qquad
H_\Psi(X)=\binom Nr^{-1}
\sum_{J\subset[N],\,|J|=r}\Psi(X^J).
\tag{38}
\]

因此 \(C=c/H_\Psi\) 精确满足

\[
\mathbb E_Q[CF]=\mathbb E_R[F].
\tag{39}
\]

这是与原文同样的有限 mixture 计算。对称性确保对子集 J 的排列不敏感。r=1 回到原文。

### 9.2 overlap 控制二阶矩

假定 \(a\leq\Psi\leq b\)，令

\[
q_{N,r}=1-\frac{\binom{N-r}{r}}{\binom Nr},
\tag{40}
\]

当 N−r<r 时分子按零处理。它是两个独立均匀 r 子集相交的概率。

不相交子集上的核值独立。相交项的 covariance 至多为 \(\operatorname{Var}_{\nu^{\otimes r}}\Psi\)，所以

\[
\operatorname{Var}_R H_\Psi
\leq q_{N,r}\operatorname{Var}_{\nu^{\otimes r}}\Psi.
\tag{41}
\]

沿 Eq.19 的推导，

\[
\boxed{\mathbb E_Q C^2
\leq1+q_{N,r}(\sqrt{b/a}-1)^2.}
\tag{42}
\]

由于固定一个 r 子集，再对另一子集的 r 个位置作 union bound，

\[
q_{N,r}\leq\min\{1,r^2/N\}.
\tag{43}
\]

跨块和时间条件迭代时，可把 Eq.20 各项的 \(1/N\) 换成相应 \(q_{N,r}\)，前提仍是跨历史的确定性 range bounds。这一结果明确显示联合阶数增加带来的校正风险预算。

### 9.3 对经验测度和成本的影响

与普通 array coupling，只需替换 r 个位置，因此

\[
|\eta_N^{\rm joint}(u)-\eta_N^{\rm ref}(u)|
\leq2r\|u\|_\infty/N.
\tag{44}
\]

在原文同样的有界测试与条件方差收敛条件下，\(r_N=o(\sqrt N)\) 足以转移同一冻结池的一次 CLT。这里没有证明完整递归的 joint-twist CLT。

对 m 个池原子，直接构造联合 categorical law 枚举 \(m^r\) 个允许重复状态的有序 tuple。直接计算生产 array 的 H 需要 \(\binom Nr\) 次 r 元核评价。每次核评价本身的工作量、状态复制和训练另计。r 增长时不能把这些成本隐去。

若固定非负 payoff 恰为 \(W(X)=H_\Psi(X)\)，则 \(CW\equiv c\)，方差为零。这给出 joint guide 与目标计算对齐的一种充分条件，不保证一般 normalizer 具有这种形式。

## 10. 独立推导：纯二元交互的精确构造

令 N=2，\(\nu\) 在 \(\{-1,1\}\) 上均匀，取

\[
W(X^1,X^2)=1+\beta X^1X^2,\qquad0<|\beta|<1.
\tag{45}
\]

它正且有界，均值为 1，基线方差为 \(\beta^2\)。对任一 child，

\[
\mathbb E[W^2\mid X^j]=1+\beta^2.
\tag{46}
\]

所以 Eq.34 中的单 child 风险投影为常数。所有正、归一化单 child guides 都可写成
\(\psi(x)=1+s x,\ |s|<1\)。直接对四个有序数组求和得到

\[
\boxed{
V(s)-V(0)
=\frac{(1+\beta)^2s^2}{2(1-s^2)}\geq0.
}
\tag{47}
\]

非恒定单 child guide 严格增加方差，常数 guide 已是该类的全局最优。

改用 r=2、\(\Psi=W\)。因为只有一个二元子集，c=1、\(H_\Psi=W\)，从而

\[
CW\equiv1.
\tag{48}
\]

joint law 保持每个 child 的边缘均匀，却改变二元相关，并消除 payoff 方差。这是一个完整的有限构造，说明联合采样可以利用各单 child 风险投影中不存在的信息。W 是这里明确定义的条件 payoff，不是未经证明的 BPF normalizer 表达式。

对 FP 的材料价值是一个可供 Astra 自主判断的数学操作：当目标仅在 joint statistics 上可见时，可以直接学习或倾斜 joint law，并显式支付联合表与校正成本。它不识别 FP 的状态、动作、学习规则或架构，也不建议把此例强制移植到核心实现。

## 11. 原文实际使用的 guide

### 11.1 局部 backward message

真实模拟模型为环上的

\[
X_t^v=0.7X_{t-1}^v+0.1(X_{t-1}^{v-1}+X_{t-1}^{v+1})
+\sigma\varepsilon_t^v.
\tag{49}
\]

LG 模型取 \(\sigma=1,\ Y_t^v=X_t^v+e_t^v\)。SV 取 \(\sigma=0.3,\ Y_t^v=\exp(X_t^v/2)e_t^v\)。guide 另用 isolated scalar AR(0.9) 近似构造，它不改变 Eq.49 的真实传播。[§4，Appendix E.1–E.2]

应用 Eq.22 时应检查固定观测的有界似然条件。LG 因子有界。SV 因子在 y≠0 时有界，但 y=0 时随 x→−∞ 无界。未检查真实 panel 中是否恰有零值，因而不把该数据的全部设置直接认证为满足一致性定理。

LG 的二次 log-message 有解析 backward recursion，例如

\[
A_s=a^2\frac{1+A_{s+1}}{2+A_{s+1}},\qquad
B_s=a\frac{y_{s+1}+B_{s+1}}{2+A_{s+1}}.
\tag{50}
\]

SV 使用 [-8,8] 上 401 点网格、24 点 Gauss–Hermite、log-message 线性插值和边界常值延拓，并在网格上归一化。这里精确的是有限 guide 表所诱导的重采样校正，不是 SV backward message 等于真实未来似然。

各块累加 site log-messages，减去当前池最大值，再在 −20 截断：

\[
\psi_{i,K}
=\exp\max\left\{
\sum_{v\in K}\log h_t^v(Z_t^{i,v})
-\max_j\sum_{v\in K}\log h_t^v(Z_t^{j,v}),-20
\right\}.
\tag{51}
\]

guide 范围为 \([e^{-20},1]\)。正比例缩放不改变 twist，截断改变其质量但不破坏同表校正。这个统一 range 满足理论条件，但 \(e^{20}\) 的最坏界在实际资源下不能解释实验降方差。

按每个窗口直接独立构造，LG messages 的朴素工作为 \(O(Td\ell)\)，SV 为 \(O(Td\ell\cdot401\cdot24)\)，当前池求值另需 \(O(TNd)\)。messages 可原则上跨运行缓存，池内最大值和截断后的最终值表依赖当前 particles。没有核实作者如何把预计算复用计入计时。

### 11.2 信息时序

| 对象 | 可使用的最晚观测 |
|---|---|
| TBPF 时间 t 的 resampling guide | \(y_{\min(T,t+\ell)}\) |
| TBPF 时间 t 的 weighted output | \(y_{\min(T,t+\ell-1)}\) |
| TPF arrival guide | \(y_{t:\min(T,t+\ell-1)}\) |

\(\ell=1\) 时 weighted output 使用截至 t 的观测，但当前重采样已经看到下一观测。\(\ell=5\) 时 weighted output 可以看到 t+4。论文的 predictable 指在 offspring 抽样前冻结，不等于 observation-time causal。[正文 §4.1]

对照 TPF 采用 Gaussian-shape guide，并对这个选定近似 guide 做解析积分与倾斜传播。它与 TBPF 不仅 twist 位置不同，guide family 也不同。比较它们不是只改变一个因素的实验。

## 12. 实验结论及实际证据范围

### 12.1 固定数据模拟

作者测试 d=64,128,256，N=128,512，T=80，最大 block size b=1,2,3,4，horizon \(\ell=1,5\)。每个 model/dimension 只生成一条固定数据，各配置运行 32 个 Monte Carlo seeds。整个原始 campaign 是 180 个 method/configuration 组合、5760 次独立 filter runs。96 个 TBPF/BPF 匹配比值复用了部分 baseline，不是 96 条独立数据。[§4，Appendix E]

Figure 2 保留全部 96 个比值，包括失败格子。观察到 70/96 降低 log-normalizer 方差，其中 LG 为 29/48、SV 为 41/48。SV 的 \(\ell=5\) 为 22/24，median ratio 0.620。四方法 horizon-matched 最低 log variance 为 69/96，最低 filtering RMSE 为 72/96。

LG RMSE 参照精确 Kalman filtering mean，SV RMSE 参照模拟 hidden state，二者风险对象不同。事后分别选择最佳配置后，BPF 与 TBPF 的 RMSE 差小于 LG 0.6%、SV 0.2%，不足以支持广泛的状态估计机制优势。

Figures S1–S2 是 retrospective envelopes。各 family 候选数为 PF 1、TPF 2、BPF 4、TBPF 8，没有把选择优势验证为一个事前 tuning rule。局部 ESS 与全状态 ESS 也不是同一尺度。

### 12.2 Gaussian block 参照和新的 seeds

作者的 deterministic Gaussian block reference 在每次更新后把 covariance 投影为 block diagonal，Table S5 比较的是它与全 Kalman recursion 的确定性差异。保留 mean 的额外 LG runs 使用 16 个共同 seeds，并明确保留总平方误差中的 cross term，不把 particle error 与 blocking error 的 RMSE 直接相加。

原 32-run 结果用作 precision pilot 后，作者预先固定每 procedure 128 个 fresh seeds，共 768 个额外 runs，仍在原固定数据上。Table S7 的 LG log-variance ratios 为 0.759、0.779，两个 95% intervals 都包含 1。SV 为 0.594、0.545，区间分别为 [0.416,0.849]、[0.384,0.801]。

另外固定 N=128、b=1、\(\ell=5\)，每个 model/dimension 新生成两条数据，每组 16 runs，共 384 次额外执行。新数据上 LG 3/6、SV 6/6 的比值小于 1，多数逐数据 bootstrap intervals 较宽且包含 1。[Appendix E.6–E.7]

这些是作者内部的新随机数和新数据确认，不是独立研究者复现。样本 log 方差与普通尺度方差没有一般等价关系。原文普通尺度 empirical CV² 从 32 个正估计量计算，代数上有 CV²≤32 的有限样本上界，这不能为真实 population tail 或 variance 提供上界。

### 12.3 真实 100-portfolio panel

作者使用 Kenneth French 的 100 个 value-weighted portfolios，报告下载 August 2026 CRSP release。2018–2019 的 503 个交易日只用于均值、标准差处理，2020 的 253 日用于评价。没有丢弃 portfolio 或日期，保留发布顺序组成模型的环。[§4.3，Appendix E.5]

SV 参数预先固定，除预处理矩外没有拟合。滤波器从共同 prior 开始，没有训练期 filter warm-up。真实数据没有可用 latent-state truth，因此没有 SV 状态准确性排名。Figure 3 上方 band 是跨 portfolio 的 10th–90th percentiles，不是 confidence interval。

固定 b=1 的比较为：

| N | horizon | log-variance ratio | paired-bootstrap 95% interval |
|---:|---:|---:|---|
| 128 | 1 | 0.950 | [0.471,1.923] |
| 128 | 5 | 0.799 | [0.435,1.526] |
| 512 | 1 | 0.437 | [0.210,0.833] |
| 512 | 5 | 0.527 | [0.245,1.064] |

每配置 32 runs，4000 bootstrap resamples。另行挑选 family minima 的 20.1% 和 56.3% reductions 是事后点估计，不是已验证调参规则。整项真实数据实验为 960 runs。

### 12.4 可复现性与结论等级

所取得源包有 TeX、样式、bib 和图文件，没有实验代码或原始 CSV。所读材料未认证可访问的实现 artifact，未给 wall-clock、硬件、峰值内存或等计算预算比较。源码注释声称检查过代码或计时，不替代已检索到的代码和报告。这里是访问范围说明，不宣称作者在其他地方绝无代码。

固定设置下的精确恒等式、局部矩和一致性是数学结果。guide 选择方向是依赖固定 continuation 的条件结果。70/96 和各 confidence intervals 是特定数据、参数、粒子数与信息时序下的观察。把它们解释成因果在线信息公平或等算力普遍优势，超出证据。

## 13. 如何作为 FP 的理论材料使用

本篇给出三个清楚的接口，供 Astra 自主选用：

- 任何已构造的正有限预测 guide 都可进入严格的 array-law change of measure，而其近似质量与期望保持分开处理。
- 在一个指定池和后续计算上，未来 squared payoff 可转成凸 guide 学习与独立验证信号，资源、尾部条件和使用的反事实数据均可计量。
- 当单 child risk projections 没有信息时，联合重采样可改变相关而保留单点边缘。Eq.38–48 给出精确实现、校正、风险预算和有限例子。

这些材料不需要宣称粒子就是 FP 状态。若将来研究某个 FP 对象，仍须明确其 history law、待估 payoff、可访问的样本或模型 kernel、冻结时序及联合表成本，再证明对象映射。当前没有修改这些核心定义。

## 14. 可复核结论与后续边界

已完成全篇实际阅读与有限数学推导。保留的主要原文工具是 distinguished-offspring mixture、增广 history 校正、条件矩、路径 chi-square/TV、固定时域 blocked consistency、普通和 log 风险的不同方向。

独立结果是 Eq.6 的一步目标分离、Eq.12–13 的条件 Rao–Blackwell 解释、Eq.30–37 的凸学习和 validation、Eq.38–44 的 joint-tuple 校正及 overlap bound，以及 Eq.45–48 的完整交互构造。没有运行经验复现、形式化认证或 FP 实验，也没有把引用文献全文计为已读。

进一步研究可检查更便宜的低阶核分解、可认证的无界 payoff validation 或真正自适应 continuation 的优化，但这些本次均未解决。下一篇按最新 Git 请求与 ownership 记录选择，不将上述开放问题自动升级为核心路线。

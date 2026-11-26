# Taghavian–Sjölund 2025 — 用有限线性证书编译正状态递推

## 版本、来源与阅读范围

- 作者：Hamed Taghavian、Jens Sjölund。题目：Minimal positive Markov realizations。
- 完整阅读对象：[arXiv:2502.21102v3](https://arxiv.org/abs/2502.21102v3)，2025-09-03 07:39:14 UTC，[6 页原始 PDF](https://arxiv.org/pdf/2502.21102v3)及[完整 TeX](https://arxiv.org/src/2502.21102v3)。2026-11-27 上海时间检查 latest，历史仍止于 v3。v1 为 2025-02-28，v2 为 2025-04-01。
- 正式版本为 IEEE CDC 2025，pp.858–863，[DOI 10.1109/CDC57313.2025.11312247](https://doi.org/10.1109/CDC57313.2025.11312247)。IEEE 存入 Crossref 的 published-print 为 2025-12-09，记录创建于 2026-01-12，二者不能混作出版日期。[Crossref 原始记录](https://api.crossref.org/works/10.1109%2FCDC57313.2025.11312247)和[大学发表列表](https://uu.diva-portal.org/smash/person.jsf?pid=authority-person%3A118071)认证了正式出版信息。
- [大学仓库具体条目](https://uu.diva-portal.org/smash/record.jsf?pid=diva2%3A2027109)和 IEEE 正文入口遇到人机验证。本次未取得最终排版正文，未认证其与 arXiv v3 的逐页一致性。最终会议版保持仅书目筛选，不重复给 full-reading credit。
- Pro-C 主读者完整读取 main.tex 全部 593 行并区分活跃正文和注释，覆盖 §§I–VI、notation、全部 Lemma 1/Theorem 1/Corollary 1 陈述与证明、一个六步角度构造、两个图、致谢及全部参考文献。PDF 6 页均目视检查。实际打印 19 条参考文献，bib 文件有 24 条，均已读过。没有表格、算法框或脚注。
- 源包中的 lowerbounds.pdf 及相应文字位于 iffalse 区域，不计入正式论文的第三图或已发表下界。两负实极点的另一段示例也被注释。没有把它们当作作者有效结论。
- 两位辅助读者分别核对构造证明及独立计算、来源元数据与图例。没有运行 LP、生成图、审计实现、读完历史引用全文或进行形式化验证。所读活跃稿与源文未发现 LLM 使用声明，这只是披露检查。

此前 request3f8e6cb 对本篇只有指定段落筛选。本次在 fresh Git 与 ownership 检查后自主选读完整 v3，不重复认领已完成请求。下文标明作者结果与独立推导，不主张标准线性系统或概率构造的新颖性。

## 1. 论文实际解决的问题

**给定一个已知的标量有理传递函数，作者用线性可行性约束寻找一种非负 companion 状态实现，并在存在有限可行上界时最小化这个实现族的维数。** 它没有解决任意正实现的全局最小化，也没有从观测数据识别未知传递函数。[§§II–IV]

写成

\[
H(z)=\frac{B(z)}{A(z)},\quad
A(z)=z^n+a_1z^{n-1}+\cdots+a_n,
\quad \deg B<n,
\tag{1}
\]

分子分母无共同根。n 是 McMillan 阶数。一般状态实现为

\[
x_{t+1}=P x_t+b u_t,\qquad y_t=c^\top x_t,
\quad H(z)=c^\top(zI-P)^{-1}b.
\tag{2}
\]

这里用 P 表示状态矩阵，避免与分母多项式 A 混淆。正实现要求 \(P,b,c\) 逐元素非负。记任意正实现的最小维数为 \(N^\star\)，作者 Markov-form 族的最小维数为 \(N_M\)。总有

\[
n\leq N^\star\leq N_M
\tag{3}
\]

只要右侧存在。\(N_M=N^\star\) 需要额外理由。

### 1.1 正确的脉冲索引

本笔记统一用 Laurent 展开

\[
H(z)=\sum_{t\geq1}h_tz^{-t},
\qquad h_t=c^\top P^{t-1}b.
\tag{4}
\]

源文 §II 写 \(h_t=CA^tB\)，但 §III 又用 \(C=(h_1,\ldots,h_N)\)、\(B=e_1\)，此时第一项必为 CB。按其传递函数 Eq.1 与实现 Eq.4，前者是一个一位索引不一致。本笔记按 Eq.4 的 Laurent 系数解释所有初始响应值。

作者假设外部正性 \(h_t\geq0\)，并把一个正 dominant pole 归一化为 1。对原始 dominant modulus \(r>0\)，可具体采用

\[
G(z)=rH(rz),
\tag{5}
\]

其极点缩小 r 倍，且第一响应值保持。若 G 的 realization 是 \((P,b,c)\)，原始 H 的 realization 为 \((rP,b,c)\)。源文展示的 \(H(z/r)\) 也给出维数不变的缩放关系，但实际归一化方向应区分。

令 \(\mathcal M\) 为满足上述假设、除 1 外没有其他正实极点的系统族。该条件按极点重数理解，因此 1 是简单正极点。其他正实极点会排除单一 Markov-form 构造，却不排除一般正 realization。

## 2. 原文的线性可行性构造

### 2.1 加入可消去的分子分母因子

取 \(N\geq n\) 及 monic 多项式

\[
Q(z)=z^{N-n}+q_1z^{N-n-1}+\cdots+q_{N-n}.
\]

令

\[
D(z)=A(z)Q(z)=z^N+d_1z^{N-1}+\cdots+d_N,
\qquad d_k=(a*q)_k.
\tag{6}
\]

分子也乘 Q，所以有理函数保持。作者要求

\[
d_k\leq0\quad(1\leq k\leq N).
\tag{7}
\]

设 \(p_k=-d_k\)。状态矩阵由其 columns 给出：

\[
Pe_j=e_{j+1}\quad(j<N),\qquad
Pe_N=(p_N,p_{N-1},\ldots,p_1)^\top,
\]

\[
b=e_1,\qquad c=(h_1,\ldots,h_N)^\top.
\tag{8}
\]

Eq.7 和外部正性使所有 entries 非负。其传递函数等于 H。因为最初 N 个 impulse outputs 与 H 相同，之后两者都服从 D 的线性递推，整个序列相同。[§III，原文 Eqs.3–6]

### 2.2 固定维数是实数 LP

固定 \(q_0=1\)，以卷积 Toeplitz 矩阵 \(\mathcal T_a\) 表示 D 的系数。去掉 leading coefficient 的选择矩阵记 W，则问题是

\[
W\mathcal T_aq\leq0,\qquad q_0=1.
\tag{9}
\]

有 \(N-n\) 个自由实变量、N 个不等式。没有要求 q 的每一项非负，更不是整数规划。

若 N 可行，则 \(z^kQ(z)\) 证明 N+k 也可行。拥有一个已知可行上界 U 后，最小 N 可用整数二分定位，需 \(O(1+\log(U-n+1))\) 次 LP 可行性调用。这是调用次数，不等于总运算量。

若 A 有两个或更多正实根，AQ 也有至少这么多正实根，而 Eq.7 的系数序列只有一次符号变化，违反 Descartes 法则。因此 Eq.9 在任何 N 下都不可行。这只否定这个 companion 族。[§IV]

### 2.3 非负递减乘子形式

分解

\[
A(z)=(z-1)\widehat A(z),\qquad
\widehat A(z)Q(z)=\sum_{k=0}^{N-1}v_kz^{N-1-k}.
\]

Lemma 1 等价地要求

\[
1=v_0\geq v_1\geq\cdots\geq v_{N-1}\geq0.
\tag{10}
\]

设 \(v_{-1}=v_N=0\)，则对 k=1,…,N，

\[
d_k=v_k-v_{k-1}.
\tag{11}
\]

源文 Lemma 1 证明第一行把左侧误写为 \((\widehat a*q)_k\)。它应是 \((a*q)_k\)。式子后面的 telescoping 与 Eq.10 一致，这个局部符号问题不改变构造。

## 3. 原文的有限上界及其真正资源

### 3.1 有理极角与非整除条件

列出上半平面极点，包括实极点，

\[
p_j=r_je^{2\pi i l_j/m_j},\quad
1=r_1\geq r_2\geq\cdots,
\quad(l_1,m_1)=(0,1).
\]

其余 \(l_j,m_j\) 互素，\(0<l_j<m_j\)。令

\[
\mu_1=1,\qquad\mu_j=m_j\mu_{j-1}.
\]

Theorem 1 的额外条件是

\[
m_j\nmid\mu_{j-1}\quad(j\geq2).
\tag{12}
\]

在这些条件下，\(U=\mu_{n_p}=\prod_jm_j\) 是可行维数。

作者实际构造

\[
P_j(z)=\sum_{s=0}^{m_j-1}
r_j^{s\mu_{j-1}}z^{m_j-1-s},
\quad
\Omega_k(z)=\prod_{j=2}^kP_j(z^{\mu_{j-1}}).
\tag{13}
\]

Eq.12 确保 p_j 的幂没有落在被有限几何和排掉的正根上，因此 \(\widehat A\) 整除 \(\Omega_{n_p}\)。系数按混合进位分成块，块内由归纳保持递减，块间由 \(r_2\geq r_3\geq\cdots\) 保持递减。于是

\[
Q(z)=\Omega_{n_p}(z)/\widehat A(z)
\]

满足 Lemma 1，且 \(\deg\Omega_{n_p}=U-1\)。这给出了真正的有限停止上界，而不是在不可行的维数上无限递增。[Theorem 1 完整证明，PDF pp.3–4]

### 3.2 不隐藏输出尺寸

U 是极角分母的乘积，可能相对 n 和分母的二进制编码长度很大。一个固定规模的 LP 可求解，不意味着整个 realization 输出尺寸为输入位长的多项式。

对给定 N，卷积约束只需 \(O(nN)\) 非零存储和组装量。得到 q 后，P 只有 shift 次对角线和末列，运行状态更新、计算输出都可做成 O(N)，实现系数和状态为 O(N) 存储。前 N 个 h_t 可从 Eq.1 在 O(nN) 算术工作中递推取得。

这里是实数算术计数。原文没有给系数位长、数值精度、条件数或浮点 feasibility 认证定理。没有解未知系统 identification 所需的样本复杂度。

## 4. 密度陈述：原文范围与受限修补

### 4.1 原作者的 Corollary 1

作者声称 LP 可行系统在 \(\operatorname{int}(\mathcal M)\) 稠密，使用极点和零点位置的和式距离。证明先把极角近似为有理数，再修改分母使 Eq.12 成立，同时保留极点模长和分子。[PDF p.4]

这不能读成对每个系统已经有精确可行证书，也不是概率意义的“几乎处处”。角度近似的存在不控制达到指定精度时所需的 U，也不自动给输入输出误差界。

该证明在实系数、固定 n 的一般情形存在一个未交代的边界：多个不同的负实极点必须留在实轴，若分别把它们的角从 π 扰动到邻近角并补上共轭，通常会改变阶数。两个不同简单负实根的小实系数邻域仍有对应实根，不能用逐根独立的非实扰动直接解决。其共同分母 2 又无法重复满足 Eq.12。

此外，若 \(\mathcal M\) 的 interior 仅相对于已经 externally positive 的集合取，必须说明新扰动仍然外部正，不能从“它靠近原点”单独推出这一点。本次不宣称 Corollary 1 的结论已被反例推翻，也不把其整段证明认证为覆盖所有实系数根型。核心有限 LP 证书不依赖这个密度推论。

### 4.2 独立推导：保留实系数的明确子类

一个充分的受限版本是：

1. 极点均非零，除简单的 1 外至多一个简单负实极点，其余为非实共轭对。
2. 在所考虑的实系数、固定阶数参数邻域内，无消去与外部正性对小扰动稳定。
3. 保持模长，只扰动每个非实共轭对的角，始终同时使用正负共轭角。

为每个非实对选一个与其他分母不同的、任意大的奇素数 m_j，以 \(l_j/m_j\) 近似上半平面的 \(\theta_j/(2\pi)\)。若有负实极点，保留它的分母 2。所有分母两两不同且为素数，所以无论模长排序如何，Eq.12 都成立。角度可任意接近原值，实系数、阶数和模长保持，假设 2 保证其他约束保持。Theorem 1 因而给出此子类的可行近似。

这不是对多个负实极点或零极点的修复，也没有去掉外部正性稳定假设。它把可用的 approximation procedure 限定到一个已给出完整理由的输入类。

## 5. 三阶区域及一般最小性

原文 §V 固定极点为 \(1,x\pm iy\)，令 \(r^2=x^2+y^2\)。分母为

\[
A(z)=z^3-(1+2x)z^2+(r^2+2x)z-r^2.
\tag{14}
\]

当 N=3，Q=1，LP 可行等价于

\[
x\geq-\tfrac12,\qquad
(x+1)^2+y^2\leq1.
\tag{15}
\]

在 externally positive、无消去的三阶目标上，这给出 \(N^\star=N_M=3\)。Eq.15 是直接展开源 LP 的独立表达，与 Figure 1(a) 相符。

作者记一般 LP 可行极点域为 \(\Psi_N\)。Eq.22 实际印 \(q\in\mathbb N^{N-n+1}\)，与 Eq.6 的 \(q\in\mathbb R^{N-n+1}\) 不一致。本笔记和算法按后者实数域。

Karpelevič 区域 \(\Theta_N\) 描述 N 维非负谱半径一矩阵的可能特征值。沿作者引用的谱下界，若

\[
p_{2,3}\in\Psi_N\setminus\Theta_{N-1},
\tag{16}
\]

则 \(N^\star=N_M=N\)。本次读了源文如何使用这个历史结果，没有重复读取或认证历史定理全文。

当 \(p_{2,3}=r e^{\pm2\pi il/m}\)，互素 l,m 给出 \(N=m\) 可行。角度对应的单位圆点不在 \(\Theta_{m-1}\) 上，故 r 足够接近一时 Eq.16 成立。原文没有给该“足够接近”的统一数值阈值。

Figure 1 有 N=3,4,5 三个子图。Figure 2 展示 \(\Psi_4\) 与先前 \(\Pi_4\) 充分条件在局部的差别。作者也明确有其他区域中本方法的维数上界更大。分子外部正性的假设不能被这两张极点图替代。

## 6. 独立推导：有限、可验证的编译证书

### 6.1 不必先假设整条序列非负

给定已知 H，若找到 N 和 q 满足 Eq.7，且直接算出的有限前缀满足

\[
h_1,\ldots,h_N\geq0,
\tag{17}
\]

则 Eq.8 是一个正 realization，并证明全部 \(h_t\geq0\)。

证明是有限递推：对 t>N，

\[
h_t=\sum_{k=1}^Np_kh_{t-k}.
\tag{18}
\]

每个 p_k 非负，归纳保证全部未来非负。该序列与原 H 相同，因为 D=AQ，分子 BQ 的阶数小于 N，故初始 N 项加 D 的 homogeneous recurrence 决定整个 Laurent 展开。

所以一份具体 feasible multiplier 和有限响应前缀就能成为全序列正性的证书。它没有为任意 H 保证搜索终止，但在证书找到时无需额外无限检查。

### 6.2 最小 Markov 维数也可携带有限证书

把 Eq.9 中固定的 q_0 消掉，写成

\[
a_{\rm tail}+Tq_{\rm free}\leq0.
\]

Farkas alternative 给出固定 N 不可行的证书：

\[
y\geq0,\qquad y^\top T=0,\qquad
y^\top a_{\rm tail}>0.
\tag{19}
\]

任意 primal 解会与这些等式、严格不等式矛盾。反向存在性是标准线性可行性 alternative。

若 N>n，一个 N 维 feasible q 加上 N−1 维的 Eq.19 证书，即证明 \(N_M=N\)，因为任意更低维可行解都能补零提升到 N−1。若 N=n，只需 primal 证书和 McMillan 下界。两者都不自动证明 \(N^\star=N\)。

有理数据下，可对 rational witnesses 做精确卷积和符号检查。浮点 solver 的“可行”或“不可行”标签不能直接替代这些等式和严格号的认证。本次没有实际求解 LP，也没有生成自动证书脚本。

## 7. 独立推导：列随机状态与一个完整例子

### 7.1 归一化后是一条 Markov reward chain

因为 \(A(1)=0\)，有

\[
0=D(1)=1-\sum_{k=1}^Np_k.
\]

Eq.8 中除末列外每列恰有一个 1，末列之和也为 1。因此

\[
\mathbf1^\top P=\mathbf1^\top,\qquad P\geq0.
\tag{20}
\]

归一化后的 companion 实际是列随机矩阵。以 \(e_1\) 初始化的 impulse state 是概率向量：

\[
v_t=P^{t-1}e_1,\quad h_t=c^\top v_t.
\tag{21}
\]

它表示一条有限状态 Markov chain 上的 expected reward。状态先确定性地从 1 移到 N，到达 N 后按 \((p_N,\ldots,p_1)\) 分布跳转。特别地

\[
\min_i c_i\leq h_t\leq\max_i c_i\quad(t\geq1).
\tag{22}
\]

c 不必小于一，也不是多符号观测的 emission probabilities。对一般外部输入，x_t 是累积的非负输入质量，而非总质量恒为一的概率。

### 7.2 精确有理实例

取

\[
P=\begin{pmatrix}
0&0&13/25\\
1&0&7/25\\
0&1&1/5
\end{pmatrix},\qquad
b=e_1,\qquad c=(1,3/2,6/5)^\top.
\tag{23}
\]

对应

\[
H(z)=
\frac{z^2+\frac{13}{10}z+\frac{31}{50}}
{z^3-\frac15z^2-\frac7{25}z-\frac{13}{25}}.
\tag{24}
\]

分母的极点为 \(1,-2/5\pm3i/5\)，与分子无消去。Q=1 是 N=3 的可行证书，前三个输出就是 c，因此全部输出非负。McMillan 下界给出 \(N^\star=N_M=3\)。

之后两项为

\[
h_4=59/50,\qquad h_5=169/125.
\]

所有未来项都落在 [1,3/2]。这由 Eq.20–22 直接证明，不依赖模拟足够多步后的观察。该例是本次手算构造，不是作者报告的实验。

## 8. 独立推导：稳定响应到吸收时间分布

这一段是标准非负系统的概率变换在上述稀疏实现上的具体应用，不主张新颖性。

设原始半径 \(0<r<1\)，\(R=rP\)，\(c\geq0\)，\(b=e_1\)。总响应有限，若

\[
S=c^\top(I-R)^{-1}b>0,\qquad
v^\top=c^\top(I-R)^{-1},
\tag{25}
\]

则 \(v^\top R+c^\top=v^\top\)。在 v_i>0 的状态上令

\[
D_v=\operatorname{diag}(v),\quad
T=D_vRD_v^{-1},\quad
\alpha=D_vb/S,\quad \beta_i=c_i/v_i.
\tag{26}
\]

v_i=0 的状态没有未来 reward，可删除后使用对应限制矩阵。由 \(v_j=c_j+\sum_i v_iR_{ij}\) 的非负各项，零 v 状态也不能转入正 v 状态，故删除不改变响应。若 I 是保留的状态集，\(\rho(R_{II})\leq r<1\)。由于 \(v_i\geq0\)、\(c_i\geq0\)，

\[
\sum_iT_{ij}+\beta_j=1,\qquad
\mathbf1^\top\alpha=1.
\]

所以 T 是 transient substochastic transition，\(\beta_j\) 是离开该 transient state 时的吸收概率。把第一次吸收记为 \(\tau\geq1\)，则

\[
\Pr(\tau=k)=\beta^\top T^{k-1}\alpha
=\frac{c^\top R^{k-1}b}{S}
=\frac{h_k^{\rm raw}}S.
\tag{27}
\]

因为 \(\rho(R)=r<1\)，这些概率总和为一。已知的稳定正响应被编译成一个确切的离散终止时间分布。

这是一字母长度分布的概率表示。它没有提供任意多符号序列的同一组 symbol-conditioned 转移，没有给 unifilar 状态恢复或一般 PSR 可识别性结论。

## 9. 独立推导：执行后的误差可以量化

### 9.1 已知递推，只估计 readout

固定同一列随机 P 与 \(b=e_1\)。若

\[
\|c-\widehat c\|_\infty\leq\delta,
\]

则对所有 t，

\[
|h_t-\widehat h_t|
=|(c-\widehat c)^\top P^{t-1}e_1|
\leq\delta.
\tag{28}
\]

这是一条全未来 uniform bound。它需要递推 P 已知且精确，不能用于同时估计未知极点时不作修改。

### 9.2 同一状态坐标上的 transition 误差

设 P、\(\widehat P\) 是同一 N、同一 companion 坐标、同一 b 下的列随机矩阵，只有末列参数不同，令

\[
\epsilon=\|p-\widehat p\|_1
=\|P-\widehat P\|_1.
\]

二者均为概率转移，因此 telescoping 得

\[
\|P^{t-1}e_1-\widehat P^{t-1}e_1\|_1
\leq\min\{2,(t-1)\epsilon\}.
\]

若 \(0\leq c_i\leq C_{\max}\) 且
\(\|c-\widehat c\|_\infty\leq\delta\)，以有界 reward 控制两概率分布的 TV，

\[
|h_t-\widehat h_t|
\leq\delta+C_{\max}
\min\{1,(t-1)\epsilon/2\}.
\tag{29}
\]

误差并未对时间自动保持 O(ε)。半径为一时，不能从有限参数误差直接宣称任意长时间的精确预测。

### 9.3 稳定缩放与有界输入

若两系统具有同一个已知原始半径 \(0<r<1\)，raw transition 为 rP、\(r\widehat P\)，Eq.29 的每个时距项乘 \(r^{t-1}\)。对零初态且 \(|u_t|\leq U\) 的共同输入，

\[
\sup_t|y_t-\widehat y_t|
\leq U\left[
\frac{\delta}{1-r}
+\frac{C_{\max}\epsilon r}{2(1-r)^2}
\right].
\tag{30}
\]

这是把几何级数与其一阶矩求和得到的充分界。r 也被估计时还需另计半径误差。r=0 属于单独的 FIR/退化情形，不通过 Eq.5 的除法处理。

Eq.28–30 是参数误差到执行误差的确定性接口，没有证明数据足以估计这些参数，也没有隐藏同坐标对齐的前提。

## 10. 经验性内容和可供 FP 使用的边界

原文的示例是三阶极点可行域及谱界比较。没有训练数据、统计重复、误差条、运行时间、LP solver、网格分辨率或容差信息。源包只有正文、书目和静态图，没有取得图生成或 LP 实现。因而图支持解析构造的几何展示，不支持相同资源下的经验性能比较。

可复用的实际对象是：

- 已知 scalar transfer function 到非负 sparse recurrence 的有限编译。
- feasible multiplier、有限 impulse prefix 与 dual infeasibility witness 组成的条件正确性和族内最小性证书。
- 归一化后 Markov reward 状态的解释，以及稳定情况下的吸收时间概率表示。
- 在明确坐标、半径和范数假设下，把 readout 与 transition 参数误差转成未来输出误差。

这些工具是已知模型的 realization 方法。没有学习未知模型的算法，没有把 N 个实数坐标等同于 N 个可观测因果状态，没有从 scalar impulse response 推出多符号、交互式或 unifilar 预测系统。与 FP 的对象映射或下一步架构选择由 Astra 决定，本次不修改核心文件。

完整阅读已经覆盖原文全部活跃内容。Corollary 1 的实系数扰动边界保持未认证，有限 LP 构造和本笔记的受限修补分别陈述。没有复现实验、正式证明脚本或历史全文重读。

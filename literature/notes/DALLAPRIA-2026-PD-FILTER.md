# Dalla Pria 等 2026 — 用分区代数构造精确滤波与可认证预测压缩

## 版本、来源与实际阅读

- 作者：Marco Dalla Pria、Matteo Ruggiero、Dario Spanò。
- 题目：Exact inference via quasi-conjugacy in two-parameter Poisson–Dirichlet hidden Markov models。
- 精确版本：[arXiv:2512.22098v4](https://arxiv.org/abs/2512.22098v4)，2026-05-18 06:48:39 UTC。[原始 PDF](https://arxiv.org/pdf/2512.22098v4)，44 个物理页。[完整 TeX 源包](https://arxiv.org/src/2512.22098v4)。PDF 标题页打印 May 19, 2026，与 arXiv 提交时间不是同一个日期字段。
- 2026-11-27 上海时间复查官方 fixed-version 与 latest 页面，历史仍止于 v4。初版为 2025-12-26，v2 为 2026-01-06，v3 为 2026-05-04。
- 官方 arXiv 标识 JASA 最终接收作者稿。[期刊 DOI 页面](https://doi.org/10.1080/01621459.2026.2676717)给出接收日期 2026-05-14、accepted-author online 2026-05-26、published online 2026-07-02。本次完整阅读对象是 arXiv v4，未将期刊另一个排版版本当作已经对齐或完整阅读。
- 主读者 Pro-C 完整读取唯一活跃科学源文件 arxiv4.tex 的全部 1799 行，覆盖正文 §§1–5、Supplement Appendices A–D、全部陈述与证明、8 个算法、13 幅图、2 个正文脚注和完整参考文献。PDF 实际排出 42 条参考文献，bib 文件有 43 条条目，均已读过。原始 PDF pp.1,4,5,7,13,14,16,17,19–21,37–42 的标题、全部图和算法布局已目视核对。
- 两个辅助读者分别核查分区组合与传播/平滑证明，并检查本笔记的有限手推。主读者亲自完成全篇。没有把引用文献的全文计为已读，没有审计作者代码、复现实验、运行穷举或做形式化认证。
- 所读稿件没有发现 LLM 使用披露。这只是披露检查，不是关于实际写作过程的推断。

下文用“原文”标明作者结论，用“独立推导”标明本次来源内的进一步构造。没有对这些标准概率工具主张新颖性，没有修改 FP 核心定义、架构或实验。

## 1. 核心贡献与可用构造

**给定一个平稳 Poisson–Dirichlet 扩散和无标号分区观测，作者把无限维隐状态的后验写成有限个条件 PD 分布的混合。预测通过分区死亡过程传播权重，更新通过两个分区的部分匹配合并权重。** 这给出过滤、平滑、插值和新分区预测的统一代数。[正文 §§2–3，Supplement B–C]

最有用的构造性内容是：

1. 归一化观测似然为后验成分提供一个显式字典。可逆性和特定 duality 使预测留在该字典的有限正组合中。
2. 分区似然的乘法具有非负有限展开，因此 Bayes 更新可以直接累计有限权重，不必枚举无限潜在原子标签。
3. 本次给出原文顶层 coag 操作的有限匹配枚举方法、重复块压缩计数及明确资源界。
4. 本次推导正时间预测的统一 size-tail 界。它认证独立于累计样本量的近似混合表示大小，并给出后续一次条件化的删除责任界。
5. 本次推导多样性指标的精确均值、二阶矩和方差读出。固定阶查询只需有限求和，不需要先抽样无限频率向量。

精确闭包对每个有限历史成立。原文没有证明长期固定维数、最小充分状态、有限位存储或从未知数据发现这套代数结构。

## 2. 模型、观测与条件分布

### 2.1 非退化参数与总质量

以下采用正文 §2 的通常参数域

\[
0\leq\alpha<1,\qquad \theta>-\alpha.
\]

隐变量是降序概率向量

\[
x=(x_1,x_2,\ldots),\qquad x_i\geq0,\quad
x_1\geq x_2\geq\cdots,\quad \sum_i x_i=1.
\]

\(X(t)\) 是以 \(\operatorname{PD}_{\alpha,\theta}\) 为平稳可逆分布的扩散。模型从该平稳分布开始，在离散时刻 \(t_k\) 对当前 \(X(t_k)\) 作给定样本量 \(n_k\) 的 iid paintbox 抽样，只观察各占据原子的计数大小，丢弃原子标签。给定隐路径，各次观测条件独立。[正文 §3.1，Supplement A]

模型没有控制环境转移的动作。时序中跨时刻同一原子的身份不可直接观测。正文对社交网络的应用是这一统计模型的例子，不是从网络数据识别出扩散生成机制的定理。

原文某些后续位置写 \(\theta\geq-\alpha\)。边界 \(\theta=-\alpha\) 涉及退化 PD/Beta 分布与零概率分区的条件化。本笔记不直接把普通采样和比值公式延伸到该边界。上述无 dust 的似然也不应不加修改地用在总质量小于一的任意向量上。

### 2.2 无标号分区似然

记 \(\lambda=(\lambda_1\geq\cdots\geq\lambda_\ell)\) 为整数分区，\(|\lambda|=n\)，\(a_j(\lambda)\) 为大小 \(j\) 的块数。定义

\[
C(\lambda)=
\frac{n!}{\prod_{i=1}^{\ell}\lambda_i!\prod_{j\geq1}a_j(\lambda)!}.
\]

观测似然为

\[
P(\lambda\mid x)=C(\lambda)
\sum_{i_1,\ldots,i_\ell\ \mathrm{distinct}}
\prod_{r=1}^{\ell}x_{i_r}^{\lambda_r}.
\tag{1}
\]

重复块大小对应的 \(a_j!\) 不可漏掉。\(P(\lambda\mid x)\) 是整个无标号形状的概率，不是某一个带标签分组的概率。[正文 Eq.4，Supplement B]

令 \((a)_{(r)}=a(a+1)\cdots(a+r-1)\)，\((a)_{(0)}=1\)。PD 下的 Ewens–Pitman sampling formula 记为

\[
q_\lambda=\mathbb E_{\mathrm{PD}}P(\lambda\mid X).
\]

对 \(n\geq1\)，可执行的约分形式为

\[
q_\lambda=
C(\lambda)
\frac{\prod_{i=1}^{\ell-1}(\theta+i\alpha)}
{(\theta+1)_{(n-1)}}
\prod_{j=1}^{\ell}(1-\alpha)_{(\lambda_j-1)}.
\tag{2}
\]

它在严格参数域内为正。原文把分子写成从 \(i=0\) 开始的乘积、分母写成 \((\theta)_{(n)}\)。合法的 \(\theta=0,\alpha>0\) 情形必须先约掉共同的 \(\theta\)，不能直接计算 \(0/0\)。

### 2.3 条件 PD 成分

定义

\[
h_\lambda(x)=P(\lambda\mid x)/q_\lambda,\qquad
\operatorname{PD}^{\lambda}(dx)=h_\lambda(x)\operatorname{PD}(dx).
\tag{3}
\]

给定 \(\lambda\)，可以令

\[
W\sim\operatorname{Beta}(\theta+\ell\alpha,n-\ell\alpha),
\quad V^{(1)}\sim\operatorname{Dir}(\lambda_1-\alpha,\ldots,\lambda_\ell-\alpha),
\]

\[
V^{(2)}\sim\operatorname{PD}_{\alpha,\theta+\ell\alpha},
\]

三者独立，并把

\[
((1-W)V^{(1)},WV^{(2)})
\]

合并降序排列，得到 \(\operatorname{PD}^{\lambda}\) 样本。[Supplement A]

特别地，\(P((1)\mid x)=1\)，所以

\[
h_{(1)}=h_\emptyset=1,\qquad
\operatorname{PD}^{(1)}=\operatorname{PD}^{\emptyset}=\operatorname{PD}.
\tag{4}
\]

一个无标号 singleton 观测不携带信息。实现可以跳过这次 likelihood 更新，保留时间传播。这也直接说明作者的分区混合表示没有被证明唯一或最小。

## 3. Coagulation 是正乘法闭包

### 3.1 允许的合并

对 \(\omega\in\mathcal P_n\)、\(\gamma\in\mathcal P_m\)，从两侧分别选出同样数量的块，建立一一匹配，将匹配块逐对相加，保留所有未匹配块，最后排序。所有输出形成 \(\operatorname{coag}(\omega,\gamma)\subset\mathcal P_{n+m}\)。

这不是任意合并。不能合并同一侧的两个块，也不能让一侧的一个块同时匹配另一侧多个块。主文的简述以 Supplement Definition 3 的正式限制为准。

### 3.2 系数的概率解释与归一化方向

给定总分区 \(\mu\in\mathcal P_{n+m}\)，均匀抽出 \(n\) 个个体分到第一组，余下 \(m\) 个放第二组。两组分别诱导 \(\omega,\gamma\) 的概率为

\[
\mathcal H(\omega,\gamma\mid\mu)=
\binom{n+m}{n}^{-1}
\sum_{\substack{z+y=\mu\\
\operatorname{sort}(z_{>0})=\omega\\
\operatorname{sort}(y_{>0})=\gamma}}
\prod_{j=1}^{\ell(\mu)}\binom{\mu_j}{z_j}.
\tag{5}
\]

这里的 \(z,y\) 是与 \(\mu\) 各块对应的非负整数向量。因此 \(0\leq\mathcal H\leq1\)，且它与 \(x,\alpha,\theta\) 无关。固定 \(\mu,n,m\) 时，对所有 \((\omega,\gamma)\) 求和等于一。

原文 Proposition 4 给出

\[
P(\omega\mid x)P(\gamma\mid x)=
\sum_{\mu\in\operatorname{coag}(\omega,\gamma)}
\mathcal H(\omega,\gamma\mid\mu)P(\mu\mid x).
\tag{6}
\]

**固定 \(\omega,\gamma\) 时，\(\mathcal H\) 对 \(\mu\) 一般不归一化。** 例如 \(\omega=\gamma=(1)\)，输出 \((2),(1,1)\) 的系数都等于一，Eq.6 就是 \(1=P((2)\mid x)+P((1,1)\mid x)\)。这里应读作有限非负线性展开。

对 Eq.6 积分后，给定已有分区 \(\omega\) 的新顾客分区概率为

\[
q^{\omega}(\gamma)=
\sum_\mu\mathcal H(\omega,\gamma\mid\mu)\frac{q_\mu}{q_\omega}.
\tag{7}
\]

真正的条件合并概率为

\[
\operatorname{Coag}_{\alpha,\theta}(\mu\mid\omega,\gamma)
=\frac{\mathcal H(\omega,\gamma\mid\mu)q_\mu}
{\sum_{\mu'}\mathcal H(\omega,\gamma\mid\mu')q_{\mu'}}.
\tag{8}
\]

不能把 Eq.5 的裸系数当作 Eq.8 的混合权重。[正文 Propositions 1–2，Supplement Propositions 4–5]

## 4. 独立推导：实现合并所需的有限计数

本节给出原文顶层 `coag` 操作的具体有限实现。它由 Eq.1 的乘积直接推出，不是作者已证明的多项式复杂度结论。

### 4.1 按编号部分匹配枚举

暂时给两侧块编号。遍历部分匹配 \(M\)，形成输出分区 \(\mu(M)\)，记

\[
N_\mu=\#\{M:\mu(M)=\mu\}.
\]

则

\[
\boxed{\mathcal H(\omega,\gamma\mid\mu)
=\frac{C(\omega)C(\gamma)}{C(\mu)}N_\mu.}
\tag{9}
\]

**证明。** 令 \(S_\lambda=P(\lambda\mid x)/C(\lambda)\)。乘积 \(S_\omega S_\gamma\) 中两组 injective 原子标签赋值的重合关系，恰好给出一个两侧块的部分匹配。按重合关系分组，得到 \(S_\omega S_\gamma=\sum_M S_{\mu(M)}\)。非负项允许重排求和。合并相同输出并恢复 \(C\) 即得 Eq.9。

若两侧块数为 \(p,q\)，匹配总数为

\[
M(p,q)=\sum_{d=0}^{\min(p,q)}\binom pd\binom qd d!
\leq\min\{(p+1)^q,(q+1)^p\}.
\tag{10}
\]

直接生成、排序和字典累计需要

\[
O(M(p,q)(p+q)\log(p+q))
\]

次算术/比较操作，另计大整数、精确有理数及字典操作成本。不同输出数 \(K\leq\min\{M(p,q),p(n+m)\}\)，其中 \(p(r)\) 是整数分区数。显式标签存储为 \(O(K(p+q))\) 个整数槽位。有限可算不等于对一般块数多项式时间。

### 4.2 用块大小乘数表减少重复

设 \(a_s=a_s(\omega),b_t=a_t(\gamma)\)，令 \(c_{st}\) 是大小 \(s\) 的旧块与大小 \(t\) 的新块之间的匹配数。要求

\[
r_s=\sum_t c_{st}\leq a_s,\qquad
u_t=\sum_s c_{st}\leq b_t.
\]

输出乘数与该表代表的编号匹配数分别为

\[
a_k(\mu)=a_k-r_k+b_k-u_k+\sum_{s+t=k}c_{st},
\tag{11}
\]

\[
N(c)=
\frac{\prod_s a_s!/(a_s-r_s)!\ \prod_t b_t!/(b_t-u_t)!}
{\prod_{s,t}c_{st}!}.
\tag{12}
\]

证明为三步选择：先将每种旧块分配到各匹配组，再分配新块，最后在每个组内建立双射。两个分配分母和一个双射阶乘相消，剩下 Eq.12。应累计 \(N_\mu=\sum_{c:\mu(c)=\mu}N(c)\)。不同格子的 \(s+t\) 相同时，不额外除以输出块的乘数阶乘，它已在 Eq.9 的 \(C(\mu)\) 中处理。

手算例：\(\omega=\gamma=(2,1,1)\)，取 \(c_{1,2}=c_{2,1}=1\)，其余零。输出 \(\mu=(3,3,1,1)\)，\(N(c)=4\)，\(C(\omega)=C(\gamma)=6\)，\(C(\mu)=280\)，故 \(\mathcal H=18/35\)。Eq.5 独立给出 \(2\cdot2\cdot9/\binom84=18/35\)。这同时检查了重复块和相同配对和。

这些组合表与 \(\alpha,\theta\) 无关，可以在重复参数评估时复用。缓存是否节省总体成本取决于实际遇到的分区，本次没有给一般摊销或多项式保证。

## 5. 原文的预测与过滤递推

### 5.1 有限起点的分区死亡对偶

扩散生成元在对称多项式域上形式为

\[
\mathcal A=
\frac12\sum_{i,j}x_i(\delta_{ij}-x_j)\partial_{ij}
-\frac12\sum_i(\theta x_i+\alpha)\partial_i.
\]

原文使用的关键历史依赖是 Griffiths、Ruggiero、Spanò、Zhou 2025 的 PD 扩散对偶。这里读取作者引用的定义和用法，没有例行重读或重新证明该历史基础。[Supplement A，B.3]

从有限分区 \(\lambda\) 出发，以大小 \(n\) 的速率

\[
\lambda_n=\frac{n(n+\theta-1)}2
\tag{13}
\]

删除一个均匀选中的个体，重新排序得到分区。给定下降到大小 \(m\)，剩余分区服从从 \(\lambda\) 无放回抽取 \(m\) 个个体的超几何限制分布。于是转移系数可分解为大小死亡概率与条件限制概率。

为覆盖整个严格 PD 参数域，本文统一将 \(\emptyset\) 和 \((1)\) 合并成基点 \(\star\)，并按大小一计数。在 \(n\geq2\) 使用 Eq.13，在一处吸收。所有这些速率都为正。

这是明确的可执行边界约定：原文部分公式写死亡至零，若把 \(n=1\) 原样代入，合法负 \(\theta\) 会产生负速率。由于 Eq.4 两个状态的 dual 函数完全相同，\(1\to0\) 对该函数的生成元项恒为零，合并不改变预测读出。原文收敛证明也采用吸收于 \((1)\) 的说法。对有限起点，基点质量可取 \(1-\sum_{m=2}^n d_{n,m}(t)\)，避免给负速率概率意义。

### 5.2 可逆性将函数 duality 变成测度传播

令 \(D_t(\lambda,\omega)\) 是该分区死亡过程转移概率。原文的特定 duality 给出

\[
P_t h_\lambda(x)=\sum_\omega D_t(\lambda,\omega)h_\omega(x).
\]

结合 PD 可逆性，得到传播定理

\[
\operatorname{PD}^{\lambda}P_t
=\sum_{\omega\preceq\lambda}D_t(\lambda,\omega)
\operatorname{PD}^{\omega}.
\tag{14}
\]

这里必须保留归一化似然族和可逆基准测度。任意模型“存在一个 dual process”并不足以推出同样的后验闭包。[Supplement Theorem 2 及证明]

对于已有有限混合 \(\nu=\sum_\lambda w_\lambda\operatorname{PD}^{\lambda}\)，预测为

\[
v_\omega=\sum_\lambda w_\lambda D_t(\lambda,\omega),\qquad
\nu P_t=\sum_\omega v_\omega\operatorname{PD}^{\omega}.
\tag{15}
\]

每条 dual 路径的大小下降，但支撑字典会扩展到原支撑的 lower closure。因此不能把“死亡”直接读成每一步字典节点数减少。

### 5.3 更新及数据似然

新观察到 \(\gamma\) 后，累计

\[
\widetilde w_\mu
=q_\mu\sum_\omega\frac{v_\omega}{q_\omega}
\mathcal H(\omega,\gamma\mid\mu),
\tag{16}
\]

\[
Z_\gamma=\sum_\mu\widetilde w_\mu
=\sum_\omega v_\omega q^\omega(\gamma),\qquad
w_\mu^+=\widetilde w_\mu/Z_\gamma.
\tag{17}
\]

同一 \(\mu\) 可从不同旧成分和不同匹配产生，必须累计在同一个键。\(Z_\gamma\) 是观测的预测概率，连续这些归一化因子的乘积给出边际数据似然。原文据此做参数网格最大似然估计，没有证明估计一致性、可识别性或全局优化复杂度。[正文 §4.3，Supplement Theorem 3]

## 6. 平滑、插值与预测查询

在 \(t_k\) 定义真正的未来消息

\[
L_k(x)=\Pr(\pi^{k+1:N}\mid X(t_k)=x)
=C_k\sum_\omega b_\omega h_\omega(x).
\tag{18}
\]

已经过滤至 \(k\) 的分布为 \(\sum_\lambda w_\lambda\operatorname{PD}^{\lambda}\)。两者相乘并归一化，得到平滑权重

\[
s_\mu\propto q_\mu
\sum_{\lambda,\omega}
\frac{w_\lambda b_\omega}{q_\lambda q_\omega}
\mathcal H(\lambda,\omega\mid\mu).
\tag{19}
\]

\(C_k\) 在最后归一化中消去。反向递推必须只吸收 \(k+1,\ldots,N\) 的观测，并保留最后一次从 \(t_{k+1}\) 回到 \(t_k\) 的传播。\(k=N\) 时未来消息等于一。

源内有可局部澄清的符号混用：\(\Omega^{k:N}\) 先被定义为 \(X(t_{k-1})\) 处关于 \(\pi^{k:N}\) 的消息，因此在 \(X(t_k)\) 与过滤分布相乘时按该定义应为 \(\Omega^{k+1:N}\)。Algorithm 7 的文字步骤确实反向处理到 \(\pi^{k+1}\)，操作意图一致。前向系数应统一理解为已吸收 \(\pi^k\) 的过滤权重，不能误用尚未更新的预测权重。Supplement D.2 有一个把 filtered law 乘未来 likelihood 直接写成 smoother 的等式，省略了归一化常数，前面的正式证明用比例式处理。[Supplement C.2–C.3，D.2]

插值时，向前消息传播 \(\delta\)，未来消息最后一段传播 \(\Delta_{k+1}-\delta\)，然后使用 Eq.19。[Corollary 2]

对任意当前或插值时刻的混合，新的 \(m\) 样本无标号分区概率为

\[
\Pr(\Pi'_m=\gamma\mid\text{已有数据})
=\sum_\lambda w_\lambda q^\lambda(\gamma).
\tag{20}
\]

可用 Eq.7 有限计算。要抽样则先抽 \(\lambda\)，从该分区启动 CRP，再只返回最后 \(m\) 位新顾客诱导的分区。不能把旧、新全部顾客的合并分区当作这个预测输出。整个查询可以绕过无限隐频率向量的抽样。[Corollary 3，Algorithm 8]

## 7. 独立推导：正时间预测的表示大小证书

本节推导的是传播之后、尚未吸收新数据的分布。实际删除质量记 \(\delta\)，目标容差记 \(\varepsilon\)。

### 7.1 大小矩界与尾界

采用大小一吸收的约定。设初始有限混合最大大小为 \(M_0\)，\(N_t\geq1\) 是死亡过程大小。令

\[
c_\theta=\min\{1,1+\theta\}>0.
\]

PD 的严格参数域蕴含 \(\theta>-1\)。对 \(n\geq2\)，

\[
\lambda_n\geq\frac{c_\theta}2n(n-1).
\]

由于过程不增加大小，它始终在有限集合内。生成元公式和方差非负给出

\[
m'(t)=-\mathbb E\lambda_{N_t}
\leq-\frac{c_\theta}2\mathbb E[N_t(N_t-1)]
\leq-\frac{c_\theta}2m(t)(m(t)-1),
\]

其中 \(m(t)=\mathbb EN_t\)，\(\lambda_1=0\)。令 \(z=m-1\)、\(a=c_\theta/2\)，积分可得

\[
z(t)\leq
\frac{z(0)}{e^{at}+z(0)(e^{at}-1)}
\leq\frac1{e^{at}-1}\leq\frac1{at}.
\tag{21}
\]

\(z(0)=0\) 时直接使用吸收性。因为对整数 \(L\geq1\)，\(N_t>L\) 蕴含 \(N_t-1\geq L\)，故

\[
\boxed{\delta_L(t):=\Pr(N_t>L)
\leq\min\left\{1,\frac1{L(e^{c_\theta t/2}-1)}\right\}
\leq\min\left\{1,\frac2{c_\theta tL}\right\}.}
\tag{22}
\]

这是直接有限状态微分论证，没有使用一个额外的“从无穷降下”交换极限定理。

### 7.2 转成混合和预测误差

保留 Eq.15 中 \(|\lambda|\leq L\) 的分量并归一化，记 \(\nu_t^{[L]}\)。若实际删除质量 \(\delta_L(t)<1\)，则

\[
\nu_t=(1-\delta_L(t))\nu_t^{[L]}+
\delta_L(t)\nu_{t,\mathrm{drop}},
\]

所以按 \(\|\mu-\nu\|_{\mathrm{TV}}=\sup_A|\mu(A)-\nu(A)|\) 的约定，

\[
\|\nu_t-\nu_t^{[L]}\|_{\mathrm{TV}}\leq\delta_L(t).
\tag{23}
\]

任何进一步的无观测 Markov 传播或 paintbox 预测不会放大该 TV 误差。任意有界查询 \(f\) 的偏差至多为 \(\operatorname{osc}(f)\delta_L(t)\)。

对 \(t>0\)、\(0<\varepsilon<1\)，可直接选

\[
\boxed{L_\varepsilon(t)=
\max\left\{1,\left\lceil
\frac1{\varepsilon(e^{c_\theta t/2}-1)}
\right\rceil\right\}.}
\tag{24}
\]

较保守的选择是 \(\max\{1,\lceil2/(c_\theta t\varepsilon)\rceil\}\)。已知 \(M_0\) 时可以再取与 \(M_0\) 的最小值。

输出分量数至多为

\[
\sum_{n=1}^{L_\varepsilon(t)}p(n).
\tag{25}
\]

对固定正时间和容差，这个表示大小界与累计观测样本量无关。每个标签至多有 \(L_\varepsilon(t)\) 个整数，另存一个实权重。**它不是计算工作量与历史无关的证明**：计算保留权重仍可能要汇总庞大的旧混合，精确数值成本也未被消除。整数分区数本身增长很快。

在 \(t=0\) 不用 Eq.24，可按已有权重取分位数或取 \(L=M_0\)。目标零误差也可取 \(M_0\)，本推导没有提供与 \(M_0\) 无关的精确截断。实际删除质量等于一时，保留后归一化没有定义。目标容差小于一的 Eq.24 排除了这一情况。正时间下有限起点到达基点有正概率，但不应在零时间沿用该理由。

### 7.3 下一次 Bayes 更新的删除责任

若

\[
\nu=(1-\delta)\nu_{\mathrm{keep}}+\delta\nu_{\mathrm{drop}},
\quad 0\leq\delta<1,
\]

新分区似然 \(g=P(\gamma\mid x)\in[0,1]\)，令

\[
Z_K=\nu_{\mathrm{keep}}g,\quad Z_D=\nu_{\mathrm{drop}}g,\quad
Z=(1-\delta)Z_K+\delta Z_D.
\]

当 \(Z_K>0\) 时，Bayes 公式给出

\[
\nu^g=(1-\eta)\nu_{\mathrm{keep}}^g+\eta\nu_{\mathrm{drop}}^g,
\qquad \eta=\frac{\delta Z_D}{Z}.
\]

若 \(Z_D=0\)，删除项责任为零，忽略其未定义的单独条件分布即可。因此

\[
\boxed{\|\nu^g-\nu_{\mathrm{keep}}^g\|_{\mathrm{TV}}
\leq\eta\leq\min\{1,\delta/Z\}.}
\tag{26}
\]

还可以只用保留模型证据计算保守界

\[
\eta\leq\frac{\delta}{(1-\delta)Z_K+\delta},
\tag{27}
\]

因为右侧是在 \(Z_D\leq1\) 下的最大值。若 \(Z_K=0<Z\)，保留模型无法解释该观测，其 Bayes 更新无定义。若 \(Z=0\)，精确模型本身也无法通常归一化。

这说明可以认证一次具体删除及条件化，但一个稀有新观测会放大原先很小的删除责任。没有额外证据下界或递归控制，Eq.22 不是持续吸收新数据的长期统一滤波误差定理。

## 8. 独立推导：无需隐状态抽样的精确矩读出

令 \(\lambda\) 大小 \(n\geq1\)、块数 \(\ell\)，并定义

\[
a_i=\lambda_i-\alpha,\qquad B=\theta+\ell\alpha.
\]

对整数 \(r\geq2\)，幂和 \(S_r(x)=\sum_i x_i^r\) 就是新 \(r\) 样本只形成一个块的条件概率，故

\[
\boxed{\mathbb E_{\mathrm{PD}^{\lambda}}S_r
=q^\lambda((r))
=\frac{\sum_i(a_i)_{(r)}+B(1-\alpha)_{(r-1)}}
{(\theta+n)_{(r)}}.}
\tag{28}
\]

证明只需把 CRP 中 \(r\) 位新顾客全部坐同一桌的事件分成两类：首人坐已有桌 \(i\)，之后全跟随，贡献 \((a_i)_{(r)}\)。首人开新桌，之后全跟随，贡献 \(B(1-\alpha)_{(r-1)}\)。共同分母为 \((\theta+n)_{(r)}\)。

对 heterozygosity \(H_2=1-S_2\)，有限混合的均值为

\[
\mathbb E_\nu H_2=1-\sum_\lambda w_\lambda q^\lambda((2)).
\tag{29}
\]

又因 \(C((2,2))=3\)，逐点有

\[
S_2^2=P((4)\mid x)+\frac13P((2,2)\mid x).
\]

因此

\[
\mathbb E_\nu H_2^2=
\sum_\lambda w_\lambda
\left[1-2q^\lambda((2))+q^\lambda((4))+
\frac13q^\lambda((2,2))\right].
\tag{30}
\]

二阶读出也可以避免枚举所有旧桌对。令

\[
T=\sum_i(a_i)_{(2)},\qquad U=\sum_i[(a_i)_{(2)}]^2.
\]

则

\[
\boxed{\frac13q^\lambda((2,2))=
\frac{T^2-U+2B(1-\alpha)T+B(B+\alpha)(1-\alpha)^2}
{(\theta+n)_{(4)}}.}
\tag{31}
\]

它按两对新顾客坐不同桌分类：两张旧桌贡献 \(T^2-U\)，旧/新两种次序贡献 \(2B(1-\alpha)T\)，两张新桌贡献最后一项。Eq.30 减去 Eq.29 的平方即得方差。

固定阶的这些读出共需 \(O(\sum_\lambda\ell(\lambda))\) 次有限求和，另计数值运算。基点可用 \(\lambda=(1)\) 代入，避免空分区在 \(\theta=0\) 的可去奇点。先验也可直接用 \(\mathbb ES_r=(1-\alpha)_{(r-1)}/(\theta+1)_{(r-1)}\)。

这是对输入混合的精确均值和方差，不是完整分布或可信区间的闭式表达。如果输入权重本身来自剪枝或 Gillespie 经验频率，读出仍只对那个近似混合精确。这个区别可以把查询抽样误差与混合近似误差分开。

## 9. 原文算法的精确性与实际资源

### 9.1 有限历史闭包没有给固定大小

截至 \(k\) 的累计观测样本数记 \(S_k=\sum_{j=0}^k n_j\)。预测不增加单个分区大小，更新满足 \(|\mu|=|\omega|+n_k\)，因此过滤成分大小至多为 \(S_k\)。全数据平滑和插值至多为 \(S_N\)。粗支撑界为

\[
|\Lambda_{0:k}|\leq\sum_{n=0}^{S_k}p(n).
\tag{32}
\]

对于单个分区，lower closure 的简单枚举界为

\[
|L(\lambda)|\leq\prod_i(\lambda_i+1).
\]

排序与相同输出合并可进一步去重。Eq.32 只证明有限历史可算，不能把混合权重向量无条件视为持续时间无关的固定维状态，也不能把实数权重个数视为有限位内存。

### 9.2 八个算法的角色

| 算法 | 实际操作 | 精度说明 |
|---|---|---|
| 1 | PD stick breaking 后按剩余质量截断 | 有限向量近似 |
| 2 | 条件 PD 的 Beta、Dirichlet 与残余 PD 分解 | 残余 PD 仍需截断 |
| 3 | 累计完整死亡转移权重并抽样成分 | 权重公式精确，返回隐向量仍使用算法 2 |
| 4 | Gillespie 路径经验频率替代传播权重 | Monte Carlo 近似 |
| 5 | 遍历 coag 并累计更新权重 | 有限展开精确，隐向量抽样仍截断 |
| 6 | 交替传播与更新 | 精度继承所选子程序和剪枝 |
| 7 | 反向消息与前向混合相乘 | 需统一时间索引和归一化 |
| 8 | 从条件 CRP 抽新顾客分区 | 给定精确混合时无需截断隐向量 |

原文 §4.2 明确承认实验用 Gillespie 近似转移权重，并使用混合剪枝。因此摘要的 exact inference 和 bypassing SMC 指解析表示与递推结构，不应扩展成“所有报告实验都没有随机误差或截断”。

### 9.3 截断阈值与吸收守卫

Algorithm 2 把残余 PD 块乘以 \(W\)，却打印阈值 \(\varepsilon/(1-W)\)。若目标是总删除质量不超过 \(\varepsilon\)，应对残余 PD 使用 \(\varepsilon/W\)。当 \(W\leq\varepsilon\) 时可省略整个残余块。这个修正来自乘数本身，不影响精确后验分解。

在同一抽样耦合下，删除质量 \(\delta\leq\varepsilon\) 后再把保留原子归一化，原子质量向量的 \(\ell_1\) 距离至多 \(2\varepsilon\)，排序不增大这一距离。这是质量向量近似界。**它不是无限维 PD 样本分布之间的 TV 界**，有限原子输出与无限原子分布可能在该意义下奇异。

Algorithm 4 没有打印大小一/零处的停止守卫，直接再次调用指数等待时间会遇到零或负速率。采用 §5.1 的合并基点，并在到达大小一时停止，就有清楚的执行语义。未经源码审计，不能由伪码问题推断作者实际程序一定同样处理。

## 10. 经验结果的证据范围

本文理论主要依赖模型和代数证明，实验展示计算效果。以下保留实际干预和比较范围。[正文 §4，Supplement D]

- Fig.7 比较样本量 10、30、50 下的六种设置：top 1、top 10、top 100，以及保留 90%、95%、100% 质量。参数 \(\alpha=0.1,\theta=1.5\)，\(N=9\)，时间间隔 0.2，PD 截断 0.005，每次更新使用 \(10^4\) 抽样。左图是秒数的对数尺度，右图是 heterozygosity 的区间分数。top 10 或保留 90% 的性能接近完整混合是这些设定的数值观察。
- Fig.D.1 展示累计质量 90%、95%、99% 所需成分比例，使用大小 10、\(T=19\)、间隔 0.1、\(10^5\) Gillespie 粒子。支撑集中不是一个已证明的普遍或递归误差界。
- 一条合成轨迹有 20 个等间隔时刻，间隔 0.025，样本量 50，真参数 \((0.1,1.5)\)。用 top 10 剪枝与 \(10^4\) Gillespie/后验抽样，网格 MLE 为 \((0,1.5)\)。Fig.8 比较过滤、平滑、bootstrap particle filter 和独立先验。Fig.D.2 展示前三个排序坐标，不能用一条轨迹建立一般性能排序。
- Fig.9 实际有六列方法：独立、bootstrap、估计参数 filter、oracle filter、估计参数 smoother、oracle smoother。图注写 five 是文字计数错误。比较包含 20 次重复，每条 10 个时刻，间隔 0.01，样本量 10，参数 \((0.1,1.0)\)。图给出散点与箱图，没有把这些观察升级为普遍严格优越性。
- 区间分数 Eq.13 从 \(k=0\) 求和到 \(N\)，分母却为 \(N\)，有一个总项数约定问题。同一数据上的方法排序不因此自动颠倒，但复现平均分时应固定定义。
- 真实数据取 2009-06-28 一天的 Infectious 接触网络，聚合成 12 个半小时窗口，把连通分量大小作为无标号分区。没有直接检验这些分区确由给定 PD diffusion 和 iid paintbox 机制生成。平滑有未来数据，不能作为相同信息集的纯在线方法比较。
- 实际数据的 filter、smoother 和 bootstrap 共用全序列拟合的 \((\widehat\alpha,\widehat\theta)=(0,0.75)\)，独立方法逐时拟合。过滤递推给定参数时在线，不代表整个含参数估计的流程只使用过去数据。
- 原文报告标准笔记本下 dual 方法后验抽样少于两分钟，bootstrap 约一小时。所读材料没有足以建立通用等预算复杂度排序的完整硬件与所有方法工作量审计，本次也没有复现。Fig.D.3 的两种 KDE 带宽显示粒子估计更粗糙，多模态本身不是错误后验的数学判据。

原文只给作者 GitHub 主页作为公开代码入口，本次没有进行版本锁定的代码审计。经验比较与解析闭包、独立误差证书保持分开。

## 11. 可复用的抽象数学接口

**独立整理，不是 FP 架构提案。** 设 \(\rho\) 是已知基准测度，\(h_i\geq0\) 且 \(\rho h_i=1\)。如果相对于 \(\rho\) 的预测密度算子满足

\[
P_t^\dagger h_i=\sum_jD_t(i,j)h_j,
\]

其中 \(D_t(i,j)\geq0\)，每个有限起点只有有限多个非零项。保质量与 \(\rho h_j=1\) 再给出 \(\sum_jD_t(i,j)=1\)。非负密度的某个线性展开本身未必有非负系数，所以该条件必须明确要求。另要求每个实际观测似然满足

\[
h_i g_y=\sum_j c_y(i,j)h_j,\qquad c_y(i,j)\geq0
\]

且右边有限，则任意有限混合 \(\sum_iw_i h_i\rho\) 的一次预测与更新都能通过这些系数精确递推。证明就是测度传播的线性性与一次 Bayes 归一化。本文用可逆性把 \(P_t^\dagger\) 换成 \(P_t\)，用特定 duality 构造 \(D_t\)，用分区匹配构造 \(c_y\)。

这个接口的可检验条件是明确的：归一化非负密度、有限传播支撑、非负乘法闭包、正的观察证据以及算子系数可计算。缺少其中任何一项，都不能直接从“预测诱导表示”这一口号得到精确算法。

如果某个 FP 候选模型另行满足这些对象映射，这篇论文可以提供已知模型的闭包模板和误差记账工具。是否能从经验发现字典、获得操作或迁移到受控交互，原文没有解决，本笔记也没有替 Astra 作决定。

## 12. 结论与恢复边界

本篇已完成 v4 全文阅读。可直接复用的数学结果为 Eq.9–12 的组合枚举，Eq.14–20 的已知模型精确消息递推，Eq.21–27 的正时间预测截断与一次更新责任证书，以及 Eq.28–31 的无隐向量抽样矩读出。

核心限定是：有限历史的精确混合，独立于历史的近似预测表示大小，以及持续在线学习的机制形成，是三个不同问题。本次只证明和记录前两者所列出的具体结论。进一步整体计算复杂度、长期剪枝误差、未知模型学习和受控版本仍需额外假设或新研究。

没有进行经验重放、整个定理系统的独立认证或形式化证明。所有历史依赖均按引用与实际局部阅读标明，没有另开旧论文全文队列。下一篇只在重新 fetch、检查 Astra 请求和现有 owner 后选择。

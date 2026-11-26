# Bonet 2026 — 有限局部松弛表、递归逻辑与可执行的图计算

## 来源、版次与实际覆盖

- Blai Bonet, **Recurrent Graph Neural Networks with Set-Based Aggregation**, arXiv **2609.15932v1**, 2026-09-14，22 个物理页。[固定版本](https://arxiv.org/abs/2609.15932v1) · [PDF](https://arxiv.org/pdf/2609.15932v1) · [TeX](https://arxiv.org/src/2609.15932v1)。研究员 Pro-B，2026-11-26 上海日期。
- 作者署名 Universidad Simón Bolívar。此版使用 AAAI 2027 的 preprint 模板，不能据此登记为 AAAI 已接收论文。未建立 OpenAI 或 Anthropic 官方工作身份。
- **主读已完整阅读**全部活动 TeX，共 13 个输入文件，覆盖主文八节、附录 pp.9–22、全部定义、定理与证明、示例、实验方法及结果、32 条印刷参考文献。六个活动表格为五个无编号表及 Table 1，没有科学 Figure。另视觉检查原 PDF pp.4、5、13、16、19、20、21、22，包含全部表格所在页。
- `toappendix` 是实际出版内容，`experiments2.tex` 及其结果文件均已读。源码中的 `Omit`、注释和模板 inactive branches 未计作发表结果。尤其未把隐藏的实现调试段作为实证证据。
- 三个辅助阅读分别核对活动源和版面、双向构造条件、实验范围。主读亲自完成上述阅读并评估反馈。独立推论见第七节，未运行作者代码、训练、实验复现或形式化证明。
- PDF 多处不同结果重复显示为 “Theorem 17”。以下按**结果标题、章节和源码 label**定位，避免用这个重复编号混淆结论。

## 一、最值得保留的结果

本篇给出一个可操作的转换链：**实数循环网络的局部松弛 → 有限 embedding 词表上的转移表 → 正向固定点方程组**。反方向从一类逻辑公式逐条构造 Boolean 寄存器、邻居 max 和变量 latch，得到对所有有限图成立的实现。这里的“可执行”有具体的数据结构、更新规则和停止论证。

精确的双向表达力对象是 Ratchet 类与

$$
\mathbf B\Sigma_1^\Diamond,
$$

即只用原子文字、合取、析取、存在模态 $\Diamond$ 和最小固定点 $\mu$ 构成的闭公式之 **Boolean closure**。等价地，可以在顶层组合这些闭块及其 $\nu,\Box$ 对偶。它是 alternation-free $\mu$-calculus 的真子类。不能省略 $\Diamond$ 上标，也不能把结论扩大为整个第一层或全部 alternation-free 逻辑。主文结论中的较宽简称应以正式定义和 Barrier 命题为准。

最适合保留和运行的是**共享的联立方程系统**。它保留局部规则与状态依赖。把它强行展开成单条闭公式会额外引入指数膨胀。另一方面，得到有限词表和完整转移表本身也可能昂贵，不能从“方程组相对表大小线性”推出“从原网络权重线性抽取解释”。

论文没有给出从预测误差或训练数据发现这些合格网络的学习规则。实验展示的是从已知逻辑构造网络，再抽回逻辑的往返一致性。其建设性贡献在计算表示、语义压缩与编译，而非已经解决结构学习。

## 二、网络、邻域类型和有限局部语义

### 2.1 固定接口

输入是有限有向图，节点带固定有限 atomic-type 字母表 $\mathrm{ATP}$ 中的类型。边 $E(u,v)$ 表示 $u$ 读取 $v$。固定宽度 $W$ 的循环更新为

$$
z_u^{\ell+1}=N\!\left(\alpha_u,z_u^\ell,\{z_v^\ell:E(u,v)\}\right)
=\rho\!\left(A_{\alpha_u}z_u^\ell+B_{\alpha_u}\bigoplus\{z_v^\ell:E(u,v)\}+C_{\alpha_u}\right),
$$

初值 $z_u^0=e_{\alpha_u}$。$\rho$ 为连续的 ReLU 或 clipped activation，$\bigoplus\varnothing=0$。关键是输入为**集合**而非带重数的 multiset。重复相同邻居值不增加信息。主要具体聚合器是逐坐标 max。固定宽度、固定类型集、共享循环权重均不随图大小改变。

对所有有限图收敛时，记节点极限为 $\Phi_u$。有限深度 embedding 由有限邻域类型决定，无限 unfolding 类型相同的节点得到相同极限。这给出 bisimulation 不变性。它不是带计数的 color-refinement 不变性的同一接口。

有限深度编译枚举类型及其 embedding。每个类型公式同时要求节点旧类型、所有邻居落在指定类型集合内、集合中每个类型都有邻居见证。递归类型空间含 powerset，层数增加可造成塔式增长。该构造提供有效性和精确语义，不承诺普遍高效的程序抽取。[原文 Finite Types and Their Embeddings、Depth-Bounded Compiler 及 pp.9 起证明]

### 2.2 冻结邻居后重新求解

对节点类型 $\alpha$ 和有限 embedding 集 $S$，定义

$$
F_\alpha(S)=\lim_{\ell\to\infty}y_\ell,
\qquad y_0=e_\alpha,
\quad y_{\ell+1}=N(\alpha,y_\ell,S).
$$

这不是把整个图运行一步，而是在**邻居输入保持不变**时，让单节点内部递归完成松弛。Regularity 要求

$$
\Phi_u=F_{\alpha_u}\!\left(\{\Phi_v:E(u,v)\}\right).
$$

该定义保留指定初值的固定点选择。一般连续网络在图上的极限满足某个固定点方程，并不自动保证从 $e_\alpha$ 再运行冻结系统会选中同一个固定点。Regularity 正是需要补上的条件，也不要求冻结系统只有唯一固定点。

词表按闭包构造：从 $\{F_\alpha(\varnothing):\alpha\in\mathrm{ATP}\}$ 开始，加入所有已得有限子集 $S$ 对应的 $F_\alpha(S)$，最后取拓扑闭包。它不是所有 transient embedding 的集合，也不是在有限训练图上观察到的极限样本集合。设这个词表 $\mathcal V$ 有限，$m=|\mathcal V|$，即可定义

$$
T:\mathrm{ATP}\times2^{\mathcal V}\longrightarrow\mathcal V,
\qquad T(\alpha,S)=F_\alpha(S).
$$

### 2.3 表驱动 game 与原网络不同

原文定义新的图上动力系统

$$
E_u^0=T(\alpha_u,\varnothing),
\qquad E_u^{k+1}=T\!\left(\alpha_u,\{E_v^k:E(u,v)\}\right).
$$

每一轮已封装一次完整局部松弛。需分别检查以下条件。[Recurrent Nets，Definition 10，pp.3–4]

| 条件 | 实际保障 |
|---|---|
| Convergence | 原实数网络在每个有限图有极限 |
| Regularity | 冻结邻居极限后重新松弛，得到同一节点极限 |
| Finite vocabulary | 局部松弛可用固定的有限表表示 |
| Admissibility | 表驱动 game 收敛到原网络的 $\Phi$ |
| Ordered | 存在词表偏序，使每个节点的 game 轨迹沿序上升 |
| Game monotonicity | 适当增加邻居见证，不会使表输出下降 |

最后一项使用 Hoare 型集合序

$$
S\sqsubseteq S'
\iff \forall e\in S\ \exists e'\in S'\quad e\preceq e',
\qquad
S\sqsubseteq S'\Longrightarrow T(\alpha,S)\preceq T(\alpha,S').
$$

具备全部条件的是 Ratchet net。有限 admissible game 在 $n$ 节点图上至多经过 $m^n$ 个状态后停止，ordered game 的严格进展次数至多 $n(m-1)$。这些是 **game** 的界，不能直接作为原实数迭代的精确停止界。有限确定性状态空间单独只保证最终周期性，admissibility 排除了非平凡周期。

## 三、建设性地获得这些条件

### 3.1 收缩路线

原文 Contractive nets 定理使用完整局部收缩条件

$$
\|N(\alpha,z,S)-N(\alpha,z',S')\|
\le\lambda\max\{\|z-z'\|,\|\oplus S-\oplus S'\|\},\quad0<\lambda<1,
$$

以及 indexed-neighbor aggregation 的 1-Lipschitz 性。对 max 和 $\ell_\infty$ 范数，充分的权重界是

$$
\|A_\alpha\|_\infty+\|B_\alpha\|_\infty<1
$$

对所有类型同时成立。这里矩阵范数是绝对行和范数。这个条件给出 convergence、regularity、良定义的词表和 admissibility。**有限词表、ordered、game monotonicity 不由此自动获得。**

较弱条件 $\|A_\alpha\|_\infty<1$ 只保证冻结系统对自身状态收缩。在另外已知整图收敛时，它支持 regularity，但不等于邻居传播也收缩。[Contractive nets 与 Appendix A1]

### 3.2 单调路线和可精确实施的子类

原文 Monotone nets 定理另行假设网络已收敛，初始化满足

$$
0\le e_\alpha\le N(\alpha,e_\alpha,\varnothing).
$$

合适的单调网络与单调聚合器给出 regularity、admissibility、ordered。max 进一步给出上述集合序下的 game monotonicity。不能把“非负权重 + ReLU”独立写成普遍收敛定理。使用 clip 才直接提供有界性。

一个充分且可精确枚举的建设性子类是

$$
\rho=\operatorname{clip}_{[0,1]},\quad\oplus=\max,
\quad A_\alpha,B_\alpha\in\mathbb Z_{\ge0}^{W\times W},
\quad C_\alpha\in\mathbb Z^W,
\quad e_\alpha\in\{0,1\}^W,
$$

加上上述初值条件。更新保持 Boolean 状态，初始状态逐步上升，单节点冻结运行和整图运行均有限停止，词表包含于 $\{0,1\}^W$。bias 可为负，例如合取需要 $-1$。

这是对原文充分条件的完整可用表述。Appendix A2 的“整数且有界所以有限”论证，字面只列 $A,B$ 整数及聚合器 1-Lipschitz，不足以单凭这些条件推出所有轨道为整数。本笔记明确补上 **bias 保整数与聚合器保整数**。反向逻辑编译器的逐条 Boolean 规则本身已经保证这一性质，不依赖该简写推论。

### 3.3 连续 transient 可以被有限语义吸收

原文第二例取宽度 1、clip、$A=-1/2$、$B=2$，黑色 bias 为 $1/2$，红色为 $1$。孤立节点从初值 0 或 1 振荡收敛到 $1/3$ 或 $2/3$，并不有限停止。完整词表却只有

$$
\mathcal V=\{1/3,\ 2/3,\ 7/9,\ 1\}.
$$

其表在邻居最大值上单调。game 在至多两轮达到极限，极限类别对应 sink、邻居皆为黑 sink 等深度至多 2 的模态性质。原文通过节点是否到达环及有限高度归纳证明收敛，再验证表的 admissibility。这个例子有负 self-weight，也不满足完整权重收缩界，说明充分条件未穷尽 Ratchet。[Examples，Appendix Proposition A5，PDF pp.5、14–15]

## 四、从有限表编译可运行的逻辑

### 4.1 较一般的 IFP 编译

仅要求 regular、有限词表、admissible、ordered，即可使用 inflationary fixed-point logic。关系 $R_i(u)$ 记录“曾访问过状态 $e_i$”，而非当前恰为 $e_i$。上升轨迹使当前状态能够由

$$
\operatorname{curr}_i(u)=R_i(u)\land\bigwedge_{e_i\prec e_j}\neg R_j(u)
$$

恢复。初始化添加 $T(\alpha,\varnothing)=e_i$ 的类型。每条后继表项用两项精确匹配邻居集合：所有邻居属于所列 current 状态，每个所列状态均有邻居见证。IFP 持续加入已访问关系，因此这里允许否定。归纳不变量为 $R_i^{k+1}(u)$ 当且仅当某轮 $\ell\le k$ 的 $E_u^\ell=e_i$。最终 current 谓词给出极限。[IFP Compiler，`thm:rec-compiler`，pp.13–14]

### 4.2 Game monotonicity 使规则只需要正见证

Ratchet 类的更强编译使用**上集**谓词

$$
X_i(u)\quad\text{表示}\quad\Phi_u\succeq e_i.
$$

从完整表生成

$$
\Theta_i(\vec X)=
\bigvee_{\alpha,S:T(\alpha,S)\succeq e_i}
\left(\alpha\land\bigwedge_{e_j\in S}\Diamond X_j\right).
$$

这里没有“除此之外不得有别的邻居”的条件。一个实际邻居可以同时见证多个较低词表元素，故满足该规则意味着 $S\sqsubseteq S_u^*$。Game monotonicity 恰好保证此时表输出不超过真实输出。若极限足够大，直接选真实邻居极限集合那一行就给出见证。

联合算子 $\vec\Theta$ 对所有 $X_i$ 正。Regularity 给出目标上集是固定点。对任何 pre-fixed tuple，沿 game 从空邻居初始化归纳，再用 admissibility，证明目标上集包含于该 tuple。故其联合**最小**固定点就是所有极限上集。

通过 Bekić 消元可以转为每个上集的闭 $\mu,\Diamond$ 公式 $\theta_i$。精确状态由

$$
\gamma_i=\theta_i\land
\bigwedge_{e_j\text{ covers }e_i}\neg\theta_j
$$

恢复。对任意读出 $h:\mathcal V\to\{0,1\}$，析取被接受的 $\gamma_i$ 即可。以上构造没有借助 Janin–Walukiewicz 完备性作为黑箱。[Net-to-logic，`thm:net-to-logic`，pp.15–16]

**可复用的认证办法。**在本篇空邻居初始化下，表的 monotonicity 已经给出 ordered：$\varnothing\sqsubseteq S$ 保证第一步上升，随后对所有邻居归纳。这是原文 Logic-to-net Step 3 已使用的证明，可直接作为有限表认证步骤，不计为本笔记的新发现。

### 4.3 真正的编译成本

完整表有 $|\mathrm{ATP}|2^m$ 行。总序且聚合器为 max 时只需区分空集及邻居最大词表元素，可降到 $O(|\mathrm{ATP}|(m+1))$ 个条目。一般偏序情形不能直接使用这个简化。

共享每行规则和辅助谓词时，原文给出相对**已编码的 quotient table**线性的系统规模。展开共享定义会多出因子，Bekić 展平可进一步指数膨胀。词表发现、求出局部极限、比较精确实数、构造偏序及验证语义条件均是另外的输入和计算成本。任意实数权重下的“公式有效可得”还依赖相应数值表示和精确局部求解接口。本文的 Boolean 构造提供这样的离散接口，不能据此把任意已训练实数网络视为同样可精确抽取。

## 五、从逻辑构造网络的明确规则

先把目标写成闭 $\Sigma_1^\Diamond$ blocks 的顶层 Boolean 组合。每个子公式设一个寄存器，每个绑定变量设一个 latch。原子命题不互斥时，atomic type 是完整的 Boolean valuation。若命题数作为输入增长，$2^{|P|}$ 类型的表示成本需另计。

| 逻辑对象 | 同步更新规则 |
|---|---|
| 原子文字 | 类型决定的 0 或 1 |
| $a\land b$ | $\operatorname{clip}(r_a+r_b-1)$ |
| $a\lor b$ | $\operatorname{clip}(r_a+r_b)$ |
| $\Diamond a$ | $\max_{E(u,v)}r_a(v)$，空邻居为 0 |
| 变量引用 $X$ | 复制其 latch $v_X$ |
| 最小固定点 latch | $v_X\leftarrow\max(v_X,r_{\mathrm{body}(X)})$ |
| 顶层对偶块的否定 | 外围派生寄存器 $1-r_a$ |

所有规则读取前一轮。循环变量按依赖 SCC 分组，正的 block 内可以同步求其联合最小解。证明以固定点和 pre-fixed point 比较为主：memoryless 寄存器在固定点满足等式，latch 满足 $v_X\ge r_{\mathrm{body}(X)}$，因此变量部分支配语义最小解。初始化又处于所有固定点之下，逐坐标上升即到达该最小解。

core 寄存器从文字真值和其余 0 开始，只会 $0\to1$。外围否定及 Boolean 电路不反馈进入 closed blocks。原文给出 $Wn$ 的**原网络**精确稳定上界，包含派生传播延迟。宽度线性于子公式和绑定变量数量，不能把它自动解释为所有稠密矩阵、类型表及总执行工作的线性界。

词表上的偏序只比较 core 坐标。派生坐标在固定点由 core 唯一决定，故仍为偏序。部分外围坐标可以下降，全部权重也不必非负。因此“由正向计算编译而来”不等于整个 embedding 在通常逐坐标序下递增。[Logic-to-net，`thm:logic-to-net`，pp.16–18]

原文的红色可达且绿色不可达例子可保留为两个独立 reachability 核心位 $s,t$，读出 $h(s,t)=s\land\neg t$。其核心表为 $T(\alpha,m)=m\lor e_\alpha$。这个小例子展示可复用计算块的组合，但两位核心不包含一个额外内置读出寄存器的费用。附录 p.19 展平的 $\theta_{11}$ 显示式漏项和模态，使用前面的表、两个正确独立 reachability 方程及 $\theta_{11}=\theta_{10}\land\theta_{01}$ 即可避免传播该局部排印问题。未据此推断实现错误。

## 六、实证支持的边界

作者实施的流程是

$$
\gamma\longrightarrow\text{按证明构造网络}
\longrightarrow(\mathcal V,T)
\longrightarrow\text{未展平的正方程组}
\longrightarrow\text{与独立逻辑求值器比较}.
$$

词表提取枚举已发现状态的可达逐坐标 max aggregate，并对每个类型和 aggregate 运行单顶点冻结系统。实验没有做 register minimization，也没有 Bekić 展平。独立求值器据作者称不与两个编译器共享代码。最终测试的是原公式与重编译方程组的 denotation，不应额外宣称每个图的全部神经 transient 也被独立比较。[Experimental Validation，pp.6、19–22，Table 1]

| 样本范围 | 报告结果 |
|---|---|
| 11 个主要性质 | 每项 $n\in\{6,10,14,20,25\}$，三种边密度，每组四张图，共 60 图、900 顶点查询 |
| 两个较大组合性质 | 每项仅 $n=5$，六张图、30 顶点查询 |
| 总计 13 个性质 | 9,960 次顶点查询，0 mismatches，按设计为 672 次图样本 |
| 最大词表 | 两个缩小测试的性质均为 64 个元素 |
| 答案分布 | 12 项有真有假，`combined_three_way` 的 30 个查询全部为假 |

图是排除自环的随机有向图，原子命题独立 Bernoulli 标记，采样密度按性质调整。覆盖独立 blocks 的顶层组合及同极性嵌套，深度至 3。9,960 不是独立图数，也不是学习任务测试准确率。

两个 64 状态系统因方程规模及朴素 Kleene 求值成本而缩小图规模。作者给出的成本形态是轮数约 $|\mathcal V|n$，再乘总方程大小和集合运算成本。原文没有逐项硬件、编译时间、峰值内存、训练 seeds、泛化划分或学习结果。其提到 frozen manifest，但本版没有打印具体 seed 整数，并表示代码及结果将在 final version 公开。本次没有核查外部当前 release，不能声称已经复现，也不能把“本版未附”写成“现在绝无代码”。

实证支持的是：证明中的寄存器构造、局部提取和符号重建已经被作者连成可运行流程，并在所测小型图上保持语义。零 mismatch 不能独立替代对所有图的证明，全部为假的组合项也没有检验其正例行为。从已训练网络抽取小而可读公式仍是论文明确保留的后续任务。

## 七、独立推论：有限词表把完整收缩变为统一精确停止证书

**归因。**下面直接使用原文 Contractive nets 证明中的 $\delta_{k+1}\le\lambda\delta_k$，再加入有限集合的最小分离。原文已证明收缩估计，未见其显式写出以下 $D/\Delta$ 界或一般有界模态深度结论。本笔记给出直接推论，不作新颖性声明。

假设第三节的**完整局部收缩**及聚合器 1-Lipschitz 条件成立，且词表 $\mathcal V$ 有限。无需 ordered 或 game monotonicity。若 $m>1$，用同一范数定义

$$
D=\max_{e,e'\in\mathcal V}\|e-e'\|,
\qquad
\Delta=\min_{e\ne e'\in\mathcal V}\|e-e'\|>0.
$$

冻结固定点满足，令 $a=\|F_\alpha(S)-F_\alpha(S')\|$、$b=\|\oplus S-\oplus S'\|$，

$$
a\le\lambda\max(a,b)\quad\Longrightarrow\quad a\le\lambda b.
$$

同图相应邻居的 1-Lipschitz 性给出

$$
\delta_k:=\max_u\|E_u^k-\Phi_u\|,
\qquad \delta_{k+1}\le\lambda\delta_k.
$$

初始化 $E^0\in\mathcal V$，表的闭包保证每轮仍在 $\mathcal V$。原文收缩定理先给出 admissibility，再由有限词表闭合得到 $\Phi_u\in\mathcal V$，所以 $\delta_0\le D$。依赖链并未预先假设待证的有限停止。于是

$$
\delta_k\le\lambda^kD.
$$

一旦 $\lambda^kD<\Delta$，任何不相等的 $E_u^k,\Phi_u$ 都会违反最小距离，因此全图已精确等于极限。可取

$$
\boxed{K=\left\lfloor\frac{\log(D/\Delta)}{\log(1/\lambda)}\right\rfloor+1.}
$$

若 $m=1$，取 $K=0$。$K$ 只依赖固定网络和词表，不依赖图大小。严格不等式解释了整数界的加一。

进一步，第零轮状态只依赖节点类型。递归定义精确状态公式

$$
\chi_i^{k+1}=
\bigvee_{T(\alpha,S)=e_i}
\left[\alpha\land
\bigwedge_{e_j\in S}\Diamond\chi_j^k\land
\Box\!\left(\bigvee_{e_j\in S}\chi_j^k\right)\right].
$$

空集项按 $\bigvee\varnothing=\bot$、$\bigwedge\varnothing=\top$ 解释。每轮增加至多一层模态深度。因此任意极限读出 $h$ 都有**无固定点、模态深度至多 $K$**的公式。

这提供两项具体用途：给完整收缩且有限词表的局部规则一个对所有图统一的精确 game 停止预算，或者在需要无界距离 reachability 时直接识别这组联合假设的适用范围。它不排除非收缩的 Boolean propagator，也不排除只有 self-contraction 的原文第二例。$\Delta$ 很小时预算仍可很大，求出精确词表与分离值仍有成本。原实数 transient 可以只渐近收敛，推论不把它改写成 $K$ 步精确停机。

## 八、表达边界与后续可用工具

原文 Barrier 命题只需 regular、有限词表、admissible，甚至不要求 ordered 或 monotone，便排除 $\nu Y.\Diamond Y$、$\mu X.\Box X$、$\mathrm{EG}\,p$ 和 $\mathrm{EF\,EG}\,p$ 的全图实现。其证明固定一种类型，令 $t_0=T(\alpha,\varnothing)$、$t_{k+1}=T(\alpha,\{t_k\})$。有向长路径的头部极限为 $t_k$，单自环的 game 是同一序列。有限词表加 admissibility 强迫后者最终常数，因此足够长路径和自环得到同一 embedding，却要求不同无限路径答案。[Barrier，`prop:barrier`，pp.18–19]

这个结论为特定查询给出边界，不能单独完成更宽类的全部逻辑分类。见证依赖有向图，自环和路径的差异在无向图上不能原样使用。与计数、显式 halting signal 或 graph-size 输入的其他 recurrent GNN 定理比较时，必须保留这些计算接口差别。

可带入后续文献比较的具体工具为：冻结邻居的局部求解器、有限词表闭包、正见证规则、独立 core blocks 与外围读出、共享固定点方程求值，以及第七节的精确停止证书。有限词表不是由训练数据自动发现的状态，逻辑到网络也不是从残差获得新操作的学习算法。把任何一个对象用作 FP 核心状态仍需 Astra 给出具体对象映射、获取规则与成本，本笔记不修改核心定义或研究路线。

## 覆盖与证据结论

**完整阅读**仅记此 v1 的 22 页。构造、定理及 Barrier 按原文来源记录，关键接口经过有界数学核查。第七节是明确假设下的独立直接推论。实验数字是作者报告，没有模型或代码复现。相关工作中的 Bollen、Rosenbluth–Grohe、Wittig 等引用只作为本篇的比较线索，不因出现在参考文献中获得全文阅读信用。

# Gap-Hamming communication lower bound — scoped dependency

## Source and reading boundary

**Amit Chakrabarti and Oded Regev, An Optimal Lower Bound on the Communication Complexity of Gap-Hamming-Distance.** The inspected source is [arXiv 1009.3460v3](https://arxiv.org/abs/1009.3460v3), submitted June 29, 2012, [20-page PDF](https://arxiv.org/pdf/1009.3460v3). The title page's October 24, 2018 date is a later typesetting date, not a new arXiv version.

The work appeared in [STOC 2011, pp. 51–60](https://doi.org/10.1145/1993636.1993644), and [SIAM Journal on Computing 41(5), pp. 1299–1317](https://doi.org/10.1137/120861072), online October 25, 2012. Publisher metadata was authenticated. The formal ACM and SIAM PDFs returned 403 in this environment. The available author and arXiv manuscripts are not silently identified with the journal typesetting.

**Scoped reading only, November 25, 2026.** The purpose is to identify the exact theorem and protocol model cited by Astra's communication result in 97fef68. Root read the problem definition and informal theorem, all of §2.1, the beginning of §2.2, Theorems 2.6–2.7 and their immediate surrounding text, and Proposition 4.4 with its proof. These are TeX spans 150–193, 418–490, 690–730 and 1290–1338. Original PDF pages 2, 5, 9 and 16 were visually inspected, including their nearby text. PDF page 1 is an unnumbered title, so these correspond to printed pages 1, 4, 8 and 15. The main Gaussian/corruption proof, most reductions and complete references remain unread. No full-reading or full-proof-verification claim is made.

## Exact model and theorem

Alice receives \(x\in\{0,1\}^n\) and Bob receives \(y\in\{0,1\}^n\). The partial function \(\mathrm{GHD}_{n,t,g}\) requires output 0 when

\[
\Delta(x,y)\le t-g
\]

and output 1 when

\[
\Delta(x,y)>t+g.
\]

Either output is permitted in the remaining gap. The source's upper side uses a strict inequality. [Definition in §1, printed p. 1]

Section 2.1 defines randomized error by a guarantee for **every promised input pair**, with probability over the protocol's randomness. Communication cost is the **worst-case total number of communicated bits**. The notation \(R(f)\) means error at most \(1/3\). The protocol class has no restriction to one message or a fixed number of rounds. Public randomness is permitted, as is explicit in the upper-bound protocol of Proposition 4.4.

**Theorem 2.6, printed p. 8 / PDF p. 9:**

\[
R\!\left(\mathrm{GHD}_{n,n/2,\sqrt n}\right)=\Omega(n).
\]

This supplies a randomized interactive communication lower bound. It does not directly count local work, storage, raw observations, public random bits or the cost of a learned prediction table. It is a theorem for a promised decision problem, rather than a prediction-loss theorem.

Theorem 2.7 is separate: there is a sufficiently small absolute error constant for which the uniform independent input distribution is hard. Its distributional error convention counts errors on promised inputs and is not the conditional error given the promise. Its stated constant is not automatically \(1/3\). The current citation to Theorem 2.6 does not require importing this stronger distributional statement.

## General gaps and a bounded endpoint observation

Proposition 4.4 prints

\[
R(\mathrm{GHD}_{n,n/2,g})
=\Theta\!\left(\min\{n,n^2/g^2\}\right).
\]

Its upper construction uses shared random coordinates, with Alice sending the selected bits to Bob. Its lower argument scales a central instance by repeating coordinates. The printed proof explicitly suppresses divisibility details.

The proposition's literal printed range is \(1\le g\le n\). That range includes a degenerate region: if \(g>n/2\), neither required-output set contains an input, and zero communication suffices. Thus the displayed two-sided formula should not be imported over that entire literal range. This elementary endpoint observation is independent of the main proof and does not challenge the large-\(n\), \(g=\sqrt n\) theorem used by Astra.

## What this lookup establishes

The citation supports a worst-case bit lower bound for arbitrary two-party randomized protocols on separated strings, including interactive protocols. A reduction to conditional KL, conditional TV or joint TV must separately exhibit the data map, decision threshold, success probability, and all communication used to release or evaluate predictions. Those are properties of the reduction, not conclusions stated by this source.

This lookup does not certify or modify Astra's reduction. It also supplies no lower bound for a chronological observer who can reconstruct the other tape locally, nor for a promised low-description-length clean rule under sparse corruption. No broader historical survey, full proof reconstruction or formal replay was undertaken.

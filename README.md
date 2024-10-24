SySeVR: A Framework for Using Deep Learning to Detect Vulnerabilities
=


Zhen Li, Deqing Zou, Shouhuai Xu, Hai Jin, Yawei Zhu, Zhaoxuan Chen. [SySeVR: A Framework for Using Deep Learning to Detect Software Vulnerabilities](https://arxiv.org/abs/1807.06756). IEEE Transactions on Dependable and Secure Computing (TDSC). 2021, 19(4): 2244-2258.  

---

We propose a general framework for using deep learning to detect vulnerabilities, named SySeVR. For evaluate the SySeVR, we collect the Semantics-based Vulnerability Candidate (SeVC) dataset, which contains all kinds of vulnerabilities that are available from the National Vulnerability Database (NVD) and the Software Assurance Reference Dataset (SARD).

At a high level, the SyVC representation corresponds to a piece of code in a program that may be vulnerable based on a syntax analysis. The SeVC representation corresponds to the extended statements of the SyVCs, with the extension to incorporate some of the other statements that are semantically related to the SyVCs.

SeVC dataset focuses on 1,591 open source C/C++ programs from the NVD and 14,000 programs from the SARD. It contains 420,627 SeVCs, including 56,395 vulnerable SeVCs and 364,232 SeVCs that are not vulnerable. Four types of SyVCs are involved.

1. Library/API Function Call : This accommodates the vulnerabilities that are related to library/API function calls.
2. Array Usage: This accommodates the vulnerabilities that are related to arrays (e.g., improper use in array element access, array address arithmetic, address transfer as a function parameter).
3. Pointer Usage: This accommodates the vulnerabilities that are related to pointers (e.g., improper use in pointer arithmetic, reference, address transfer as a function parameter).
4. Arithmetic Expression: This accommodates the vulnerabilities that are related to improper arithmetic expressions (e.g., integer overflow).



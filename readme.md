# 3D-IC Partitioning

> 3D IC Partitioning Technique Design Based on HEVC Motion Estimation Module.

*2016 Excellent graduate thesis in Department of Micro-Nano Electronics, Shanghai Jiao Tong University* 

### Abstract

In this paper, a 3D IC partitioning algorithm is designed for the motion estimation module of HEVC.  Including the initial partition algorithm based on BFS and the iterative optimization algorithm. And for HEVC motion estimation module, design a 3D IC partitioning algorithm evaluation platform, the main functions include parsing circuit file, comprehensive analysis of DC area report, the establishment of hypergraph data structure to describe unit circuit interconnection relations, the hierarchy structure of motion stimation circuit module according to the size of the module distribution was launched down, a variety of ways to generate an initial partition, applying partition algorithm and classification of the results of the assessment. The IDCT module and ME module using the design of three-dimensional integrated circuit partitioning algorithm is partitioned, from the number of cut edges, area utilization, and other aspects of the evaluation of the partition results. 

### Usage

- hevc/: working directory for the HEVC motion estimation module partition job.
- hevc/N_layer_partition.py: perform partition algorithm for HEVC motion estimation module to N layer 3D IC implementation, taking "area_report.rpt" (module area report after design complier synthesize) and "me_full.ast" (HEVC motion estimation circuit file) as input.
- partition.sh: parsing circuit file
- fm_partition.py: full implementation of several partitioning algorithms and evaluation platform. It is not the final version used in partitioning job.
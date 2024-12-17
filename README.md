**Supplementary material to the article:**

## AGGA - A method for automated algorithm configuration of anytime algorithms
<br>

### Configuration scenarios

We tested our approach on the following algorithms:

+ **[Loandra](https://github.com/jezberg/loandra):** Version 1.0 [1]  
+ **[WBO](https://github.com/sbjoshi/Open-WBO-Inc):** [2]  
+ **[HGS]( https://github.com/vidalt/HGS-CVRP/):** Version: 2.0.0 [3]  
+ **[CPLEX](https://www.ibm.com/products/ilog-cplex-optimization-studio):** Version: 22.1.1.0 [4]  

Each configuration scenario contains:  
+ Parameter files for AGGA, PyDGGA [5], irace [6], and SMAC [7];  
+ Training and test instance files;  
+ Reference quality used to compute the hypervolume as feedback;  
+ Scenario files;  
+ Files used to run the target algorithms.  

***

### Get the instances

Instances can be obtained from:
+ CVRP [8] - in this repository  
+ MIP[9]  - in this repository  
+ [MaxSAT](http://www.cs.toronto.edu/maxsat-lib/maxsat-instances/master-set/unweighted/) [10]  

### References

[1] Berg, J., Demirović, E., and Stuckey, P. J. (2019). Core-boosted linear search for incomplete MaxSAT. In Integration of Constraint Programming, Artificial Intelligence, and Operations Research, pages 39–56. Springer.

[2] Nadel, A. (2018). Solving MaxSAT with bit-vector optimization. In Theory and Applications of Satisfiability Testing, pages 54–72. Springer.

[3] Vidal, T., Crainic, T. G., Gendreau, M., Lahrichi, N., and Rei, W. (2012). A hybrid genetic algorithm for multidepot and periodic vehicle routing problems. Operations Research, 60(3):611–624.

[4] IBM (2022). ILOG CPLEX optimization studio 22.1.1: User’s manual.

[5] Ansótegui, C., Pon, J., Sellmann, M., and Tierney, K. (2021). PyDGGA: Distributed GGA for automatic configuration. In Theory and Applications of Satisfiability Testing - SAT, volume 12831 of Lecture Notes in Computer Science, pages 11–20. Springer.

[6] López-Ibáñez, M., Dubois-Lacoste, J., Leslie, P. C., Birattari, M., and Stützle, T. (2016). The irace package: Iterated racing for automatic algorithm configuration. Operations Research Perspectives, 3:43–58.

[7] Lindauer, M., Eggensperger, K., Feurer, M., Biedenkapp, A., Deng, D., Benjamins, C., Sass, R., and Hutter, F. (2021). SMAC3: A versatile bayesian optimization package for hyperparameter optimization. CoRR, abs/2109.09831.

[8] Kool, W., van Hoof, H., and Welling, M. (2019). Attention, Learn to Solve Routing Problems! In International Conference on Learning Representations, ICLR.

[9] Merschformann, M. (2024). SardineCan. https://github.com/merschformann/sardine-can, commit fa7ccc7.

[10] Bacchus, F., Berg, J., Järvisalo, M., and Martins, R. (2020). MaxSAT evaluation 2020: Solver and benchmark descriptions.

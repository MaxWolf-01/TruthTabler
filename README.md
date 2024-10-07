Visualizations of circuits made possible by [Lelleck](https://github.com/Lelleck).

###### Features

- Solve any boolean expression and create CCNF(POS), CDNF(SOP) 
- Minimize expressions using the [Quine-McCluskey algorithm](https://en.wikipedia.org/wiki/Quine%E2%80%93McCluskey_algorithm).
- Convert boolean expressions to only use NAND or NOR gates and draw them. 

###### Setup & Usage

```bash
git clone --depth 1 https://github.com/MaxWolf-01/TruthTabler.git
pip install -r requirements.txt
cd src && python main.py
```

In modes with multiple available commands, type `?` to show them. Go to the previous mode by typing `exit`.
If prompted to enter variables, enter them as a string without seperators (e.g. `abc`).
The availabe operator symbols for entering an expression can be found [here](https://github.com/MaxWolf-01/TruthTabler/blob/e3fccb9353ce026887685b35ee6b030fdbd1b247/src/operator_symbols.py#L3-L10)

###### Examples

Solving an expression:

![example1](https://github.com/MaxWolf-01/TruthTabler/blob/master/example1.png)

NAND/NOR conversion:

![example2](https://github.com/MaxWolf-01/TruthTabler/blob/master/example2.png)

The above expression with only NAND gates:

![example3](https://github.com/MaxWolf-01/TruthTabler/blob/master/example3.png)

The above expression with only NOR gates:

![example4](https://github.com/MaxWolf-01/TruthTabler/blob/master/example4.png)


> [!WARNING] 
> - This old and ugly code from my early days of programming - it works, but there are bugs like saving the circuits does not work on windows.
> - Minimization for expressions with 7 variables and beyond may take some time (and memory), since it has exponential complexity (and the code is not optimized).

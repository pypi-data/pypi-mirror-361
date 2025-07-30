![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white)
![PyPI](https://img.shields.io/badge/PyPI-3775A9?style=for-the-badge&logo=PyPI&logoColor=white)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)


The English version of the README.md file was created by a translator. Therefore, the translation may not be accurate. If you can use Korean, we recommend that you view the Korean document.
[한국어 문서 바로가기(korean)](https://github.com/yhg4908/ranpick.py/blob/main/README_KR.md)

# Ranpick
[![PyPI - Version](https://img.shields.io/pypi/v/ranpick)](https://pypi.org/project/ranpick)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ranpick)
[![PyPI Downloads](https://static.pepy.tech/badge/ranpick/month)](https://pepy.tech/projects/ranpick)
[![PyPI Downloads](https://static.pepy.tech/badge/ranpick)](https://pepy.tech/projects/ranpick)



Ranpick complements the shortcomings of the existing PRNG method and generates random numbers with nanoseconds and hash-based systems.


---



## Installation



1. Use 'pip' to install the ranpick:

   ```bash
   pip install ranpick
   ```
2. Add the import statement below to the code (.py) to import the ranpick:

   ```python
   from ranpick import (modules)
   ```



## Modules and Use Guides


As of `2024.12.22 (KST)`, the modules currently available are as follows.

- rannumber: `Produces a random number in the form of a number`
- ranrandom: `Select a random value from the list.` (2.1.0~)



### number - Generating a numeric random number


`Number` generates a random number in the form of a normal number.

You can generate numbers up to 0 ~ 1 (Supported from 3.0.0)



#### The basics



The number module can be used in the following ways.
```python
random_number = rannumber()  # random_number variable, store the random number (0 ~ 1) that is selected as the random number module.

print(random_number) # print_number The value of the variable random_number.
print(rannumber()) #rampicknumber Outputs the value of the random number drawn by the module.
```
This is the basic method of using the number module. You can generate random numbers with `rannumber()`.


#### Limiting the Number of Random Numbers



You can also limit the number of random numbers. The example code below limits random numbers to between 5 and 10.
```python
limit_number = rannumber(5, 10)

print(limit_number)
print(rannumber(5, 10))
```
`number(5, 10)` is a code that limits the number of random numbers to between 5 and 10. You can complete it by adding `starting numbers, arriving numbers` in `()`.

Calculations such as ' `2+3,10/2` can also be used to limit the number of random numbers and can be used in all the contents to be described later.


#### Set decimal place



By default, a generated random number can only be generated with integers. However, if you refer to the example below, you can output a small number of outputs.
```python
decimal_number = rannumber(0, 1, "d3")

print(decimal_number)
print(rannumber(0,1, "d3"))
```
This example code is a code that outputs numbers between 0 and 1 up to three decimal places. `"d3"` means that it outputs up to three decimal places.

If `"d4"` is used, it can be output up to four decimal places.

It can be up to 20 digits.(3.0.0~)


#### Application



The codes below are created by applying this module, other libraries, and modules. In addition to the examples used here, a variety of other libraries and applications are possible.

##### DataTime Library Application
Below is the code applied using the datetime library.
```python
import ranpick
from datetime import datetime

date_number = int(datetime.now().strftime("%Y%m%d%H%M%S"))

print(rannumber(date_number, date_number × 10))
```
This code was made to output random numbers by leveraging the time output from the datetime library.

### ranrandom - Random Value Selection
`ranrandom` selects and outputs a random value from a list.

#### Basic Usage
You can use the `ranrandom` module as shown below:
```python
random = ranrandom("left", "right", "center", "miss")

print(random)
print(ranrandom("left", "right", "center", "miss"))
```
You can use `ranrandom()`. Inside the parentheses, you can input items in a format such as `("win", "miss")`.
One of the items listed here will be randomly selected.
At least two items must be provided.

#### Setting Probabilities
You can set the probabilities for each item. Please refer to the example code below:
```python
random = ranrandom(("left", 33), ("right", 33), ("center", 33), ("miss", 1))

print(random)
print(ranrandom(("left", 33), ("right", 33), ("center", 33), ("miss", 1)))
```
You can add another pair of parentheses `()` inside the main `()`.
Within this added `()`, you can specify items in the format `("item_name", probability[%])`.
The total sum of all probabilities must equal 100, otherwise an error will occur.
```python
print(ranrandom("left", ("right", 50), "center", "miss"))
```
If some probabilities are omitted as shown above, the remaining probabilities will be automatically redistributed among the unspecified items.

#### Multiple selection (2.2.0~)
Of course, multiple selection is possible. Please follow the example below.
```python
random = ranrandom("a", "b", "c", "d", DS=2)

print(random)
```
This code selects 2 out of a, b, c, d and prints them. DS is in charge of how many to select and print.

If the value of DS is 2, 2 are selected from the list. If `DS=3`, 3 are selected and printed.
```r
a, d
```
It is printed like this.

##### Print in list form
Duplicated values ​​can also be printed in list form. 
```python
random = ranrandom("a", "b", "c", "d", DS=3, as_list=True)

print(random)
```
If you want to print in list format, use `as_list`. If you set the value of as_list to True and run it, it will print as follows.
```r
['b', 'c', 'a']
```

## Bug report


Please report bugs on the site below (github).

<https://github.com/yhg4908/ranpick.py/issues>

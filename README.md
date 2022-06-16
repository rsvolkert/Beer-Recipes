# Beer-Recipes
 
Uses a GAM to generate novel beer recipes.

Data sourced from [https://www.brewersfriend.com/](https://www.brewersfriend.com/).

## Usage

```python
from generate_recipe import model, generate_combos

# must specify Name, Style, Method, and temperatures iterable
## make an all-grain IPA called Lemon Drop
generate_combos(model, 'Lemon Drop', 'American IPA', 'All Grain', [0.2])
```

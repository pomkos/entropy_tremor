# Introduction

Calculate SamEn and ApEn of tremors measured with the KinesiaONE system

# Dependencies
The following libraries must be installed:
```
pandas
scypi
matplotlip
numpy
sampen
glob
os
sys
```

Download and install EntroPy as per the link: https://github.com/raphaelvallat/entropy

# Steps

1. Change line 25 to directory of EntroPy
2. Change line 37 to "pre" or "post", depending which you data is being analyzed
3. Change line 38 to "samen" or "apen", depending which entropy is being calculated
4. Run script. Files will be saved in the current directory
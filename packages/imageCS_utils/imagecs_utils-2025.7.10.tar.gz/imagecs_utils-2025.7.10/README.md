# ImageCS-Utils

<div align="center">

[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FFengodChen%2FimageCS-utils&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FFengodChen%2FimageCS-utils&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)
[![GitHub repo stars](https://img.shields.io/github/stars/FengodChen/imageCS-utils?style=flat&logo=github&logoColor=whitesmoke&label=Stars)](https://github.com/FengodChen/imageCS-utils/stargazers)

</div>

Some useful utils for deep learning (PyTorch) image compressive sensing (CS).

## Project Url

[pypi](https://pypi.org/project/imageCS-utils/)
[github](https://github.com/FengodChen/imageCS-utils)


## Install
```
python -m pip install imageCS-utils
```

## Usage
e.g.

```
import torch
from imageCS_utils.utils import load_single_image
x = load_single_image("./image.png")
```
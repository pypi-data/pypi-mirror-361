# jsw-pillow
> Pillow for jsw.

## installation
```shell
pip install jsw-pillow -U
```

## usage
- watermark

### Watermark
> Watermark 水印的基本生成API。

![Alt text](https://tva1.sinaimg.cn/large/008vxvgGgy1h7su9f3j8pj30uh0p6n1z.jpg)

```python
# watermark
from jsw_pillow import Watermark

# watermark - single
im1 = Watermark.multiple(
    source='./__tests__/assets/test.png',
    mark='js.work',
    font_size=50,
    angle=45,
    position='center',
    color=(0, 255, 0, int(255 * 0.5)),
)

# watermark - multiple
im2 = Watermark.multiple(
    source='./__tests__/assets/test.png',
    mark='js.work',
    font_size=50,
    angle=45,
    color=(0, 255, 0, int(255 * 0.5)),
)
```

## positions
> Only for single watermark.

![Alt text](https://tva1.sinaimg.cn/large/008vxvgGgy1h7u1m6nmvkj30gh0evt92.jpg)
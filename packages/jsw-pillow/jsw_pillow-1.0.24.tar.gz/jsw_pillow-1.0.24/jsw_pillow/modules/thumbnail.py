from PIL import Image
from resizeimage import resizeimage
from .std_source import std_source
from .converter import Converter


class Thumbnail:
    @classmethod
    def resize(cls, **kwargs):
        source = kwargs.pop('source')
        method = kwargs.pop('method', 'contain')
        size = kwargs.pop('size')
        target = kwargs.pop('target')
        save_mode = kwargs.pop('save_mode', 'file')

        std_src, is_str = std_source(source)
        im = Image.open(std_src)

        resized_im = resizeimage.resize(method, im, size, **kwargs)
        convert = getattr(Converter, save_mode)
        result = convert(resized_im, target=target)
        return resized_im, result

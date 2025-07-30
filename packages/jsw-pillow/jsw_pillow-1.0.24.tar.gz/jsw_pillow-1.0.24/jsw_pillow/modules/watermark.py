import os
import imghdr
from PIL import Image, ImageDraw, ImageFont
from .std_source import std_source
from .converter import Converter
from .get_position import get_position

# 原理在这里: https://stackoverflow.com/questions/62910445/watermarking-pasting-rotated-text-to-empty-image
"""
使用说明:
source: 源图片地址，这里只能是本地图片地址，如果是远程图片，请自行配合 requests 得到 content 结合 io.BytesIO
target: 处理好的图片地址，只有 save_mode = file 时才需要
text: 水印文字
font_family: 字体
font_size: 字号
color: 字体颜色
angle: 旋转角度
opacity: 透明度
save_mode: 保存模式，file 为保存到文件，base64 为返回 base64 编码, buffer 为返回 io.BytesIO 对象
"""


class Watermark:
    @classmethod
    def font_family(cls):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(dir_path, 'fonts', 'qnhghp.ttf')

    """
    @description: 生成水印图片，只有1个mark
    原文件 source = 'test.jpg'
    水印文字 text = 'js.work'
    字体名称 font_family = './fonts/ali_pht_heavy.otf'
    字号大小 font_size = 20
    """

    @classmethod
    def single(cls, **kwargs):
        source_image, rotated_text_image, watermarks_image, target, save_mode = cls._preprocess(**kwargs)

        source_image_size = source_image.size
        rotated_text_image_size = rotated_text_image.size
        debug = kwargs.get('debug', False)
        offset = kwargs.get('offset', (20, 20))
        position = kwargs.get('position', 'center')

        # 水印位置 center
        x, y = get_position(position, source_image_size, rotated_text_image_size, offset)
        watermarks_image.paste(rotated_text_image, (x, y), rotated_text_image)

        # 合并
        result = Image.alpha_composite(source_image, watermarks_image)
        result.save(target)

        # 水印空图中添加水印文字
        watermarks_image.paste(rotated_text_image, (x, y))

        # 原图与水印图合并
        combined_image = Image.alpha_composite(source_image, watermarks_image)

        return cls._postprocess(
            combined_image=combined_image,
            target=target,
            debug=debug,
            save_mode=save_mode,
        )

    """
    @description: 生成 repeat 方式的文字水印图
    """

    @classmethod
    def multiple(cls, **kwargs):
        source_image, rotated_text_image, watermarks_image, target, save_mode = cls._preprocess(**kwargs)

        source_image_size = source_image.size
        rotated_text_image_size = rotated_text_image.size
        debug = kwargs.get('debug', False)
        parts = kwargs.get('parts', 8)

        combined_image = source_image
        offset_x = source_image_size[0] // parts
        offset_y = source_image_size[1] // parts

        start_x = source_image_size[0] // parts - rotated_text_image_size[0] // 2
        start_y = source_image_size[1] // parts - rotated_text_image_size[1] // 2

        for a in range(0, parts, 2):
            for b in range(0, parts, 2):
                x = start_x + a * offset_x
                y = start_y + b * offset_y
                # image with the same size and transparent color (..., ..., ..., 0)
                watermarks_image = Image.new(
                    'RGBA', source_image_size, (255, 255, 255, 0))
                # put text in expected place on watermarks image
                watermarks_image.paste(rotated_text_image, (x, y))
                # put watermarks image on source image
                combined_image = Image.alpha_composite(
                    combined_image, watermarks_image)

        return cls._postprocess(
            combined_image=combined_image,
            target=target,
            debug=debug,
            save_mode=save_mode,
        )

    @classmethod
    def compose(cls, **kwargs):
        # background/foreground
        bg, _ = std_source(kwargs.get('bg'))
        fg, _ = std_source(kwargs.get('fg'))
        target = kwargs.get('target')
        opacity = kwargs.get('opacity', 1)
        position = kwargs.get('position', 'center')
        offset = kwargs.get('offset', (0, 0))
        save_mode = kwargs.get('save_mode', 'file')
        im_bg = Image.open(bg)
        im_fg = Image.open(fg)

        x, y = get_position(position, im_bg.size, im_fg.size, offset)

        # set opacity for im_fg
        im_fg_mask = im_fg.copy()
        im_fg.putalpha(int(opacity * 255))

        im_bg_res = im_bg.copy()
        im_bg_res.paste(im_fg, (x, y), im_fg_mask)

        convert = getattr(Converter, save_mode)
        return im_bg_res, convert(im_bg_res, target=target)

    @classmethod
    def _preprocess(cls, **kwargs):
        # 参数处理
        source, is_str = std_source(kwargs.get('source'))
        save_mode = kwargs.get('save_mode', 'file')  # FILE or BUFFER
        opacity = kwargs.get('opacity', 0.5)
        if save_mode == 'file':
            filename, ext = os.path.splitext(kwargs.get('source')) if is_str else ('tmp', '.jpg')
            target = kwargs.get('target', f'{filename}.watermark{ext}')
        else:
            target = kwargs.get('target', None)

        text = kwargs.get('text', 'js.work')
        font_family = kwargs.get('font_family', cls.font_family())
        font_size = kwargs.get('font_size', 20)
        color = kwargs.get('color', (255, 255, 255, int(255 * opacity)))
        angle = kwargs.get('angle', 45)

        # 打开原图
        file_type = imghdr.what(source)
        convert_type = 'RGBA' if file_type == 'png' else 'RGB'
        source_image = Image.open(source).convert(convert_type)
        source_image_size = source_image.size

        # 字体及 bound 信息
        font = ImageFont.truetype(font_family, font_size)
        _, _, *text_size = font.getmask(text).getbbox()

        # 计算水印位置
        text_image = Image.new('RGBA', text_size, (255, 255, 255, 0))
        text_draw = ImageDraw.Draw(text_image)
        text_draw.text((0, 0), text, color, font=font)

        # 旋转水印
        rotated_text_image = text_image.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0))
        watermarks_image = Image.new('RGBA', source_image_size, (255, 255, 255, 0))

        return source_image, rotated_text_image, watermarks_image, target, save_mode

    @classmethod
    def _postprocess(cls, **kwargs):
        # debug 模式下，输出水印图
        combined_image = kwargs.get('combined_image')
        target = kwargs.get('target')
        debug = kwargs.get('debug')
        save_mode = kwargs.get('save_mode')

        if debug:
            combined_image.show()

        # call class method
        convert = getattr(Converter, save_mode)
        result = convert(combined_image, target=target)
        return combined_image, result

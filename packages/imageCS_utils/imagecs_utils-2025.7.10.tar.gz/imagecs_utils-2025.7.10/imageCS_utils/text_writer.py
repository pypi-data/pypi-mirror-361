"""write text to cv image"""
import torch
import cv2 as cv
import numpy as np

def get_text_size(text, font, font_scale, thickness):
    """auto get text pixel size via font"""
    (text_size, baseline) = cv.getTextSize(
        text = text,
        fontFace = font,
        fontScale = font_scale,
        thickness = thickness
    )

    text_h = text_size[1] + baseline
    text_w = text_size[0]

    text_size = (text_w, text_h)

    return (text_size, baseline)

def draw_text(img, text, pos, font, font_scale, color, thickness, line_type):
    """draw text to img"""
    cv.putText(
        img = img, 
        text = text, 
        org = pos, 
        fontFace = font, 
        fontScale = font_scale, 
        color = color, 
        thickness = thickness, 
        lineType = line_type
)

def adaptive_scale(img_l, text_l, l_spacing):
    """auto get the scale of font"""
    scale = (img_l - l_spacing) / text_l
    return scale

def get_bound(img_l, text_l, l_spacing, draw_mode, scale=1.0):
    """
    mode 0: left or top
    mode 1: right or bottom
    mode 2: center
    """
    text_l = int(text_l * scale)
    # calculate bound
    if draw_mode == 0:
        text_small = l_spacing
    elif draw_mode == 1:
        text_small = (img_l-1) - l_spacing - text_l
    elif draw_mode == 2:
        assert l_spacing == 0
        img_l_center = (img_l-1) // 2
        text_l_center = (text_l-1) // 2
        text_small = img_l_center - text_l_center

    text_big = text_small + text_l

    return (text_small, text_big)

def get_draw_info(
        img_size, text, font, font_scale, thickness,
        w_mode, h_mode, w_spacing=0, h_spacing=0,
        adaptive_mode = False
    ):
    """get draw info"""
    assert w_mode in ["left", "right", "center"]
    assert h_mode in ["top", "bottom", "center"]

    mode_dict = dict(
        left = 0,
        top = 0,
        right = 1,
        bottom = 1,
        center = 2
    )

    (img_h, img_w) = img_size

    assert 0 <= w_spacing <= img_w
    assert 0 <= h_spacing <= img_h

    (text_size, baseline) = get_text_size(
        text = text,
        font = font,
        font_scale = font_scale,
        thickness = thickness
    )

    (text_w, text_h) = text_size

    if adaptive_mode:
        text_w_scale = adaptive_scale(
            img_l = img_w,
            text_l = text_w,
            l_spacing = w_spacing
        )
        text_h_scale = adaptive_scale(
            img_l = img_h,
            text_l = text_h,
            l_spacing = h_spacing
        )

        scale = min(text_w_scale, text_h_scale)
        baseline = round(baseline * scale / font_scale)
        font_scale = scale

    # (text_left, text_right)
    (text_left, _) = get_bound(
        img_l = img_w,
        text_l = text_w,
        l_spacing = w_spacing,
        draw_mode = mode_dict[w_mode],
        scale = font_scale
    )

    # (text_top, text_bottom)
    (_, text_bottom) = get_bound(
        img_l = img_h,
        text_l = text_h,
        l_spacing = h_spacing,
        draw_mode = mode_dict[h_mode],
        scale = font_scale
    )

    pos_w = text_left
    pos_h = text_bottom - baseline
    pos = (pos_w, pos_h)
    
    return (pos, font_scale)

class TensorTextWriter:
    """write text to an tensor type image"""
    def __init__(self, font=cv.FONT_HERSHEY_SIMPLEX, thickness=1, line_type=cv.LINE_AA) -> None:
        self.font = font
        self.thickness = thickness
        self.line_type = line_type
    
    def get_draw_img(self, img:torch.Tensor, text:str, color, font_scale, w_mode, h_mode, w_spacing, h_spacing, adaptive_mode):
        """using parmas to auto get an writed text img"""
        assert len(img.size()) == 3
        # (C, H, W)
        (_, img_h, img_w) = img.size()
        img_size = (img_h, img_w)

        img = img.permute(1, 2, 0).numpy()
        img = np.array(img)

        (pos, font_scale) = get_draw_info(
            img_size=img_size,
            text=text,
            font=self.font,
            font_scale=font_scale,
            thickness=self.thickness,
            w_mode=w_mode,
            h_mode=h_mode,
            w_spacing=w_spacing,
            h_spacing=h_spacing,
            adaptive_mode=adaptive_mode
        )

        draw_text(
            img=img,
            text=text,
            pos=pos,
            font=self.font,
            font_scale=font_scale,
            color=color,
            thickness=self.thickness,
            line_type=self.line_type
        )

        img = torch.from_numpy(img).permute(2, 0, 1)
        return img
    
    def get_draw_img_easy(self, img:torch.Tensor, text:str, color=1.0, w_mode="center", w_spacing=0):
        """using parmas to auto get an writed text img (simple some params)"""
        assert len(img.size()) == 3
        # (C, H, W)
        (img_c, _, _) = img.size()
        color = [color] * img_c

        img = self.get_draw_img(
            img = img,
            text = text,
            color = color,
            font_scale = 1,
            w_mode = w_mode,
            h_mode = "center",
            w_spacing = w_spacing,
            h_spacing = 0,
            adaptive_mode = True
        )

        return img
    
    def get_text_image(self, text:str, img_h:int, img_w:int, back_color=0.0, draw_type="easy", **kwargs):
        """
        directly return a text image with background, draw_type = "easy" or "norm"
        **kwargs if the kwargs of draw function
        """
        assert draw_type in ["easy", "norm"]
        img = torch.ones((1, img_h, img_w), dtype=torch.float32)
        img = img * back_color

        if draw_type == "easy":
            img = self.get_draw_img_easy(img, text, **kwargs)
        else:
            img = self.get_draw_img(img, text, **kwargs)
        
        return img

    
    def add_tag(self, image, text, ratio=0.3, background="white", pos="bottom"):
        """add text image to the image's top or bottom"""
        assert pos in ["top", "bottom"]
        assert background in ["white", "black"]
        assert len(image.size()) == 3

        text_list = text.split("\n")
        (_, img_h, _) = image.size()
        tag_h = int(img_h * ratio / len(text_list))

        tag_image_list = []
        for text in text_list:
            tag_image = torch.empty_like(image)[:, :tag_h, :]
            if background == "white":
                tag_image[:, :, :] = 0.0
                text_color = 1.0
            elif background == "black":
                tag_image[:, :, :] = 1.0
                text_color = 0.0
        
            tag_image = self.get_draw_img_easy(tag_image, text, color=text_color)
            tag_image_list.append(tag_image)

        if pos == "top":
            tagged_image = torch.cat(tag_image_list + [image], dim=1)
        elif pos == "bottom":
            tagged_image = torch.cat([image] + tag_image_list, dim=1)
        
        return tagged_image

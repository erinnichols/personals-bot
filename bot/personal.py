#!/bin/python3
import hashlib
import re
import textwrap
from PIL import Image, ImageFont, ImageDraw
from random import choice, random
from textgenrnn import textgenrnn
from bot.filters import NoPadPunctuation, RightPadPunctuation, LeftPadPunctuation, MaybePluralParens, Ellip, \
    SentenceCase, TitleCase, AllCaps


class PostConfig(object):
    START_X = 100
    START_Y = 200
    START_COORDS = (START_X, START_Y)
    IMAGE_SIZE = (750, 936)
    FONTS = {
        'heading': {
            'family': '/Library/Fonts/Courier New Bold.ttf',
            'size': 32,
            'color': 'rgb(0, 0, 0)',
            # 'color': 'rgb(255, 255, 255)'
        },
        'body': {
            'family': '/Library/Fonts/Courier New.ttf',
            'size': 32,
            'color': 'rgb(0, 0, 0)',
            # 'color': 'rgb(255, 255, 255)'
        },
        'spacing': 10
    }
    BACKGROUND = [
        (0, 255, 255),   # cyan
        (244, 254, 253), # extremely light cyan
        # (41, 102, 198),  # blue
    ]

    @staticmethod
    def get_body_start_coords(heading_lines):
        return (
            PostConfig.START_X,
            PostConfig.START_Y + (
                (PostConfig.FONTS['heading']['size'] + PostConfig.FONTS['spacing'] + 2) * (heading_lines + 1)
            )
        )

class Personal(object):
    def __init__(self, heading, body, handle, location):
        self._heading = heading.strip()
        self._body = body.strip()
        self._handle = handle.strip()
        self._location = location.strip()

    @property
    def heading(self):
        return '\n'.join(textwrap.wrap(self._heading, 24))

    @property
    def body(self):
        filters = [NoPadPunctuation, RightPadPunctuation, LeftPadPunctuation, MaybePluralParens, Ellip]
        if random() > .1:
            filters.append(SentenceCase)
        if random() > .2:
            filters += [TitleCase, AllCaps]
        b = self._body
        for filter in filters:
            b = filter(b).apply()
        return '\n'.join(textwrap.wrap(b, 30))

    @property
    def handle(self):
        return self._handle

    @property
    def location(self):
        return '\n'.join(textwrap.wrap(self._location, 30))

    @property
    def identifier(self):
        m = hashlib.md5()
        m.update(self._heading.encode('utf-8'))
        m.update(self._body.encode('utf-8'))
        m.update(self._handle.encode('utf-8'))
        m.update(self._location.encode('utf-8'))
        return m.hexdigest()

    def preview(self):
        print('\033[1m')
        print(self.heading, '\033[0m')
        print(self.body)
        print(self.handle)
        print(self.location)

    def save_ad(self):
        bgcolor = choice(PostConfig.BACKGROUND)
        image = Image.new('RGB', PostConfig.IMAGE_SIZE, color=bgcolor)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(
            PostConfig.FONTS['heading']['family'],
            PostConfig.FONTS['heading']['size']
        )
        (x, y) = PostConfig.START_COORDS
        color = PostConfig.FONTS['heading']['color']
        draw.text(
            (x, y),
            self.heading,
            fill=color,
            font=font,
            spacing=PostConfig.FONTS['spacing']
        )
        (x, y) = PostConfig.get_body_start_coords(self.heading.count('\n'))
        font = ImageFont.truetype(PostConfig.FONTS['body']['family'], PostConfig.FONTS['body']['size'])
        draw.text(
            (x, y),
            '{body}\n{handle}\n{location}\n'.format(
                body=self.body,
                handle=self.handle,
                location=self.location
            ),
            fill=PostConfig.FONTS['body']['color'],
            font=font,
            spacing=PostConfig.FONTS['spacing']
        )
        filename = 'ads-draft/personal-%s.png' % self.identifier
        image.save(filename)


def write_ads(n=1, heading_temp=.5, handle_temp=1.5, location_temp=.6, body_temp=.6):
    textgen_headings = textgenrnn(
        weights_path='models/headings_weights.hdf5',
        vocab_path='models/headings_vocab.json',
        config_path='models/headings_config.json'
    )
    textgen_bodies = textgenrnn(
        weights_path='models/bodies0_weights.hdf5',
        vocab_path='models/bodies0_vocab.json',
        config_path='models/bodies0_config.json'
    )
    textgen_handles = textgenrnn(
        weights_path='models/handles_weights.hdf5',
        vocab_path='models/handles_vocab.json',
        config_path='models/handles_config.json'
    )
    textgen_locations = textgenrnn(
        weights_path='models/locations_weights.hdf5',
        vocab_path='models/locations_vocab.json',
        config_path='models/locations_config.json'
    )

    headings = textgen_headings.generate(n, return_as_list=True, temperature=heading_temp)
    handles = textgen_handles.generate(n, return_as_list=True, temperature=handle_temp)
    locations = textgen_locations.generate(n, return_as_list=True, temperature=location_temp)
    bodies = textgen_bodies.generate(n, return_as_list=True, temperature=body_temp)

    for i in range(n):

        h = re.sub(r'^.*?@(.*?)$', r'\1', handles[i])
        url = 'https://www.instagram.com/%s' % h
        print(url)

        ad = Personal(headings[i], bodies[i], handles[i], locations[i])
        ad.preview()
        ad.save_ad()

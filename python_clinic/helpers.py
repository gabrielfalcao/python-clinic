#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

# thanks docker!
# https://github.com/docker/docker/blob/ab31d950/pkg/namesgenerator/names-generator.go
adjectives = [
    "admiring",
    "adoring",
    "agitated",
    "amazing",
    "angry",
    "awesome",
    "big",
    "clever",
    "compassionate",
    "determined",
    "distracted",
    "dreamy",
    "drunk",
    "ecstatic",
    "elated",
    "elegant",
    "fervent",
    "focused",
    "furious",
    "gigantic",
    "gloomy",
    "happy",
    "high",
    "nerdy",
    "dorky",
    "dope",
    "speedy",
    "hopeful",
    "hungry",
    "insane",
    "loving",
    "mad",
    "naughty",
    "pensive",
    "reverent",
    "romantic",
    "serene",
    "sharp",
    "silly",
    "exuberant",
    "small",
    "stoic",
    "stupefied",
    "tender",
    "thirsty",
    "trusting",
]

last_names = [
    'http',
    'tcp',
    'server',
    'api',
    'service',
    'restful',
    'concurrency',
    'scalable',
]


def generate_name(char='-'):
    return char.join([random.choice(adjectives), random.choice(last_names)])


class fake:
    @staticmethod
    def project_name():
        return generate_name('_')

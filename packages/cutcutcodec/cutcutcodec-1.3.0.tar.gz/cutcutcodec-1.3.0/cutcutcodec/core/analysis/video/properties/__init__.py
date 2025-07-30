#!/usr/bin/env python3

"""Recover basic video information."""

from .duration import get_duration_video
from .nb_frames import get_nb_frames
from .rate import get_rate_video
from .timestamps import get_timestamps_video


__all__ = ["get_duration_video", "get_nb_frames", "get_rate_video", "get_timestamps_video"]

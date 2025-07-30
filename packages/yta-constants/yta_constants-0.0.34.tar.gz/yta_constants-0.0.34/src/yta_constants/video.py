from yta_constants.enum import YTAEnum as Enum


class VideoCombinatorAudioMode(Enum):
    """
    The mode in which the audio of the videos
    must be handled when combining them.
    """

    BOTH_CLIPS_AUDIO = 'both_clips_audio'
    """
    Both, the main clip and the added clip audios 
    are preserved.
    """
    ONLY_MAIN_CLIP_AUDIO = 'only_main_clip_audio'
    """
    Only the main clip audio is preserved. The one
    from the added clip is not included.
    """
    ONLY_ADDED_CLIP_AUDIO = 'only_added_clip_audio'
    """
    Only the added clip audio is preserved. The one
    from the main clip is not included.
    """

class ExtendVideoMode(Enum):
    """
    The strategy to follow when extending 
    the duration of a video.
    """

    LOOP = 'loop'
    """
    The video will loop (restart from the
    begining) until it reaches the 
    expected duration.
    """
    FREEZE_LAST_FRAME = 'freeze_last_frame'
    """
    Freeze the last frame of the video and
    repeat it until it reaches the 
    expected duration.
    """
    SLOW_DOWN = 'slow_down'
    """
    Change the speed of the video by
    deccelerating it until it reaches the
    expected duration.

    This mode changes the whole video
    duration so the result could be
    unexpected. Use it carefully.
    """
    BLACK_TRANSPARENT_BACKGROUND = 'black_background'
    """
    Add a black and transparent background
    clip the rest of the time needed to
    fulfil the required duration. This is
    useful when we need to composite
    different clips with different 
    durations so we can force all of them
    to have the same.
    """

class EnshortVideoMode(Enum):
    """
    The strategy to follow when enshorting 
    the duration of a video.
    """
    
    CROP = 'crop'
    """
    Remove the last part of the clip until
    it fits the expected duration.
    """
    SPEED_UP = 'speed_up'
    """
    Speed the video up to fit the expected
    duration. Good option for transitions.

    This mode changes the whole video
    duration so the result could be
    unexpected. Use it carefully.
    """

class MoviepyFrameMaskingMethod(Enum):
    """
    The method to be used when transforming
    a moviepy normal video frame into a
    moviepy mask video frame.
    """

    MEAN = 'mean'
    """
    Calculate the mean value of the RGB pixel color
    values and use it as a normalized value between
    0.0 and 1.0 to set as the transparency.
    """
    PURE_BLACK_AND_WHITE = 'pure_black_and_white'
    """
    Apply a threshold and turn pixels into pure black
    and white pixels, setting them to pure 1.0 or 0.0
    values to be completely transparent or opaque.
    """

    # We don't want functionality here to
    # to avoid dependencies.
    # def to_mask_frame(
    #     self,
    #     frame: np.ndarray
    # ):
    #     """
    #     Process the provided video normal 'frame'
    #     according to this type of masking
    #     processing method and turns it into a frame
    #     that can be used as a mask frame.
    #     """
    #     frame = ImageParser.to_numpy(frame)

    #     if not MoviepyVideoFrameHandler.is_normal_frame(frame):
    #         raise Exception('The provided "frame" is not actually a moviepy normal video frame.')

    #     return {
    #         FrameMaskingMethod.MEAN: np.mean(frame, axis = -1) / 255.0,
    #         FrameMaskingMethod.PURE_BLACK_AND_WHITE: pure_black_and_white_image_to_moviepy_mask_numpy_array(frame_to_pure_black_and_white_image(frame))
    #     }[self]

class ResizeMode(Enum):
    """
    The strategies we can apply when
    resizing a video.
    """

    RESIZE_KEEPING_ASPECT_RATIO = 'resize_keeping_aspect_ratio'
    """
    Resize the video to fit the expected
    larger size by keeping the aspect
    ratio, that means that a part of the
    video can be lost because of cropping
    it.
    """
    RESIZE = 'resize'
    """
    Resize the video to fit the expected
    larger size by keeping not the aspect
    ratio, so the whole video will be
    visible but maybe not properly. Use
    another option if possible.
    """
    FIT_LIMITING_DIMENSION = 'fit_limiting_dimension'
    """
    Resize the video to fit the most
    limiting dimension and it is placed
    over a black background of the
    expected size.
    """
    BACKGROUND = 'background'
    """
    The video is just placed over a black
    background clip, in the center. The
    background has the expected dimensions.
    This will work exactly as the
    FIT_LIMITING_DIMENSION if the video
    provided is larger than the expected
    size.
    """
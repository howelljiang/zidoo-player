"""Support for interface with Zidoo Media Player."""
import logging

from .zidoorc import ZidooRC, ZCONTENT_MUSIC, ZCONTENT_VIDEO
import voluptuous as vol

from homeassistant.components.media_player import PLATFORM_SCHEMA, MediaPlayerEntity
from homeassistant.components.media_player.const import (
    SUPPORT_BROWSE_MEDIA,
    SUPPORT_CLEAR_PLAYLIST,
    SUPPORT_NEXT_TRACK,
    SUPPORT_PAUSE,
    SUPPORT_PLAY,
    SUPPORT_PLAY_MEDIA,
    SUPPORT_PREVIOUS_TRACK,
    SUPPORT_SEEK,
    SUPPORT_SELECT_SOURCE,
    SUPPORT_SELECT_SOUND_MODE,
    SUPPORT_SHUFFLE_SET,
    SUPPORT_STOP,
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
    SUPPORT_VOLUME_MUTE,
    SUPPORT_VOLUME_SET,
    SUPPORT_VOLUME_STEP,
    MEDIA_TYPE_MUSIC,
    MEDIA_TYPE_TVSHOW,
    MEDIA_TYPE_MOVIE,
    MEDIA_TYPE_APP,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    STATE_IDLE,
    STATE_OFF,
    STATE_PAUSED,
    STATE_PLAYING,
)
from .const import (
    DOMAIN,
    _LOGGER,
    CLIENTID_PREFIX,
    CLIENTID_NICKNAME,
)

import homeassistant.helpers.config_validation as cv

from homeassistant.util.dt import utcnow
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.helpers.network import is_internal_request

from .media_browser import browse_media  # build_item_response, library_payload

DEFAULT_NAME = "Zidoo Media Player"

SUPPORT_ZIDOO = (
    SUPPORT_VOLUME_STEP
    | SUPPORT_VOLUME_MUTE
    | SUPPORT_TURN_ON
    | SUPPORT_TURN_OFF
    | SUPPORT_SELECT_SOURCE
    | SUPPORT_BROWSE_MEDIA
    | SUPPORT_SEEK
)
# SUPPORT_CLEAR_PLAYLIST # SUPPORT_SEEK # SUPPORT_SELECT_SOUND_MODE # SUPPORT_SHUFFLE_SET # SUPPORT_VOLUME_SET

SUPPORT_MEDIA_MODES = (
    SUPPORT_PAUSE
    | SUPPORT_STOP
    | SUPPORT_PREVIOUS_TRACK
    | SUPPORT_NEXT_TRACK
    | SUPPORT_PLAY
    | SUPPORT_PLAY_MEDIA
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Add Media Player form configuration."""

    _LOGGER.warning(
        "Loading zidoo via platform config is deprecated, it will be automatically imported; Please remove it afterwards"
    )

    config_new = {
        CONF_NAME: config[CONF_NAME],
        CONF_HOST: config[CONF_HOST],
    }

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=config_new
        )
    )


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add Media Player from a config entry."""

    player = ZidooRC(config_entry.data[CONF_HOST])

    async_add_entities([ZidooPlayerDevice(hass, player, config_entry)])

class ZidooPlayerDevice(MediaPlayerEntity):
    """Representation of a Zidoo Media."""

    def __init__(self, hass, player, config_entry):
        """Initialize the Zidoo device."""

        self._player = player
        self._hass = hass
        self._name = config_entry.title
        self._unique_id = config_entry.entry_id
        self._state = STATE_OFF
        self._muted = False
        self._source = None
        self._source_list = []
        self._content_mapping = {}
        self._playing = False
        self._media_type = None
        self._media_info = {}
        self._min_volume = None
        self._max_volume = None
        self._volume = None
        self._last_update = None
        self._config_entry = config_entry

        # response = self._player.connect(CLIENTID_PREFIX, CLIENTID_NICKNAME)
        # if response is not None:
        #    self.update()
        # else:
        #    self._state = STATE_OFF

    def update(self):
        """Update TV info."""
        if not self._player.is_connected():
            if self._player.get_power_status() != "off":
                self._player.connect(CLIENTID_PREFIX, CLIENTID_NICKNAME)
            if not self._player.is_connected():
                return

        # Retrieve the latest data.
        try:
            power_status = self._player.get_power_status()
            if power_status == "on":
                self._state = STATE_PAUSED
                playing_info = self._player.get_playing_info()
                self._media_info = {}
                if playing_info is None or not playing_info:
                    self._media_type = MEDIA_TYPE_APP
                    self._state = STATE_IDLE
                else:
                    self._media_info = playing_info
                    status = playing_info.get("status")
                    if status and status is not None:
                        if status == 1 or status is True:
                            self._state = STATE_PLAYING
                    mediatype = playing_info.get("source")
                    if mediatype and mediatype is not None:
                        if mediatype == "video":
                            item_type = self._media_info.get("type")
                            if item_type is not None and item_type == "tv":
                                self._media_type = MEDIA_TYPE_TVSHOW
                            else:
                                self._media_type = MEDIA_TYPE_MOVIE
                            self._source = ZCONTENT_VIDEO
                        else:
                            self._media_type = MEDIA_TYPE_MUSIC
                            self._source = ZCONTENT_MUSIC
                    else:
                        self._media_type = MEDIA_TYPE_APP
                    self._last_update = utcnow()
                self._refresh_channels()
            else:
                self._state = STATE_OFF

        except Exception as exception_instance:  # pylint: disable=broad-except
            _LOGGER.error(exception_instance)
            # self._state = STATE_OFF

    def _refresh_volume(self):
        """Refresh volume information."""
        volume_info = self._player.get_volume_info()
        if volume_info is not None:
            self._volume = volume_info.get("volume")
            self._min_volume = volume_info.get("minVolume")
            self._max_volume = volume_info.get("maxVolume")
            self._muted = volume_info.get("mute")

    def _refresh_channels(self):
        if not self._source_list:
            self._content_mapping = self._player.load_source_list()
            self._source_list = [ZCONTENT_VIDEO, ZCONTENT_MUSIC]
            for key in self._content_mapping:
                self._source_list.append(key)

    @property
    def unique_id(self):
        """Return the unique id of the device."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def source(self):
        """Return the current input source."""
        return self._source

    @property
    def source_list(self):
        """List of available input sources."""
        return self._source_list

    @property
    def media_content_type(self):
        """Content type of current playing media."""
        return self._media_type

    # @property
    # def volume_level(self):
    #    """Volume level of the media player (0..1)."""
    #    if self._volume is not None:
    #        return self._volume / 100
    #    return None

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._muted

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_ZIDOO | SUPPORT_MEDIA_MODES

    @property
    def media_title(self):
        """Title of current playing media."""
        title = self._media_info.get("movie_name")
        if title is None:
            title = self._media_info.get("episode_name")
        if title is not None:
            return title
        return self._media_info.get("title")

    @property
    def media_artist(self):
        """Artist of current playing media."""
        return self._media_info.get("artist")

    @property
    def media_album_name(self):
        """Album of current playing media."""
        return self._media_info.get("album")

    @property
    def media_track(self):
        """Track number of current playing media (Music track only)."""
        return self._media_info.get("track")

    @property
    def media_series_title(self):
        """Return the title of the series of current playing media."""
        return self._media_info.get("series_name")

    @property
    def media_season(self):
        """Season of current playing media (TV Show only)."""
        return str(self._media_info.get("season")).zfill(2)

    @property
    def media_episode(self):
        """Episode of current playing media (TV Show only)."""
        return str(self._media_info.get("episode")).zfill(2)

    @property
    def media_duration(self):
        """Duration of current playing media in seconds."""
        return self._media_info.get("duration")

    @property
    def media_position(self):
        """Position of current playing media in seconds."""
        return self._media_info.get("position")

    @property
    def media_position_updated_at(self):
        """Last time status was updated."""
        return self._last_update

    @property
    def app_name(self):
        """Return the current running application."""
        """NOTE: Shows as small print for movies too"""
        date = self._media_info.get("date")
        if date is not None:
            return "({})".format(date.year)

    # def set_volume_level(self, volume):
    #    """Set volume level, range 0..1."""
    #    self._player.set_volume_level(volume)

    def turn_on(self):
        """Turn the media player on."""
        self._player.turn_on()

    def turn_off(self):
        """Turn off media player."""
        self._player.turn_off()

    def volume_up(self):
        """Volume up the media player."""
        self._player.volume_up()

    def volume_down(self):
        """Volume down media player."""
        self._player.volume_down()

    def mute_volume(self, mute):
        """Send mute command."""
        self._player.mute_volume()

    def select_source(self, source):
        """Set the input source."""
        if source in self._content_mapping:
            self._player.start_app(source)

    def media_play_pause(self):
        """Simulate play pause media player."""
        if self._playing:
            self.media_pause()
        else:
            self.media_play()

    def media_play(self):
        """Send play command."""
        self._playing = True
        self._player.media_play()

    def media_pause(self):
        """Send media pause command."""
        if self._player.media_pause():
            self._playing = False

    def media_stop(self):
        """Send media stop command."""
        if self._player.media_stop():
            self._playing = False

    def media_next_track(self):
        """Send next track command."""
        self._player.media_next_track()
        self.schedule_update_ha_state()

    def media_previous_track(self):
        """Send the previous track command."""
        self._player.media_previous_track()
        self.schedule_update_ha_state()

    def play_media(self, media_type, media_id, **kwargs):
        """Play a piece of media."""
        if media_type and media_type == "file":
            self._player.play_file(media_id)
        else:
            self._player.play_movie(media_id)

    def media_seek(self, position):
        """Send media_seek command to media player."""
        self._player.set_media_position(position, self.media_duration)

    @property
    def media_image_url(self):
        """Image url of current playing media."""
        return self._player.generate_current_image_url()

    async def async_browse_media(self, media_content_type=None, media_content_id=None):
        """Implement the websocket media browsing helper"""

        is_internal = is_internal_request(self.hass)

        return await self.hass.async_add_executor_job(
            browse_media,
            self,
            is_internal,
            media_content_type,
            media_content_id,
        )

    async def async_get_browse_image(
        self, media_content_type, media_content_id, media_image_id=None
    ):
        """Get media image from server."""
        image_url = self._player.generate_image_url(
            media_content_id, media_content_type
        )
        if image_url:
            result = await self._async_fetch_image(image_url)
            return result

        return (None, None)

# Application Notes
The following are application notes based on feedback from other users.

## Rapid Update
The integration uses `local polling` with the Zidoo REST API to access data.  **As of version 2.0.0, Rapid Update is built-in** with polling times of 1 second when the player is on, and 5 seconds when the player is off or not available.

If you want alternative polling times, the recommended method is to create automatons to activate the `homeassistant.update_entity' service.

For example:
```
alias: Zidoo Rapid Update
description: ''
trigger:
  - platform: time_pattern
    seconds: '*'
condition:
  - condition: state
    entity_id: media_player.zidoo
    state: playing
action:
  - service: homeassistant.update_entity
    data: {}
    target:
      entity_id: media_player.zidoo
mode: single
```

_NOTE: You can disable the default polling from within the Integration settings._

## Using Additional Attributes (dev)
In addition to the native media player attributes, support for extra attributes is available in the `main` beta release when the zidoo video or audio player is playing.

The list as of 4/23 includes
- "media_uri" - the file reference,
- "media_height" - the source video height
- "media_width" - the source video height
- "media_zoom" - the current player zoom mode,
- "media_tag" - the movie tag-line from the HT db
- "media_date" - the movie release date from th HT db
- "media_bitrate" - the video reported bitrate
- "media_fps" - the video reported frames per second
- "media_audio" - the source audio format
- "media_video" - the source video format

### Getting aspect ratio
An example of using a template sensor to return the aspect-ratio

```
template:
  - sensor:
      - unique_id: zidoo_aspect_ratio
        name: Zidoo Aspect Ratio
        state: >
          {% set width = state_attr('media_player.zidoo', 'media_width')|float(0) %}
          {% set height = state_attr('media_player.zidoo', 'media_height')|float(1) %}
          {% set ratio = (width / height)|round(2) %}
          {% if ratio >= 2.35 %}
            2.35:1
          {% elif ratio >= 1.9 %}
            1.90:1
          {% elif ratio >= 1.77 %}
            16:9
          {% else -%}
            4:3
          {% endif %}
```
You can customize the state to achieve the desired result based on your requirements. NOTE: 'media_zoom' may also be needed

### Accessing Cover Art

The media_player has a entity_picture attribute when available which references an api call.  You can access the call directly, or use it as a reference in some frontend cards.  The format is `https://<ip_address>:<port>/api/media_player_proxy/media_player.<name>?token=xxxxxxxx`.  

For direct access you need to check the token from the attribute states or lookup how long-lived tokens work.  You can also use [mqtt-api-camera](https://github.com/wizmo2/mqtt-api-camera?tab=readme-ov-file#mqtt-api-camera) to create a virtual camera.

I use the customizable Mini Media Player Card, available through HACS or [github](https://github.com/kalkih/mini-media-player).  An example configuration to show a full screen image with minimal playing details is

```
title: nowplaying
path: nowplaying
type: panel
cards:
  - type: custom:mini-media-player
    entity: media_player.zidoo
    artwork: full-cover
    hide:
      name: false
      icon: true
      info: false
      power: true
      source: true
      sound_mode: true
      controls: true
      prev: true
      next: true
      play_pause: true
      play_stop: true
      jump: true
      volume: true
      volume_level: true
      mute: true
      progress: false
      runtime: true
      runtime_remaining: true
      artwork_border: true
      power_state: true
      icon_state: true
      shuffle: true
      repeat: true
      state_label: true
```

![image](https://github.com/user-attachments/assets/bb30c91e-5569-4de9-bb9d-b3f392c32b57)

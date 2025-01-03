# Home-assistant component for Zidoo media players

This is a functioning solution for controlling Zidoo media player on Home-Assistant.  Based on the Zidoo REST API, it is developed using a Z9S, but should work on all Zidoo devices (feedback/PRs welcome)

## Features

- Control Zidoo devices as media players through HA
- Album art and movie backdrops
- Browse movies, music, file system, and share mounts through HA Media Browser

**NOTE: From release 2.0.0, Rapid Update is updated in the integration. If you previously added an automation based on the documentation example, this can now be removed, but please re-enable automatic update if necessary**


![Media_Library](images/media_browser.png) ![Media_Player](images/tvshow_browse.png) 
![Media_Player](images/movie_playing.png) ![Music_Player](images/music_player.png) ![TVshow_Player](images/tvshow_player.png)

Streaming content currently uses a hack with the players uPNP functions.  There are limitations with content, including issues with the Media Player 6.0 (audio files are streamed to the Video Player for now).  Playlists can be handled using Kodi or ZDMC (this includes support for camera stream, although it is a little buggy). 

A Custom Lovelace card `zidoo-search-card` can be used to filter media browser results.[^7] Use the Media Search text editor to add a keyword, then select the desired Media Type button.  The results will be displayed in the standard Media Browser panel.

![Search Card](images/search-card.png)

Use the Media Search text editor to add a keyword, then select the desired Media Type button.  The results will be displayed in the standard Media Browser panel.

## Installation

### HACS Install 

1. Search for `Zidoo` under `Integrations` in the HACS Store tab.
2. **You will need to restart after installation for the component to start working.**
3. Configure the integation (see Configuration section)

### Manual Install

1. Copy `zidoo` folder from zidoo-player/custom_components to `\config\custom_components` (create folder if this is your first custom integration)
2. Restart HA

### Configuration

1. Add `Zidoo` Integration from the 'Configuraion-Integration' menu
2. Enter the IP address of player
3. Enter the Password if you have authentication enabled
4. Add standard Media Control card for newly added media_player device

### Options

Access the Options menu by pressing the CONFIGURE button on the Integration card

![Configure Shortcuts](images/config.png)

The Media browser allows access to the Movie Library, plus file access to local devices and saved SMB shares.  By default, the RECENT, MOVIE and TVSHOW Library searches are displayed.  Additional search shortcuts can be added.[^3]. 

Use Power Off control to enable Standby instead of a full power down.[^4]

### Services

Set Subtitle - switch through list or select video player subtitle.[^5]

Set Audio - switch through list or select video audio track.[^5]

Set Zoom - switch through list or select video zoom mode[^9]

Remote Send Command = send remote control button key (see [Key Commands](key_commands.md))[^8]

### Custom Search Card
After adding the integration, 'Edit' the dashboard and add the new card using the '+Add Card' button. Select the `custom:zidoo-search-card`, then edit the yaml to include a single `entity` value with your zidoo media_player id.
 _*NOTE:  The card requires the [card-tools](https://github.com/thomasloven/lovelace-card-tools) helper.  You can install it from HACS or add [manually](https://github.com/thomasloven/hass-config/wiki/Lovelace-Plugins)*_

```
type: custom:zidoo-search-card
entity: media_player.zidoo

# Optional fields to control which Media buttons are available
# from "video","movie","tvshow","music","album","artist"
buttons:
  - movie
  - tvshow 
```

## FAQs
> Q: Power-on does not work
>
>  A. _See [Power-On Info](power.md)._
> 
> Q: I'm having issues with the installation
>
> A. If you installed versions prior to 1.2.5 using HACS and the integration is not availble in ADD INTEGRATIONS
>  1. _See  [Add / Remove HACS Integration](add_remove.md)_
>  2. _Clear your Browser Cache_
>  
> A. If you have issues connecting with the device, it may be an authorization issue.  
>  1. _Try opening the 'Control Center' app on the media player and retry._
>  2. _Try turning off validation using the button in the app._  
>
> A. To switch from Wifi to LAN, the integration must be deleted and re added to update the new IP Address  
>
> Q. Is there anything else I might need to know?
>
> A. _Here are some [Application Notes](notes.md) based on feedback from other users_

## ToDo

- Testing on other devices
- Add Discovery (dev branch tested with z9s, need testing and/or DNLA header information for other device support)
- ZidooRC API will eventually needs to be released as a python library per HA requirements.  

## Major Changes

[^1]: Release 1.1 - can be used on older HA versions, requires manual integration and is limited to basic player control.
[^2]: Release 1.2 - adds config flow
[^3]: Release 1.2.9 - Extended search shortcuts.  Requires HA 2022.2 or above
[^4]: Release 1.2.10 - Standby option.  Not recommended on Z9S or UHD3000
[^5]: Release 1.2.11 - Subtitle and Audio services
[^6]: Release 1.3.0 - Bump zidoorc .  Add Send Key service
[^7]: Release 1.4.0 - Add music functionality and search card
[^8]: Release 2.0.1 - Convert to zidoaio.  Add Remote entity
[^9]: Release 2.0.2 - Add zoom mode service

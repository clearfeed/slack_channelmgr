# Getting a Slack Auth Token

In order to access Slack via APIs - we need an auth token. In order to do so - you can create a Slack App that has the required scopes. To do so:

1. _Either_ follow the steps described in the following section on [Creating a Slack App using Manifest](#create-slack-app-using-manifest). This approach is *strongly recommended*.

<br>

2. _Or_ create it manually using a guide, example:
https://docs.celigo.com/hc/en-us/articles/7140655476507-How-to-create-an-app-and-retrieve-OAuth-token-in-Slack

  *Scopes Required*

  If you are using this second approach to create the app - then please be sure to add the following scopes The token provided should at the minimum have the following scopes:

  * `channel:write.invites`
  * `channels:write`
  * `channels:read`
  * `users:read`
  
  This will allow this utility to work on public channels. In addition - if you want the user to also work on private channels - then the following scopes are required:
  * `groups:read`
  * `groups:write.invites`
  * `groups:write`

  Both of these scopes are only possible with `User Oauth Scopes` (so the bot can, at the minimum, act on behalf of the authorizing user - and add/delete users to Slack Connect channels).


## Create Slack App Using Manifest

  In order to create a Slack App whose auth tokens can be used to manage Slack channels, do the following:

1. Navigate to: https://api.slack.com/apps and hit `Create New App`.

2. On the `Create an app` pop-up - select the `From an app manifest` option.

3. After selecting a workspace to create the App in, paste in the JSON manifest as shown below and hit `Create`
```
{
    "display_information": {
        "name": "ClearFeed-Channel-Manager",
        "description": "An app with scopes to allow adding/deleting users to many channels at a time",
        "background_color": "#422637"
    },
    "features": {
        "app_home": {
            "home_tab_enabled": false,
            "messages_tab_enabled": true,
            "messages_tab_read_only_enabled": true
        },
        "bot_user": {
            "display_name": "ClearFeed Channel Manager",
            "always_online": true
        }
    },
    "oauth_config": {
        "scopes": {
            "user": [
                "channels:read",
                "channels:write.invites",
                "groups:read",
                "groups:write.invites",
                "users:read",
                "channels:write",
                "groups:write",
                "bookmarks:write",
                "bookmarks:read",
                "pins:read",
                "pins:write",
                "canvases:write",
                "canvases:read"
            ],
            "bot": [
                "app_mentions:read",
                "channels:history",
                "channels:join",
                "channels:manage",
                "channels:read",
                "channels:write.invites",
                "chat:write",
                "chat:write.customize",
                "chat:write.public",
                "groups:read",
                "groups:write",
                "groups:write.invites",
                "team:read",
                "users.profile:read",
                "users:read",
                "users:write",
                "bookmarks:write",
                "bookmarks:read",
                "pins:read",
                "pins.write",
                "canvases:write",
                "canvases:read"
            ]
        }
    },
    "settings": {
        "event_subscriptions": {
            "bot_events": [
                "app_mention"
            ]
        },
        "interactivity": {
            "is_enabled": true
        },
        "org_deploy_enabled": false,
        "socket_mode_enabled": true,
        "token_rotation_enabled": false
    }
}
```

4. At this point we have created the App - but not installed it. Hit `Install to Workspace` button. Go through the installation flow.

5. When you are done installing, select `OAuth and Permissions` from the Left Menu. In the section titled `OAuth Tokens for Your Workspace` - you will see a `User OAuth Token` and a `Bot User OAuth Token`. This notebook works best with `User OAuth Token`. Copy that and populate it into the Secrets as described earlier. (The User OAuth token is required to be able to operate on channels that the bot is not part of and to be able to see and invite users to Private Channels)

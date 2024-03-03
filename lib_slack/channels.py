import logging
import json
import requests


def get_all_channels(headers, public_only=False, private_only=False):
  channels = []
  nc = None

  visibility = 'public_channel, private_channel'
  if public_only:
    visibility = 'public_channel'
  if private_only:
    visibility = 'private_channel'

  rs = f"https://slack.com/api/conversations.list?types={visibility}"
  rs = rs + "&limit=999&exclude_archived=true"

  while True:
    rstring = rs
    if nc is not None:
      rstring = rstring + '&cursor=%s' % (nc)

    logging.info("Requesting: %s with header %s" % (rstring, json.dumps(headers)))
    response = requests.get(rstring, headers=headers).json()

    clist = response.get('channels')
    if clist is not None:
      channels.extend(clist)
    else:
      raise Exception('Channels attribute missing in response: '
                        + json.dumps(response))

    if (response.get('response_metadata', None) is not None and
        response.get('response_metadata').get('next_cursor', None) is not None):
      nc = response.get('response_metadata').get('next_cursor', None)
      if nc == '':
        break
    else:
      break

  return channels


def meets_channel_filters(channel, slack_connect_only=False, channel_name_includes="", channel_name_excludes=""):
  meets = True
  if slack_connect_only:
    meets = channel['is_shared'] and (channel.get('is_ext_shared') or channel.get('is_pending_ext_shared'))

  if len(channel_name_includes.strip()) != 0:
    imeets = False
    ielem = channel_name_includes.strip().split(',')
    for i in ielem:
      imeets = imeets or i.strip() in channel['name']
    meets = meets and imeets

  if len(channel_name_excludes.strip()) != 0:
    emeets = True
    eelem = channel_name_excludes.strip().split(',')
    for i in eelem:
      emeets = emeets and i.strip() not in channel['name']
    meets = meets and emeets

  return meets

def find_matching_channels(headers, **kwargs):
  filtered_kwargs = {k: v for k, v in kwargs.items() if k in ['public_only', 'private_only']}
  channels = get_all_channels(headers, **filtered_kwargs)

  filtered_kwargs = {k: v for k, v in kwargs.items() if k in ['slack_connect_only', 
                                                              'channel_name_includes', 
                                                              'channel_name_excludes']}                       
  
  return [item for item in channels if meets_channel_filters(item, **filtered_kwargs)]


def invite_user_to_channels(headers, clist, user):
  success_list = []
  already_present_list = []
  error_list = []

  for c in clist:
    rstring = f"https://slack.com/api/conversations.invite?channel={c['id']}&users={user['id']}"
    logging.info("Posting: %s with header %s" % (rstring, json.dumps(headers)))
    response = requests.post(rstring, headers=headers).json()

    success = ((response.get('ok') == True) and
                (response.get('channel') is not None) and
                (response.get('channel').get('id') == c['id']))
    if not success:
      if response.get('error') == 'already_in_channel':
        already_present_list.append(c)
      else:
        logging.error(f"Error trying to invite user on channel {c['name']}: {response.get('error')}")
        error_list.append((c, response.get('error')))
    else:
      success_list.append(c)

  return (success_list, already_present_list, error_list)


def remove_user_from_channels(headers, channels, user):
  success_list = []
  already_deleted_list = []
  error_list = []

  for c in channels:
    rstring = f"https://slack.com/api/conversations.kick?channel={c['id']}&user={user['id']}"
    logging.info("Posting: %s with header %s" % (rstring, json.dumps(headers)))
    response = requests.post(rstring, headers=headers).json()

    success = response.get('ok') == True
    if not success:
      if response.get('error') == 'not_in_channel':
        already_deleted_list.append(c)
      else:
        logging.error(f"Error trying to remove user from channel {c['name']}: {response.get('error')}")
        error_list.append((c, response.get('error')))
    else:
      success_list.append(c)

  return (success_list, already_deleted_list, error_list)


import logging
import json
import requests

def get_user_or_bot_id_list(headers):
  users = []
  nc = None
  rs = 'https://slack.com/api/users.list?limit=999'
  while True:
    # below private_channel scope is removed for testing
    rstring = rs
    if nc is not None:
      rstring = rstring + '&cursor=%s' % (nc)

    logging.info("Requesting: %s with header %s" % (rstring, json.dumps(headers)))
    response = requests.get(rstring, headers=headers).json()

    ulist = response.get('members')
    if ulist is not None:
      users.extend(response['members'])
    else:
      raise Exception('Members attribute missing in response: ' + json.dumps(response))

    if ((response.get('response_metadata', None) is not None) and
        (response.get('response_metadata').get('next_cursor', None) is not None)):
      nc = response.get('response_metadata').get('next_cursor', None)
      if nc == '':
        break
    else:
      break

  return users

def find_user_or_bot(headers, name):
  users = get_user_or_bot_id_list(headers)
  filtered_users = [item for item
                    in users
                    if ((item['name'].lower() == name.lower()) and
                        not item['deleted'])
                    ]
  if len(filtered_users) != 1:
    filtered_users = [item for item
                      in users
                      if ((item.get('real_name') is not None) and
                          (item['real_name'].lower() == name.lower()) and
                          not item['deleted'])
                      ]

  if len(filtered_users) == 1:
    return filtered_users[0]
  else:
    if (len(filtered_users) == 0):
      raise ValueError(f"Unable to find {name}")
    else:
      raise ValueError(f"Found multiple users matching {name}" +
                       str(filtered_users))

import streamlit as st
import logging
import sys
from pathlib import Path

# Add the root directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from lib_slack import channels
from lib_slack import users

def main():
    st.title('ClearFeed Bulk Channel Manager')
    st.write('Welcome! Let\'s help you make changes to lots of Slack channels at once!')

    logging.basicConfig(level=logging.INFO)
    # Input parameters from the user
    slack_api_token = st.text_input("Slack API Token", placeholder="xoxb-xxxxxxxxxx")
    user_or_bot_name = st.text_input("User or Bot Name", placeholder="lalit")
    action = st.selectbox('Action', ['Add', 'Remove'])
    slack_connect_only = st.checkbox('Slack Connect Only')
    public_only = st.checkbox('Public Only')
    private_only = st.checkbox('Private Only')
    channel_name_includes = st.text_input("Channel Name Includes", placeholder="clearfeed-, ext-")
    channel_name_excludes = st.text_input("Channel Name Excludes", placeholder="disney, costco")

    for some_var in ['clist', 'status_placeholder']:
        if some_var not in st.session_state:
            st.session_state[some_var] = None

    
    
    submit_clicked = st.button("Generate Plan", key="GeneratePlan")
    status_placeholder = st.empty()
    col1, col2 = st.columns(2)
    with col1:
        yes_clicked = st.button("Yes", key="Yes")
    with col2:
        no_clicked = st.button("No", key="No")
    
    if (yes_clicked or no_clicked) and st.session_state.clist is not None:
        logging.info("Have Plan and Yes/No click")
        # we have a plan already. get the plan variables
        clist = st.session_state.clist
        headers = st.session_state.headers
        user = st.session_state.user
        action = st.session_state.action

        if no_clicked:
            logging.info("No clicked")
            status_placeholder.markdown("**Cancelled !** -  Enter parameters and hit Generate Plan again")

        if yes_clicked:
            logging.info("Yes clicked")
            if action == "Add":
                status_placeholder.markdown("OK - Adding user ..  \n \n")
                logging.info("Adding user")
                ret = channels.invite_user_to_channels(headers, clist, user)
                success_list, already_invited_list, error_list = ret
                success_summary = f"Invited to {len(success_list)} channels successfully."
                already_invited_summary = f"User was already invited to {len(already_invited_list)} channels."
                error_summary = f"Errors occurred in {len(error_list)} channels."
                status_placeholder.markdown(f"**Action Summary:**  \n  \n"
                                            f"{success_summary}  \n"
                                            f"{already_invited_summary}  \n"
                                            f"{error_summary}  \n \n"
                                            "**Enter new parameters and hit Generate Plan again**\n")
            else:
                status_placeholder.markdown("OK - Removing user ..  \n \n")
                logging.info("Removing user")
                ret = channels.remove_user_from_channels(headers, clist, user)
                success_list, already_deleted_list, error_list = ret
                success_summary = f"Removed from {len(success_list)} channels successfully."
                already_deleted_summary = f"User was not present in {len(already_deleted_list)} channels."
                error_summary = f"Errors occurred in {len(error_list)} channels."
                status_placeholder.markdown(f"**Action Summary:**  \n  \n"
                                            f"{success_summary}  \n"
                                            f"{already_deleted_summary}  \n"
                                            f"{error_summary}  \n \n"
                                            "**Enter new parameters and hit Generate Plan again**\n")
                    
        # we are done with this plan. clear it
        st.session_state.clist = None
        return

    if submit_clicked:
        logging.info("Generating Plan")
        
        # we clear out old status only when we start working on new plan
        status_placeholder.empty()

        headers = {'Authorization': 'Bearer %s' % slack_api_token.strip(),
                    'Content-type': 'application/x-www-form-urlencoded; charset=utf-8'}
        if private_only and public_only:
          status_placeholder.text("private_only and public_only both cannot be true. Try again")
          return
        if (len(user_or_bot_name.strip()) == 0):
          status_placeholder.text("User or Bot Name cannot be empty. Try again")
          return
        if (len(slack_api_token.strip()) == 0):
          status_placeholder.text("Slack API Token cannot be empty. Try again")
          return
        
        status_placeholder.text("Finding matching channels...")
        clist = channels.find_matching_channels(headers,
                                                channel_name_includes=channel_name_includes, 
                                                channel_name_excludes=channel_name_excludes, 
                                                slack_connect_only=slack_connect_only, 
                                                public_only=public_only, 
                                                private_only=private_only)
        if (len(clist) == 0):
          status_placeholder.text("Could not find any matching channels to perform action on. Try again")
          return

        status_placeholder.text("Finding user/bot ...")      
        try:
            user = users.find_user_or_bot(headers, user_or_bot_name)
        except ValueError as e:
          status_placeholder.text(e)
          return
        
        channel_details_str = '  \n\t'.join([f"*id*: {item['id']}, *name*: {item['name']}" for item in clist])        
        user_details = (
            f"*id*: {user['id']}, *Name*: {user['name']}",
            f"*Real Name*: {user.get('real_name', 'N/A')}",
            f"*Email*: {user['profile'].get('email', 'N/A')}"
        )
        user_details_str = '  \n\t'.join(user_details)

        status_placeholder.empty()
        status_placeholder.markdown(f"**User Inputs:**  \n  \n"
                                    f"**Action:** {action}  \n  \n"
                                    f"**User Details:**  \n\t{user_details_str}  \n  \n"
                                    f"**Channels:**  \n\t{channel_details_str} \n  \n**Hit Yes or No!** \n")
        st.session_state.clist = clist
        st.session_state.user = user
        st.session_state.action = action
        st.session_state.headers = headers

        return
    else:
        status_placeholder.text("Enter parameters and hit Generate Plan")

        

#if __name__ == '__main__':
main()

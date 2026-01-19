from uagents import Context

def _get_user_orderd_key(user_id: str) -> str:
    return f"ordered-{user_id}"

def mark_user_as_ordered(ctx: Context, user_id: str) -> None:
    ctx.storage.set(_get_user_orderd_key(user_id), True)

def user_has_ordered(ctx: Context, user_id: str) -> bool: 
    return ctx.storage.get(_get_user_orderd_key(user_id))

# TODO
def get_message_history(chat_id: str) -> list:
    """
    TODO: Retrieve the message history for a particular chat ID.
    
    This function is a placeholder and needs to be implemented. We don't know how
    the developer API will work yet. Developers should look into the implementation
    and get back to the team with their findings.
    
    Args:
        chat_id: The unique identifier for the chat whose message history should be retrieved
    
    Returns:
        List of messages for the specified chat ID
    
    Note:
        This is a TODO item. Implementation details need to be researched and discussed with the team.
    """
    pass

# TODO
def append_message_to_history(chat_id: str, message: str) -> None:
    """
    TODO: Append a message to the message history for a particular chat ID.
    
    This function is a placeholder and needs to be implemented. We don't know how
    the developer API will work yet. Developers should look into the implementation
    and get back to the team with their findings.
    
    Args:
        chat_id: The unique identifier for the chat to append the message to
        message: The message content to append to the chat history
    
    Returns:
        None
    
    Note:
        This is a TODO item. Implementation details need to be researched and discussed with the team.
    """
    pass
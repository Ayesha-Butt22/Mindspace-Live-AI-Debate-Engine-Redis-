from db import message_repository

# This is the layer your scripts (publisher, subscriber, crud_demo) actually call.
# It sits between the "raw database" (repository) and the "user-facing script".
# If you later add rules like "don't save empty messages" or "log every delete",
# this is where that logic goes - not in the repository, not in the scripts.


def create_message(sender, content):
    if not content.strip():
        print("Cannot save an empty message.")
        return
    message_repository.insert(sender, content)


def list_messages():
    return message_repository.find_all()


def get_message(msg_id):
    return message_repository.find_by_id(msg_id)


def edit_message(msg_id, new_content):
    if not message_repository.find_by_id(msg_id):
        print(f"No message found with id {msg_id}.")
        return
    message_repository.update(msg_id, new_content)


def remove_message(msg_id):
    if not message_repository.find_by_id(msg_id):
        print(f"No message found with id {msg_id}.")
        return
    message_repository.delete(msg_id)

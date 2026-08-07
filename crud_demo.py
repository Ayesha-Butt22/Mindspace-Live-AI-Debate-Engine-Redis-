from db.connection import create_table
from controllers import message_controller

create_table()

while True:
    print("\n--- CRUD Menu ---")
    print("1. Create a message")
    print("2. Read all messages")
    print("3. Update a message")
    print("4. Delete a message")
    print("5. Exit")

    choice = input("Choose an option (1-5): ")

    if choice == "1":
        sender = input("Sender name: ")
        content = input("Message content: ")
        message_controller.create_message(sender, content)
        print("Message created successfully.")

    elif choice == "2":
        rows = message_controller.list_messages()
        if not rows:
            print("No messages found.")
        for row in rows:
            print(f"ID: {row[0]} | Sender: {row[1]} | Content: {row[2]} | Time: {row[3]}")

    elif choice == "3":
        msg_id = input("Enter message ID to update: ")
        new_content = input("Enter new content: ")
        message_controller.edit_message(msg_id, new_content)
        print("Message updated successfully.")

    elif choice == "4":
        msg_id = input("Enter message ID to delete: ")
        message_controller.remove_message(msg_id)
        print("Message deleted successfully.")

    elif choice == "5":
        print("Exiting CRUD demo.")
        break

    else:
        print("Invalid choice, try again.")

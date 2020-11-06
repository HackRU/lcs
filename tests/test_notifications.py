# This is different from regular lambda functions because it does not have a response to a user
# In the event that this function fails, the only side effect is that Firebase notifications will not be made

from src import notifications

def test_notifications():
    try:
        notifications.main()
    except Exception as e:
        print(f"Error: {e}")

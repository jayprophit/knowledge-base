"""
Modular Website & App Platform for 3D Blockchain
------------------------------------------------
Implements core pluggable modules and microservices to support:
- User management (DID, roles, authentication)
- Content management (CMS, versioning)
- Marketplace/e-commerce
- Messaging & communication (real-time, video, forums)
- Plugin/microservice system for extensibility

See documentation in docs/blockchain/modular_platform.md
"""

class UserManagement:
    """
    Smart contract for decentralized user management: registration, authentication, roles.
    """
    def __init__(self):
        self.users = {}  # user_id -> profile_data
        self.roles = {}  # user_id -> role
    def register_user(self, user_id, profile_data, role="user"):
        """Register a new user with profile data and role."""
        if user_id in self.users:
            raise Exception("User already exists.")
        self.users[user_id] = profile_data
        self.roles[user_id] = role
    def update_profile(self, user_id, new_data):
        """Update user profile data."""
        if user_id not in self.users:
            raise Exception("User not found.")
        self.users[user_id].update(new_data)
    def set_role(self, user_id, role):
        """Assign a new role to a user."""
        if user_id not in self.users:
            raise Exception("User not found.")
        self.roles[user_id] = role

class ContentManagement:
    """
    Smart contract for decentralized content management with versioning.
    """
    def __init__(self):
        self.contents = {}  # content_id -> content_data
        self.versions = {}  # content_id -> [versions]
    def create_content(self, content_id, content_data):
        """Create new content and start version history."""
        if content_id in self.contents:
            raise Exception("Content already exists.")
        self.contents[content_id] = content_data
        self.versions[content_id] = [content_data.copy()]
    def update_content(self, content_id, new_data):
        """Update content and save version."""
        if content_id not in self.contents:
            raise Exception("Content not found.")
        self.contents[content_id].update(new_data)
        self.versions[content_id].append(self.contents[content_id].copy())
    def get_versions(self, content_id):
        """Get all versions of a content item."""
        return self.versions.get(content_id, [])
    def delete_content(self, content_id):
        """Delete content and its version history."""
        if content_id not in self.contents:
            raise Exception("Content not found.")
        del self.contents[content_id]
        del self.versions[content_id]

class Marketplace:
    """
    Smart contract for decentralized marketplace: product listing, purchase, and updates.
    """
    def __init__(self):
        self.products = {}  # product_id -> product_data
    def list_product(self, product_id, product_data):
        """List a new product for sale."""
        if product_id in self.products:
            raise Exception("Product already exists.")
        self.products[product_id] = product_data
    def purchase_product(self, buyer_id, product_id):
        """Simulate product purchase (stock decremented)."""
        if product_id not in self.products:
            raise Exception("Product not found.")
        product = self.products[product_id]
        if product.get('stock', 0) <= 0:
            raise Exception("Out of stock.")
        product['stock'] -= 1
    def update_product(self, product_id, updated_data):
        """Update product details."""
        if product_id not in self.products:
            raise Exception("Product not found.")
        self.products[product_id].update(updated_data)

class MessagingSystem:
    """
    Smart contract for decentralized messaging (chat, notifications).
    """
    def __init__(self):
        self.messages = []  # List of messages
    def send_message(self, sender, receiver, content):
        """Send a message from sender to receiver."""
        message = {"sender": sender, "receiver": receiver, "content": content}
        self.messages.append(message)
    def get_messages(self, user_id):
        """Get all messages for a user."""
        return [msg for msg in self.messages if msg['receiver'] == user_id]

class PluginManager:
    """
    Plugin/microservice system for extensibility.
    """
    def __init__(self):
        self.plugins = {}  # plugin_name -> plugin_instance
    def register_plugin(self, plugin_name, plugin_instance):
        """Register a new plugin/microservice."""
        self.plugins[plugin_name] = plugin_instance
    def get_plugin(self, plugin_name):
        """Retrieve a plugin by name."""
        return self.plugins.get(plugin_name)


class ContentManagement:
    def __init__(self):
        self.contents = {}  # content_id -> content_data
        self.versions = {}  # content_id -> [versions]
    def create_content(self, content_id, content_data):
        self.contents[content_id] = content_data
        self.versions[content_id] = [content_data.copy()]
        print(f"Content {content_id} created.")
    def update_content(self, content_id, new_data):
        if content_id in self.contents:
            self.contents[content_id].update(new_data)
            self.versions[content_id].append(self.contents[content_id].copy())
            print(f"Content {content_id} updated.")
        else:
            print("Content not found.")
    def get_versions(self, content_id):
        return self.versions.get(content_id, [])

class Marketplace:
    def __init__(self):
        self.products = {}  # product_id -> product_data
    def list_product(self, product_id, product_data):
        self.products[product_id] = product_data
        print(f"Product {product_id} listed for sale.")
    def purchase_product(self, buyer_id, product_id):
        if product_id in self.products:
            print(f"{buyer_id} purchased {self.products[product_id]['name']}.")
        else:
            print("Product not found.")

class MessagingSystem:
    def __init__(self):
        self.messages = []
    def send_message(self, sender, receiver, content):
        message = {"sender": sender, "receiver": receiver, "content": content}
        self.messages.append(message)
        print(f"Message sent from {sender} to {receiver}: {content}")

# Plugin/microservice system
class PluginManager:
    def __init__(self):
        self.plugins = {}  # plugin_name -> plugin_instance
    def register_plugin(self, plugin_name, plugin_instance):
        self.plugins[plugin_name] = plugin_instance
        print(f"Plugin {plugin_name} registered.")
    def get_plugin(self, plugin_name):
        return self.plugins.get(plugin_name)

# Example usage for documentation is provided in docs/blockchain/modular_platform.md

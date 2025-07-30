# In or_gym_inventory/__init__.py

import sys
from gymnasium.envs.registration import register

print("--- Registering or_gym_inventory environments ---", file=sys.stderr)

__version__ = "1.0.0" 

# --- Newsvendor Environment ---
register(
    id='or_gym_inventory/Newsvendor-v0',
    entry_point='or_gym_inventory.newsvendor:NewsvendorEnv',
    # Optional: Add default max_episode_steps if you want truncation
    # max_episode_steps=50,
)

# --- Inventory Management Environments ---
register(
    id='or_gym_inventory/InvManagementBacklog-v0',
    entry_point='or_gym_inventory.inventory_management:InvManagementBacklogEnv',
)
register(
    id='or_gym_inventory/InvManagementLostSales-v0',
    entry_point='or_gym_inventory.inventory_management:InvManagementLostSalesEnv',
)

# --- Network Management Environments ---
register(
    id='or_gym_inventory/NetInvMgmtBacklog-v0',
    entry_point='or_gym_inventory.network_management:NetInvMgmtBacklogEnv',
)
register(
    id='or_gym_inventory/NetInvMgmtLostSales-v0',
    entry_point='or_gym_inventory.network_management:NetInvMgmtLostSalesEnv',
)

# --- Making environment classes directly accessible ---
from .newsvendor import NewsvendorEnv
from .inventory_management import InvManagementBacklogEnv, InvManagementLostSalesEnv
from .network_management import NetInvMgmtBacklogEnv, NetInvMgmtLostSalesEnv
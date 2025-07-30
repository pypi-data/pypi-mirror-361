# Gymnasium-Compatible Inventory Management Environments & Benchmarks (or-gym-inventory)

This repository provides `or_gym_inventory`, an installable Python package containing implementations of classic inventory management environments. These environments are adapted from the original [OR-Gym library](https://github.com/hubbs5/or-gym) and updated for compatibility with the [Gymnasium](https://gymnasium.farama.org/) API (the successor to OpenAI Gym).

The package also includes comprehensive benchmarking scripts (located in the `examples/` directory of the source repository) to compare various heuristic, optimization-inspired, and Reinforcement Learning (RL) policies on these environments.

**Environments Included:**
1.  **Newsvendor (`or_gym_inventory.newsvendor`):** Multi-period newsvendor problem with lead times and stochastic Poisson demand (based on Zipkin (2000, 2008), and Balaji et al. 2019, https://arxiv.org/abs/1911.10641). Class: `NewsvendorEnv`.
2.  **Inventory Management (`or_gym_inventory.inventory_management`):** Multi-period, multi-echelon inventory system for a single product (based on Paul Glasserman and Sridhar Tayur (1995) and D. Hubbs (2020)). Includes `InvManagementBacklogEnv` and `InvManagementLostSalesEnv`. 
3.  **Network Inventory Management (`or_gym_inventory.network_management`):** Multi-period, multi-node inventory system with a network structure (factories, distributors, retailers, markets). Includes `NetInvMgmtBacklogEnv` and `NetInvMgmtLostSalesEnv` (based on Paul Glasserman and Sridhar Tayur (1995) and Perez et al. (2021)).

## Features

*   **Installable Package:** Easily install using pip (`pip install or_gym_inventory`).
*   **Gymnasium Compatible:** Environments adhere to the modern Gymnasium API standard (`reset` returns `obs, info`, `step` returns `obs, reward, terminated, truncated, info`).
*   **Three Core Environments:** Covers single-item, multi-echelon, and network inventory problems.
*   **Backlog & Lost Sales Variants:** Specific environment classes (`*BacklogEnv`, `*LostSalesEnv`) implement these dynamics.
*   **Comprehensive Benchmarking Examples:** Includes dedicated scripts (`examples/benchmark_*.py` in the source repo) comparing various agents:
    *   **Baselines:** Random Agent.
    *   **Heuristics:** Relevant heuristics adapted for each environment type (e.g., Order-Up-To, Classic Newsvendor, (s,S) for Newsvendor; Base Stock, Constant Order for multi-echelon/network).
    *   **Stable Baselines3 Agents:** PPO, SAC, TD3, A2C, DDPG examples.
    *   **Ray RLlib Agents:** PPO, SAC examples.
*   **Detailed Reporting (from Benchmarks):** Benchmark examples generate:
    *   Summary tables (CSV).
    *   Raw results per episode (CSV).
    *   Detailed step-by-step data (optional, JSON Lines).
    *   Comparison plots (PNG).

## Installation

You can install the core package using pip:

```bash
pip install or_gym_inventory
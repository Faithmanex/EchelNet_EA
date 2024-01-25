import random
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
from matplotlib.animation import FuncAnimation

def generate_synthetic_data(price, step_size=0.1, break_frequency=150):
    """
    Generate synthetic market data.

    Parameters:
    price (float): The current price of the asset.
    step_size (float): The size of each price movement.
    break_frequency (int): The frequency of a breakout movement.

    Returns:
    float: The new price after the movement.
    float: The movement that occurred.
    """
    movement = random.choice([-1, 1]) * step_size

    # Occasionally break through the borders
    if random.randint(1, break_frequency) == 1:
        movement *= 10  # Increase the movement for a breakout

    price += movement

    return price, movement

def update(frame, prices, movements, step_size, break_frequency):
    """
    Update the market data and candlestick chart.

    Parameters:
    frame (int): The frame number of the animation.
    prices (list): The list of prices.
    movements (list): The list of price movements.
    step_size (float): The size of each price movement.
    break_frequency (int): The frequency of a breakout movement.
    """
    price, movement = generate_synthetic_data(prices[-1], step_size, break_frequency)

    # Append new data to the lists
    prices.append(price)
    movements.append(movement)

    # Update candlestick chart
    ax.clear()
    ax.plot(range(len(prices)), prices, color='black', linewidth=1)
    ax.set_title('Synthetic Indices Market (1 Minute)')
    ax.set_ylabel('Price')
    ax.set_xlabel('Time')
    ax.grid(True)

# Initialize the figure and axis
fig, ax = plt.subplots(figsize=(10, 6))

# Initial data
initial_price = 1000
initial_movement = 0.0
initial_prices = [initial_price]
initial_movements = [initial_movement]

# Set the animation update function
animation = FuncAnimation(fig, update, frames=range(1), fargs=(initial_prices, initial_movements, 0.1, 150),
                          interval=0.1, repeat=True)

plt.show()
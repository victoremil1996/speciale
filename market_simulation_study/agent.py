from typing import NoReturn, Tuple
from numpy import ndarray
import abc
import numpy as np
import pandas as pd
import random

from keras.models import Sequential
from keras.layers import Dense, SimpleRNN, LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import math

class Agent(abc.ABC):
    """
    Abstract class for agents
    """

    # @abc.abstractmethod
    # def __init__(self,
    #              agent_id: int = None,
    #              delta: float = None,
    #              position: int = 0,
    #              pnl: float = None,
    #              buy_price: float = None,
    #              sell_price: float = None,
    #              all_trades: np.ndarray = None):
    #     """
    #     Constructor
    #     :param latency: latency when matching agents in the market environment
    #     """
    #
    #     self.agent_id = agent_id
    #     self.delta = delta
    #     self.latency = delta
    #     self.position = position
    #     self.pnl = pnl
    #     self.buy_price = buy_price
    #     self.sell_price = sell_price
    #     self.buy_volume = buy_volume
    #     self.sell_volume = sell_volume
    #     self.all_trades = all_trades
    #     self.buy_order = pd.DataFrame(np.array([[self.buy_price, self.buy_volume, self.latency, self.agent_id]]),
    #                                   columns = ["buy_price", "buy_volume", "latency", "agent_id"])
    #     self.sell_order = pd.DataFrame(np.array([[self.sell_price, self.sell_volume, self.latency, self.agent_id]]),
    #                                   columns = ["sell_price", "sell_volume", "latency", "agent_id"])
    @abc.abstractmethod
    def calculate_buy_price(self, state: dict) -> float:
        """
        Calculates buy price

        :param state:
        :return:
        """
        raise NotImplementedError("Abstract Class")

    @abc.abstractmethod
    def calculate_sell_price(self, state: dict) -> float:
        """
        Calculates sell price

        :param state:
        :return:
        """
        raise NotImplementedError("Abstract Class")

    @abc.abstractmethod
    def calculate_buy_volume(self, state: dict) -> float:
        """
        Calculates buy price

        :param state:
        :return:
        """
        raise NotImplementedError("Abstract Class")

    @abc.abstractmethod
    def calculate_sell_volume(self, state: dict) -> float:
        """
        Calculates sell price

        :param state:
        :return:
        """
        raise NotImplementedError("Abstract Class")

    @abc.abstractmethod
    def calculate_profit_and_loss(self, state: dict) -> float:
        """
        Calculates profit and loss

        :param state:
        :return:
        """
        raise NotImplementedError("Abstract Class")

    @abc.abstractmethod
    def update(self, state: dict) -> NoReturn:
        """
        Updates agents ask and bid prices, and corresponding volumes, when new state is provided

        :param state:
        :return:
        """
        # Update trades and position

        # Update prices


class RandomAgent(Agent):
    """
    Agent which makes noisy buy and sell prices around market_prices
    """

    def __init__(self,
                 agent_id: int = None,
                 delta: float = None,
                 position: int = 0,
                 pnl: float = None,
                 buy_price: float = None,
                 sell_price: float = None,
                 all_trades: np.ndarray = None,
                 buy_volume: float = None,
                 sell_volume: float = None,
                 noise_range: Tuple = None):
        """
        Constructor
        :param latency: latency when matching agents in the market environment
        """
        self.agent_class = "Random"
        self.agent_id = agent_id
        self.delta = delta
        self.latency = delta
        self.position = position
        self.pnl = pnl
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.all_trades = all_trades if all_trades else np.array([0, 0])
        self.buy_volume = buy_volume
        self.sell_volume = sell_volume
        self.noise_range = noise_range if noise_range else [0.01, 0.03]
        self.random_agent_price = None
        self.buy_order = pd.DataFrame(np.array([[self.buy_price, self.buy_volume, self.latency, self.agent_id]]),
                                      columns=["buy_price", "buy_volume", "latency", "agent_id"])
        self.sell_order = pd.DataFrame(np.array([[self.sell_price, self.sell_volume, self.latency, self.agent_id]]),
                                       columns=["sell_price", "sell_volume", "latency", "agent_id"])

    def calculate_buy_price(self, state: dict) -> float:
        """
        Calculates buy price

        :param state: market state information
        :return: buy price
        """
        buy_price = self.random_agent_price * (
                    1 - np.random.uniform(low=self.noise_range[0], high=self.noise_range[1]))
        buy_price = np.maximum(buy_price, 0)
        return buy_price

    def calculate_sell_price(self, state: dict) -> float:
        """
        Calculates sell price

        :param state: market state information
        :return: sell price
        """
        sell_price = self.random_agent_price * (
                    1 + np.random.uniform(low=self.noise_range[0], high=self.noise_range[1]))
        sell_price = np.maximum(sell_price, 0)
        return sell_price

    def calculate_buy_volume(self, state: dict) -> float:
        """
        Calculates buy price

        :param state:
        :return:
        """
        volume = np.random.randint(0, 3)

        return volume

    def calculate_sell_volume(self, state: dict) -> float:
        """
        Calculates sell price

        :param state:
        :return:
        """
        volume = np.random.randint(0, 3)

        return volume

    def calculate_profit_and_loss(self, state: dict) -> NoReturn:
        """
        Calculates profit and loss

        :param state: market state information
        :return: total profit and loss
        """
        realized_value = np.sum(self.all_trades[:, 0] * self.all_trades[:, 1])
        unrealized_value = self.position * state["market_prices"][-1] * (1 - state["slippage"])

        self.pnl = realized_value + unrealized_value

    def update(self, state: dict) -> NoReturn:
        """
        Updates agents ask and bid prices, and corresponding volumes, when new state is provided

        :param state: market state information
        :return: NoReturn
        """
        # Update latency

        self.latency = self.delta + np.random.uniform(1e-6, 1)

        # Update prices and volume
        self.random_agent_price = state["market_prices"][-1] + np.random.normal(loc=0, scale=2)

        self.buy_price = self.calculate_buy_price(state)
        self.sell_price = self.calculate_sell_price(state)
        self.buy_volume = self.calculate_buy_volume(state)
        self.sell_volume = self.calculate_sell_volume(state)

        # Update orders

        self.buy_order = pd.DataFrame(np.array([[self.buy_price, self.buy_volume, self.latency, self.agent_id]]),
                                      columns=["buy_price", "buy_volume", "latency", "agent_id"],
                                      index=[self.agent_id])
        self.sell_order = pd.DataFrame(np.array([[self.sell_price, self.sell_volume, self.latency, self.agent_id]]),
                                       columns=["sell_price", "sell_volume", "latency", "agent_id"],
                                       index=[self.agent_id])


class InvestorAgent(Agent):
    """
    Agent which buys or sells large orders in chunks over small periods. Similiar to Institutional Investors.
    """

    def __init__(self,
                 agent_id: int = None,
                 delta: float = None,
                 position: int = 0,
                 pnl: float = None,
                 buy_price: float = None,
                 sell_price: float = None,
                 all_trades: np.ndarray = None,
                 buy_volume: float = 20,
                 sell_volume: float = 20,
                 intensity: float = None,
                 n_orders: int = 5,
                 orders_in_queue: int = 0,
                 price_margin: float = 0.1,
                 is_buying: bool = False):
        """
        Constructor
        :param latency: latency when matching agents in the market environment
        """
        self.agent_class = "Investor"
        self.agent_id = agent_id
        self.delta = delta
        self.latency = delta
        self.position = position
        self.pnl = pnl
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.all_trades = all_trades if all_trades else np.array([0, 0])
        self.buy_volume = buy_volume
        self.sell_volume = sell_volume
        self.intensity = intensity
        self.n_orders = n_orders
        self.orders_in_queue = orders_in_queue
        self.price_margin = price_margin
        self.is_buying = is_buying
        self.buy_order = pd.DataFrame(np.array([[self.buy_price, self.buy_volume, self.latency, self.agent_id]]),
                                      columns=["buy_price", "buy_volume", "latency", "agent_id"],
                                      index=[self.agent_id])
        self.sell_order = pd.DataFrame(np.array([[self.sell_price, self.sell_volume, self.latency, self.agent_id]]),
                                       columns=["sell_price", "sell_volume", "latency", "agent_id"],
                                       index=[self.agent_id])

    def calculate_buy_price(self, state: dict) -> float:
        """
        Calculates buy price

        :param state: market state information
        :return: buy price
        """
        buy_price = state["market_prices"][-1] * (1 + self.price_margin)
        buy_price = np.maximum(buy_price, 0)
        return buy_price

    def calculate_sell_price(self, state: dict) -> float:
        """
        Calculates sell price

        :param state: market state information
        :return: sell price
        """
        sell_price = state["market_prices"][-1]
        sell_price = np.maximum(sell_price, 0) * (1 - self.price_margin)
        return sell_price

    def calculate_buy_volume(self, state: dict) -> float:
        """
        Calculates buy price

        :param state:
        :return:
        """
        volume = self.buy_volume

        return volume

    def calculate_sell_volume(self, state: dict) -> float:
        """
        Calculates sell price

        :param state:
        :return:
        """
        volume = self.sell_volume

        return volume

    def calculate_profit_and_loss(self, state: dict) -> NoReturn:
        """
        Calculates profit and loss

        :param state: market state information
        :return: total profit and loss
        """
        realized_value = np.sum(self.all_trades[:, 0] * self.all_trades[:, 1])
        unrealized_value = self.position * state["market_prices"][-1] * (1 - state["slippage"])

        self.pnl = realized_value + unrealized_value

    def update(self, state: dict) -> NoReturn:
        """
        Updates agents ask and bid prices, and corresponding volumes, when new state is provided

        :param state: market state information
        :return: NoReturn
        """
        # Update latency
        self.latency = self.delta + np.random.uniform(1 + 1e-6, 2)

        # instantiate no prices
        self.buy_price = np.nan
        self.sell_price = np.nan

        # check if investor wants to buy or sell and calculate prices if so
        will_buy = np.random.uniform(0, 1) < self.intensity
        will_sell = (np.random.uniform(0, 1) < self.intensity) and (self.position >= self.n_orders * self.sell_volume)

        if self.orders_in_queue == 0:
            self.is_buying = False

        if self.orders_in_queue > 0 and self.is_buying:  # buying
            self.orders_in_queue -= 1
            self.buy_price = self.calculate_buy_price(state)

        elif self.orders_in_queue > 0 and not self.is_buying:  # selling
            self.orders_in_queue -= 1
            self.sell_price = self.calculate_sell_price(state)

        elif will_buy and self.orders_in_queue == 0:  # starts to buy
            self.orders_in_queue = self.n_orders - 1
            self.is_buying = True
            self.buy_price = self.calculate_buy_price(state)

        elif will_sell and self.orders_in_queue == 0:  # starts to sell
            self.orders_in_queue = self.n_orders - 1
            self.sell_price = self.calculate_sell_price(state)

        # Update volume

        self.buy_volume = self.calculate_buy_volume(state)
        self.sell_volume = self.calculate_sell_volume(state)

        # Update orders
        self.buy_order = pd.DataFrame(np.array([[self.buy_price, self.buy_volume, self.latency, self.agent_id]]),
                                      columns=["buy_price", "buy_volume", "latency", "agent_id"],
                                      index=[self.agent_id])
        self.sell_order = pd.DataFrame(np.array([[self.sell_price, self.sell_volume, self.latency, self.agent_id]]),
                                       columns=["sell_price", "sell_volume", "latency", "agent_id"],
                                       index=[self.agent_id])


class TrendAgent(Agent):
    """
    Agent which makes noisy buy and sell prices around market_prices
    """

    def __init__(self,
                 agent_id: int = None,
                 delta: float = None,
                 position: int = 0,
                 pnl: float = None,
                 buy_price: float = None,
                 sell_price: float = None,
                 all_trades: np.ndarray = None,
                 buy_volume: float = 0,
                 sell_volume: float = 0,
                 price_margin: float = 0.05,
                 const_position_size: int = 5,
                 moving_average_one: int = 50,
                 moving_average_two: int = 200):
        """
        Constructor
        :param latency: latency when matching agents in the market environment
        """
        self.agent_class = "Trend"
        self.agent_id = agent_id
        self.delta = delta
        self.latency = delta
        self.position = position
        self.pnl = pnl
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.all_trades = all_trades if all_trades else np.array([0, 0])
        self.buy_volume = buy_volume
        self.sell_volume = sell_volume
        self.price_margin = price_margin
        self.const_position_size = const_position_size
        self.moving_average_one = moving_average_one
        self.moving_average_two = moving_average_two
        self.buy_order = pd.DataFrame(np.array([[self.buy_price, self.buy_volume, self.latency, self.agent_id]]),
                                      columns=["buy_price", "buy_volume", "latency", "agent_id"],
                                      index=[self.agent_id])
        self.sell_order = pd.DataFrame(np.array([[self.sell_price, self.sell_volume, self.latency, self.agent_id]]),
                                       columns=["sell_price", "sell_volume", "latency", "agent_id"],
                                       index=[self.agent_id])

    def calculate_buy_price(self, state: dict) -> float:
        """
        Calculates buy price

        :param state: market state information
        :return: buy price
        """
        noise = np.random.normal(loc=0, scale=0.01)
        buy_price = state["market_prices"][-1] * (1 + self.price_margin + noise)
        buy_price = np.maximum(buy_price, 0)
        return buy_price

    def calculate_sell_price(self, state: dict) -> float:
        """
        Calculates sell price

        :param state: market state information
        :return: sell price
        """
        noise = np.random.normal(loc=0, scale=0.01)
        sell_price = state["market_prices"][-1] * (1 + noise)
        sell_price = np.maximum(sell_price, 0)
        return sell_price

    def calculate_buy_volume(self, state: dict) -> float:
        """
        Calculates buy price

        :param state:
        :return:
        """
        volume = self.const_position_size  # np.random.randint(1, 2)

        return volume

    def calculate_sell_volume(self, state: dict) -> float:
        """
        Calculates sell price

        :param state:
        :return:
        """
        volume = self.const_position_size  # np.random.randint(1, 2)

        return volume

    def calculate_profit_and_loss(self, state: dict) -> NoReturn:
        """
        Calculates profit and loss

        :param state: market state information
        :return: total profit and loss
        """
        realized_value = np.sum(self.all_trades[:, 0] * self.all_trades[:, 1])
        unrealized_value = self.position * state["market_prices"][-1] * (1 - state["slippage"])

        self.pnl = realized_value + unrealized_value

    def update(self, state: dict) -> NoReturn:
        """
        Updates agents ask and bid prices, and corresponding volumes, when new state is provided

        :param state: market state information
        :return: NoReturn
        """
        # update latency
        self.latency = self.delta + np.random.uniform(1e-6, 1)

        # check trend direction and aim for strategic position

        ma1 = np.average(state["market_prices"][- self.moving_average_one:])
        ma2 = np.average(state["market_prices"][- self.moving_average_two:])

        trend = ma1 / ma2

        self.buy_price = np.nan
        self.sell_price = np.nan

        if trend >= 1 and self.position < self.const_position_size:
            self.buy_price = self.calculate_buy_price(state)
            self.buy_volume = self.calculate_buy_volume(state) - self.position
        elif trend >= 1 and self.position >= self.const_position_size:
            pass
        elif trend < 1 and self.position >= - self.const_position_size:
            self.sell_price = self.calculate_sell_price(state)
            self.sell_volume = self.calculate_sell_volume(state) + self.position
        elif trend < 1 and self.position < - self.const_position_size:
            pass

        # Update orders
        self.buy_order = pd.DataFrame(np.array([[self.buy_price, self.buy_volume, self.latency, self.agent_id]]),
                                      columns=["buy_price", "buy_volume", "latency", "agent_id"],
                                      index=[self.agent_id])
        self.sell_order = pd.DataFrame(np.array([[self.sell_price, self.sell_volume, self.latency, self.agent_id]]),
                                       columns=["sell_price", "sell_volume", "latency", "agent_id"],
                                       index=[self.agent_id])


class MarketMakerAgent(Agent):
    """
    Market making agent class
    """

    def __init__(self,
                 agent_id: int = None,
                 delta: float = None,
                 gamma: float = None,
                 gamma2: float = None,
                 position: int = 0,
                 pnl: float = None,
                 buy_price: float = None,
                 sell_price: float = None,
                 all_trades: np.ndarray = None):
        """
        Constructor
        :param latency: latency when matching agents in the market environment
        """
        self.agent_class = "MM"
        self.agent_id = agent_id
        self.delta = delta  # base latency
        self.gamma = gamma  # midprice sensitivity to position size
        self.gamma2 = gamma2  # spread sensitivity to local volatility
        self.latency = delta
        self.position = position
        self.pnl = pnl
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.all_trades = all_trades if all_trades else np.array([0, 0])
        self.buy_volume = None
        self.sell_volume = None
        self.spread = None
        self.mid_price = None
        self.buy_order = pd.DataFrame(np.array([[self.buy_price, self.buy_volume, self.latency, self.agent_id]]),
                                      columns=["buy_price", "buy_volume", "latency", "agent_id"],
                                      index=[self.agent_id])
        self.sell_order = pd.DataFrame(np.array([[self.sell_price, self.sell_volume, self.latency, self.agent_id]]),
                                       columns=["sell_price", "sell_volume", "latency", "agent_id"],
                                       index=[self.agent_id])

    def calculate_volatility(self, state: dict, n_observations=10) -> float:
        """
        calculates market price volatility

        :param state:
        :param n_observations: dats to calculate volatility for
        :return:
        """
        vol = np.std(state["market_prices"][-n_observations:])
        return vol

    def calculate_spread(self, state: dict) -> float:
        """
        updates agents bid-ask spread

        :param state:
        :return:
        """
        vol = self.calculate_volatility(state)
        spread = vol * self.gamma2
        return spread

    def calculate_mid_price(self, state: dict) -> float:
        """
        updates agents own midprice to place ask and bids from

        :param state:
        :return:
        """

        market_mid_price = state["market_prices"][-1]
        market_leaning = self.gamma * self.position
        mid_price = market_mid_price * (1 - market_leaning)
        return mid_price

    def calculate_buy_price(self) -> float:
        """
        Calculates buy price

        :param state:
        :return:
        """
        buy_price = self.mid_price - self.spread / 2 + np.random.normal(loc=0, scale=0.01)
        return buy_price

    def calculate_sell_price(self) -> float:
        """
        Calculates sell price

        :param state:
        :return:
        """
        sell_price = self.mid_price + self.spread / 2 + np.random.normal(loc=0, scale=0.01)
        return sell_price

    def calculate_buy_volume(self) -> float:
        """
        Calculates buy price

        :param state:
        :return:
        """
        buy_volume = 3
        return buy_volume

    def calculate_sell_volume(self) -> float:
        """
        Calculates sell price

        :param state:
        :return:
        """
        sell_volume = 3
        return sell_volume

    def calculate_profit_and_loss(self, state: dict) -> NoReturn:
        """
        Calculates profit and loss

        :param state:
        :return:
        """
        realized_value = np.sum(self.all_trades[:, 0] * self.all_trades[:, 1])
        unrealized_value = self.position * state["market_prices"][-1] * (1 - state["slippage"])

        self.pnl = realized_value + unrealized_value

    def update(self, state: dict) -> NoReturn:
        """
        Updates agents ask and bid prices, and corresponding volumes, when new state is provided

        :param state:
        :return:
        """
        # Update latency
        self.latency = self.delta / (1 + np.random.uniform(1e-6, 1))

        # Update parameters to calculate prices
        self.mid_price = self.calculate_mid_price(state)
        self.spread = self.calculate_spread(state)

        # Update volumes
        self.buy_volume = self.calculate_buy_volume()
        self.sell_volume = self.calculate_sell_volume()

        # Update prices
        self.buy_price = self.calculate_buy_price()
        self.sell_price = self.calculate_sell_price()

        self.buy_order = pd.DataFrame(np.array([[self.buy_price, self.buy_volume, self.latency, self.agent_id]]),
                                      columns=["buy_price", "buy_volume", "latency", "agent_id"],
                                      index=[self.agent_id])
        self.sell_order = pd.DataFrame(np.array([[self.sell_price, self.sell_volume, self.latency, self.agent_id]]),
                                       columns=["sell_price", "sell_volume", "latency", "agent_id"],
                                       index=[self.agent_id])


class RLAgent(Agent):
    """
    Agent which makes noisy buy and sell prices around market_prices
    """

    def __init__(self,
                 agent_id: int = None,
                 delta: float = None,
                 position: int = 0,
                 pnl: float = None,
                 buy_price: float = None,
                 sell_price: float = None,
                 all_trades: np.ndarray = None,
                 buy_volume: float = None,
                 sell_volume: float = None,
                 epsilon: float = 0.1,
                 state_size: int = 2,
                 lr: float = 0.1,
                 alpha: float = 0.6,
                 noise_range: Tuple = [0.01, 0.1],
                 gamma: float = 0.99,
                 nn_parameters: dict = {"n_layers": 10, "n_units": 20, "n_features": 11, "batch_size": 1,
                                        "dense_units": 1, "n_timepoints": 16, "n_epochs": 20},
                 function_approximator: str = "rnn"):

        """
        Constructor
        :param latency: latency when matching agents in the market environment
        """
        self.agent_class = "RL"
        self.agent_id = agent_id
        self.delta = delta
        self.latency = delta
        self.position = position
        self.pnl = pnl
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.all_trades = all_trades if all_trades else np.array([0, 0])
        self.buy_volume = buy_volume
        self.sell_volume = sell_volume
        self.noise_range = noise_range
        self.random_agent_price = None
        self.epsilon = epsilon
        self.lr = lr
        self.alpha = alpha
        self.state_size = state_size
        self.gamma = gamma
        self.nn_parameters = nn_parameters
        self.data = np.ndarray(shape = (0, self.nn_parameters["n_features"]))
        if function_approximator == "rnn":
            self.model = self.rnn_model()

    def calculate_buy_price(self, state: dict) -> float:
        """
        Calculates buy price

        :param state: market state information
        :return: buy price
        """
        buy_price = self.random_agent_price * (
                    1 - np.random.uniform(low=self.noise_range[0], high=self.noise_range[1] - 0.02))
        buy_price = np.maximum(buy_price, 0)
        return buy_price

    def calculate_sell_price(self, state: dict) -> float:
        """
        Calculates sell price

        :param state: market state information
        :return: sell price
        """
        sell_price = self.random_agent_price * (
                    1 + np.random.uniform(low=self.noise_range[0], high=self.noise_range[1]))
        sell_price = np.maximum(sell_price, 0)
        return sell_price

    def calculate_buy_volume(self, state: dict) -> float:
        """
        Calculates buy price

        :param state:
        :return:
        """
        volume = np.random.randint(0, 3)

        return volume

    def calculate_sell_volume(self, state: dict) -> float:
        """
        Calculates sell price

        :param state:
        :return:
        """
        volume = np.random.randint(0, 3)

        return volume

    def calculate_profit_and_loss(self, state: dict) -> NoReturn:
        """
        Calculates profit and loss

        :param state: market state information
        :return: total profit and loss
        """
        realized_value = np.sum(self.all_trades[:, 0] * self.all_trades[:, 1])
        unrealized_value = self.position * state["market_prices"][-1] * (1 - state["slippage"])

        self.pnl = realized_value + unrealized_value

    def create_features(self, state):
        ma1 = np.average(state["market_prices"][-50:])
        ma2 = np.average(state["market_prices"][-200:])
        trend_feature = ma1 / ma2
        spread_feature = np.round(state["mean_buy_price"] - state["mean_sell_price"], 1)
        feature_list = [ma1, ma2, trend_feature, spread_feature]
        return feature_list

    def store_data(self, state) -> NoReturn:
        last_pnl = self.pnl
        self.calculate_profit_and_loss(state)
        self.reward = self.pnl - last_pnl
        #ma1 = np.average(state["market_prices"][-50:])
        #ma2 = np.average(state["market_prices"][-200:])
        #trend_feature = ma1 / ma2
        #spread_feature = np.round(state["mean_buy_price"] - state["mean_sell_price"], 1)
        features = self.create_features(self, state)
        # data = np.array([ma1, ma2, trend_feature, spread_feature, state["market_prices"][-1],
        #                      self.position, self.buy_volume, self.sell_volume, self.buy_price,
        #                      self.sell_price, self.reward])
        data = np.array([features[0], features[1], features[2], features[3], state["market_prices"][-1],
                             self.position, self.buy_volume, self.sell_volume, self.buy_price,
                             self.sell_price, self.reward])
        self.data = np.vstack((self.data, data))
        
    def data_to_feather(self) -> NoReturn:
        pd.DataFrame(self.data, columns = ['ma1', 'ma2', 'trend_feature',
                                               'spread_feature', 'market_prices', 'position',
                                               'buy_volume', 'sell_volume', 'buy_price',
                                               'sell_price', 'reward']).to_feather('data/data.feather')
    
    def scale_and_reshape(self, data):
        feature_vector = data.iloc[:, :-1]
        col_names = feature_vector.columns
        scaler = MinMaxScaler(feature_range=(0, 1))
        feature_vector = pd.DataFrame(scaler.fit_transform(feature_vector), columns = col_names)
        
        # RESHAPING
        rows_x = len(feature_vector[:,0])
        x = feature_vector[range(self.nn_parameters["n_timepoints"] * rows_x), :]
        feature_vector_reshaped = np.reshape(x, (rows_x, self.nn_parameters["n_timepoints"], self.nn_parameters["n_features"]))
        return feature_vector_reshaped
        
    def train_model(self):

        data = pd.DataFrame(self.data, columns = ['ma1', 'ma2', 'trend_feature',
                                        'spread_feature', 'market_prices', 'position',
                                        'buy_volume', 'sell_volume', 'buy_price',
                                        'sell_price', 'reward'])
        reward_vector = data.iloc[:, -1].values
        
        disc_reward = np.zeros_like(reward_vector)
        cum_reward = 0
        for i in reversed(range(len(reward_vector))):
            cum_reward = cum_reward * self.gamma + reward_vector[i]
            disc_reward[i] = cum_reward
            
        feature_vector_reshaped = self.scale_and_reshape(data)
        # TRAIN
        self.model.fit(feature_vector_reshaped, disc_reward, epochs=self.nn_parameters["n_epochs"], batch_size=1, verbose=2)


    def rnn_model(self):
        model = Sequential()
        #     model.add(SimpleRNN(hidden_units, input_shape=input_shape, 
        #                         activation=activation[0]))
        model.add(LSTM(self.nn_parameters["n_units"], batch_input_shape=(self.nn_parameters["batch_size"], self.time_steps, self.nn_parameters["n_features"]), stateful=True, return_sequences=True))
        model.add(LSTM(self.nn_parameters["n_units"], batch_input_shape=(self.nn_parameters["batch_size"], self.time_steps, self.nn_parameters["n_features"]), stateful=True))
        model.add(Dense(units=self.nn_parameters["dense_units"], activation="linear"))
        model.compile(loss='mean_squared_error', optimizer='adam')
        return model
   
    def predict_state(self, state):
        state_feature_vector = self.create_features(state)
        data = pd.DataFrame(state_feature_vector)
        state_feature_vector_reshaped = self.scale_and_reshape(data)
        prediction = self.model.predict(state_feature_vector_reshaped, batch_size = 1)
        return prediction
    
    def take_action(self):
        grid = []
        predictions = []
        for i in grid:
            predictions.append(self.predict_state())
    
    def nn(self, hidden_units, dense_units, input_shape, activation):
        model = Sequential()
        model.add(SimpleRNN(hidden_units, input_shape=input_shape, 
                            activation=activation[0]))
        model.add(Dense(units=dense_units, activation=activation[1]))
        model.compile(loss='mean_squared_error', optimizer='adam')
        return model


    def take_action(self, state) -> NoReturn:
        # Volume and price range 
        vol_range_lower, vol_range_upper = 0, 10
        price_range_lower, price_range_upper = state["market_prices"][-1] * 0.99, state["market_prices"][-1] * 1.01
        
        # Update volumes
        self.buy_volume = random.randint(vol_range_lower, vol_range_upper)
        self.sell_volume = random.randint(vol_range_lower, vol_range_upper)

        # Update prices
        self.buy_price = random.uniform(price_range_lower, price_range_upper)
        self.sell_price = random.uniform(price_range_lower, price_range_upper)

        self.buy_order = pd.DataFrame(np.array([[self.buy_price, self.buy_volume, self.latency, self.agent_id]]),
                              columns=["buy_price", "buy_volume", "latency", "agent_id"],
                              index=[self.agent_id])
        self.sell_order = pd.DataFrame(np.array([[self.sell_price, self.sell_volume, self.latency, self.agent_id]]),
                                       columns=["sell_price", "sell_volume", "latency", "agent_id"],
                                       index=[self.agent_id])

    def update(self, state: dict) -> NoReturn:
        """
        Updates agents ask and bid prices, and corresponding volumes, when new state is provided

        :param state: market state information
        :return: NoReturn
        """
        # Update trades (pays cash buys and receive for sells) and position

        temp_state = state
        self.last_price = state["market_prices"][-1]
        self.store_data(temp_state)
        self.take_action(state)


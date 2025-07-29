
import numpy as np
import pandas as pd
import math
from scipy.stats import norm


class greek:
    """
    A class to calculate implied volatility (IV) and Greek values for options.
    Supports both scalar float inputs and Pandas Series for batch calculations.
    """

    @staticmethod
    def iv(S, K, R, D,P, flag='C'):
        """
        Calculate the implied volatility (IV) using a binary search method.

        Parameters:
        - S (float or pd.Series): Spot price
        - K (float or pd.Series): Strike price
        - R (float or pd.Series): Interest rate (decimal form, e.g., 0.08 for 8%)
        - D (float or pd.Series): Days to expiration
        - P (float or pd.Series): Last traded price of option
        - flag (str or pd.Series, optional): Option type C/P

        Returns:
        - float or pd.Series: Implied volatility in decimal form
        """

        t = np.where(D > 0, D / 365, 1)  # Convert days to years, avoid division by zero
        high, low = 500.0, 0.0
        mid = (high + low) / 2

        for i in range(10000):	# To avoid infinite loops

            mid = (high + low) / 2

            #calculate guess call and put prices
            # Replace math functions with numpy
            gvol = mid  # Guess vol for calculating option prices
            x = gvol * np.sqrt(t)  # Use np.sqrt instead of ** 0.5
            d1 = (np.log(S / K) + (R + (gvol**2) / 2) * t) / x  # Use np.log instead of log
            d2 = d1 - x
            call = S * norm.cdf(d1) - K * np.exp(-R * t) * norm.cdf(d2)  # Use np.exp instead of e**
            put = K * np.exp(-R * t) * norm.cdf(-d2) - S * norm.cdf(-d1)  # Use np.exp instead of e**

            estimate = call if flag.lower() == 'c' else put

            if mid < 0.00001:
                mid = 0.00001

            if round(estimate, 6) == P: 
                break
            elif estimate > P: 
                high = mid
            elif estimate < P: 
                low = mid

        # print(f'strike:{K}, Price:{P}, estimate: {estimate}, flag:{flag}, IV:{mid}')
        return round(mid,6)


    @staticmethod
    def greeks(S, K, R, D, P, flag='C'):
        """
        Calculate first and second-order Greeks for options.

        Parameters:
        - S (float or pd.Series): Spot price
        - K (float or pd.Series): Strike price
        - R (float or pd.Series): Interest rate (decimal form, e.g., 0.08 for 8%)
        - D (float or pd.Series): Days to expiration
        - P (float or pd.Series): Last traded price of option
        - flag (str or pd.Series, optional): Option type C/P

        Returns:
        - dict: A dictionary containing option Greeks and implied volatility
        """
        t = np.where(D > 0, D / 365, 1)
        T = np.sqrt(t)

        iv = greek.iv(S, K, R, D, P, flag)

        x = iv * T

        # print(S,K,R,D,P,flag,iv,x)

        d1 = (np.log(S / K) + (R + (iv ** 2) / 2) * t) / x
        d2 = d1 - x
        d1_pdf = norm.pdf(d1)
        d2_cdf = norm.cdf(d2)

        delta_ce = norm.cdf(d1) 
        delta_pe = -norm.cdf(-d1)

        vega = (S * d1_pdf * T) / 100
        theta = ((-S * d1_pdf * iv) / (2 * T) - R * K * np.exp(-R * t) * d2_cdf) / 365

        rho = K * t * np.exp(-R * t) * d2_cdf / 100

        gamma = d1_pdf / (S * iv * T)
        vanna = -d1_pdf * (d2 / iv)

        charm = -d1_pdf * (2*(0.5 * iv **2)*t - d2 * x) / (2 * t * x)
        #charm is same for ce and pe. For pe it is negative and ce it is position

        speed = - gamma * (d1/x + 1) / S
        vomma = vega * (d1 * d2)/iv

        #print(f'strike:{K}, delta_ce:{delta_ce}, delta_pe: {delta_pe}, vega:{vega}, theta:{theta}, IV:{iv}')

        return {
            'iv': float(np.round(iv * 100, 2)),
            'delta_ce': float(np.round(delta_ce, 4)),
            'delta_pe': float(np.round(delta_pe, 4)),
            'vega': float(np.round(vega, 2)),
            'theta': float(np.round(theta, 2)),
            'rho': float(np.round(rho, 2)),
            'gamma': float(np.round(gamma, 4)),
            'vanna': float(np.round(vanna, 2)),
            'charm': float(np.round(charm, 2)),
            'speed': float(np.round(speed, 10)),
            'vomma': float(np.round(vomma, 2))
        }



    @staticmethod
    def iv_vectorized(S, K, R, D, P, flag):

        t = np.where(D > 0, D / 365, 1)
        high = np.full_like(S, 500.0, dtype=np.float64)
        low = np.full_like(S, 0.0, dtype=np.float64)
        mid = (high + low) / 2

        for _ in range(100):  # fewer iterations needed for most cases
            mid = (high + low) / 2
            gvol = mid
            x = gvol * np.sqrt(t)
            d1 = (np.log(S / K) + (R + (gvol**2) / 2) * t) / x
            d2 = d1 - x

            call = S * norm.cdf(d1) - K * np.exp(-R * t) * norm.cdf(d2)
            put = K * np.exp(-R * t) * norm.cdf(-d2) - S * norm.cdf(-d1)

            # estimate = call if flag == 'c' else put → vectorized
            estimate = np.where(np.char.lower(flag) == 'c', call, put)

            high = np.where(estimate > P, mid, high)
            low = np.where(estimate < P, mid, low)

        return np.round(mid, 6)


    @staticmethod
    def compute_greeks_vectorized(
        df: pd.DataFrame,
        columns: dict = None
    ) -> pd.DataFrame:
        """
        Computes option Greeks in a vectorized way.

        Parameters:
            df (pd.DataFrame): Input DataFrame
            columns (dict): Optional column name mapping. Keys:
                - sfut_price
                - strike_price
                - dte
                - count
                - ce_ltp
                - pe_ltp
        
        Returns:
            pd.DataFrame: DataFrame with Greeks added
        """

        default_cols = {
            "sfut_price": "sfut_price",
            "strike_price": "strike_price",
            "dte": "dte",
            "count": "count",
            "ce_ltp": "ce_ltp",
            "pe_ltp": "pe_ltp"
        }

        # Override defaults with user-defined columns
        if columns:
            default_cols.update(columns)

        # Extract column values using mapping
        S = df[default_cols["sfut_price"]].to_numpy()
        K = df[default_cols["strike_price"]].to_numpy()
        D = df[default_cols["dte"]].to_numpy()
        count = df[default_cols["count"]].to_numpy()
        ce_ltp = df[default_cols["ce_ltp"]].to_numpy()
        pe_ltp = df[default_cols["pe_ltp"]].to_numpy()

        # Option price and flag
        P = np.where(count > 0, ce_ltp, pe_ltp)
        flag = np.where(count > 0, 'c', 'p')

        R = 0  # risk-free rate
        t = D
        T = np.sqrt(t)

        iv = greek.iv_vectorized(S, K, R, D, P, flag)

        x = iv * T
        with np.errstate(divide='ignore', invalid='ignore'):
            d1 = (np.log(S / K) + (R + (iv ** 2) / 2) * t) / x
            d2 = d1 - x
            d1_pdf = norm.pdf(d1)
            d2_cdf = norm.cdf(d2)

            delta_ce = norm.cdf(d1)
            delta_pe = -norm.cdf(-d1)

            vega = (S * d1_pdf * T) / 100
            theta = ((-S * d1_pdf * iv) / (2 * T) - R * K * np.exp(-R * t) * d2_cdf) / 365
            rho = K * t * np.exp(-R * t) * d2_cdf / 100
            gamma = d1_pdf / (S * iv * T)
            vanna = -d1_pdf * (d2 / iv)

        df_out = pd.DataFrame({
            "iv": np.round(iv * 100, 2),
            "delta_ce": np.round(delta_ce, 2),
            "delta_pe": np.round(delta_pe, 2),
            "vega": np.round(vega, 2),
            "theta": np.round(theta, 2),
            'rho': np.round(rho, 4),
            "gamma": np.round(gamma, 4),
            "vanna": np.round(vanna, 4),
        })

        df = pd.concat([df.reset_index(drop=True), df_out], axis=1)
        df = df.replace([np.inf, -np.inf], np.nan).fillna(0)

        return df



    @staticmethod
    def compute_exposure(df):
        def calculate_exposure(row):
            return {
                'dex_ce': int(row['delta_ce'] * row['ce_oi'] * row['lot_size']),
                'dex_pe': int(row['delta_pe'] * row['pe_oi'] * row['lot_size']),
                'gex_ce': int(row['gamma'] * row['ce_oi'] * row['lot_size']),
                'gex_pe': int(row['gamma'] * row['pe_oi'] * row['lot_size']),
                'vex_ce': int(row['vanna'] * row['ce_oi'] * row['lot_size']),
                'vex_pe': int(row['vanna'] * row['pe_oi'] * row['lot_size']),
                'charmex_ce': int(row['charm'] * row['ce_oi'] * row['lot_size']),
                'charmex_pe': int(-row['charm'] * row['pe_oi'] * row['lot_size']),
                'speedex_ce': int(row['speed'] * row['ce_oi'] * row['lot_size']),
                'speedex_pe': int(row['speed'] * row['pe_oi'] * row['lot_size']),
                'vommaex_ce': int(row['vomma'] * row['ce_oi'] * row['lot_size']),
                'vommaex_pe': int(row['vomma'] * row['pe_oi'] * row['lot_size'])
            }

        df_ex = df.apply(calculate_exposure, axis=1)

        # Convert list of dicts into a DataFrame and concatenate
        df = pd.concat([df, pd.DataFrame(df_ex.tolist())], axis=1)

        return df
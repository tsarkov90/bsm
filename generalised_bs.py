from math import log, sqrt, exp
try:
    from scipy.stats import norm

except ImportError:
    print('Program requires scipy to work properly')
    print('How to install: https://www.scipy.org/install.html')
    print('pip install scipy')


# Black_Scholes(S, K, r, q, volatility, T, is_fut: bool, dividends: list, result)
class BS:

    def __init__(self, spot_price, strike_price, risk_free_rate, exp_time, volatility, div_yield=0.0, dividends=None, is_fut=False):

        # if underlying_type = 'currency': div_yield = foreign risk-free rate
        # if underlying_type = 'index' : div_yield
        # if underlying_type = 'future': div_yiled = None
        # if underlying_type = 'equity': check if dividends is not None

        self.S = spot_price
        self.K = strike_price
        self.r = risk_free_rate / 100  # to decimals
        self.T = exp_time / 365  # to years
        self.sigma = volatility / 100  # to decimals

        self.q = div_yield / 100  # to decimals

        for i in ['call_price', 'put_price', 'call_delta', 'put_delta',
                  'call_theta', 'put_theta', 'call_rho', 'put_rho',
                  'vega', 'gamma']:
            self.__dict__[i] = None

        self.pv_K = 0.0
        self.sigma_root_T = 0.0
        self.pv_div = 0.0

        if dividends:
            self.q = 0.0
            for div in dividends:
                if 0 < div[1] / 365 <= self.T:
                    self.pv_div += div[0] * exp(-self.r * div[1] / 365)

        if is_fut:
            self.q = self.r

        if self.pv_div > 0:
            self.q = 0
            self.S -= self.pv_div
            self.pv_div = 1
        else:
            self.pv_div = exp(-self.q * self.T)
            self.S *= self.pv_div

        self.pv_K = self.K * exp(-self.r * self.T)
        self.sigma_root_T = self.sigma * sqrt(self.T)

        self.d1 = log(self.S / self.pv_K) / \
            self.sigma_root_T + 0.5 * self.sigma_root_T
        self.d2 = self.d1 - self.sigma_root_T

        [self.call_price, self.put_price] = self._price()

        [self.call_delta, self.put_delta] = self._delta()
        [self.call_theta, self.put_theta] = self._theta()
        [self.call_rho, self.put_rho] = self._rho()
        self.vega = self._vega()
        self.gamma = self._gamma()

    def _price(self):
        '''Returns the option price: [Call price, Put price]'''
        if self.sigma == 0 or self.T == 0:
            call = max(0.0, self.S - self.K)
            put = max(0.0, self.K - self.S)

            return [call, put]

        if self.K == 0:
            # raise ZeroDivisionError('The strike price cannot be zero')
            return -999999

        call = self.S * norm.cdf(self.d1) - self.pv_K * norm.cdf(self.d2)
        put = -self.S * norm.cdf(-self.d1) + self.pv_K * norm.cdf(-self.d2)

        return [call, put]

    def _delta(self):
        '''Returns the option delta: [Call delta, Put delta]'''
        if self.sigma == 0 or self.T == 0:
            call = 1.0 if self.S > self.K else 0.0
            put = -1.0 if self.S < self.K else 0.0

            return [call, put]

        if self.K == 0:
            # raise ZeroDivisionError('The strike price cannot be zero')
            return -999999

        call = self.pv_div * norm.cdf(self.d1)
        put = self.pv_div * (norm.cdf(self.d1) - 1)

        return [call, put]

    def _vega(self):
        '''Returns the option vega'''
        if self.sigma == 0 or self.T == 0:
            return 0.0

        if self.K == 0:
            # raise ZeroDivisionError('The strike price cannot be zero')
            return -999999

        return self.S * norm.pdf(self.d1) * sqrt(self.T) / 100

    def _theta(self):
        '''Returns the option theta: [Call theta, Put theta]'''
        call = (-self.S * norm.pdf(self.d1) * self.sigma_root_T / (2 * self.T) + self.q *
                self.S * norm.cdf(self.d1) - self.r * self.pv_K * norm.cdf(self.d2))

        put = (-self.S * norm.pdf(self.d1) * self.sigma_root_T / (2 * self.T) - self.q *
               self.S * norm.cdf(-self.d1) + self.r * self.pv_K * norm.cdf(-self.d2))

        return [call / 365, put / 365]

    def _rho(self):
        '''Returns the option rho: [Call rho, Put rho]'''
        call = self.pv_K * self.T * norm.cdf(self.d2)
        put = -self.pv_K * self.T * norm.cdf(-self.d2)

        return [call / 100, put / 100]

    def _gamma(self):
        '''Returns the option gamma'''
        return self.pv_div * norm.pdf(self.d1) / (self.S * self.sigma_root_T / self.pv_div)
    

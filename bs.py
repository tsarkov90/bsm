from math import log, sqrt, exp
try:
    from scipy.stats import norm

except ImportError:
    print('Program requires scipy to work properly')
    print('How to install: https://www.scipy.org/install.html')
    print('pip install scipy')


class BS:
    '''
    Black Scholes Model
    Used for pricing European otions on stocks (including with dividends)
    '''
    def __init__(self, args, sigma, dividends=None):
        self.S = args[0]
        self.K = args[1]
        self.r = args[2] / 100
        self.T = args[3] / 365
        self.sigma = sigma / 100
        
        self.F = None
        
        for i in ['call_price', 'put_price', 'call_delta', 'put_delta',
                  'call_theta', 'put_theta', 'call_rho', 'put_rho',
                  'vega', 'gamma']:
            self.__dict__[i] = None
            
        if dividends:
            self.F = self.S
            for elem in dividends:
                red = elem[0] / (1 + self.r)**(elem[1] / 365)
                self.F -= red
            
        
        a = self.sigma * sqrt(self.T)
        self.d1 = (log(self.S / self.K) + \
                    (self.r + (self.sigma**2) / 2) * self.T) / a
        self.d2 = self.d1 - a
        
        [self.call_price, self.put_price] = self._price()
        
        [self.call_delta, self.put_delta] = self._delta()
        [self.call_theta, self.put_theta] = self._theta()
        [self.call_rho, self.put_rho] = self._rho()
        
        self.vega = self._vega()
        self.gamma = self._gamma()
        
        # TODO: implied volatility and proving parity
        
    def _price(self):
        '''Returns the option price: [Call price, Put price]'''
        if self.sigma == 0 or self.T == 0:
            if self.F:
                self.S = self.F
            call = max(0.0, self.S - self.K)
            put = max(0.0, self.K - self.S)
            
            return [call, put]
        
        if self.K == 0:
#             raise ZeroDivisionError('The strike price cannot be zero')
            return -999999
            
        if self.F:
            call = exp(-self.r * self.T) * \
                (self.F * norm.cdf(self.d1) - self.K * norm.cdf(self.d2))
            
            put = exp(-self.r * self.T) * \
                (self.K * norm.cdf(-self.d2) - self.F * norm.cdf(-self.d1))
        
        else:
            call = norm.cdf(self.d1) * self.S - \
                norm.cdf(self.d2) * self.K * exp(-self.r * self.T)
            
            put = norm.cdf(-self.d2) * self.K * exp(-self.r * self.T) - \
                norm.cdf(-self.d1) * self.S
            
        return [call, put]
    
    def _delta(self):
        '''Returns the option delta: [Call delta, Put delta]'''
        if self.sigma == 0 or self.T == 0:
            if self.F:
                self.S = self.F
            call = 1.0 if self.S > self.K else 0.0
            put = -1.0 if self.S < self.K else 0.0

            return [call, put]
        
        if self.K == 0:
#             raise ZeroDivisionError('The strike price cannot be zero')
            return -999999
            
        if self.F:
            call = exp(-self.r * self.T) * norm.cdf(self.d1)
            put = -exp(-self.r * self.T) * norm.cdf(-self.d1)
        
        else:
            call = norm.cdf(self.d1)
            put = -norm.cdf(-self.d1)

        return [call, put]
    
    def _vega(self):
        '''Returns the option vega'''
        if self.sigma == 0 or self.T == 0:
            return 0.0
        
        if self.K == 0:
#             raise ZeroDivisionError('The strike price cannot be zero')
            return -999999

        if self.F:
            call = self.F * exp(-self.r * self.T) * \
                norm.pdf(self.d1) * sqrt(self.T)
            
        else:
            call = self.S * norm.pdf(self.d1) * sqrt(self.T)
            
        return call / 100
    
    def _theta(self):
        '''Returns the option theta: [Call theta, Put theta]'''
        if self.F:
            first = - (self.F * exp(-self.r * self.T) * self.sigma) / \
                (2 * sqrt(self.T))
            second = self.r * self.K * exp(-self.r * self.T)
            third = self.r * self.F * exp(-self.r * self.T)
            
            call = first * norm.pdf(self.d1) - \
                second * norm.cdf(self.d2) + third * norm.cdf(self.d1)
            put = first * norm.pdf(-self.d1) + \
                second * norm.cdf(-self.d2) - third * norm.cdf(-self.d1)
            
        else:
            first = -(self.S * self.sigma) / (2 * sqrt(self.T))
            second = self.r * self.K * exp(-self.r * self.T)
            
            call = first * norm.pdf(self.d1) - second * norm.cdf(self.d2)
            put = first * norm.pdf(self.d1) + second * norm.cdf(-self.d2)
            
        return [call / 365, put / 365]
    
    def _rho(self):
        '''Returns the option rho: [Call rho, Put rho]'''
        if self.F:
            first = self.K * self.T * exp(-self.r * self.T)
            
            call = first * norm.cdf(self.d2)
            put = -first * norm.cdf(-self.d2)
        
        else:

            call = self.K * self.T * exp(-self.r * self.T) * norm.cdf(self.d2)
            put = -self.K * self.T * exp(-self.r * self.T) * norm.cdf(-self.d2)

        return [call / 100, put / 100]
        
    def _gamma(self):
        '''Returns the option gamma'''
        if self.F:
            call = exp(-self.r * self.T) * norm.pdf(self.d1) / \
                (self.F * self.sigma * sqrt(self.T))
        else:
            call = norm.pdf(self.d1) / (self.S * self.sigma * sqrt(self.T))
            
        return call
from PyQt5 import QtWidgets
from mydesign import Ui_MainWindow
import sys
import datetime
from bs import BS


class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        for i in ['spot_price', 'strike_price', 'risk_rate', 'exp_time', 'sigma']:
            self.__dict__[i] = ''

        self.dividends = []
        self.info_text = ''

        self.ui.calculateButton.clicked.connect(self.calculateButtonClicked)
        self.ui.divAddButton.clicked.connect(self.divAddButtonClicked)
        self.ui.divBox.activated[str].connect(self.onActivated)
        self.ui.divDeleteButton.clicked.connect(self.divDeleteButtonClicked)
        self.ui.divAllDeleteButton.clicked.connect(
            self.divAllDeleteButtonClicked)

    def calculateButtonClicked(self):
        self.info_text = ''
        try:
            self.spot_price = float(eval(self.ui.spotPrice.text().replace(',', '.')))
            self.info_text += f"Spot Price: {self.spot_price}\n"
        except:
            self.info_text += "Enter the spot price...\n"

        try:
            self.strike_price = float(eval
                (self.ui.strikePrice.text().replace(',', '.')))
            self.info_text += f"Strike Price: {self.strike_price}\n"
        except:
            self.info_text += "Enter the strike price...\n"

        try:
            self.risk_rate = float(self.ui.riskFreeRate.text().replace(',', '.'))
            self.info_text += f"Risk-free rate: {self.risk_rate}%\n"
        except:
            self.info_text += "Enter the risk-free rate...\n"

        try:
            self.sigma = float(self.ui.volatility.text().replace(',', '.'))
            self.info_text += f"Volatility: {self.sigma}%\n"
        except:
            self.info_text += "Enter the volatility...\n"

        if days_to_date(self.ui.startDate.text(), self.ui.expDate.text()) > 0:
            self.exp_time = days_to_date(
                self.ui.startDate.text(), self.ui.expDate.text())
            self.info_text += f"Start Date : {self.ui.startDate.text()}\nExpiration Date: {self.ui.expDate.text()}\nExpires in {self.exp_time} days\n"

        else:
            self.info_text += "Check the expiration date. It must be later than start date\n"

        if self.dividends:
            self.info_text += "Including dividents payments"

        self.ui.infoText.setText(self.info_text)
        if 'Enter' in self.info_text:
            return

        bs = BS([self.spot_price, self.strike_price, self.risk_rate,
                 self.exp_time], sigma=self.sigma, dividends=self.dividends)

        self.ui.callPrice.setText(str(round(bs.call_price, 6)))
        self.ui.putPrice.setText(str(round(bs.put_price, 6)))

        self.ui.callDelta.setText(str(round(bs.call_delta, 6)))
        self.ui.putDelta.setText(str(round(bs.put_delta, 6)))

        self.ui.gamma.setText(str(round(bs.gamma, 6)))
        self.ui.vega.setText(str(round(bs.vega, 6)))

        self.ui.callRho.setText(str(round(bs.call_rho, 6)))
        self.ui.putRho.setText(str(round(bs.put_rho, 6)))

        self.ui.callTheta.setText(str(round(bs.call_theta, 6)))
        self.ui.putTheta.setText(str(round(bs.put_theta, 6)))

        self.ui.d1.setText(str(round(bs.d1, 6)))
        self.ui.d2.setText(str(round(bs.d2, 6)))

    def divAddButtonClicked(self):
        div_pay, div_time = '', ''
        self.info_text = ''
        try:
            div_pay = float(eval(self.ui.divPayment.text().replace(',', '.')))
        except:
            self.info_text += "Check divident payments\n"

        if days_to_date(self.ui.startDate.text(), self.ui.divDate.text()) > 0:
            div_time = days_to_date(
                self.ui.startDate.text(), self.ui.divDate.text())
        else:
            self.info_text += "Check divident payments. The divident payment date must be later than start date\n"

        if [div_pay, div_time] not in self.dividends and div_pay and div_time:
            self.dividends.insert(0, [div_pay, div_time])
            self.ui.divBox.insertItem(0,
                                      f"{div_pay} at {self.ui.divDate.text()} (in {div_time} days)")
            self.ui.divBox.setCurrentIndex(0)

        self.ui.infoText.setText(self.info_text)

    def onActivated(self, text):
        words = text.split(' ')
        self.ui.divPayment.setText(words[0])
        self.ui.divDate.setDate(
            datetime.datetime.strptime(words[2], '%d.%m.%Y').date())

    def divDeleteButtonClicked(self):
        div_pay = float(self.ui.divPayment.text().replace(',', '.'))
        div_time = days_to_date(
            self.ui.startDate.text(), self.ui.divDate.text())

        itd = None
        for i, elem in enumerate(self.dividends):
            if elem == [div_pay, div_time]:
                itd = i

        try:
            self.dividends.remove([div_pay, div_time])
            self.ui.divBox.removeItem(itd)

        except:
            self.ui.infoText("This dividend payment is not found")

    def divAllDeleteButtonClicked(self):
        self.dividends = []
        self.ui.divBox.clear()
        self.ui.infoText.setText("All dividend payments has been removed")


def days_to_date(date_str1, date_str2):
    date1 = datetime.datetime.strptime(date_str1, "%d.%m.%Y")
    date2 = datetime.datetime.strptime(date_str2, "%d.%m.%Y")
    diff = date2 - date1

    return int(diff.days)


app = QtWidgets.QApplication(sys.argv)
application = mywindow()
application.show()

sys.exit(app.exec())

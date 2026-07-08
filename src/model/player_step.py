import utils.player
import utils.train_cards

class PlayerStepFSM:
    def __init__(self):
        self.state = "new"
        self.states = {
            "new": self._handle_new,
            "paid": self._handle_paid,
            "shipped": self._handle_shipped,
        }

    def _handle_new(self, event):
        if event == "pay":
            print("Заказ оплачен")
            return "paid"
        return "new"

    def _handle_paid(self, event):
        if event == "ship":
            print("Заказ отправлен")
            return "shipped"
        return "paid"

    def _handle_shipped(self, event):
        print("Заказ уже отправлен, ничего не делаем")
        return "shipped"

    def dispatch(self, event):
        if self.state not in self.states:
            raise RuntimeError(f"Нет состояния {self.state}")
        self.state = self.states[self.state](event)

# Использование
order = OrderFSM()
order.dispatch("pay")   # Заказ оплачен
order.dispatch("ship")  # Заказ отправлен
order.dispatch("pay")   # Заказ уже отправлен, ничего не делаем
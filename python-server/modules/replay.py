from strategy import BasicStrategy


class Replay(BasicStrategy):
    def __init__(self, trade_id, socket=None):
        super().__init__(trade_id, socket)
        cursor = self.dealer.user.cursor()
        cursor.execute('select trade_state from trade_list where t_id= %s', self.trade_id)
        self.agent_id = cursor.fetchall()[0][0].split('.')[0]
        cursor.close()

    def get_order(self, s_id, curr):
        ids, amount = [], []
        cursor = self.dealer.user.cursor()
        cursor.execute('select stock_id,volume,direction,price from trade_detail ' +
                       'where transaction_datetime=%s and t_id= %s', [self.n_time, self.agent_id])
        for item in cursor:
            ids.append(item[0])
            amount.append(item[1])
        cursor.close()
        return ids, amount

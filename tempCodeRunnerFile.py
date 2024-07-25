                    self.worker1 = worker_Thread(capturing_flg=False,predictioin_flg=True,main_window=self)
                    self.worker1.start()
                    self.predictioin_flg=False
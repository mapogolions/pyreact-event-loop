    # def test_read_streams_are_handled_earlier_than_write_streams(self):
    #     mock, loop = unittest.mock.Mock(), self.create_event_loop()
    #     stream, another = self.create_socket_pair()

    #     def cleanup(stream):
    #         nonlocal loop, mock
    #         mock("write")
    #         loop.remove_read_stream(stream)
    #         loop.remove_write_stream(stream)
    #         stream.close()

    #     loop.add_read_stream(stream, lambda *args: mock("read"))
    #     loop.add_write_stream(stream, cleanup)
    #     another.close()
    #     loop.run()
    #     self.close_sockets(stream, another)
    #     self.assertEqual(
    #         [unittest.mock.call("read"), unittest.mock.call("write")],
    #         mock.call_args_list
    #     )





# def test_BUG_operation_on_closed_socket_crash(self):
    #     """All loops are crashed"""
    #     mock = unittest.mock.Mock()
    #     rstream, wstream = self.create_socket_pair()
    #     loop = SelectLoop()
    #     loop.add_read_stream(rstream, lambda stream: mock(1))
    #     loop.add_write_stream(wstream, lambda stream:  mock(2))
    #     wstream.close() # bug here
    #     self.next_tick(loop)
    #     self.close_sockets(rstream, wstream)
    #     self.assertEqual(
    #         [unittest.mock.call(1), unittest.mock.call(2)],
    #         mock.call_args_list
    #         )

    # def test_read_earlier_than_write_on_different_sockets(self):
    #     """libev: false Loop(libev.EVBACKEND_SELECT), libuv and select: true"""
    #     mock = unittest.mock.Mock()
    #     rstream, wstream = self.create_socket_pair()
    #     loop = LibuvLoop()
    #     loop.add_read_stream(rstream, lambda stream: mock(1))
    #     loop.add_write_stream(wstream, lambda stream:  mock(2))
    #     wstream.send(b"hello")
    #     self.next_tick(loop)
    #     self.close_sockets(rstream, wstream)
    #     self.assertEqual(
    #         [unittest.mock.call(1), unittest.mock.call(2)],
    #         mock.call_args_list
    #     )

    def test_read_and_write_on_the_same_socket(self):
        mock = unittest.mock.Mock()
        rstream, wstream = self.create_socket_pair()
        # loop = SelectLoop() true
        # loop = LibevLoop() true
        loop = LibuvLoop() # only call(2)
        loop.add_read_stream(rstream, lambda stream: mock(1))
        loop.add_write_stream(rstream, lambda stream: mock(2))
        wstream.send(b"Hello")
        self.next_tick(loop)
        self.close_sockets(rstream, wstream)
        self.assertEqual(
            [unittest.mock.call(1), unittest.mock.call(2)],
            mock.call_args_list
        )








    # def test_signal(self):
    #     def cleanup():
    #         nonlocal timer
    #         self.loop.remove_signal(signal.SIGUSR1, cleanup)
    #         self.loop.remove_signal(signal.SIGUSR2, self.mock)
    #         self.loop.cancel_timer(timer)
    #         self.mock("signal")

    #     timer = self.loop.add_periodic_timer(1, lambda: self.mock("timer"))
    #     self.loop.add_signal(signal.SIGUSR2, self.mock)
    #     self.loop.add_signal(signal.SIGUSR1, cleanup)
    #     self.loop.future_tick(lambda: os.kill(os.getpid(), signal.SIGUSR1))
    #     self.loop.run()

    #     self.assertEqual(
    #         [unittest.mock.call("signal")],
    #         self.mock.call_args_list
    #     )

    # def test_signal_multiple_usages_for_the_same_listener(self):
    #     self.loop.add_timer(1, lambda: None)
    #     self.loop.add_signal(signal.SIGUSR1, self.mock)
    #     self.loop.add_signal(signal.SIGUSR1, self.mock)
    #     self.loop.add_timer(0.4, lambda: os.kill(os.getpid(), signal.SIGUSR1))
    #     self.loop.add_timer(
    #         0.9,
    #         lambda: self.loop.remove_signal(signal.SIGUSR1, self.mock)
    #     )
    #     self.loop.run()
    #     self.mock.assert_called_once()







    # IF SEPARETE OK
    # def test_signals_arent_handled_without_the_running_loop(self):
    #     self.loop.add_signal(signal.SIGUSR1, self.mock)
    #     os.kill(os.getpid(), signal.SIGUSR1)
    #     self.mock.assert_not_called()



    # BUG HERE!!!
    # def test_only_signals(self):
    #     def cleanup():
    #         self.mock(20)
    #         self.loop.remove_signal(signal.SIGUSR1, listener)
    #         self.loop.remove_signal(signal.SIGUSR2, cleanup)

    #     # listener = lambda: self.mock(1)
    #     counter = 1
    #     def listener():
    #         nonlocal counter
    #         self.mock(counter)
    #         counter += 1
    #     self.loop.add_signal(signal.SIGUSR1, listener)
    #     self.loop.add_signal(signal.SIGUSR2, cleanup)
    #     for signum in [signal.SIGUSR1, signal.SIGUSR1, signal.SIGUSR2]:
    #         os.kill(os.getpid(), signum)
    #     self.loop.run()
    #     self.assertEqual(
    #         # [unittest.mock.call(1),
    #         #  unittest.mock.call(1),
    #         #  unittest.mock.call(2)],
    #         [],
    #         self.mock.call_args_list
    #     )


    # def test_order_of_signals(self):
    #     ev_loop = libev.Loop()
    #     usr1 = ev_loop.signal(signal.SIGUSR1, lambda *args: self.mock(1), None, 0)
    #     hup = ev_loop.signal(signal.SIGHUP, lambda *args: self.mock(3), None, 0)
    #     hup.start()
    #     usr1.start()
    #     os.kill(os.getpid(), signal.SIGUSR1)
    #     os.kill(os.getpid(), signal.SIGHUP)
    #     ev_loop.start(libev.EVRUN_ONCE)
    #     self.assertEqual(
    #         [unittest.mock.call(1),
    #          unittest.mock.call(3)],
    #         self.mock.call_args_list
    #     )
        # self.loop.add_signal(signal.SIGUSR1, lambda *args: self.mock(1))
        # self.loop.add_signal(signal.SIGUSR2, lambda *args: self.mock(2))
        # self.loop.add_signal(signal.SIGHUP, lambda *args: self.mock(3))
        # for signum in [signal.SIGHUP, signal.SIGUSR2, signal.SIGUSR1]:
        #     os.kill(os.getpid(), signum)
        # self.next_tick()
        # self.assertEqual(
        #     [unittest.mock.call(3),
        #      unittest.mock.call(2),
        #      unittest.mock.call(1)],
        #     self.mock.call_args_list
        # )


    # def test_handle_only_unique_signals_per_tick(self):
    #     mock = unittest.mock.Mock()
    #     counter = 1

    #     def func(*args):
    #         nonlocal counter
    #         mock(counter)
    #         counter += 1

    #     self.loop.add_signal(signal.SIGUSR1, func)
    #     os.kill(os.getpid(), signal.SIGUSR1)
    #     os.kill(os.getpid(), signal.SIGUSR1)
    #     self.next_tick()
    #     os.kill(os.getpid(), signal.SIGUSR1)
    #     os.kill(os.getpid(), signal.SIGUSR1)
    #     self.next_tick()
    #     self.assertEqual(
    #         [unittest.mock.call(1),
    #          unittest.mock.call(2)],
    #         mock.call_args_list
    #     )

    # def test_many_handler_per_signal(self):
    #     mock1 = unittest.mock.Mock()
    #     mock2 = unittest.mock.Mock()
    #     self.loop.add_signal(signal.SIGUSR1, mock1)
    #     self.loop.add_signal(signal.SIGUSR1, mock2)
    #     os.kill(os.getpid(), signal.SIGUSR1)
    #     self.next_tick()
    #     mock1.assert_called_once()
    #     mock2.assert_called_once()
    # ========================================================================









    # def test_signals_keep_the_loop_running(self):
    #     self.loop.add_signal(signal.SIGUSR1, self.mock)
    #     self.loop.add_timer(
    #         0.2,
    #         lambda: self.loop.remove_signal(signal.SIGUSR1, self.mock)
    #     )
    #     self.assert_run_faster_than(0.3)

    # def test_timer_inteval_can_be_far_in_future(self):
    #     timer = self.loop.add_timer(10 ** 6, self.mock)
    #     self.loop.future_tick(lambda: self.loop.cancel_timer(timer))
    #     self.assert_run_faster_than(0.02)

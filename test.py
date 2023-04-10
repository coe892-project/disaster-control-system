from dispatch.dispatch import Dispatch

dispatch = Dispatch([10, 10])
dispatch.generate_map()
dispatch.generate_stations(4)
dispatch.generate_disaster([2, 7], 1)

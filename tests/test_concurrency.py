import os
import threading

from entoolkit import EN_PRESSURE, EPANETProject

NET1_PATH = os.path.join(os.path.dirname(__file__), "networks", "Net1.inp")

def run_simulation(results, thread_id):
    try:
        p = EPANETProject()
        p.open(NET1_PATH, f"test_thread_{thread_id}.rpt", "")
        p.solveH()
        
        idx = p.getnodeindex("10")
        pressure = p.getnodevalue(idx, EN_PRESSURE)
        results[thread_id] = pressure
        
        p.close()
        if os.path.exists(f"test_thread_{thread_id}.rpt"):
            os.remove(f"test_thread_{thread_id}.rpt")
    except Exception as e:
        results[thread_id] = e

def test_multithreading():
    results = {}
    t1 = threading.Thread(target=run_simulation, args=(results, 1))
    t2 = threading.Thread(target=run_simulation, args=(results, 2))
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    assert isinstance(results.get(1), float)
    assert isinstance(results.get(2), float)
    # They should have the same value since it's the same network, 
    # but the key is they both finished without crashing.
    assert results[1] == results[2]
    assert results[1] > 0

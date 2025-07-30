from z3 import Solver, Int, Bool, Implies, Not, sat

def model_state_transitions():
    release_called = Bool("release_called")
    cancel_called = Bool("cancel_called")
    is_released = Bool("is_released")
    is_funded = Bool("is_funded")

    s = Solver()
    s.add(is_funded == True)
    s.add(Implies(release_called, is_released))    
    s.add(Implies(is_released, Not(cancel_called)))

    if s.check() == sat:
        print("⚠️  Invariant violated:")
        print(s.model())
        return False
    else:
        print("✅ No logical violations (cancel blocked after release)")
        return True


def model_balance_invariants():
    balance = Int("balance")
    amount = Int("amount")

    s = Solver()
    s.add(balance >= 0)
    s.add(amount >= 0)
    s.add(balance - amount < 0) 

    if s.check() == sat:
        print("⚠️  Balance underflow possible:")
        print(s.model())
        return False
    else:
        print("✅ Balance constraint holds")
        return True
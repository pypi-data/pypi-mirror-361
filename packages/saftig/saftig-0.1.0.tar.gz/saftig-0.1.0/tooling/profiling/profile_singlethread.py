import os
os.environ["OMP_NUM_THREADS"] = "1" # limit numy to a single thread

import profile

if __name__ == "__main__":
    profile.MULTITHREAD = False
    profile.main()

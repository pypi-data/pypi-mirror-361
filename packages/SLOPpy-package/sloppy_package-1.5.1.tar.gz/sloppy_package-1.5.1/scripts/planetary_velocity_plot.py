"""from classes.kepler_exo import *

# Mass of the star HD189733 (in Solar masses)
#Ms = 0.823
Ms = 1.148
# Mass of the planet (in Solar masses)
#Mp = 1.138 / 1.047348644e3
Mp = 0.69 / 1.047348644e3

K1 = kepler_K1(Mp,Ms,3.52474854657,86.59,0.0082)
print K1


## update
"""

import matplotlib.pyplot as plt
import numpy as np
from SLOPpy.subroutines.constants import *
import argparse
from scipy.optimize import fsolve
from SLOPpy.subroutines.kepler_exo import *

def get_mass(M_star2, M_star1, Period, K1, e0):
    # M_star1, M_star2 in solar masses
    # P in days -> Period is converted in seconds in the routine
    # inclination assumed to be 90 degrees
    # Gravitational constant is given in m^3 kg^-1 s^-2
    # output in m/s
    output = K1 - (2. * np.pi * G_grav * M_sun / 86400.0) ** (1.0 / 3.0) * (1.000 / np.sqrt(1.0 - e0 ** 2.0)) * (
                                                                                                                    Period) ** (
                                                                                                                    -1.0 / 3.0) * (
                      M_star2 * (M_star1 + M_star2) ** (-2.0 / 3.0))
    return output




star_mass = 0.500
P = 5.
i = 90.
e = 0.00


planet_mass = np.arange(0,20, 0.1)
planet_K = planet_mass*0.

for i_val, m_val in enumerate(planet_mass):
    planet_K[i_val] = kepler_K1(m_val  * Mjups , star_mass, P, i, e)/ 1000.

plt.plot(planet_mass, planet_K)
plt.show()

#sampler = args.sample[0]
#file_conf = args.config_file[0]

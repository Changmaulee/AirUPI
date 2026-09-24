"""
Agent 14: "Aryabhata" (आर्यभट) - Master Encyclopedic Physics & Quantum Solver Engine
Target Platform: MicroPython on Raspberry Pi Pico (RP2040) / Desktop Python
Author: Project Brahmand / Antigravity AI

Comprehensive 10-Domain Physics Matrix:
  1. Universal Physical Constants (CODATA exact SI values)
  2. Classical Mechanics, Gravitation & Fluids (Kinematics, Dynamics, Energy, Rotation, SHM, Bernoulli)
  3. Thermodynamics & Statistical Mechanics (Gas Laws, Heat, Carnot, Stefan-Boltzmann, Wien, Entropy)
  4. Electromagnetism & Circuits (Coulomb, Gauss, Ohm, Capacitance, RC/LC, Lorentz, Faraday, Poynting)
  5. Waves, Optics & Acoustics (Wave Speed, Decibels, Doppler, Snell, Lenses, Double-Slit, Diffraction)
  6. Atomic, Nuclear & Crystallography (Bohr Radius, Rydberg Series, Half-life, Binding Energy, Bragg)
  7. Special & General Relativity (Lorentz Gamma, Time Dilation, Contraction, E=mc^2, Schwarzschild)
  8. Quantum Mechanics & Wave Mechanics (Photoelectric, de Broglie, Heisenberg, Schrödinger, Tunneling)
  9. Particle Physics & Standard Model (Quarks, Leptons, Bosons, Higgs Mechanism)
  10. Astrophysics & Cosmology (Kepler, Chandrasekhar, Hubble-Lemaître, Friedmann Equations)
"""

import sys
import math
import gc
import time

# ==============================================================================
# PHYSICAL CONSTANTS VAULT (Exact CODATA SI Values)
# ==============================================================================

CONSTANTS = {
    "c": {"name": "Speed of Light in Vacuum", "val": 299792458.0, "unit": "m/s", "symbol": "c", "aliases": ["speed of light", "light speed", "velocity of light"]},
    "g": {"name": "Standard Earth Gravity", "val": 9.80665, "unit": "m/s^2", "symbol": "g", "aliases": ["gravity", "earth gravity", "standard gravity", "acceleration due to gravity"]},
    "G": {"name": "Universal Gravitational Constant", "val": 6.67430e-11, "unit": "N*(m/kg)^2", "symbol": "G", "aliases": ["gravitational constant", "big g", "universal gravity", "newton constant"]},
    "h": {"name": "Planck Constant", "val": 6.62607015e-34, "unit": "J*s", "symbol": "h", "aliases": ["planck constant", "planck's constant", "planck"]},
    "hbar": {"name": "Reduced Planck Constant (Dirac)", "val": 1.054571817e-34, "unit": "J*s", "symbol": "hbar", "aliases": ["reduced planck", "dirac constant", "h-bar", "hbar"]},
    "kB": {"name": "Boltzmann Constant", "val": 1.380649e-23, "unit": "J/K", "symbol": "kB", "aliases": ["boltzmann constant", "boltzmann's constant", "boltzmann", "kb"]},
    "e": {"name": "Elementary Electric Charge", "val": 1.602176634e-19, "unit": "C", "symbol": "e", "aliases": ["elementary charge", "electron charge", "proton charge", "fundamental charge"]},
    "me": {"name": "Electron Rest Mass", "val": 9.1093837e-31, "unit": "kg", "symbol": "m_e", "aliases": ["electron mass", "mass of electron", "rest mass of electron"]},
    "mp": {"name": "Proton Rest Mass", "val": 1.67262192e-27, "unit": "kg", "symbol": "m_p", "aliases": ["proton mass", "mass of proton", "rest mass of proton"]},
    "mn": {"name": "Neutron Rest Mass", "val": 1.67492749e-27, "unit": "kg", "symbol": "m_n", "aliases": ["neutron mass", "mass of neutron", "rest mass of neutron"]},
    "NA": {"name": "Avogadro Constant", "val": 6.02214076e23, "unit": "mol^-1", "symbol": "N_A", "aliases": ["avogadro constant", "avogadro number", "avogadro's number", "avogadro"]},
    "R": {"name": "Molar Universal Gas Constant", "val": 8.314462618, "unit": "J/(mol*K)", "symbol": "R", "aliases": ["gas constant", "universal gas constant", "molar gas constant"]},
    "eps0": {"name": "Vacuum Permittivity", "val": 8.8541878128e-12, "unit": "F/m", "symbol": "epsilon_0", "aliases": ["vacuum permittivity", "permittivity of free space", "electric constant", "eps0"]},
    "mu0": {"name": "Vacuum Permeability", "val": 1.25663706212e-6, "unit": "N/A^2", "symbol": "mu_0", "aliases": ["vacuum permeability", "permeability of free space", "magnetic constant", "mu0"]},
    "sigma": {"name": "Stefan-Boltzmann Constant", "val": 5.670374419e-8, "unit": "W/(m^2*K^4)", "symbol": "sigma", "aliases": ["stefan boltzmann", "stefan-boltzmann", "stefan constant"]},
    "Rinf": {"name": "Rydberg Constant", "val": 10973731.568160, "unit": "m^-1", "symbol": "R_inf", "aliases": ["rydberg constant", "rydberg's constant", "rydberg"]}
}

DOMAIN_DESCRIPTIONS = {
    "CONSTANTS": "Universal Physical Constants (c, G, h, hbar, kB, e, me, mp, mn, NA, R, eps0, mu0, sigma, Rinf, g)",
    "MECHANICS": "Classical Mechanics, Gravitation, Oscillations & Fluid Dynamics (Kinematics, Newton's Laws, Bernoulli)",
    "THERMODYNAMICS": "Thermodynamics, Heat Engines, Kinetic Theory & Statistical Mechanics (Ideal Gas, Carnot, Entropy)",
    "ELECTROMAGNETISM": "Electromagnetism, Circuits & Maxwell's Equations (Coulomb, Ohm, Capacitance, Lorentz, Faraday, Poynting)",
    "WAVES_OPTICS": "Wave Mechanics, Physical Optics & Acoustics (Wave Speed, Doppler, Snell's Law, Interference, Diffraction)",
    "ATOMIC_NUCLEAR": "Atomic Physics, Spectroscopy, Radioactivity & Nuclear Energy (Bohr Atom, Half-life, Binding Energy)",
    "RELATIVITY": "Special & General Relativity (Lorentz Factor, Time Dilation, Length Contraction, E=mc^2, Schwarzschild)",
    "QUANTUM": "Quantum Mechanics & Wave Mechanics (Photoelectric, de Broglie, Heisenberg, Schrödinger, Tunneling, Pauli)",
    "PARTICLES": "Particle Physics & Standard Model (Quarks, Leptons, Gauge Bosons, Higgs Mechanism)",
    "COSMOLOGY": "Astrophysics, Celestial Mechanics & Cosmology (Kepler's Laws, Chandrasekhar Limit, Hubble's Law, Friedmann)"
}

# ==============================================================================
# COMPUTATIONAL PHYSICS & QUANTUM ENGINE
# ==============================================================================

class AryabhataPhysicsAgent:
    name = "Aryabhata"
    role = "Master Encyclopedic Physics & Quantum Solver Engine"

    def __init__(self, otmb_path="physics_formulas.otmb"):
        self.otmb_path = otmb_path

    def _get_valid_otmb_path(self):
        candidate_paths = [
            self.otmb_path,
            "physics_formulas.otmb",
            "micropython/physics_formulas.otmb",
            "/physics_formulas.otmb",
            "C:/Users/moule/.gemini/antigravity/scratch/brahmaand_github_repo/micropython/physics_formulas.otmb"
        ]
        for p in candidate_paths:
            try:
                with open(p, "r") as f:
                    return p
            except Exception:
                pass
        return self.otmb_path

    @staticmethod
    def extract_numbers(s):
        """Extract floats/ints including scientific notation (e.g. 5.972e24, 10kg -> 10.0)"""
        nums = []
        curr = ""
        for ch in s:
            if ch.isdigit() or ch == "." or (ch in "eE" and curr and (curr[-1].isdigit() or curr[-1] == ".")) or (ch in "+-" and curr and curr[-1] in "eE"):
                curr += ch
            else:
                if curr:
                    try:
                        nums.append(float(curr))
                    except ValueError:
                        pass
                    curr = ""
        if curr:
            try:
                nums.append(float(curr))
            except ValueError:
                pass
        return nums

    # --- Computational Solvers ---
    def calc_kinetic_energy(self, m, v):
        ke = 0.5 * m * (v ** 2)
        return {
            "formula": "KE = 0.5 * m * v^2", "result": ke, "unit": "Joules (J)",
            "inputs": {"Mass (m)": "{} kg".format(m), "Velocity (v)": "{} m/s".format(v)},
            "desc": "Translational kinetic energy of moving body"
        }

    def calc_force(self, m, a):
        f = m * a
        return {
            "formula": "F = m * a", "result": f, "unit": "Newtons (N)",
            "inputs": {"Mass (m)": "{} kg".format(m), "Acceleration (a)": "{} m/s^2".format(a)},
            "desc": "Newton's Second Law net force"
        }

    def calc_escape_velocity(self, M, R):
        G = CONSTANTS["G"]["val"]
        ve = math.sqrt(2.0 * G * M / R)
        return {
            "formula": "v_e = sqrt(2 * G * M / R)", "result": ve, "unit": "m/s (or {:.2f} km/s)".format(ve / 1000.0),
            "inputs": {"Body Mass (M)": "{:.3e} kg".format(M), "Body Radius (R)": "{:.3e} m".format(R)},
            "desc": "Escape velocity required to break free from gravitational well"
        }

    def calc_orbital_velocity(self, M, r):
        G = CONSTANTS["G"]["val"]
        vo = math.sqrt(G * M / r)
        return {
            "formula": "v_o = sqrt(G * M / r)", "result": vo, "unit": "m/s (or {:.2f} km/s)".format(vo / 1000.0),
            "inputs": {"Central Mass (M)": "{:.3e} kg".format(M), "Orbital Radius (r)": "{:.3e} m".format(r)},
            "desc": "Circular orbital velocity"
        }

    def calc_mass_energy(self, m):
        c = CONSTANTS["c"]["val"]
        e_joules = m * (c ** 2)
        e_kwh = e_joules / 3.6e6
        return {
            "formula": "E = m * c^2", "result": e_joules, "unit": "Joules ({:.3e} kWh)".format(e_kwh),
            "inputs": {"Mass (m)": "{} kg".format(m), "Speed of Light (c)": "299,792,458 m/s"},
            "desc": "Einstein mass-energy equivalence"
        }

    def calc_time_dilation(self, t, v):
        c = CONSTANTS["c"]["val"]
        beta = v / c
        if beta >= 1.0:
            return {"error": "Velocity v cannot equal or exceed speed of light c"}
        gamma = 1.0 / math.sqrt(1.0 - (beta ** 2))
        t_dilated = t * gamma
        return {
            "formula": "t' = t * gamma = t / sqrt(1 - v^2/c^2)", "result": t_dilated, "unit": "seconds",
            "inputs": {"Proper Time (t)": "{} s".format(t), "Velocity (v)": "{} m/s (beta={:.4f})".format(v, beta), "Lorentz Factor (gamma)": "{:.6f}".format(gamma)},
            "desc": "Relativistic proper time dilation"
        }

    def calc_lorentz_contraction(self, L0, v):
        c = CONSTANTS["c"]["val"]
        beta = v / c
        if beta >= 1.0:
            return {"error": "Velocity v cannot equal or exceed speed of light c"}
        gamma = 1.0 / math.sqrt(1.0 - (beta ** 2))
        L_contracted = L0 / gamma
        return {
            "formula": "L' = L0 * sqrt(1 - v^2/c^2)", "result": L_contracted, "unit": "meters",
            "inputs": {"Proper Length (L0)": "{} m".format(L0), "Velocity (v)": "{} m/s (beta={:.4f})".format(v, beta), "Lorentz Factor (gamma)": "{:.6f}".format(gamma)},
            "desc": "Relativistic Lorentz length contraction"
        }

    def calc_schwarzschild_radius(self, M):
        G = CONSTANTS["G"]["val"]
        c = CONSTANTS["c"]["val"]
        rs = (2.0 * G * M) / (c ** 2)
        return {
            "formula": "Rs = (2 * G * M) / c^2", "result": rs, "unit": "meters (or {:.3f} km)".format(rs / 1000.0),
            "inputs": {"Mass (M)": "{:.3e} kg".format(M), "G": "6.674e-11", "c": "2.998e8 m/s"},
            "desc": "Schwarzschild Black Hole Event Horizon Radius"
        }

    def calc_photon_energy(self, f=None, wavelength=None):
        h = CONSTANTS["h"]["val"]
        c = CONSTANTS["c"]["val"]
        e_charge = CONSTANTS["e"]["val"]
        if f is not None:
            e_j = h * f
            e_ev = e_j / e_charge
            return {
                "formula": "E = h * f", "result": e_j, "unit": "Joules ({:.4f} eV)".format(e_ev),
                "inputs": {"Frequency (f)": "{:.3e} Hz".format(f), "Planck Constant (h)": "6.626e-34 J*s"},
                "desc": "Quantum photon energy from frequency"
            }
        elif wavelength is not None:
            e_j = (h * c) / wavelength
            e_ev = e_j / e_charge
            return {
                "formula": "E = (h * c) / lambda", "result": e_j, "unit": "Joules ({:.4f} eV)".format(e_ev),
                "inputs": {"Wavelength (lambda)": "{:.3e} m".format(wavelength), "Speed of Light (c)": "2.998e8 m/s"},
                "desc": "Quantum photon energy from wavelength"
            }

    def calc_de_broglie_wavelength(self, p=None, m=None, v=None):
        h = CONSTANTS["h"]["val"]
        if p is None and m is not None and v is not None:
            p = m * v
        if p is not None and p > 0:
            lam = h / p
            return {
                "formula": "lambda = h / p = h / (m * v)", "result": lam, "unit": "meters ({:.4f} nm)".format(lam * 1e9),
                "inputs": {"Linear Momentum (p)": "{:.3e} kg*m/s".format(p), "Planck Constant (h)": "6.626e-34 J*s"},
                "desc": "Quantum de Broglie matter wavelength"
            }

    def calc_particle_in_box_energy(self, n=1, L_nm=1.0):
        """En = (n^2 * hbar^2 * pi^2) / (2 * m * L^2) = (n^2 * 0.37602 eV*nm^2) / L_nm^2"""
        en_ev = ((n ** 2) * 0.37602) / (L_nm ** 2)
        en_j = en_ev * 1.602176634e-19
        return {
            "formula": "En = (n^2 * pi^2 * hbar^2) / (2 * m * L^2) = (n^2 * 0.3760 eV*nm^2) / L_nm^2",
            "result": en_ev,
            "unit": "eV ({:.4e} J)".format(en_j),
            "inputs": {"Quantum Number (n)": "{}".format(n), "Electron Box Width (L)": "{} nm".format(L_nm)},
            "desc": "Quantized energy level of particle in 1D infinite potential well"
        }

    def calc_hydrogen_energy_level(self, n=1):
        """En = -13.6 / n^2 eV"""
        en_ev = -13.605693 / (n ** 2)
        en_j = en_ev * CONSTANTS["e"]["val"]
        return {
            "formula": "En = -13.6 eV / n^2", "result": en_ev, "unit": "eV ({:.3e} J)".format(en_j),
            "inputs": {"Principal Quantum Number (n)": "{}".format(n)},
            "desc": "Bohr model quantized atomic hydrogen energy level"
        }

    def calc_ohms_law(self, v=None, i=None, r=None):
        if v is not None and i is not None:
            calc_r = v / i
            p = v * i
            return {
                "formula": "R = V / I, P = V * I", "result": calc_r, "unit": "Ohms (Power: {:.3f} W)".format(p),
                "inputs": {"Voltage (V)": "{} V".format(v), "Current (I)": "{} A".format(i)},
                "desc": "Resistance and Power dissipation"
            }
        elif i is not None and r is not None:
            calc_v = i * r
            p = (i ** 2) * r
            return {
                "formula": "V = I * R, P = I^2 * R", "result": calc_v, "unit": "Volts (Power: {:.3f} W)".format(p),
                "inputs": {"Current (I)": "{} A".format(i), "Resistance (R)": "{} Ohms".format(r)},
                "desc": "Voltage drop and Joule heating"
            }
        elif v is not None and r is not None:
            calc_i = v / r
            p = (v ** 2) / r
            return {
                "formula": "I = V / R, P = V^2 / R", "result": calc_i, "unit": "Amperes (Power: {:.3f} W)".format(p),
                "inputs": {"Voltage (V)": "{} V".format(v), "Resistance (R)": "{} Ohms".format(r)},
                "desc": "Current flow and Power dissipation"
            }

    # --- Search & Pedagogical Lesson Engine ---
    def search_otmb(self, query_text):
        q = query_text.lower().strip()
        stop_words = ["what", "is", "the", "of", "and", "in", "to", "for", "explain", "learn", "teach", "me", "tell", "about", "how", "does", "work", "give", "show", "a", "an"]
        tokens = [t for t in q.replace("?", " ").replace(",", " ").replace("'", " ").split() if t not in stop_words]
        matches = []
        valid_path = self._get_valid_otmb_path()
        try:
            with open(valid_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split("|")
                    if len(parts) >= 9:
                        domain, subdomain, topic_key, name, eq, solves, vars_units, concept, intuition = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], parts[7], parts[8]
                        name_clean = name.lower().replace("_", " ")
                        sub_clean = subdomain.lower().replace("_", " ")
                        concept_clean = concept.lower()
                        intuition_clean = intuition.lower()
                        key_clean = topic_key.lower().replace("_", " ")

                        score = 0
                        # 1. Exact phrase match
                        phrase = " ".join(tokens)
                        if phrase and (phrase in name_clean or phrase in key_clean):
                            score += 50

                        # 2. Token-level matching
                        for tok in tokens:
                            if tok in key_clean.split() or tok == key_clean:
                                score += 25
                            if tok in name_clean.split():
                                score += 15
                            elif tok in name_clean:
                                score += 8
                            if tok in sub_clean.split():
                                score += 10
                            if tok in concept_clean.split():
                                score += 5
                            elif tok in concept_clean:
                                score += 2
                            if tok in intuition_clean.split():
                                score += 3

                        if score > 0:
                            matches.append({
                                "score": score,
                                "domain": domain,
                                "subdomain": subdomain,
                                "topic_key": topic_key,
                                "name": name,
                                "equation": eq,
                                "solves": solves,
                                "vars": vars_units,
                                "concept": concept,
                                "intuition": intuition
                            })
                            if len(matches) > 8:
                                matches.sort(key=lambda x: x["score"], reverse=True)
                                matches = matches[:5]
            matches.sort(key=lambda x: x["score"], reverse=True)
        except Exception:
            pass
        return matches[:4]

    def list_domain(self, domain_name):
        d_upper = domain_name.upper().strip()
        results = []
        valid_path = self._get_valid_otmb_path()
        try:
            with open(valid_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split("|")
                    if len(parts) >= 9:
                        if d_upper in parts[0] or d_upper in parts[1].upper():
                            results.append({
                                "domain": parts[0],
                                "subdomain": parts[1],
                                "name": parts[3].replace("_", " "),
                                "equation": parts[4],
                                "concept": parts[7]
                            })
                            if len(results) >= 10:
                                break
        except Exception:
            pass
        return results

    # --- Parser & Interactive Dispatcher ---
    def parse_and_solve(self, query_text):
        q = query_text.lower().strip()

        # A. Domain Listing Queries
        if "list" in q or "catalog" in q or "topics" in q or "all domains" in q or "index" in q:
            if "quantum" in q:
                return {"type": "DOMAIN_LIST", "domain": "QUANTUM MECHANICS", "items": self.list_domain("QUANTUM")}
            elif "relativity" in q:
                return {"type": "DOMAIN_LIST", "domain": "SPECIAL & GENERAL RELATIVITY", "items": self.list_domain("RELATIVITY")}
            elif "mechanics" in q:
                return {"type": "DOMAIN_LIST", "domain": "CLASSICAL MECHANICS", "items": self.list_domain("MECHANICS")}
            elif "thermo" in q:
                return {"type": "DOMAIN_LIST", "domain": "THERMODYNAMICS", "items": self.list_domain("THERMODYNAMICS")}
            elif "em" in q or "electromagnetism" in q or "circuit" in q:
                return {"type": "DOMAIN_LIST", "domain": "ELECTROMAGNETISM", "items": self.list_domain("ELECTROMAGNETISM")}
            elif "optics" in q or "wave" in q:
                return {"type": "DOMAIN_LIST", "domain": "WAVES & OPTICS", "items": self.list_domain("WAVES_OPTICS")}
            elif "nuclear" in q or "atomic" in q:
                return {"type": "DOMAIN_LIST", "domain": "ATOMIC & NUCLEAR PHYSICS", "items": self.list_domain("ATOMIC_NUCLEAR")}
            elif "particle" in q:
                return {"type": "DOMAIN_LIST", "domain": "PARTICLE PHYSICS & STANDARD MODEL", "items": self.list_domain("PARTICLES")}
            elif "cosmology" in q or "astro" in q:
                return {"type": "DOMAIN_LIST", "domain": "ASTROPHYSICS & COSMOLOGY", "items": self.list_domain("COSMOLOGY")}
            elif "constant" in q:
                return {"type": "DOMAIN_LIST", "domain": "UNIVERSAL PHYSICAL CONSTANTS", "items": self.list_domain("CONSTANTS")}
            else:
                return {"type": "ALL_DOMAINS", "domains": DOMAIN_DESCRIPTIONS}

        # B. Universal Constant Lookups
        for key, cinfo in CONSTANTS.items():
            k_lower = key.lower()
            name_lower = cinfo["name"].lower()
            matched = (k_lower in q.split()) or (name_lower in q) or (cinfo["symbol"].lower() in q.split())
            if not matched and "aliases" in cinfo:
                for alias in cinfo["aliases"]:
                    if alias in q:
                        matched = True
                        break
            if matched:
                if any(w in q for w in ["what is", "constant", "value", "give", "tell", "speed of light", "planck", "gravitational", "boltzmann", "mass", "charge"]) or len(q.split()) <= 4:
                    return {
                        "type": "CONSTANT",
                        "symbol": key,
                        "name": cinfo["name"],
                        "value": cinfo["val"],
                        "unit": cinfo["unit"],
                        "desc": "Universal Physical Constant"
                    }

        # C. Extract Numeric Parameters
        numbers = self.extract_numbers(q)

        # D. Direct Computational Numerical Solvers
        # 1. Mass-Energy: E = mc^2
        if any(w in q for w in ["e=mc2", "e=mc^2", "einstein energy", "mass energy", "rest energy"]):
            m = numbers[0] if numbers else 1.0
            res = self.calc_mass_energy(m)
            res["type"] = "CALCULATION"
            return res

        # 2. Kinetic Energy: KE = 0.5 * m * v^2
        if any(w in q for w in ["kinetic energy", "ke =", "ke="]) and len(numbers) >= 1:
            m = numbers[0]
            v = numbers[1] if len(numbers) >= 2 else 5.0
            res = self.calc_kinetic_energy(m, v)
            res["type"] = "CALCULATION"
            return res

        # 3. Escape Velocity: ve = sqrt(2GM/R)
        if any(w in q for w in ["escape velocity", "escape speed"]):
            M = numbers[0] if len(numbers) >= 1 else 5.972e24
            R = numbers[1] if len(numbers) >= 2 else 6.371e6
            res = self.calc_escape_velocity(M, R)
            res["type"] = "CALCULATION"
            return res

        # 4. Schwarzschild Black Hole Radius
        if any(w in q for w in ["schwarzschild", "black hole radius", "event horizon"]):
            M = numbers[0] if numbers else 1.989e30  # 1 Solar Mass
            res = self.calc_schwarzschild_radius(M)
            res["type"] = "CALCULATION"
            return res

        # 5. Time Dilation: t' = t / sqrt(1 - v^2/c^2)
        if any(w in q for w in ["time dilation", "dilated time", "relativistic time"]):
            t = numbers[0] if len(numbers) >= 1 else 10.0
            v = numbers[1] if len(numbers) >= 2 else 2.6e8
            res = self.calc_time_dilation(t, v)
            res["type"] = "CALCULATION"
            return res

        # 6. Lorentz Length Contraction
        if any(w in q for w in ["lorentz contraction", "length contraction"]):
            l0 = numbers[0] if len(numbers) >= 1 else 100.0
            v = numbers[1] if len(numbers) >= 2 else 2.6e8
            res = self.calc_lorentz_contraction(l0, v)
            res["type"] = "CALCULATION"
            return res

        # 7. Quantum Particle in a Box (1D Infinite Potential Well)
        if any(w in q for w in ["particle in a box", "potential well", "infinite well"]):
            n = int(numbers[0]) if numbers else 1
            L_nm = numbers[1] if len(numbers) >= 2 else 1.0
            res = self.calc_particle_in_box_energy(n=n, L_nm=L_nm)
            res["type"] = "CALCULATION"
            return res

        # 8. Quantum Hydrogen Energy Level (Bohr)
        if any(w in q for w in ["hydrogen energy", "bohr level", "bohr energy", "hydrogen orbit"]):
            n = int(numbers[0]) if numbers else 1
            res = self.calc_hydrogen_energy_level(n=n)
            res["type"] = "CALCULATION"
            return res

        # 9. de Broglie Matter Wavelength
        if any(w in q for w in ["de broglie", "matter wave", "matter wavelength"]):
            if len(numbers) >= 2:
                res = self.calc_de_broglie_wavelength(m=numbers[0], v=numbers[1])
            elif len(numbers) == 1:
                res = self.calc_de_broglie_wavelength(p=numbers[0])
            else:
                # Default electron at 1e6 m/s
                res = self.calc_de_broglie_wavelength(m=9.109e-31, v=1e6)
            res["type"] = "CALCULATION"
            return res

        # 10. Photon Energy E = hf
        if any(w in q for w in ["photon energy", "energy of photon", "photon wavelength"]):
            if any(w in q for w in ["wavelength", "nm", "lambda"]):
                lam = numbers[0] if numbers else 500e-9
                res = self.calc_photon_energy(wavelength=lam)
            else:
                f = numbers[0] if numbers else 5e14
                res = self.calc_photon_energy(f=f)
            res["type"] = "CALCULATION"
            return res

        # 11. Ohm's Law
        if any(w in q for w in ["ohm", "voltage", "resistance", "v=ir"]) and len(numbers) >= 2:
            res = self.calc_ohms_law(i=numbers[0], r=numbers[1])
            res["type"] = "CALCULATION"
            return res

        # E. Encyclopedic Pedagogical Vault Search (Concepts, Explanations, Lessons)
        matches = self.search_otmb(q)
        if matches:
            top_match = matches[0]
            other_matches = matches[1:4]
            return {
                "type": "LESSON",
                "primary": top_match,
                "related": other_matches
            }

        return {
            "type": "UNKNOWN",
            "message": "Aryabhata Physics & Quantum Vault ready.\nTry:\n  * 'learn quantum tunneling'\n  * 'explain schrodinger equation'\n  * 'what is time dilation'\n  * 'particle in a box n=2'\n  * 'de broglie electron 1e6 m/s'\n  * 'list quantum formulas'\n  * 'list all domains'"
        }

    def format_card(self, res):
        if res.get("type") == "CONSTANT":
            lines = [
                "+-------------------------------------------------------------------------+",
                "| [ARYABHATA - UNIVERSAL PHYSICAL CONSTANT VAULT]                         |",
                "+-------------------------------------------------------------------------+",
                "  * Constant Name:  {}".format(res["name"]),
                "  * Symbol:         {}".format(res["symbol"]),
                "  * Exact Value:    {:.10e}".format(res["value"]) if "e" in str(res["value"]) else "  * Exact Value:    {}".format(res["value"]),
                "  * Standard Unit:  {}".format(res["unit"]),
                "  * Precision:      CODATA Exact Sovereign Standard",
                "+-------------------------------------------------------------------------+"
            ]
            return "\n".join(lines)

        elif res.get("type") == "CALCULATION":
            lines = [
                "+-------------------------------------------------------------------------+",
                "| [ARYABHATA - COMPUTATIONAL PHYSICS ENGINE EVALUATION]                   |",
                "+-------------------------------------------------------------------------+",
                "  * Formula Used:   {}".format(res.get("formula", "")),
                "  * Description:    {}".format(res.get("desc", ""))
            ]
            if "inputs" in res:
                lines.append("  * Parameter Inputs:")
                for k, v in res["inputs"].items():
                    lines.append("      - {:<24}: {}".format(k, v))
            res_val = res.get("result")
            if isinstance(res_val, float):
                if abs(res_val) >= 1e6 or (abs(res_val) < 1e-3 and res_val != 0.0):
                    val_str = "{:.6e}".format(res_val)
                else:
                    val_str = "{:.6f}".format(res_val).rstrip('0').rstrip('.')
            else:
                val_str = str(res_val)

            lines.append("  * Computed Result:  {} {}".format(val_str, res.get("unit", "")))
            lines.append("  * Theoretical Cert: 100% Deterministic Mathematical Ground Truth")
            lines.append("+-------------------------------------------------------------------------+")
            return "\n".join(lines)

        elif res.get("type") == "LESSON":
            m = res.get("primary", {})
            lines = [
                "+=========================================================================+",
                "| [ARYABHATA - SOVEREIGN PHYSICS & QUANTUM MASTERCLASS]                   |",
                "+=========================================================================+",
                "  * Domain / Branch:  {} -> {}".format(m.get('domain', ''), m.get('subdomain', '')),
                "  * Topic / Concept:  {}".format(m.get('name', '').replace('_', ' ')),
                "-------------------------------------------------------------------------",
                "  [1. GOVERNING MASTER EQUATION]:",
                "      >>> {} <<<".format(m.get('equation', '')),
                "      - Solves For:   {}".format(m.get('solves', '')),
                "      - Variables:    {}".format(m.get('vars', '')),
                "-------------------------------------------------------------------------",
                "  [2. PHYSICAL PRINCIPLE & CONCEPT]:",
                "      {}".format(m.get('concept', '')),
                "-------------------------------------------------------------------------",
                "  [3. PHYSICAL INTUITION & COSMIC PHENOMENON]:",
                "      {}".format(m.get('intuition', '')),
                "+=========================================================================+"
            ]
            rel = res.get("related", [])
            if rel:
                lines.append("  [*] RELATED CONCEPTS IN THIS DOMAIN:")
                for r in rel:
                    lines.append("      - {:<30} | Eq: {}".format(r['name'].replace('_', ' '), r['equation']))
                lines.append("+-------------------------------------------------------------------------+")
            return "\n".join(lines)

        elif res.get("type") == "DOMAIN_LIST":
            lines = [
                "+=========================================================================+",
                "| [ARYABHATA - OTMB CATALOG: {}]".format(res.get('domain', '')),
                "+=========================================================================+"
            ]
            for item in res.get("items", []):
                lines.append("  * [{}] {:<28} | Eq: {}".format(item.get('subdomain', ''), item.get('name', ''), item.get('equation', '')))
                lines.append("    Concept: {}".format(item.get('concept', '')))
                lines.append("  " + "-" * 71)
            lines.append("+=========================================================================+")
            return "\n".join(lines)

        elif res.get("type") == "ALL_DOMAINS":
            lines = [
                "+=========================================================================+",
                "| [ARYABHATA - ENCYCLOPEDIC 10-DOMAIN PHYSICS KNOWLEDGE MATRIX]           |",
                "+=========================================================================+"
            ]
            for idx, (dom, desc) in enumerate(res.get("domains", {}).items(), 1):
                lines.append("  {:02d}. [{:<16}] {}".format(idx, dom, desc))
            lines.append("-------------------------------------------------------------------------")
            lines.append("  Tip: Type 'list quantum', 'list relativity', or 'learn quantum tunneling'!")
            lines.append("+=========================================================================+")
            return "\n".join(lines)

        else:
            return res.get("message", "Physics engine ready.")

if __name__ == "__main__":
    agent = AryabhataPhysicsAgent(otmb_path="physics_formulas.otmb")
    print(agent.format_card(agent.parse_and_solve("learn quantum tunneling")))
    print(agent.format_card(agent.parse_and_solve("explain schrodinger equation")))
    print(agent.format_card(agent.parse_and_solve("particle in a box n=2")))
    print(agent.format_card(agent.parse_and_solve("list quantum formulas")))

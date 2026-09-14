"""About section.

Each string in ABOUT becomes one paragraph, in order.
Write plain text: quotes, accents, & and < are handled for you.

Light formatting is available anywhere text is written on this site:
    **bold**            ->  bold
    *italic*            ->  italic
    [text](https://..)  ->  link

After editing, run:  python3 build.py
"""

ABOUT = [
    """
    Hi! I am a PhD student at the University of Washington, working in the [Brunton lab](https://www.eigensteve.com).
    My main interests are in **data-driven modeling** and **optimization of engineering systems**, particularly within fluid flows and aerodynamics.
    Right now, my research focuses on integrating active learning and multi-fidelity, uncertainty-aware surrogate models 
    to build faster optimization processes,
    but I also bring experience in reduced-order modeling, system identification, and prediction methods for fluid flows.
    """,

    """
    Before the PhD, I worked as an intern in the Aero Science & Technology group at the **Alpine F1 Team**, where I developed data-driven methods
    to improve the pre- and post-processing of Particle Image Velocimetry (PIV) and wind tunnel data. 
    I earned my BSc and MSc in **Aeronautical Engineering** from Universidad Carlos III de Madrid, where my time in the
    [EAP lab](https://aero.uc3m.es/eap-lab/) gave me invaluable experience that shaped my initial path as a researcher.
    I also have a **deep passion for creativity**, and I use my research as a vessel to explore ideas, 
    aiming to make science more approachable through storytelling and visualization.
    """,
]

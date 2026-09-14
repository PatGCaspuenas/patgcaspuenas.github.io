"""News items shown in the sidebar.

Each entry is a dict:

    {"date": "2026-09-01", "text": "What happened."}

Dates are written YYYY-MM-DD and are rendered as the little calendar chip.
The list is sorted newest-first automatically, so you can just add new
items anywhere - the top is the natural place.

Text supports **bold**, *italic* and [links](https://...).

After editing, run:  python3 build.py
"""

NEWS = [
    {"date": "2026-07-27", "text": "📄 Our pre-print on **The balance between compactness and forecast accuracy of data-driven latent-space reduced-order models in controlled wake flows** is now available on arXiv [here](https://doi.org/10.48550/arXiv.2607.24569)!"},
    {"date": "2026-07-01", "text": "📄 Our pre-print on **Active Learning for Calibrating Entangling Gates via Surrogate-Based Optimization** is now available on arXiv [here](https://arxiv.org/abs/2607.00284)!"},
    {"date": "2026-05-28", "text": "✈️ Gave a talk as part of the Brunton Lab on **Active Learning in Engineering Optimization** at the [Boeing Advanced Research Collaboration Annual Symposium](https://www.barc.uw.edu/about/about-the-barc/)."},
    {"date": "2025-10-08", "text": "🎉 Gave a [talk](https://m.youtube.com/watch?v=u7udB6wqvWA&pp=ygUTQ2VydGFtZW4gYXJxdWltZWRlcw%3D%3D) on **Autoencoders for reduction and prediction of fluid flows** at the Spanish national young researchers competition, [Certamen Universitario Arquímedes 2024](https://www.ciencia.gob.es/Convocatorias/2024/Arquimedes2024.html), for which I was awarded the **third prize** in the Engineering and Architecture category!"},
    {"date": "2025-08-08", "text": "📖 Our work on **POD-Galerkin time-supersampling** has just been published in Phys. Rev. Fluids [here](https://doi.org/10.1103/2lqd-g9mt)!"},
    {"date": "2024-11-29", "text": "🎉 Was [awarded](https://coiae.es/premio-mtf-del-master-habilitante-en-ingenieria-aeronautica-de-2024/) with the **Best MSc Thesis** for my work on **Autoencoders for reduction and prediction of fluid flows** by the COIAE (Official College of Aeronautical Engineers in Spain)!"},
]

"""Research section: one tab per topic, any number of projects inside each tab.

TABS is a list of topics. Each topic is a dict:

    {
        "label":    text on the tab button,
        "projects": [ ...list of projects, shown top to bottom... ],
    }

Each project is a dict. Only "title" is required:

    {
        "title":   project title,
        "authors": "A. Author, **P. García Caspueñas**, B. Author"
                   (or a list of names: ["A. Author", "P. García Caspueñas"]).
                   Wrap your own name in ** ** to bold it.
        "year":    2026            - year of publication,
        "tags":    ["POD", "Deep learning"]   - beige chips under the byline,
        "image":   path to the figure, relative to this site
                   (spaces are fine - "images/my photo.jpeg").
                   .png, .jpg, .gif, .webp and .svg are used as they are.
                   A .pdf is converted automatically: build.py writes a
                   .svg next to it and links that instead, so the figure
                   stays vector and is sharp at any size and on any
                   screen. (If no vector converter is installed it falls
                   back to a 300 dpi .png.) The converted file is
                   refreshed whenever the .pdf changes, and both belong
                   in the repository.
        "image_frame": True draws a thin beige border with a little white
                   mat around the figure. Off by default, because most
                   figures already carry their own frame or whitespace
                   and a second one looks like a double border.
        "image_position": "above" (default) puts the figure on its own,
                   full width, above the summary. "left" or "right" puts
                   it in a column beside the summary instead.
        "image_width":  how wide to draw it - "60%", 420, "420px".
                   With "above" this sizes the image (and a figure
                   narrower than the card is centred); with "left" or
                   "right" it sizes the figure column, capped at 70% so
                   the text always keeps a column of its own.
        "image_height": how tall to draw it - "220px".
                   Give just one of width/height and the other follows
                   the aspect ratio; give neither and the figure spans
                   the card. On phones a side figure stacks on top.
        "summary": what the work does and what the key contributions are.
                   A plain string is one paragraph. A list may mix both:
                   a string in it is a paragraph, a nested list is a
                   bullet list, e.g.

                       "summary": [
                           "What the work does, in two or three sentences.",
                           ["First key contribution",
                            "Second key contribution"],
                       ],
        "links":   [ ...optional list of buttons... ],
    }

The card is laid out in this order:

    title  ->  authors · year  ->  tags  ->  figure  ->  summary  ->  links

with "image_position": "left" or "right", the last two share a row:

    title  ->  authors · year  ->  tags  ->  [ figure | summary + links ]

Every field except "title" is optional - leave one out and that row of the
card simply disappears. To show a paper button but no code button, list only
the paper; to show no buttons at all, drop "links" entirely.

Each link is a dict:

    {"label": "Paper", "url": "docs/paper.pdf", "icon": "paper"}

"icon" picks the little glyph. Available names:
    paper, code, slides, poster, video, data, web, doi
(or write a Font Awesome class directly, e.g. "fa-solid fa-flask").

To add a project: copy one of the blocks below and edit it.
To add a tab: copy a whole {...} topic block.
Text supports **bold**, *italic* and [links](https://...).

After editing, run:  python3 build.py
"""

TABS = [
    {
            "label": "Surrogate-based optimization",
            "projects": [
                {
                    "title": "Active Learning for Calibrating Entangling Gates via Surrogate-Based Optimization",
                    "authors": "C. Walton, **P. García Caspueñas**, F. Zacchei, A. Larrañaga, S. L. Brunton, S. Mouradian",
                    "year": 2026,
                    "tags": ["GPR", "Active Learning", "Bayesian Optimization", "Quantum calibration"],
                    "image": "images/QuantumActiveLearning.pdf",
                    "summary": ["""
                        The fidelity of a quantum gate is sensitive to small deviations in the physical 
                        control parameters, and often necessitates on-device calibration. We present 
                        an active learning framework based on Bayesian optimization with a Gaussian Process 
                        surrogate to accelerate the discovery of the optimal parameter set. We validate the technique through numerical 
                        calibration of the laser amplitude and frequencies that implement the trapped-ion Mølmer Sørensen
                        gate.  
                    """,
                    [   
                        "Introduce known heteroskedastic Gaussian Process regression to model the quantum projection noise of the data",
                        "Show that a Gaussian Process can model the Hamiltonian dynamics of a quantum system",
                        "Quantify fidelity limits due to quantum projection noise and design space ranges",
                    ],
                    ],
                    "links": [
                        {"label": "Paper", "url": "https://doi.org/10.48550/arXiv.2607.00284", "icon": "paper"},
                        {"label": "Code", "url": "https://github.com/PatGCaspuenas/QuantumFidelityOptimization", "icon": "code"},
                    ],
                },
            ],
    },
    {
        "label": "Prediction with ROMs",
        "projects": [
            {
                "title": "The balance between compactness and forecast accuracy of data-driven latent-space reduced-order models in controlled wake flows",
                "authors": "A. Solera Rico, **P. García Caspueñas**, C. Sanmiguel Vila, S. Discetti",
                "year": 2026,
                "tags": ["POD", "AE", "LSTM", "Control", "Flow prediction", "DNS"],
                "image": "images/AE-POD.pdf",
                "image_width": "50%",
                "image_position": "left",
                "summary": ["""
                    Within the context of model-based active flow control, we study how the choice of 
                    a Reduced Order Model affects the predictability of the resulting latent coordinates
                    of the high-dimensional velocity fields under control inputs. 
                    Using two actuated 2D wake configurations, a simplified 
                    truck wake and the fluidic pinball, we compare Proper Orthogonal Decomposition 
                    against non-linear Convolutional Autoencoders and two types of variational 
                    autoencoders for compression, and evaluate several temporal predictors based on 
                    Long Short-Term Memory networks. 
                """,
                [
                    "Assess three different temporal predictor architectures for latent-space dynamics",
                    "Evaluate the predictability of the linear or non-linear encoder, revealing a clear trade-off between compactness and forecast accuracy",
                ],
                ],
                "links": [
                    {"label": "Paper", "url": "https://doi.org/10.48550/arXiv.2607.24569", "icon": "paper"},
                ],
            },
            {
                "title": "Model-based time super-sampling of turbulent flow field sequences",
                "authors": "Q. L. Li-Hu, **P. García Caspueñas**, A. Ianiro, S. Discetti",
                "year": 2025,
                "tags": ["POD", "Galerkin", "Flow prediction", "PIV", "DNS"],
                "image": "images/Galerkin-POD.pdf",
                "image_width": "75%",
                "summary": [
                    """We propose a method to increase the temporal resolution of flow field sequences measured at a low sampling rate. 
                    For this purpose, an empirical Galerkin projection of the Navier-Stokes equations on a data-tailored basis (Proper Orthogonal Decomposition) is performed. 
                    Time super-sampling is achieved by a forward-backwards integration of the identified dynamical system, taking the consecutive snapshots as initial conditions. 
                    A Direct Numerical Simulation of the fluidic pinball flow at Re=130 and a Particle Image Velocimetry experiment of a turbulent jet flow at Re=3330 are the benchmarks of this analysis.
                    """,
                    [
                    "Introduce a hybrid time super-sampling technique applicable to experimental data",
                    "Reduce reconstruction errors against interpolation of POD temporal coefficients",
                    "Assess mode truncation and sampling rate effects on the reconstruction accuracy",
                    ]
                ],
                "links": [
                    {"label": "Paper", "url": "https://doi.org/10.1103/2lqd-g9mt", "icon": "paper"},
                    {"label": "Code", "url": "https://github.com/PatGCaspuenas/POD-Galerkin", "icon": "code"},
                ],
            },
        ],
    },
]

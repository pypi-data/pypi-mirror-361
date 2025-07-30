# ViVa-SAFELAND

[![PyPI version](https://badge.fury.io/py/viva_safeland.svg)](https://badge.fury.io/py/viva-safeland)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/pypi/pyversions/viva_safeland.svg)](https://pypi.org/project/viva-safeland)

<!-- <figure markdown="span"> -->
  ![ViVa SAFELAND](assets/viva.png)
  <!-- <figcaption>ViVa-SAFELAND: a Visual Validation Safe Landing tool</figcaption>
</figure> -->

**ViVa-SAFELAND** is an open-source framework for testing and evaluating vision-based navigation strategies for aerial vehicles, with a special focus on autonomous landing in compliance with safety regulations.

This documentation contains the official implementation for the paper "[ViVa-SAFELAND: A New Freeware for Safe Validation of Vision-based Navigation in Aerial Vehicles](https://arxiv.org/abs/2503.14719)". It provides a safe, simple, and fair comparison baseline to evaluate and compare different visual navigation solutions under the same conditions.

<!-- <figure markdown="span"> -->
  ![ViVa SAFELAND](assets/viva_operation.png)
  <!-- <figcaption>Example of ViVa-SAFELAND operation</figcaption> -->
<!-- </figure> -->

## Key Features

-   **Real-World Scenarios:** Utilize a collection of high-definition aerial videos from unstructured urban environments, including dynamic obstacles like cars and people.
-   **Emulated Aerial Vehicle (EAV):** Navigate within video scenarios using a virtual moving camera that responds to high-level commands.
-   **Standardized Evaluation:** Provides a safe and fair baseline for comparing different visual navigation solutions under identical, repeatable conditions.
-   **Development & Data Generation:** Facilitates the rapid development of autonomous landing strategies and the creation of custom image datasets for training machine learning models.
-   **Safety-Focused:** Enables rigorous testing and debugging of navigation logic in a simulated environment, eliminating risks to hardware and ensuring compliance with safety regulations.

## Documentation
For detailed usage instructions, examples, and API documentation, please refer to the [ViVa-SAFELAND Documentation](https://juliodltv.github.io/viva_safeland/).
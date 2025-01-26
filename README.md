# LLM Twin pipeline

## Architecture notes

### System architecture

We use the 3-pipeline architecture, also known as FTI architecture (Feature/Training/Inference). It is a well-known design pattern for machine learning systems. This architecture divides the ML system into three main components:

![3-pipeline-architecture](src/diagrams/three-pipeline-design.svg)

The advances of FTI architecture are:
* It brings structure to your ML systems; basically, all ML systems can be reduced to these three components.
* It defines a transparent interface between the three components.
* The ML system is built with modularity in mind from the beginning.
* Any component can use the best stack of technologies.
* Any component can be deployed, scaled, and monitored independently.

System architecture:

![System architecture](src/diagrams/architecture.svg)

#### Data pipeline

The data collection pipeline contains ETLs that load, clean, normalize, and store the input data in a NoSQL database. The data sources include multiple social media platforms and blog platforms. Finally, the data is stored in the message broker for processing by the feature pipeline using the CDC pattern.

| Note: The data collection pipeline isn't directly part of the FTI architecture. For large systems, the data team is responsible for this part of the pipeline.   

#### Feature pipeline

> will be used to create features from the input data

#### Training pipeline

> will take features and labels (in case of supervised learning) and create models

#### Inference pipeline

> will take features and models and make predictions


